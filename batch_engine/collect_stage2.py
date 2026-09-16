import json
import sys
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build_registry import (
    get_build_request,
    get_latest_batch_run,
    set_batch_status,
    update_batch_run,
)

ACTIVE_STATUSES = (
    "validating",
    "in_progress",
    "finalizing",
    "cancelling",
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

    batch_dir = ROOT / "data" / "batches" / rid

    submission_file = (
        batch_dir / "stage2_submission.json"
    )

    output_file = (
        batch_dir / "stage2_output.jsonl"
    )

    if not submission_file.is_file():
        raise RuntimeError(
            "Stage 2 submission state missing."
        )

    state = json.loads(
        submission_file.read_text(
            encoding="utf-8"
        )
    )

    run_id = state.get("batch_run_id")

    if not run_id:
        raise RuntimeError(
            "Stage 2 submission has no batch_run_id."
        )

    run = get_latest_batch_run(
        rid,
        stage=2,
        provider="OPENAI"
    )

    if run is None:
        raise RuntimeError(
            "Stage 2 batch run is missing."
        )

    if int(run["id"]) != int(run_id):
        raise RuntimeError(
            "Stage 2 batch_run_id mismatch."
        )

    batch_id = state.get("openai_batch_id")

    if not batch_id:
        raise RuntimeError(
            "Stage 2 submission has no openai_batch_id."
        )

    if (
        run.get("external_batch_id")
        and
        str(run["external_batch_id"])
        != str(batch_id)
    ):
        raise RuntimeError(
            "Stage 2 OpenAI batch ID mismatch."
        )

    client = OpenAI()

    batch = client.batches.retrieve(
        batch_id
    )

    print("REQUEST:", rid)
    print("RUN ID:", run_id)
    print("BATCH:", batch.id)
    print("STATUS:", batch.status)

    counts = batch.request_counts

    if counts:
        print("TOTAL:", counts.total)
        print("COMPLETED:", counts.completed)
        print("FAILED:", counts.failed)

    if batch.status in ACTIVE_STATUSES:
        if not update_batch_run(
            run_id,
            str(batch.status).upper(),
            external_batch_id=batch.id,
        ):
            raise RuntimeError(
                "Could not update Stage 2 run status."
            )

        return 0

    if batch.status != "completed":
        message = (
            "Stage 2 OpenAI Batch ended with status: "
            + str(batch.status)
        )

        update_batch_run(
            run_id,
            str(batch.status).upper(),
            external_batch_id=batch.id,
            error=message,
        )

        set_batch_status(
            rid,
            "BATCH_STAGE2_FAILED",
            message,
        )

        print(message)
        return 1

    if not batch.output_file_id:
        raise RuntimeError(
            "Completed Stage 2 Batch has no output file."
        )

    if output_file.exists():
        print(
            "Output already downloaded:",
            output_file
        )

        if not update_batch_run(
            run_id,
            "COMPLETED",
            external_batch_id=batch.id,
            output_file_id=batch.output_file_id,
        ):
            raise RuntimeError(
                "Could not update completed Stage 2 run."
            )

        if request["status"] != "BATCH_STAGE2_DOWNLOADED":
            if not set_batch_status(
                rid,
                "BATCH_STAGE2_DOWNLOADED"
            ):
                raise RuntimeError(
                    "Could not restore "
                    "BATCH_STAGE2_DOWNLOADED."
                )

        return 0

    content = client.files.content(
        batch.output_file_id
    )

    output_file.write_bytes(
        content.read()
    )

    state["status"] = "completed"
    state["openai_output_file_id"] = (
        batch.output_file_id
    )

    submission_file.write_text(
        json.dumps(
            state,
            indent=2
        ),
        encoding="utf-8",
    )

    if not update_batch_run(
        run_id,
        "COMPLETED",
        external_batch_id=batch.id,
        output_file_id=batch.output_file_id,
    ):
        raise RuntimeError(
            "Could not complete Stage 2 run."
        )

    if not set_batch_status(
        rid,
        "BATCH_STAGE2_DOWNLOADED"
    ):
        raise RuntimeError(
            "Could not transition request to "
            "BATCH_STAGE2_DOWNLOADED."
        )

    print("OUTPUT:", output_file)
    print("REGISTRY: BATCH_STAGE2_DOWNLOADED")

    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python3 "
            "batch_engine/collect_stage2.py "
            "<REQUEST_ID>"
        )

    raise SystemExit(main(sys.argv[1]))
