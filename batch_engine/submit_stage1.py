import json
import sys
from pathlib import Path

from openai import OpenAI

ROOT = Path(
    "/volume1/docker/curriculum-builder"
)

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build_registry import mark_batch_submitted


RID = "REQ_20260821_194142_DF1A41D6"

BATCH_DIR = (
    ROOT
    / "data"
    / "batches"
    / RID
)

INPUT_FILE = (
    BATCH_DIR
    / "stage1_input.jsonl"
)

SUBMISSION_FILE = (
    BATCH_DIR
    / "stage1_submission.json"
)


def main():

    if not INPUT_FILE.is_file():
        raise RuntimeError(
            f"Batch input missing: {INPUT_FILE}"
        )

    if SUBMISSION_FILE.exists():
        raise RuntimeError(
            "Submission state already exists. "
            "Refusing duplicate submission."
        )

    client = OpenAI()

    print("Uploading Batch input...")

    with INPUT_FILE.open("rb") as handle:

        uploaded = client.files.create(
            file=handle,
            purpose="batch"
        )

    print("INPUT FILE ID:", uploaded.id)

    state = {
        "request_id": RID,
        "openai_input_file_id": uploaded.id,
        "openai_batch_id": None,
        "status": "FILE_UPLOADED"
    }

    SUBMISSION_FILE.write_text(
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
            "request_id": RID,
            "stage": "1"
        }
    )

    state["openai_batch_id"] = batch.id
    state["status"] = batch.status

    SUBMISSION_FILE.write_text(
        json.dumps(
            state,
            indent=2
        ),
        encoding="utf-8"
    )

    if not mark_batch_submitted(
        RID,
        batch.id
    ):
        raise RuntimeError(
            "OpenAI Batch was created, but registry "
            "could not transition to BATCH_SUBMITTED. "
            f"Batch ID: {batch.id}"
        )

    print("BATCH ID:", batch.id)
    print("BATCH STATUS:", batch.status)
    print("REGISTRY: BATCH_SUBMITTED")


if __name__ == "__main__":
    main()
