"""Automatically discover and process finished Moodle quiz attempts."""

import os
import time
import traceback
from datetime import datetime, timezone

from build_registry import (
    get_active_analytics_quizzes,
)
from learning_analytics.attempt_detector import (
    FinishedAttemptDetector,
)


POLL_SECONDS = int(
    os.getenv(
        "ANALYTICS_POLL_SECONDS",
        "300",
    )
)

if POLL_SECONDS < 60:
    raise RuntimeError(
        "ANALYTICS_POLL_SECONDS must be at least 60."
    )


def timestamp():
    return datetime.now(
        timezone.utc
    ).isoformat()


def run_cycle():
    """Run one complete analytics discovery/processing cycle."""

    quizzes = get_active_analytics_quizzes()

    detector = FinishedAttemptDetector()

    summary = {
        "quizzes": len(quizzes),
        "new_attempts": 0,
        "processed": 0,
        "errors": 0,
    }

    print(
        f"[{timestamp()}] "
        f"Starting analytics scan: "
        f"{len(quizzes)} active quizzes",
        flush=True,
    )

    for quiz in quizzes:

        quiz_id = int(
            quiz["moodle_quiz_id"]
        )

        curriculum_code = str(
            quiz["curriculum_code"]
        )

        try:
            result = detector.process_new(
                moodle_quiz_id=quiz_id
            )

            new_count = int(
                result.get(
                    "new_attempts_found",
                    0,
                )
            )

            processed_count = int(
                result.get(
                    "processed_count",
                    0,
                )
            )

            summary["new_attempts"] += (
                new_count
            )

            summary["processed"] += (
                processed_count
            )

            if new_count or processed_count:
                print(
                    f"[{timestamp()}] "
                    f"Quiz {quiz_id} "
                    f"{curriculum_code}: "
                    f"new={new_count}, "
                    f"processed={processed_count}",
                    flush=True,
                )

        except Exception as exc:
            summary["errors"] += 1

            print(
                f"[{timestamp()}] "
                f"ERROR quiz {quiz_id} "
                f"{curriculum_code}: "
                f"{type(exc).__name__}: {exc}",
                flush=True,
            )

            traceback.print_exc()

    print(
        f"[{timestamp()}] "
        "Analytics scan complete: "
        f"quizzes={summary['quizzes']}, "
        f"new={summary['new_attempts']}, "
        f"processed={summary['processed']}, "
        f"errors={summary['errors']}",
        flush=True,
    )

    return summary


def main():
    print(
        f"[{timestamp()}] "
        "Learning analytics worker started; "
        f"poll interval={POLL_SECONDS}s",
        flush=True,
    )

    while True:
        try:
            run_cycle()

        except Exception as exc:
            # Protect the long-running worker from failures that occur
            # outside an individual quiz processing operation.
            print(
                f"[{timestamp()}] "
                "WORKER CYCLE ERROR: "
                f"{type(exc).__name__}: {exc}",
                flush=True,
            )

            traceback.print_exc()

        print(
            f"[{timestamp()}] "
            f"Sleeping {POLL_SECONDS}s",
            flush=True,
        )

        time.sleep(
            POLL_SECONDS
        )


if __name__ == "__main__":
    main()
