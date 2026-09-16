import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build_registry import get_build_request


def run_script(script, rid, *args):
    command = [
        sys.executable,
        str(ROOT / script),
        rid,
        *args,
    ]

    print("=" * 70)
    print("RUNNING:", " ".join(command))
    print("=" * 70)

    result = subprocess.run(
        command,
        cwd=str(ROOT),
    )

    if result.returncode != 0:
        raise RuntimeError(
            script
            + " failed with exit code "
            + str(result.returncode)
        )


def process(rid):
    request = get_build_request(rid)

    if request is None:
        raise RuntimeError(
            "Request not found: " + rid
        )

    if request["processing_mode"] != "QUEUE_BATCH":
        raise RuntimeError(
            "Request is not QUEUE_BATCH: " + rid
        )

    status = str(
        request["status"]
    ).strip().upper()

    print("=" * 70)
    print("BATCH WORKER")
    print("REQUEST:", rid)
    print("STATUS :", status)
    print("=" * 70)

    if status == "BATCH_STAGE1_READY":
        run_script(
            "batch_engine/submit_stage1.py",
            rid,
        )

    elif status == "BATCH_STAGE1_SUBMITTED":
        run_script(
            "batch_engine/collect_stage1.py",
            rid,
        )

    elif status == "BATCH_STAGE1_DOWNLOADED":
        run_script(
            "batch_engine/apply_stage1.py",
            rid,
        )

    elif status == "BATCH_STAGE1_APPLIED":
        run_script(
            "batch_engine/prepare_stage2.py",
            rid,
        )

    elif status == "BATCH_STAGE2_READY":
        run_script(
            "batch_engine/submit_stage2.py",
            rid,
        )

    elif status == "BATCH_STAGE2_SUBMITTED":
        run_script(
            "batch_engine/collect_stage2.py",
            rid,
        )

    elif status == "BATCH_STAGE2_DOWNLOADED":
        run_script(
            "batch_engine/apply_stage2.py",
            rid,
        )

    elif status == "BATCH_STAGE2_APPLIED":
        run_script(
            "batch_engine/run_external_assets.py",
            rid,
            "--run-images",
            "--run-gamma",
            "--finalize",
        )

    elif status == "EXTERNAL_ASSETS_COMPLETED":
        run_script(
            "batch_engine/publish_batch.py",
            rid,
            "--publish",
        )

    elif status == "PUBLISHED":
        print("REQUEST ALREADY PUBLISHED")
        print("NO ACTION REQUIRED")

    elif status.endswith("_FAILED"):
        print("REQUEST IS IN FAILED STATE")
        print("STATUS:", status)
        print("MANUAL REVIEW REQUIRED")

    else:
        raise RuntimeError(
            "Worker does not yet support status: "
            + status
        )

    print()
    print("WORKER STEP COMPLETE")

    updated = get_build_request(rid)

    if updated:
        print(
            "NEW STATUS:",
            updated["status"]
        )

    return 0


def process_loop(rid, max_steps=20):
    waiting_statuses = {
        "BATCH_STAGE1_SUBMITTED",
        "BATCH_STAGE2_SUBMITTED",
    }

    for step in range(1, max_steps + 1):
        before = get_build_request(rid)

        if before is None:
            raise RuntimeError(
                "Request not found: " + rid
            )

        before_status = str(
            before["status"]
        ).strip().upper()

        print()
        print(
            "AUTOMATION STEP:",
            step,
            "| STATUS:",
            before_status
        )

        process(rid)

        after = get_build_request(rid)

        after_status = str(
            after["status"]
        ).strip().upper()

        if after_status == "PUBLISHED":
            print("AUTOMATION COMPLETE")
            return 0

        if after_status.endswith("_FAILED"):
            print(
                "AUTOMATION STOPPED:",
                after_status
            )
            return 1

        if (
            before_status == after_status
            and after_status in waiting_statuses
        ):
            print(
                "WAITING FOR ASYNC BATCH:",
                after_status
            )
            return 0

        if before_status == after_status:
            raise RuntimeError(
                "Worker made no status progress from "
                + before_status
            )

    raise RuntimeError(
        "Maximum automation steps reached."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "request_id"
    )

    parser.add_argument(
        "--loop",
        action="store_true"
    )

    args = parser.parse_args()

    if args.loop:
        raise SystemExit(
            process_loop(args.request_id)
        )

    raise SystemExit(
        process(args.request_id)
    )
