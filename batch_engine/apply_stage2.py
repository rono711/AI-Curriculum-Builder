import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from batch_engine.apply_stage1 import extract_text
from quiz_engine.builder import QuizBuilder
from activities_engine.builder import ActivitiesBuilder
from recap_engine.builder import RecapBuilder
from build_registry import (
    get_build_request,
    get_build_request_items,
    set_batch_status,
)


EXPECTED_TYPES = (
    "QUIZ",
    "ACTIVITIES",
    "RECAP",
    "IMAGE_PROMPT",
)

DESCRIPTION_FILES = {
    "QUIZ":
        "checking_your_thinking.json",
    "ACTIVITIES":
        "lets_do_it.json",
    "RECAP":
        "what_we_discovered.json",
}


def load_json(path):
    return json.loads(
        Path(path).read_text(
            encoding="utf-8"
        )
    )


def load_jsonl(path):
    rows = []

    with Path(path).open(
        encoding="utf-8"
    ) as handle:
        for line in handle:
            if line.strip():
                rows.append(
                    json.loads(line)
                )

    return rows


def validate_batch_files(
        manifest,
        output_rows
):
    entries = manifest.get("entries") or []

    expected = {
        row["custom_id"]
        for row in entries
    }

    returned = [
        row.get("custom_id")
        for row in output_rows
    ]

    actual = set(returned)

    if len(entries) != 8:
        raise RuntimeError(
            "Stage 2 manifest must contain "
            "exactly 8 entries."
        )

    if len(output_rows) != 8:
        raise RuntimeError(
            "Stage 2 output must contain "
            "exactly 8 rows."
        )

    if len(actual) != 8:
        raise RuntimeError(
            "Stage 2 output contains "
            "duplicate custom IDs."
        )

    if expected != actual:
        raise RuntimeError(
            "Stage 2 manifest/output "
            "identity mismatch."
        )

    types = Counter(
        row["prompt_type"]
        for row in entries
    )

    required = Counter({
        "QUIZ": 2,
        "ACTIVITIES": 2,
        "RECAP": 2,
        "IMAGE_PROMPT": 2,
    })

    if types != required:
        raise RuntimeError(
            "Unexpected Stage 2 result types: "
            + str(dict(types))
        )

    return entries


def build_lesson_map(
        request_id,
        prepare_state
):
    children = {
        int(row["id"]): row
        for row in get_build_request_items(
            request_id
        )
    }

    lessons = {}

    prepared_lessons = (
        prepare_state.get(
            "prepared_lessons"
        )
        or []
    )

    for prepared in prepared_lessons:
        item_id = int(
            prepared["item_id"]
        )

        child = children.get(
            item_id
        )

        if child is None:
            raise RuntimeError(
                "Missing child item: "
                + str(item_id)
            )

        lesson_rows = (
            prepared.get("lesson_rows")
            or []
        )

        if len(lesson_rows) != 1:
            raise RuntimeError(
                "Expected exactly one lesson row "
                "for item "
                + str(item_id)
            )

        package_id = str(
            lesson_rows[0][
                "lesson_package_id"
            ]
        ).strip()

        workbook_path = Path(
            prepared["workbook_path"]
        )

        if not workbook_path.is_file():
            raise RuntimeError(
                "Workbook missing: "
                + str(workbook_path)
            )

        lessons[package_id] = {
            "item_id":
                item_id,
            "lesson_package_id":
                package_id,
            "parent_code":
                str(
                    child["parent_code"]
                ).strip(),
            "curriculum_code":
                str(
                    child["curriculum_code"]
                ).strip(),
            "lesson_number":
                int(
                    child["lesson_number"]
                ),
            "topic_id":
                child["topic_id"],
            "lesson_text":
                str(
                    child["lesson_text"]
                    or ""
                ).strip(),
            "workbook_path":
                str(workbook_path),
        }

    if len(lessons) != 2:
        raise RuntimeError(
            "Expected exactly 2 Stage 2 lessons; "
            "found "
            + str(len(lessons))
        )

    return lessons


