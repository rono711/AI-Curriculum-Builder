import fcntl
import os
import signal
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
LOCK_PATH = ROOT / "data" / "standard_queue_automation.lock"
INTERVAL_SECONDS = max(
    15,
    int(os.getenv("STANDARD_QUEUE_INTERVAL", "60")),
)

running = True


def log(*parts):
    print(
        datetime.now(timezone.utc).isoformat(),
        *parts,
        flush=True,
    )


def stop(signum, frame):
    global running
    running = False
    log("STOP REQUESTED", signum)


def run_cycle():
    command = [
        sys.executable,
        "-u",
        str(ROOT / "build-app" / "queue_worker.py"),
    ]

    log("STANDARD QUEUE CYCLE START")

    result = subprocess.run(
        command,
        cwd=str(ROOT),
        check=False,
    )

    log("STANDARD QUEUE CYCLE END", "exit=", result.returncode)

    if result.returncode != 0:
        log(
            "QUEUE WORKER REPORTED A FAILURE; "
            "THE NEXT CYCLE WILL CONTINUE WITH THE NEXT REQUEST"
        )


def main():
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)

    with LOCK_PATH.open("w") as lock_file:
        try:
            fcntl.flock(
                lock_file.fileno(),
                fcntl.LOCK_EX | fcntl.LOCK_NB,
            )
        except BlockingIOError:
            log("ANOTHER STANDARD QUEUE WORKER IS ALREADY RUNNING")
            return 2

        lock_file.write(str(os.getpid()))
        lock_file.flush()

        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)

        log(
            "STANDARD QUEUE AUTOMATION STARTED",
            "interval=",
            INTERVAL_SECONDS,
        )

        while running:
            try:
                run_cycle()
            except Exception:
                log("UNEXPECTED STANDARD QUEUE ERROR")
                traceback.print_exc()

            for _ in range(INTERVAL_SECONDS):
                if not running:
                    break
                time.sleep(1)

        log("STANDARD QUEUE AUTOMATION STOPPED")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
