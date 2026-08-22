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
    get_queued_requests,
)

LP_URL = "http://lesson-package-builder:8003/build"
PROMPT_URL = "http://prompt-engine:8005/prompt"


def prepare_request(item):
    rid = item["request_id"]

    if not claim_build_request(rid):
        print("SKIP:", rid)
        return False

    try:
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
            r = client.post(LP_URL, json=payload)
            r.raise_for_status()
            prepared = r.json()

            if prepared.get("status") != "PREPARED":
                raise RuntimeError(str(prepared))

            prompt_results = []

            for row in prepared["lesson_rows"]:
                lp = row["lesson_package_id"]

                for prompt_type in STAGE1_PROMPT_TYPES:
                    r = client.post(
                        PROMPT_URL,
                        json={
                            "workbook_path": prepared["workbook_path"],
                            "lesson_package_id": lp,
                            "prompt_type": prompt_type,
                            "generation_mode": "BATCH_PREPARE",
                        },
                        timeout=600,
                    )
                    r.raise_for_status()
                    result = r.json()

                    if result.get("ai") is not None:
                        raise RuntimeError(
                            "Unexpected AI result: " + prompt_type
                        )

                    prompt_results.append(result)

        batch = Stage1BatchBuilder().build(
            request_id=rid,
            prompt_results=prompt_results,
            output_root=ROOT / "data" / "batches",
        )

        state = {
            "request_id": rid,
            "build_id": prepared["build_id"],
            "workbook_path": prepared["workbook_path"],
            "build_root": prepared["build_root"],
            "build_name": prepared["build_name"],
            "lesson_rows": prepared["lesson_rows"],
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

        print("BATCH STAGE 1 READY")
        print("REQUEST:", rid)
        print("BUILD:", prepared["build_id"])
        print("COUNT:", batch["request_count"])
        print("INPUT:", batch["input_file"])
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
