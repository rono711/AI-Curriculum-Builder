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
LOCK_PATH = ROOT / "data" / "batch_automation.lock"
INTERVAL_SECONDS = max(
    15,
    int(os.getenv("BATCH_AUTOMATION_INTERVAL", "60")),
)

running = True


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def log(*parts):
    print(timestamp(), *parts, flush=True)


def stop(signum, frame):
    global running
    running = False
    log("STOP REQUESTED", signum)


def run_script(relative_path, *args):
    command = [
        sys.executable,
        "-u",
        str(ROOT / relative_path),
        *args,
    ]

    log("RUN", " ".join(command))

    result = subprocess.run(
        command,
        cwd=str(ROOT),
        check=False,
    )

    log("EXIT", relative_path, result.returncode)
    return result.returncode


def cycle():
    log("AUTOMATION CYCLE START")

    # Claim and prepare one newly queued request. Repeated cycles drain
    # additional queued requests without allowing concurrent preparation.
    prepare_code = run_script(
        "batch_engine/prepare_worker.py"
    )

    if prepare_code != 0:
        log(
            "PREPARE WORKER REPORTED A FAILURE; "
            "CONTINUING WITH OTHER ACTIVE REQUESTS"
        )

    # Advance every active request as far as possible. The dispatcher exits
    # normally when OpenAI is still processing; a later cycle polls again.
    dispatch_code = run_script(
        "batch_engine/dispatcher.py"
    )

    if dispatch_code != 0:
        log(
            "DISPATCHER REPORTED ONE OR MORE FAILURES; "
            "NEXT CYCLE WILL CONTINUE WITH REMAINING REQUESTS"
        )

    log("AUTOMATION CYCLE END")


def main():
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)

    with LOCK_PATH.open("w") as lock_file:
        try:
            fcntl.flock(
                lock_file.fileno(),
                fcntl.LOCK_EX | fcntl.LOCK_NB,
            )
        except BlockingIOError:
            log("ANOTHER BATCH AUTOMATION PROCESS IS ALREADY RUNNING")
            return 2

        lock_file.write(str(os.getpid()))
        lock_file.flush()

        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)

        log(
            "BATCH AUTOMATION STARTED",
            "interval=",
            INTERVAL_SECONDS,
        )

        while running:
            try:
                cycle()
            except Exception:
                log("UNEXPECTED AUTOMATION ERROR")
                traceback.print_exc()

            for _ in range(INTERVAL_SECONDS):
                if not running:
                    break
                time.sleep(1)

        log("BATCH AUTOMATION STOPPED")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