def prepare_results(
        manifest,
        output_rows,
        lessons
):
    manifest_by_id = {
        row["custom_id"]: row
        for row in manifest["entries"]
    }

    grouped = {}

    for row in output_rows:
        custom_id = row["custom_id"]

        entry = manifest_by_id[
            custom_id
        ]

        package_id = str(
            entry["lesson_package_id"]
        ).strip()

        prompt_type = str(
            entry["prompt_type"]
        ).strip().upper()

        if package_id not in lessons:
            raise RuntimeError(
                "Unknown lesson package: "
                + package_id
            )

        response = row.get(
            "response"
        ) or {}

        if response.get("status_code") != 200:
            raise RuntimeError(
                custom_id
                + ": HTTP "
                + str(
                    response.get(
                        "status_code"
                    )
                )
            )

        body = response.get(
            "body"
        ) or {}

        if body.get("status") != "completed":
            raise RuntimeError(
                custom_id
                + ": response status "
                + str(
                    body.get("status")
                )
            )

        text = extract_text(
            body
        ).strip()

        if not text:
            raise RuntimeError(
                custom_id
                + ": empty result text"
            )

        grouped.setdefault(
            package_id,
            {}
        )[prompt_type] = {
            "text":
                text,
            "model":
                body.get("model") or "",
            "custom_id":
                custom_id,
        }

    for package_id, results in grouped.items():
        missing = (
            set(EXPECTED_TYPES)
            - set(results)
        )

        if missing:
            raise RuntimeError(
                package_id
                + " missing result types: "
                + str(sorted(missing))
            )

    return grouped


def load_descriptions(
        workbook_path
):
    workbook = Path(
        workbook_path
    )

    build_root = (
        workbook.parent.parent
    )

    build_name = workbook.stem

    content_folder = (
        build_root
        / "Content"
        / build_name
    )

    descriptions = {}

    for prompt_type, filename in (
        DESCRIPTION_FILES.items()
    ):
        path = (
            content_folder
            / filename
        )

        if not path.is_file():
            raise RuntimeError(
                "Description file missing: "
                + str(path)
            )

        data = load_json(
            path
        )

        markdown = str(
            data.get("markdown")
            or ""
        ).strip()

        if not markdown:
            raise RuntimeError(
                "Description markdown empty: "
                + str(path)
            )

        descriptions[
            prompt_type
        ] = markdown

    return descriptions


def stage_image_prompt(
        workbook_path,
        curriculum_code,
        prompt
):
    workbook = Path(
        workbook_path
    )

    build_root = (
        workbook.parent.parent
    )

    build_name = workbook.stem

    folder = (
        build_root
        / "Images"
        / build_name
    )

    folder.mkdir(
        parents=True,
        exist_ok=True
    )

    path = (
        folder
        / (
            str(curriculum_code)
            + "_batch_prompt.md"
        )
    )

    path.write_text(
        str(prompt).strip(),
        encoding="utf-8"
    )

    return str(path)


