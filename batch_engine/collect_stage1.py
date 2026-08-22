import json
import sys
from pathlib import Path

from openai import OpenAI

ROOT = Path(
    "/volume1/docker/curriculum-builder"
)

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build_registry import set_batch_status


RID = "REQ_20260821_194142_DF1A41D6"

ROOT_DIR = (
    ROOT
    / "data"
    / "batches"
    / RID
)

SUBMISSION = (
    ROOT_DIR
    / "stage1_submission.json"
)

OUTPUT = (
    ROOT_DIR
    / "stage1_output.jsonl"
)


def main():

    state = json.loads(
        SUBMISSION.read_text()
    )

    batch_id = state[
        "openai_batch_id"
    ]

    client = OpenAI()

    batch = client.batches.retrieve(
        batch_id
    )

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
            RID,
            "BATCH_FAILED",
            message
        )

        print(message)
        return 1

    if not batch.output_file_id:
        raise RuntimeError(
            "Completed Batch has no output file."
        )

    if OUTPUT.exists():
        print(
            "Output already downloaded:",
            OUTPUT
        )
        return 0

    content = client.files.content(
        batch.output_file_id
    )

    OUTPUT.write_bytes(
        content.read()
    )

    state["status"] = "completed"
    state["openai_output_file_id"] = (
        batch.output_file_id
    )

    SUBMISSION.write_text(
        json.dumps(
            state,
            indent=2
        ),
        encoding="utf-8"
    )

    set_batch_status(
        RID,
        "BATCH_STAGE1_DOWNLOADED"
    )

    print("OUTPUT:", OUTPUT)
    print("STAGE 1 DOWNLOADED")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
