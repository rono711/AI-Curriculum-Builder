#!/bin/sh

PROJECT="/volume1/docker/curriculum-builder"
LOG="$PROJECT/logs/standard_queue.log"

cd "$PROJECT" || exit 1

echo "============================================================" >> "$LOG"
echo "Queue worker started: $(date -Iseconds)" >> "$LOG"

sudo /usr/local/bin/docker exec build-app \
    python /volume1/docker/curriculum-builder/build-app/queue_worker.py \
    >> "$LOG" 2>&1

RC=$?

echo "Queue worker finished: $(date -Iseconds) rc=$RC" >> "$LOG"

exit "$RC"
