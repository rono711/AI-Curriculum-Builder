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
    get_connection,
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

    if request["status"] != "BATCH_STAGE1_READY":
        raise RuntimeError(
            f"Request must be BATCH_STAGE1_READY, "
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

    existing_state = None

    if submission_file.exists():
        existing_state = json.loads(
            submission_file.read_text(
                encoding="utf-8"
            )
        )

        existing_batch_id = (
            existing_state.get("openai_batch_id")
        )

        if existing_batch_id:
            print(
                "RECOVERING EXISTING OPENAI BATCH:",
                existing_batch_id
            )

            with get_connection() as connection:
                cursor = connection.execute(
                    """
                    UPDATE build_requests
                    SET status = 'BATCH_STAGE1_SUBMITTED',
                        openai_batch_id = ?,
                        completed_at = NULL,
                        updated_at = CURRENT_TIMESTAMP,
                        error = NULL
                    WHERE request_id = ?
                      AND processing_mode = 'QUEUE_BATCH'
                      AND status = 'BATCH_STAGE1_READY'
                    """,
                    (
                        existing_batch_id,
                        rid,
                    )
                )

                connection.commit()

            if cursor.rowcount != 1:
                raise RuntimeError(
                    "Existing OpenAI Batch found, but "
                    "registry recovery failed. "
                    "Batch ID: "
                    + str(existing_batch_id)
                )

            print("REQUEST:", rid)
            print(
                "BATCH ID:",
                existing_batch_id
            )
            print(
                "REGISTRY: BATCH_STAGE1_SUBMITTED"
            )

            return 0

        print(
            "INCOMPLETE SUBMISSION STATE FOUND; "
            "RESTARTING STAGE 1 SUBMISSION."
        )

        submission_file.unlink()

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

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE build_requests
            SET status = 'BATCH_STAGE1_SUBMITTED',
                openai_batch_id = ?,
                completed_at = NULL,
                updated_at = CURRENT_TIMESTAMP,
                error = NULL
            WHERE request_id = ?
              AND processing_mode = 'QUEUE_BATCH'
              AND status = 'BATCH_STAGE1_READY'
            """,
            (
                batch.id,
                rid,
            )
        )

        connection.commit()

    if cursor.rowcount != 1:
        raise RuntimeError(
            "OpenAI Batch was created, but registry "
            "could not transition to "
            "BATCH_STAGE1_SUBMITTED. "
            f"Batch ID: {batch.id}"
        )

    print("REQUEST:", rid)
    print("BATCH ID:", batch.id)
    print("BATCH STATUS:", batch.status)
    print("REGISTRY: BATCH_STAGE1_SUBMITTED")

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
