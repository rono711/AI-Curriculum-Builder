import json
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from batch_engine.config import STAGE1_PROMPT_TYPES
from batch_engine.stage1_builder import Stage1BatchBuilder
from build_registry import (
    claim_build_request,
    fail_build_request,
    get_build_request_items,
    get_queued_requests,
    get_connection,
)

LP_URL = "http://lesson-package-builder:8003/build"
PROMPT_URL = "http://prompt-engine:8005/prompt"


def prepare_single_lesson(
        client,
        request,
        parent_code,
        lesson_number
):
    payload = {
        "requested_by": request["requested_by"],
        "learning_area": request["learning_area"],
        "subject": request["subject"],
        "year_level": request["year_level"],
        "strand": request["strand"],
        "sub_strand": request["sub_strand"] or "",
        "parent_code": str(parent_code).strip(),
        "lesson_numbers": [int(lesson_number)],
        "build_mode": "NEW",
        "update_components": [],
        "publication_mode": "GENERATE_ONLY",
        "execution_mode": "PREPARE_ONLY",
    }

    response = client.post(
        LP_URL,
        json=payload
    )
    response.raise_for_status()

    prepared = response.json()

    if prepared.get("status") != "PREPARED":
        raise RuntimeError(
            "Lesson preparation failed: "
            + str(prepared)
        )

    lesson_rows = prepared.get(
        "lesson_rows"
    ) or []

    if len(lesson_rows) != 1:
        raise RuntimeError(
            "Expected exactly one prepared lesson for "
            + str(parent_code)
            + " lesson "
            + str(lesson_number)
            + "; received "
            + str(len(lesson_rows))
            + "."
        )

    return prepared


def prepare_prompt_results(
        client,
        prepared
):
    results = []

    for row in prepared["lesson_rows"]:
        lp = row["lesson_package_id"]

        for prompt_type in STAGE1_PROMPT_TYPES:
            response = client.post(
                PROMPT_URL,
                json={
                    "workbook_path":
                        prepared["workbook_path"],
                    "lesson_package_id":
                        lp,
                    "prompt_type":
                        prompt_type,
                    "generation_mode":
                        "BATCH_PREPARE",
                },
                timeout=600,
            )

            response.raise_for_status()
            result = response.json()

            if result.get("ai") is not None:
                raise RuntimeError(
                    "Unexpected AI result: "
                    + prompt_type
                )

            results.append(result)

    return results


def prepare_request(item):
    rid = item["request_id"]

    if not claim_build_request(rid):
        print("SKIP:", rid)
        return False

    try:
        child_items = get_build_request_items(rid)

        payload = {
            "requested_by": item["requested_by"],
            "learning_area": item["learning_area"],
            "subject": item["subject"],
            "year_level": item["year_level"],
            "strand": item["strand"],
            "sub_strand": item["sub_strand"] or "",
            "parent_code": item["parent_code"],
            "lesson_numbers": item["lesson_numbers"],
            "build_mode": "NEW",
            "update_components": [],
            "publication_mode": "GENERATE_ONLY",
            "execution_mode": "PREPARE_ONLY",
        }

        with httpx.Client(timeout=1800) as client:
            if child_items:
                prompt_results = []
                prepared_lessons = []

                print(
                    "MULTI-CONTENT BATCH:",
                    rid,
                    "ITEMS:",
                    len(child_items)
                )

                for child in child_items:
                    prepared_child = prepare_single_lesson(
                        client,
                        item,
                        child["parent_code"],
                        child["lesson_number"]
                    )

                    prompt_results.extend(
                        prepare_prompt_results(
                            client,
                            prepared_child
                        )
                    )

                    prepared_lessons.append({
                        "item_id": child["id"],
                        "parent_code": child["parent_code"],
                        "curriculum_code":
                            child["curriculum_code"],
                        "lesson_number":
                            child["lesson_number"],
                        "topic_id": child["topic_id"],
                        "build_id":
                            prepared_child["build_id"],
                        "workbook_path":
                            prepared_child["workbook_path"],
                        "lesson_rows":
                            prepared_child["lesson_rows"],
                    })

            else:
                r = client.post(LP_URL, json=payload)
                r.raise_for_status()
                prepared = r.json()

                if prepared.get("status") != "PREPARED":
                    raise RuntimeError(str(prepared))

                prompt_results = (
                    prepare_prompt_results(
                        client,
                        prepared
                    )
                )

                prepared_lessons = [{
                    "item_id": None,
                    "parent_code": item["parent_code"],
                    "curriculum_code": None,
                    "lesson_number": None,
                    "topic_id": None,
                    "build_id": prepared["build_id"],
                    "workbook_path":
                        prepared["workbook_path"],
                    "lesson_rows":
                        prepared["lesson_rows"],
                }]

        batch = Stage1BatchBuilder().build(
            request_id=rid,
            prompt_results=prompt_results,
            output_root=ROOT / "data" / "batches",
        )

        state = {
            "request_id": rid,
            "mode": (
                "MULTI"
                if child_items
                else "LEGACY"
            ),
            "prepared_lessons":
                prepared_lessons,
            "stage1": batch,
        }

        state_path = (
            ROOT / "data" / "batches" / rid /
            "prepare_state.json"
        )

        state_path.write_text(
            json.dumps(state, indent=2),
            encoding="utf-8",
        )

        with get_connection() as connection:
            cursor = connection.execute(
                """
                UPDATE build_requests
                SET status = 'BATCH_STAGE1_READY',
                    completed_at = NULL,
                    updated_at = CURRENT_TIMESTAMP,
                    error = NULL
                WHERE request_id = ?
                  AND processing_mode = 'QUEUE_BATCH'
                  AND status = 'PROCESSING'
                """,
                (rid,)
            )

            connection.commit()

        if cursor.rowcount != 1:
            raise RuntimeError(
                "Stage 1 files were prepared, but registry "
                "could not transition to BATCH_STAGE1_READY."
            )

        print("BATCH STAGE 1 READY")
        print("REQUEST:", rid)
        print("LESSONS:", len(prepared_lessons))
        print("COUNT:", batch["request_count"])
        print("INPUT:", batch["input_file"])
        print("REGISTRY: BATCH_STAGE1_READY")
        return True

    except Exception as exc:
        fail_build_request(rid, str(exc))
        print("FAILED:", rid)
        print("ERROR:", exc)
        return False


def run_once():
    rows = get_queued_requests(
        processing_mode="QUEUE_BATCH",
        limit=1,
    )

    if not rows:
        print("No QUEUE_BATCH requests waiting.")
        return 0

    return 0 if prepare_request(rows[0]) else 1


if __name__ == "__main__":
    raise SystemExit(run_once())
