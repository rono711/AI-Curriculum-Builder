import json
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from batch_engine.stage2_builder import Stage2BatchBuilder
from build_registry import (
    get_build_request,
    get_build_request_items,
    set_batch_status,
)

PROMPT_URL = "http://prompt-engine:8005/prompt"

PREPARE_TYPES = (
    "GAMMA_SLIDES",
    "QUIZ",
    "ACTIVITIES",
    "RECAP",
    "IMAGE",
)

OPENAI_TYPES = (
    "QUIZ",
    "ACTIVITIES",
    "RECAP",
)


def prepare_prompt(
        client,
        workbook_path,
        lesson_package_id,
        prompt_type
):
    response = client.post(
        PROMPT_URL,
        json={
            "workbook_path": workbook_path,
            "lesson_package_id": lesson_package_id,
            "prompt_type": prompt_type,
            "generation_mode": "BATCH_PREPARE",
        },
        timeout=600,
    )

    response.raise_for_status()
    result = response.json()

    if result.get("status") != "SUCCESS":
        raise RuntimeError(
            "Prompt preparation failed: "
            + str(result)
        )

    if result.get("ai") is not None:
        raise RuntimeError(
            "Unexpected AI result during Stage 2: "
            + prompt_type
        )

    return result


def main(request_id):
    rid = str(request_id).strip()

    request = get_build_request(rid)

    if request is None:
        raise RuntimeError(
            "Build request does not exist: " + rid
        )

    if request["processing_mode"] != "QUEUE_BATCH":
        raise RuntimeError(
            "Request is not QUEUE_BATCH: " + rid
        )

    if request["status"] != "BATCH_STAGE1_APPLIED":
        raise RuntimeError(
            "Request must be BATCH_STAGE1_APPLIED; "
            "found " + str(request["status"])
        )

    batch_dir = ROOT / "data" / "batches" / rid

    stage1_state_file = (
        batch_dir / "prepare_state.json"
    )
    stage2_state_file = (
        batch_dir / "stage2_prepare_state.json"
    )
    stage2_input_file = (
        batch_dir / "stage2_input.jsonl"
    )
    stage2_manifest_file = (
        batch_dir / "stage2_manifest.json"
    )

    if not stage1_state_file.is_file():
        raise RuntimeError(
            "Stage 1 prepare state missing."
        )

    if (
        stage2_state_file.exists()
        or stage2_input_file.exists()
        or stage2_manifest_file.exists()
    ):
        raise RuntimeError(
            "Stage 2 preparation already exists."
        )

    stage1_state = json.loads(
        stage1_state_file.read_text(
            encoding="utf-8"
        )
    )

    prepared_lessons = (
        stage1_state.get("prepared_lessons")
        or []
    )

    if not prepared_lessons:
        raise RuntimeError(
            "No prepared lessons found."
        )

    child_items = {
        int(row["id"]): row
        for row in get_build_request_items(rid)
    }

    batch_prompt_results = []
    all_prepared_prompts = []

    with httpx.Client(timeout=1800) as client:

        for lesson in prepared_lessons:
            item_id = lesson.get("item_id")

            child = (
                child_items.get(int(item_id))
                if item_id is not None
                else None
            )

            if child is None:
                raise RuntimeError(
                    "No child item for item_id "
                    + str(item_id)
                )

            workbook_path = str(
                lesson["workbook_path"]
            )

            lesson_rows = (
                lesson.get("lesson_rows") or []
            )

            if len(lesson_rows) != 1:
                raise RuntimeError(
                    "Expected one lesson row for "
                    + str(item_id)
                )

            lesson_package_id = str(
                lesson_rows[0]["lesson_package_id"]
            ).strip()

            curriculum_code = str(
                child["curriculum_code"]
            ).strip()

            lesson_text = str(
                child["lesson_text"] or ""
            ).strip()

            if not lesson_text:
                raise RuntimeError(
                    "Empty lesson_text for "
                    + curriculum_code
                )

            print("=" * 60)
            print("STAGE 2 LESSON:", curriculum_code)
            print("PACKAGE:", lesson_package_id)
            print("=" * 60)

            prepared_by_type = {}

            for prompt_type in PREPARE_TYPES:
                result = prepare_prompt(
                    client,
                    workbook_path,
                    lesson_package_id,
                    prompt_type,
                )

                prepared_by_type[prompt_type] = result

                all_prepared_prompts.append({
                    "lesson_package_id":
                        lesson_package_id,
                    "curriculum_code":
                        curriculum_code,
                    "prompt_type":
                        prompt_type,
                    "prompt_file":
                        result["prompt_file"],
                    "metadata_file":
                        result["metadata_file"],
                })

                print("PREPARED:", prompt_type)

            for prompt_type in OPENAI_TYPES:
                result = prepared_by_type[
                    prompt_type
                ]

                batch_prompt_results.append({
                    "lesson_package_id":
                        lesson_package_id,
                    "curriculum_code":
                        curriculum_code,
                    "prompt_type":
                        prompt_type,
                    "source_prompt_type":
                        prompt_type,
                    "prompt":
                        result["prompt"],
                    "prompt_file":
                        result["prompt_file"],
                    "metadata_file":
                        result["metadata_file"],
                    "workbook_path":
                        workbook_path,
                })

            image_result = prepared_by_type["IMAGE"]

            image_prompt = str(
                image_result["prompt"]
            )

            image_prompt += (
                "\n\nCURRENT LESSON IDENTITY\n\n"
                "Curriculum code:\n"
                + curriculum_code
                + "\n\nSpecific Elaboration:\n"
                + lesson_text
                + "\n\nGenerate the image for this "
                "specific Elaboration.\n"
            )

            batch_prompt_results.append({
                "lesson_package_id":
                    lesson_package_id,
                "curriculum_code":
                    curriculum_code,
                "prompt_type":
                    "IMAGE_PROMPT",
                "source_prompt_type":
                    "IMAGE",
                "prompt":
                    image_prompt,
                "prompt_file":
                    image_result["prompt_file"],
                "metadata_file":
                    image_result["metadata_file"],
                "workbook_path":
                    workbook_path,
            })

    batch = Stage2BatchBuilder().build(
        request_id=rid,
        prompt_results=batch_prompt_results,
        output_root=ROOT / "data" / "batches",
    )

    state = {
        "request_id": rid,
        "prepared_lesson_count":
            len(prepared_lessons),
        "prepared_prompt_count":
            len(all_prepared_prompts),
        "batch_request_count":
            batch["request_count"],
        "prepared_prompts":
            all_prepared_prompts,
        "stage2":
            batch,
    }

    stage2_state_file.write_text(
        json.dumps(
            state,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8",
    )

    if not set_batch_status(
        rid,
        "BATCH_STAGE2_READY"
    ):
        raise RuntimeError(
            "Could not transition to "
            "BATCH_STAGE2_READY."
        )

    print("=" * 60)
    print("BATCH STAGE 2 READY")
    print("REQUEST:", rid)
    print("LESSONS:", len(prepared_lessons))
    print(
        "PROMPTS PREPARED:",
        len(all_prepared_prompts)
    )
    print(
        "OPENAI REQUESTS:",
        batch["request_count"]
    )
    print("INPUT:", batch["input_file"])
    print("REGISTRY: BATCH_STAGE2_READY")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python3 "
            "batch_engine/prepare_stage2.py "
            "<REQUEST_ID>"
        )

    raise SystemExit(main(sys.argv[1]))
