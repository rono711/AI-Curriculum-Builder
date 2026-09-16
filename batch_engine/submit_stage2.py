import json
import sys
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build_registry import (
    create_batch_run,
    get_build_request,
    get_latest_batch_run,
    set_batch_status,
    update_batch_run,
)


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

    if request["status"] != "BATCH_STAGE2_READY":
        raise RuntimeError(
            "Request must be BATCH_STAGE2_READY; "
            "found " + str(request["status"])
        )

    batch_dir = ROOT / "data" / "batches" / rid

    input_file = batch_dir / "stage2_input.jsonl"
    submission_file = (
        batch_dir / "stage2_submission.json"
    )

    if not input_file.is_file():
        raise RuntimeError(
            "Stage 2 input missing: "
            + str(input_file)
        )

    if submission_file.exists():
        raise RuntimeError(
            "Stage 2 submission state already exists."
        )

    existing = get_latest_batch_run(
        rid,
        stage=2,
        provider="OPENAI"
    )

    if existing is not None:
        raise RuntimeError(
            "Stage 2 OpenAI batch run already exists: "
            + str(existing)
        )

    run_id = create_batch_run(
        rid,
        stage=2,
        provider="OPENAI",
        attempt=1,
    )

    client = OpenAI()

    state = {
        "request_id": rid,
        "stage": 2,
        "batch_run_id": run_id,
        "openai_input_file_id": None,
        "openai_batch_id": None,
        "status": "CREATED",
    }

    submission_file.write_text(
        json.dumps(state, indent=2),
        encoding="utf-8",
    )

    try:
        print("Uploading Stage 2 Batch input...")

        with input_file.open("rb") as handle:
            uploaded = client.files.create(
                file=handle,
                purpose="batch",
            )

        state["openai_input_file_id"] = uploaded.id
        state["status"] = "FILE_UPLOADED"

        submission_file.write_text(
            json.dumps(state, indent=2),
            encoding="utf-8",
        )

        if not update_batch_run(
            run_id,
            "FILE_UPLOADED",
            input_file_id=uploaded.id,
        ):
            raise RuntimeError(
                "Could not record Stage 2 input file."
            )

        print("INPUT FILE ID:", uploaded.id)
        print("Creating Stage 2 OpenAI Batch...")

        batch = client.batches.create(
            input_file_id=uploaded.id,
            endpoint="/v1/responses",
            completion_window="24h",
            metadata={
                "request_id": rid,
                "stage": "2",
            },
        )

        state["openai_batch_id"] = batch.id
        state["status"] = batch.status

        submission_file.write_text(
            json.dumps(state, indent=2),
            encoding="utf-8",
        )

        if not update_batch_run(
            run_id,
            str(batch.status).upper(),
            external_batch_id=batch.id,
            input_file_id=uploaded.id,
        ):
            raise RuntimeError(
                "Could not record Stage 2 Batch."
            )

        if not set_batch_status(
            rid,
            "BATCH_STAGE2_SUBMITTED"
        ):
            raise RuntimeError(
                "Stage 2 Batch was created, but "
                "request status could not transition."
            )

        print("REQUEST:", rid)
        print("RUN ID:", run_id)
        print("BATCH ID:", batch.id)
        print("BATCH STATUS:", batch.status)
        print("REGISTRY: BATCH_STAGE2_SUBMITTED")

        return 0

    except Exception as exc:
        update_batch_run(
            run_id,
            "FAILED",
            error=str(exc),
        )
        raise


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python3 "
            "batch_engine/submit_stage2.py "
            "<REQUEST_ID>"
        )

    raise SystemExit(main(sys.argv[1]))
