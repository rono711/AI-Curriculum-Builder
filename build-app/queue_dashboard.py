from fastapi import APIRouter, HTTPException

from build_registry import get_connection


router = APIRouter()


STATUS_LABELS = {
    "QUEUED": "Queued",
    "PROCESSING": "Preparing lesson",
    "BATCH_STAGE1_READY": "Ready for OpenAI Stage 1",
    "BATCH_STAGE1_SUBMITTED": "Generating - OpenAI Stage 1",
    "BATCH_STAGE1_DOWNLOADED": "Stage 1 results received",
    "BATCH_STAGE1_APPLIED": "Stage 1 generated",
    "BATCH_STAGE2_READY": "Ready for OpenAI Stage 2",
    "BATCH_STAGE2_SUBMITTED": "Generating - OpenAI Stage 2",
    "BATCH_STAGE2_DOWNLOADED": "Stage 2 results received",
    "BATCH_STAGE2_APPLIED": "Lesson generation complete",
    "EXTERNAL_ASSETS_COMPLETED": "Ready to publish",
    "PUBLISHED": "Published",
    "FAILED": "Failed",
    "BATCH_STAGE1_FAILED": "OpenAI Stage 1 failed",
    "BATCH_STAGE2_FAILED": "OpenAI Stage 2 failed",
}


def status_label(value):
    status = str(value or "").strip().upper()

    if status in STATUS_LABELS:
        return STATUS_LABELS[status]

    if status:
        return status.replace("_", " ").title()

    return "Unknown"


def mode_label(value):
    mode = str(value or "").strip().upper()

    if mode == "QUEUE_STANDARD":
        return "Standard Queue"

    if mode == "QUEUE_BATCH":
        return "OpenAI Batch"

    return mode.replace("_", " ").title()


@router.get("/api/queue/health")
def queue_health():
    return {
        "status": "ok",
        "service": "queue-dashboard",
    }


def item_is_failed(item):
    status = str(
        item["status"] or ""
    ).strip().upper()

    stage = str(
        item["stage"] or ""
    ).strip().upper()

    return (
        status == "FAILED"
        or status.endswith("_FAILED")
        or stage == "FAILED"
        or stage.endswith("_FAILED")
    )


def request_summary(parent, items):
    total = len(items)

    published = sum(
        1
        for item in items
        if str(
            item["status"] or ""
        ).strip().upper() == "PUBLISHED"
    )

    failed = sum(
        1
        for item in items
        if item_is_failed(item)
    )

    processing = sum(
        1
        for item in items
        if str(
            item["status"] or ""
        ).strip().upper() == "PROCESSING"
    )

    queued = max(
        0,
        total - published - failed - processing
    )

    percent = 0

    if total:
        percent = int(
            sum(
                int(item["percent"] or 0)
                for item in items
            )
            / total
        )

    return {
        "request_id":
            parent["request_id"],

        "processing_mode":
            parent["processing_mode"],

        "processing_mode_label":
            mode_label(
                parent["processing_mode"]
            ),

        "subject":
            parent["subject"],

        "year_level":
            parent["year_level"],

        "strand":
            parent["strand"],

        "parent_code":
            parent["parent_code"],

        "status":
            parent["status"],

        "status_label":
            status_label(
                parent["status"]
            ),

        "openai_batch_id":
            parent["openai_batch_id"],

        "error":
            parent["error"],

        "created_at":
            parent["created_at"],

        "updated_at":
            parent["updated_at"],

        "completed_at":
            parent["completed_at"],

        "lesson_count":
            total,

        "published_count":
            published,

        "failed_count":
            failed,

        "processing_count":
            processing,

        "queued_count":
            queued,

        "percent":
            percent,
    }


@router.get("/api/queue/requests")
def queue_requests():
    with get_connection() as db:
        parents = db.execute(
            """
            SELECT *
            FROM build_requests
            WHERE processing_mode IN (
                'QUEUE_STANDARD',
                'QUEUE_BATCH'
            )
            ORDER BY id DESC
            """
        ).fetchall()

        result = []

        for parent in parents:
            items = db.execute(
                """
                SELECT *
                FROM build_request_items
                WHERE request_id = ?
                ORDER BY id
                """,
                (
                    parent["request_id"],
                )
            ).fetchall()

            result.append(
                request_summary(
                    parent,
                    items
                )
            )

    return {
        "count": len(result),
        "requests": result,
    }


@router.get("/api/queue/requests/{request_id}")
def queue_request_detail(request_id: str):
    with get_connection() as db:
        parent = db.execute(
            """
            SELECT *
            FROM build_requests
            WHERE request_id = ?
            """,
            (request_id,)
        ).fetchone()

        if parent is None:
            raise HTTPException(
                status_code=404,
                detail="Queue request not found."
            )

        rows = db.execute(
            """
            SELECT *
            FROM build_request_items
            WHERE request_id = ?
            ORDER BY lesson_number, id
            """,
            (request_id,)
        ).fetchall()

        summary = request_summary(
            parent,
            rows
        )

        items = []

        for row in rows:
            item = dict(row)

            current_stage = (
                row["stage"]
                or row["status"]
            )

            item["status_label"] = (
                status_label(current_stage)
            )

            item["failed"] = (
                item_is_failed(row)
            )

            items.append(item)

    return {
        "request": summary,
        "lesson_count": len(items),
        "items": items,
    }
