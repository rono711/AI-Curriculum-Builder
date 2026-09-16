import json
import sys
from pathlib import Path

from openai import OpenAI

ROOT = Path(
    "/volume1/docker/curriculum-builder"
)

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build_registry import (
    get_build_request,
    mark_batch_submitted,
)


def main(request_id):
    rid = str(request_id).strip()

    request = get_build_request(rid)

    if request is None:
        raise RuntimeError(
            f"Build request does not exist: {rid}"
        )

    if request["processing_mode"] != "QUEUE_BATCH":
        raise RuntimeError(
            f"Request is not QUEUE_BATCH: {rid}"
        )

    if request["status"] != "BATCH_READY":
        raise RuntimeError(
            f"Request must be BATCH_READY, "
            f"found {request['status']}: {rid}"
        )

    batch_dir = (
        ROOT
        / "data"
        / "batches"
        / rid
    )

    input_file = (
        batch_dir
        / "stage1_input.jsonl"
    )

    submission_file = (
        batch_dir
        / "stage1_submission.json"
    )

    if not input_file.is_file():
        raise RuntimeError(
            f"Batch input missing: {input_file}"
        )

    if submission_file.exists():
        raise RuntimeError(
            "Submission state already exists. "
            "Refusing duplicate submission."
        )

    client = OpenAI()

    print("Uploading Batch input...")

    with input_file.open("rb") as handle:
        uploaded = client.files.create(
            file=handle,
            purpose="batch"
        )

    print(
        "INPUT FILE ID:",
        uploaded.id
    )

    state = {
        "request_id": rid,
        "openai_input_file_id": uploaded.id,
        "openai_batch_id": None,
        "status": "FILE_UPLOADED"
    }

    submission_file.write_text(
        json.dumps(
            state,
            indent=2
        ),
        encoding="utf-8"
    )

    print("Creating OpenAI Batch...")

    batch = client.batches.create(
        input_file_id=uploaded.id,
        endpoint="/v1/responses",
        completion_window="24h",
        metadata={
            "request_id": rid,
            "stage": "1"
        }
    )

    state["openai_batch_id"] = batch.id
    state["status"] = batch.status

    submission_file.write_text(
        json.dumps(
            state,
            indent=2
        ),
        encoding="utf-8"
    )

    if not mark_batch_submitted(
        rid,
        batch.id
    ):
        raise RuntimeError(
            "OpenAI Batch was created, but registry "
            "could not transition to BATCH_SUBMITTED. "
            f"Batch ID: {batch.id}"
        )

    print("REQUEST:", rid)
    print("BATCH ID:", batch.id)
    print("BATCH STATUS:", batch.status)
    print("REGISTRY: BATCH_SUBMITTED")

    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python3 "
            "batch_engine/submit_stage1.py "
            "<REQUEST_ID>"
        )

    raise SystemExit(
        main(sys.argv[1])
    )
