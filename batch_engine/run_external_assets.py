import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from image_engine.builder import ImageBuilder
from gamma_engine.builder import GammaBuilder

from build_registry import (
    get_build_request,
    get_build_request_items,
    set_batch_status,
    update_build_request_item,
)


def read_json(path):
    return json.loads(
        Path(path).read_text(encoding="utf-8")
    )


def build_plan(rid):
    request = get_build_request(rid)

    if request is None:
        raise RuntimeError(
            "Request not found: " + rid
        )

    if request["status"] != "BATCH_STAGE2_APPLIED":
        raise RuntimeError(
            "Expected BATCH_STAGE2_APPLIED, found "
            + str(request["status"])
        )

    batch_dir = ROOT / "data" / "batches" / rid

    prepare = read_json(
        batch_dir / "prepare_state.json"
    )

    applied = read_json(
        batch_dir / "stage2_applied.json"
    )

    children = {
        int(x["id"]): x
        for x in get_build_request_items(rid)
    }

    images = {
        x["lesson_package_id"]: x
        for x in applied["entries"]
        if x["prompt_type"] == "IMAGE_PROMPT"
    }

    plan = []

    for item in prepare["prepared_lessons"]:
        item_id = int(item["item_id"])
        child = children[item_id]

        rows = item["lesson_rows"]

        if len(rows) != 1:
            raise RuntimeError(
                "Unexpected lesson row count."
            )

        package = rows[0]["lesson_package_id"]
        image = images[package]

        workbook = Path(
            item["workbook_path"]
        )

        build_name = workbook.stem
        build_root = workbook.parent.parent

        image_prompt = Path(
            image["prompt_file"]
        )

        gamma_prompt = (
            build_root
            / "Prompts"
            / build_name
            / "gamma_slides.md"
        )

        gamma_metadata = (
            build_root
            / "Prompts"
            / build_name
            / "gamma_slides.json"
        )

        required = [
            workbook,
            image_prompt,
            gamma_prompt,
            gamma_metadata,
        ]

        for path in required:
            if not path.is_file():
                raise RuntimeError(
                    "Missing: " + str(path)
                )

        plan.append({
            "item_id": item_id,
            "package": package,
            "curriculum_code":
                child["curriculum_code"],
            "parent_code":
                child["parent_code"],
            "elaboration":
                child["lesson_text"],
            "build_root":
                str(build_root),
            "build_name":
                build_name,
            "workbook":
                str(workbook),
            "image_prompt":
                str(image_prompt),
            "image_model":
                image.get("model") or "",
            "gamma_prompt":
                str(gamma_prompt),
            "gamma_metadata":
                str(gamma_metadata),
        })

    if not plan:
        raise RuntimeError(
            "No lessons available for external assets."
        )

    return plan


