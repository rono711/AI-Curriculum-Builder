import argparse
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "build_registry.db"

ACTIVE_STATUSES = (
    "BATCH_STAGE1_READY",
    "BATCH_STAGE1_SUBMITTED",
    "BATCH_STAGE1_DOWNLOADED",
    "BATCH_STAGE1_APPLIED",
    "BATCH_STAGE2_READY",
    "BATCH_STAGE2_SUBMITTED",
    "BATCH_STAGE2_DOWNLOADED",
    "BATCH_STAGE2_APPLIED",
    "EXTERNAL_ASSETS_COMPLETED",
)


def get_active_requests():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row

    try:
        placeholders = ",".join(
            "?"
            for _ in ACTIVE_STATUSES
        )

        rows = db.execute(
            f"""
            SELECT
                request_id,
                status,
                created_at
            FROM build_requests
            WHERE processing_mode = 'QUEUE_BATCH'
              AND status IN ({placeholders})
            ORDER BY created_at, id
            """,
            ACTIVE_STATUSES,
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:
        db.close()


def dispatch(dry_run=False):
    requests = get_active_requests()

    print("=" * 70)
    print("BATCH QUEUE DISPATCHER")
    print("ACTIVE REQUESTS:", len(requests))
    print("=" * 70)

    if not requests:
        print("NO ACTIVE BATCH REQUESTS")
        return 0

    failures = []

    for index, request in enumerate(
        requests,
        start=1
    ):
        rid = request["request_id"]

        print()
        print(
            "REQUEST",
            index,
            "OF",
            len(requests)
        )
        print("ID    :", rid)
        print("STATUS:", request["status"])

        if dry_run:
            print("ACTION: DRY RUN - SKIPPED")
            continue

        command = [
            sys.executable,
            str(
                ROOT
                / "batch_engine"
                / "worker.py"
            ),
            rid,
            "--loop",
        ]

        result = subprocess.run(
            command,
            cwd=str(ROOT),
        )

        if result.returncode != 0:
            failures.append(rid)

            print(
                "DISPATCH FAILED:",
                rid,
                "exit=",
                result.returncode
            )

            # Continue with other independent requests.
            continue

        print(
            "DISPATCH COMPLETE:",
            rid
        )

    print()
    print("=" * 70)

    if failures:
        print(
            "DISPATCHER COMPLETED WITH FAILURES:",
            len(failures)
        )

        for rid in failures:
            print("FAILED:", rid)

        return 1

    print("DISPATCHER COMPLETE")
    print("FAILURES: 0")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--dry-run",
        action="store_true"
    )

    args = parser.parse_args()

    raise SystemExit(
        dispatch(
            dry_run=args.dry_run
        )
    )