def main(
        request_id,
        validate_only=False
):
    rid = str(
        request_id
    ).strip()

    request = get_build_request(
        rid
    )

    if request is None:
        raise RuntimeError(
            "Build request does not exist: "
            + rid
        )

    if request["status"] != (
        "BATCH_STAGE2_DOWNLOADED"
    ):
        raise RuntimeError(
            "Request must be "
            "BATCH_STAGE2_DOWNLOADED; found "
            + str(request["status"])
        )

    batch_dir = (
        ROOT
        / "data"
        / "batches"
        / rid
    )

    manifest_file = (
        batch_dir
        / "stage2_manifest.json"
    )

    output_file = (
        batch_dir
        / "stage2_output.jsonl"
    )

    prepare_file = (
        batch_dir
        / "prepare_state.json"
    )

    applied_file = (
        batch_dir
        / "stage2_applied.json"
    )

    if applied_file.exists():
        raise RuntimeError(
            "Stage 2 has already been applied."
        )

    for path in (
        manifest_file,
        output_file,
        prepare_file,
    ):
        if not path.is_file():
            raise RuntimeError(
                "Required Stage 2 file missing: "
                + str(path)
            )

    manifest = load_json(
        manifest_file
    )

    prepare_state = load_json(
        prepare_file
    )

    output_rows = load_jsonl(
        output_file
    )

    validate_batch_files(
        manifest,
        output_rows
    )

    lessons = build_lesson_map(
        rid,
        prepare_state
    )

    grouped = prepare_results(
        manifest,
        output_rows,
        lessons
    )

    print("=" * 70)
    print("STAGE 2 APPLICATION VALIDATION")
    print("REQUEST:", rid)
    print("=" * 70)

    for package_id in sorted(
        lessons
    ):
        lesson = lessons[
            package_id
        ]

        results = grouped[
            package_id
        ]

        descriptions = (
            load_descriptions(
                lesson["workbook_path"]
            )
        )

        print()
        print("PACKAGE:", package_id)
        print(
            "CURRICULUM:",
            lesson["curriculum_code"]
        )
        print(
            "WORKBOOK:",
            lesson["workbook_path"]
        )

        for prompt_type in (
            EXPECTED_TYPES
        ):
            print(
                prompt_type,
                "CHARS:",
                len(
                    results[
                        prompt_type
                    ]["text"]
                )
            )

        print(
            "QUIZ DESCRIPTION:",
            len(descriptions["QUIZ"])
        )
        print(
            "ACTIVITIES DESCRIPTION:",
            len(
                descriptions[
                    "ACTIVITIES"
                ]
            )
        )
        print(
            "RECAP DESCRIPTION:",
            len(
                descriptions["RECAP"]
            )
        )

    if validate_only:
        print()
        print("=" * 70)
        print("VALIDATION OVERALL: PASS")
        print("NO FILES OR WORKBOOKS MODIFIED")
        print("=" * 70)
        return 0

    applied = []

    quiz_builder = QuizBuilder()
    activities_builder = ActivitiesBuilder()
    recap_builder = RecapBuilder()

    for package_id in sorted(lessons):
        lesson = lessons[package_id]
        results = grouped[package_id]

        descriptions = load_descriptions(
            lesson["workbook_path"]
        )

        quiz = results["QUIZ"]

        quiz_result = (
            quiz_builder.apply_batch_result(
                workbook_path=
                    lesson["workbook_path"],
                lesson_package_id=
                    package_id,
                content=
                    quiz["text"],
                description=
                    descriptions["QUIZ"],
                model=
                    quiz["model"],
            )
        )

        print(
            "APPLIED:",
            package_id,
            "QUIZ"
        )

        applied.append({
            "lesson_package_id":
                package_id,
            "curriculum_code":
                lesson["curriculum_code"],
            "prompt_type":
                "QUIZ",
            "status":
                quiz_result["status"],
        })

        activities = results[
            "ACTIVITIES"
        ]

        activities_result = (
            activities_builder.apply_batch_result(
                workbook_path=
                    lesson["workbook_path"],
                lesson_package_id=
                    package_id,
                content=
                    activities["text"],
                description=
                    descriptions["ACTIVITIES"],
                model=
                    activities["model"],
            )
        )

        print(
            "APPLIED:",
            package_id,
            "ACTIVITIES"
        )

        applied.append({
            "lesson_package_id":
                package_id,
            "curriculum_code":
                lesson["curriculum_code"],
            "prompt_type":
                "ACTIVITIES",
            "status":
                activities_result["status"],
        })

        recap = results["RECAP"]

        recap_result = (
            recap_builder.apply_batch_result(
                workbook_path=
                    lesson["workbook_path"],
                lesson_package_id=
                    package_id,
                content=
                    recap["text"],
                description=
                    descriptions["RECAP"],
                model=
                    recap["model"],
            )
        )

        print(
            "APPLIED:",
            package_id,
            "RECAP"
        )

        applied.append({
            "lesson_package_id":
                package_id,
            "curriculum_code":
                lesson["curriculum_code"],
            "prompt_type":
                "RECAP",
            "status":
                recap_result["status"],
        })

        image_prompt = results[
            "IMAGE_PROMPT"
        ]

        image_prompt_file = (
            stage_image_prompt(
                lesson["workbook_path"],
                lesson["curriculum_code"],
                image_prompt["text"],
            )
        )

        print(
            "STAGED:",
            package_id,
            "IMAGE_PROMPT"
        )

        applied.append({
            "lesson_package_id":
                package_id,
            "curriculum_code":
                lesson["curriculum_code"],
            "prompt_type":
                "IMAGE_PROMPT",
            "status":
                "STAGED",
            "prompt_file":
                image_prompt_file,
            "model":
                image_prompt["model"],
        })

    applied_file.write_text(
        json.dumps(
            {
                "request_id": rid,
                "count": len(applied),
                "entries": applied,
            },
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    if not set_batch_status(
        rid,
        "BATCH_STAGE2_APPLIED"
    ):
        raise RuntimeError(
            "Stage 2 results were applied, but "
            "registry could not transition to "
            "BATCH_STAGE2_APPLIED."
        )

    print()
    print("=" * 70)
    print("STAGE 2 APPLIED:", len(applied))
    print("LOCAL COMPONENTS: 6")
    print("IMAGE PROMPTS STAGED: 2")
    print("REGISTRY: BATCH_STAGE2_APPLIED")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "request_id"
    )

    parser.add_argument(
        "--validate-only",
        action="store_true"
    )

    args = parser.parse_args()

    raise SystemExit(
        main(
            args.request_id,
            validate_only=args.validate_only
        )
    )