def load_state(rid, plan):
    path = (
        ROOT / "data" / "batches"
        / rid / "external_assets_state.json"
    )

    if path.is_file():
        state = read_json(path)

        changed = False

        for item in plan:
            package = item["package"]

            lesson_state = (
                state.get("lessons", {})
                .get(package)
            )

            if lesson_state is None:
                continue

            if lesson_state.get("item_id") is None:
                lesson_state["item_id"] = (
                    item["item_id"]
                )
                changed = True

        if changed:
            save_state(
                path,
                state
            )

            print(
                "EXTERNAL STATE UPGRADED "
                "WITH ITEM IDS"
            )

        return path, state

    state = {
        "request_id": rid,
        "lessons": {}
    }

    for item in plan:
        state["lessons"][item["package"]] = {
            "item_id":
                item["item_id"],
            "curriculum_code":
                item["curriculum_code"],
            "image": {
                "status": "PENDING",
                "result": None,
                "error": None,
            },
            "gamma": {
                "status": "PENDING",
                "result": None,
                "error": None,
            },
        }

    path.write_text(
        json.dumps(
            state,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    return path, state


def save_state(path, state):
    path.write_text(
        json.dumps(
            state,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )


def run_images(plan, state_path, state):
    builder = ImageBuilder()

    for item in plan:
        package = item["package"]
        asset = state["lessons"][package]["image"]

        if asset["status"] == "COMPLETED":
            print("IMAGE SKIP:", package, "already completed")
            continue

        print()
        print("IMAGE START:", package)

        prompt = Path(
            item["image_prompt"]
        ).read_text(
            encoding="utf-8"
        ).strip()

        asset["status"] = "RUNNING"
        asset["error"] = None
        save_state(state_path, state)

        try:
            result = builder.generate_from_batch_prompt(
                build_root=item["build_root"],
                build_name=item["build_name"],
                lesson_package_id=package,
                parent_code=item["parent_code"],
                curriculum_code=item["curriculum_code"],
                elaboration=item["elaboration"],
                final_prompt=prompt,
                text_model=item["image_model"],
                force_regenerate=False,
            )

            asset["status"] = "COMPLETED"
            asset["result"] = result
            asset["error"] = None

            save_state(state_path, state)

            print("IMAGE COMPLETED:", package)

        except Exception as exc:
            asset["status"] = "FAILED"
            asset["error"] = str(exc)

            save_state(state_path, state)

            print("IMAGE FAILED:", package)
            print("ERROR:", exc)

            raise


def run_gamma(plan, state_path, state):
    builder = GammaBuilder()

    for item in plan:
        package = item["package"]
        asset = state["lessons"][package]["gamma"]

        if asset["status"] == "COMPLETED":
            print("GAMMA SKIP:", package, "already completed")
            continue

        print()
        print("GAMMA START:", package)

        asset["status"] = "RUNNING"
        asset["error"] = None
        save_state(state_path, state)

        try:
            result = builder.generate(
                build_root=item["build_root"],
                build_name=item["build_name"],
                lesson_package_id=package,
            )

            asset["status"] = "COMPLETED"
            asset["result"] = result
            asset["error"] = None

            save_state(state_path, state)

            print("GAMMA COMPLETED:", package)

        except Exception as exc:
            asset["status"] = "FAILED"
            asset["error"] = str(exc)

            save_state(state_path, state)

            print("GAMMA FAILED:", package)
            print("ERROR:", exc)

            raise


def finalize_assets(rid, state):
    incomplete = []

    for package, lesson in state["lessons"].items():
        for asset_type in ("image", "gamma"):
            status = lesson[asset_type]["status"]

            if status != "COMPLETED":
                incomplete.append(
                    package + ":" + asset_type + "=" + str(status)
                )

    if incomplete:
        raise RuntimeError(
            "External assets incomplete: "
            + ", ".join(incomplete)
        )

    for package, lesson in state["lessons"].items():
        item_id = lesson.get("item_id")

        if item_id is None:
            raise RuntimeError(
                "Missing item_id for external asset "
                "state: " + package
            )

        update_build_request_item(
            item_id,
            "ASSETS_READY",
            "Images and presentation completed.",
            90
        )

        print(
            "CHILD PROGRESS:",
            item_id,
            "ASSETS_READY",
            "90%"
        )

    if not set_batch_status(
        rid,
        "EXTERNAL_ASSETS_COMPLETED"
    ):
        raise RuntimeError(
            "Could not set EXTERNAL_ASSETS_COMPLETED."
        )

    print("REGISTRY: EXTERNAL_ASSETS_COMPLETED")


def main(
        rid,
        run_images_flag=False,
        run_gamma_flag=False,
        finalize_flag=False
):
    plan = build_plan(rid)

    state_path, state = load_state(
        rid,
        plan
    )

    print("STATE:", state_path)

    print("=" * 70)
    print("EXTERNAL ASSET VALIDATION")
    print("REQUEST:", rid)

    for item in plan:
        image_text = Path(
            item["image_prompt"]
        ).read_text(
            encoding="utf-8"
        ).strip()

        gamma_text = Path(
            item["gamma_prompt"]
        ).read_text(
            encoding="utf-8"
        ).strip()

        if not image_text:
            raise RuntimeError(
                "Empty image prompt."
            )

        if not gamma_text:
            raise RuntimeError(
                "Empty Gamma prompt."
            )

        print()
        print("PACKAGE:", item["package"])
        print(
            "CURRICULUM:",
            item["curriculum_code"]
        )
        print(
            "BUILD:",
            item["build_name"]
        )
        print(
            "IMAGE PROMPT:",
            len(image_text),
            "chars"
        )
        print(
            "GAMMA PROMPT:",
            len(gamma_text),
            "chars"
        )

    print()
    print("VALIDATION: PASS")

    if (
        not run_images_flag
        and not run_gamma_flag
        and not finalize_flag
    ):
        print("NO EXTERNAL API CALLS MADE")
        return 0

    if run_images_flag:
        run_images(
            plan,
            state_path,
            state
        )

        print()
        print("IMAGE PHASE COMPLETE")

    if run_gamma_flag:
        run_gamma(
            plan,
            state_path,
            state
        )

        print()
        print("GAMMA PHASE COMPLETE")

    if finalize_flag:
        finalize_assets(
            rid,
            state
        )

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("request_id")
    parser.add_argument(
        "--run-images",
        action="store_true"
    )

    parser.add_argument(
        "--run-gamma",
        action="store_true"
    )

    parser.add_argument(
        "--finalize",
        action="store_true"
    )

    args = parser.parse_args()

    raise SystemExit(
        main(
            args.request_id,
            run_images_flag=args.run_images,
            run_gamma_flag=args.run_gamma,
            finalize_flag=args.finalize,
        )
    )
