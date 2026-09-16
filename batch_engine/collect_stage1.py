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
    set_batch_status,
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

    root_dir = (
        ROOT
        / "data"
        / "batches"
        / rid
    )

    submission = (
        root_dir
        / "stage1_submission.json"
    )

    output = (
        root_dir
        / "stage1_output.jsonl"
    )

    if not submission.is_file():
        raise RuntimeError(
            f"Submission state missing: {submission}"
        )

    state = json.loads(
        submission.read_text(
            encoding="utf-8"
        )
    )

    batch_id = state.get(
        "openai_batch_id"
    )

    if not batch_id:
        raise RuntimeError(
            "Submission state has no "
            "openai_batch_id."
        )

    client = OpenAI()

    batch = client.batches.retrieve(
        batch_id
    )

    print("REQUEST:", rid)
    print("BATCH:", batch.id)
    print("STATUS:", batch.status)

    counts = batch.request_counts

    if counts:
        print("TOTAL:", counts.total)
        print("COMPLETED:", counts.completed)
        print("FAILED:", counts.failed)

    if batch.status in (
        "validating",
        "in_progress",
        "finalizing",
        "cancelling"
    ):
        return 0

    if batch.status != "completed":
        message = (
            "OpenAI Batch ended with status: "
            + str(batch.status)
        )

        set_batch_status(
            rid,
            "BATCH_FAILED",
            message
        )

        print(message)

        return 1

    if not batch.output_file_id:
        raise RuntimeError(
            "Completed Batch has no output file."
        )

    if output.exists():
        print(
            "Output already downloaded:",
            output
        )

        if request["status"] != "BATCH_STAGE1_DOWNLOADED":
            set_batch_status(
                rid,
                "BATCH_STAGE1_DOWNLOADED"
            )

        return 0

    content = client.files.content(
        batch.output_file_id
    )

    output.write_bytes(
        content.read()
    )

    state["status"] = "completed"
    state["openai_output_file_id"] = (
        batch.output_file_id
    )

    submission.write_text(
        json.dumps(
            state,
            indent=2
        ),
        encoding="utf-8"
    )

    set_batch_status(
        rid,
        "BATCH_STAGE1_DOWNLOADED"
    )

    print("OUTPUT:", output)
    print(
        "REGISTRY: BATCH_STAGE1_DOWNLOADED"
    )

    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python3 "
            "batch_engine/collect_stage1.py "
            "<REQUEST_ID>"
        )

    raise SystemExit(
        main(sys.argv[1])
    )
