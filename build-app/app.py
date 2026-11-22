import os
import asyncio
import uuid
from pathlib import Path
from datetime import datetime, timezone

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from api.workbook_reader import WorkbookReader
import httpx
from fastapi.responses import FileResponse
from publish_generated import publish_generated_lesson
from queue_dashboard import router as queue_dashboard_router

from build_registry import (
    get_connection,
    mark_published,
    create_build_request,
    create_multi_build_request
)

# ==========================================================
# Service URLs
# ==========================================================

LESSON_PACKAGE_BUILDER_URL = os.getenv(
    "LESSON_PACKAGE_BUILDER_URL",
    "http://192.168.1.108:8003/build"
)

PUBLISHER_ENGINE_URL = os.getenv(
    "PUBLISHER_ENGINE_URL",
    "http://publisher-engine:8012/publish"
)

# ==========================================================
# FastAPI App
# ==========================================================

app = FastAPI(title="Rono AI Curriculum Builder")

app.include_router(queue_dashboard_router)


# ==========================================================
# Static Files
# ==========================================================

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)


# ==========================================================
# HTML Templates
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


# ==========================================================
# Workbook
# ==========================================================

reader = WorkbookReader()

DASHBOARD_COURSE_TOTALS = {
    ("Australian Curriculum", "English", "Year 3"): 75,
}



def dashboard_default_course():
    conn = get_connection()
    import sqlite3
    conn.row_factory = sqlite3.Row

    row = conn.execute(
        """
        SELECT
            subject,
            year_level,
            COUNT(*) AS published_count
        FROM elaboration_builds
        WHERE status = 'PUBLISHED'
           OR moodle_course_id IS NOT NULL
        GROUP BY subject, year_level
        ORDER BY published_count DESC, subject, year_level
        LIMIT 1
        """
    ).fetchone()

    conn.close()

    if not row:
        return {
            "framework": "Australian Curriculum",
            "subject": "English",
            "year_level": "Year 3"
        }

    return {
        "framework": "Australian Curriculum",
        "subject": row["subject"],
        "year_level": row["year_level"]
    }

# ==========================================================
# Build Jobs
# ==========================================================

build_jobs = {}


def utc_now():

    return datetime.now(
        timezone.utc
    ).isoformat()


def update_job(
        job_id,
        *,
        status=None,
        stage=None,
        message=None,
        percent=None,
        result=None,
        error=None
):

    job = build_jobs.get(job_id)

    if not job:
        return

    if status is not None:
        job["status"] = status

    if stage is not None:
        job["stage"] = stage

    if message is not None:
        job["message"] = message

    if percent is not None:
        job["percent"] = percent

    if result is not None:
        job["result"] = result

    if error is not None:
        job["error"] = error

    job["updated_at"] = utc_now()


# Background Worker
async def run_build_job(
        job_id,
        payload
):

    try:

        update_job(
            job_id,
            status="RUNNING",
            stage="BUILDING",
            message="Building lesson package...",
            percent=20
        )

        downstream_payload = dict(
            payload
        )

        downstream_payload[
            "progress_job_id"
        ] = job_id

        downstream_payload[
            "progress_url"
        ] = "http://build-app:8002"

        async with httpx.AsyncClient() as client:

            response = await client.post(
                LESSON_PACKAGE_BUILDER_URL,
                json=downstream_payload,
                timeout=1800
            )
        print("=" * 60)
        print("LESSON PACKAGE BUILDER RESPONSE")
        print("JOB:", job_id)
        print("STATUS:", response.status_code)
        print("URL:", LESSON_PACKAGE_BUILDER_URL)
        print("=" * 60)

        if response.status_code != 200:

            try:

                error_data = response.json()

                error_detail = (
                    error_data.get("detail")
                    or
                    error_data.get("message")
                    or
                    str(error_data)
                )

            except Exception:

                error_detail = response.text

            raise RuntimeError(
                "Lesson Package Builder returned "
                f"HTTP {response.status_code}: "
                f"{error_detail}"
            )

        update_job(
            job_id,
            stage="FINALISING",
            message="Finalising lesson package...",
            percent=90
        )

        result = response.json()

        update_job(
            job_id,
            status="SUCCESS",
            stage="COMPLETE",
            message="Lesson package completed.",
            percent=100,
            result=result
        )

    except Exception as exc:

        print("=" * 60)
        print("BACKGROUND BUILD FAILED")
        print("JOB:", job_id)
        print(str(exc))
        print("=" * 60)

        update_job(
            job_id,
            status="FAILED",
            stage="FAILED",
            message="Lesson package build failed.",
            error=str(exc)
        )

# ==========================================================
# Home Page
# ==========================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="studio/dashboard.html",
        context={
            "title": "Rono AI Curriculum Builder"
        }
   )

# ==========================================================
# Curriculum Studio v4
# ==========================================================

@app.get("/v4", response_class=HTMLResponse)
async def curriculum_studio_v4(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index_v4.html",
        context={
            "title": "RONO'S SCHOOL | Curriculum Studio"
        }
    )


# ==========================================================
# Curriculum Studio
# ==========================================================

@app.get("/studio", response_class=HTMLResponse)
async def studio(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="studio/lesson_builder.html",
        context={
            "title": "Curriculum Studio"
        }
    )


@app.get("/analytics", response_class=HTMLResponse)
async def analytics(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="learning_analytics.html",
        context={
            "title": "Learning Analytics"
        }
    )



@app.get("/studio/curriculum-assistant", response_class=HTMLResponse)
async def curriculum_assistant(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="studio/curriculum_assistant.html",
        context={
            "title": "Curriculum Assistant"
        }
    )


# ==========================================================
# Health Check
# ==========================================================



@app.get("/analytics/docs")
async def analytics_docs():

    return RedirectResponse(
        url="http://localhost:8014/docs"
    )

@app.get("/health")
async def health():

    return {
        "status": "OK",
        "service": "Build App"
    }

# ==========================================================
# Year Levels
# ==========================================================




@app.get("/api/dashboard/courses")
def dashboard_courses():
    conn = get_connection()
    import sqlite3
    conn.row_factory = sqlite3.Row

    rows = conn.execute(
        """
        SELECT
            subject,
            year_level,
            COUNT(*) AS registry_count,
            SUM(
                CASE
                    WHEN status = 'PUBLISHED'
                      OR moodle_course_id IS NOT NULL
                    THEN 1 ELSE 0
                END
            ) AS published_count,
            MAX(updated_at) AS latest_update
        FROM elaboration_builds
        GROUP BY subject, year_level
        ORDER BY published_count DESC, latest_update DESC
        """
    ).fetchall()

    conn.close()

    courses = []

    for row in rows:
        framework = "Australian Curriculum"
        total = DASHBOARD_COURSE_TOTALS.get(
            (framework, row["subject"], row["year_level"]),
            row["registry_count"]
        )

        courses.append({
            "framework": framework,
            "subject": row["subject"],
            "year_level": row["year_level"],
            "label": f"{row['subject']} · {row['year_level']}",
            "published": row["published_count"] or 0,
            "registry_total": row["registry_count"],
            "total": total
        })

    return {
        "courses": courses
    }


@app.get("/api/dashboard/course-progress")
def dashboard_course_progress(
        subject: str = "English",
        year_level: str = "Year 3"
):
    conn = get_connection()
    conn.row_factory = __import__("sqlite3").Row

    rows = conn.execute(
        """
        SELECT
            curriculum_code,
            status,
            moodle_course_id,
            updated_at
        FROM elaboration_builds
        WHERE subject = ?
          AND year_level = ?
        ORDER BY curriculum_code
        """,
        (subject, year_level)
    ).fetchall()

    registry_total = len(rows)

    try:
        curriculum_total = reader.count_master_lessons(
            subject=subject,
            year_level=year_level
        )
    except Exception as exc:
        print("MASTER LESSON COUNT FAILED:", exc)
        curriculum_total = registry_total

    total = max(curriculum_total, registry_total)

    published = sum(
        1 for row in rows
        if row["status"] == "PUBLISHED"
           or row["moodle_course_id"] is not None
    )
    failed = sum(
        1 for row in rows
        if "FAIL" in str(row["status"]).upper()
           or "ERROR" in str(row["status"]).upper()
    )
    update_ready = sum(
        1 for row in rows
        if row["status"] == "UPDATE_READY"
    )
    remaining = max(total - published, 0)
    progress = round((published / total) * 100) if total else 0

    published_rows = [
        row for row in rows
        if row["status"] == "PUBLISHED"
           or row["moodle_course_id"] is not None
    ]
    unpublished_rows = [
        row for row in rows
        if not (
            row["status"] == "PUBLISHED"
            or row["moodle_course_id"] is not None
        )
    ]

    last_completed = (
        published_rows[-1]["curriculum_code"]
        if published_rows else ""
    )
    next_lesson = (
        unpublished_rows[0]["curriculum_code"]
        if unpublished_rows else ""
    )

    active_request = conn.execute(
        """
        SELECT
            request_id,
            processing_mode,
            subject,
            year_level,
            lesson_numbers,
            status,
            started_at,
            updated_at,
            created_at
        FROM build_requests
        WHERE status IN (
            'QUEUED',
            'RUNNING',
            'PROCESSING',
            'BUILDING',
            'PUBLISHING',
            'BATCH_PROCESSING',
            'BATCH_STAGE1_READY',
            'BATCH_STAGE1_SUBMITTED',
            'BATCH_STAGE1_DOWNLOADED',
            'BATCH_STAGE1_APPLIED',
            'BATCH_STAGE2_READY',
            'BATCH_STAGE2_SUBMITTED',
            'BATCH_STAGE2_DOWNLOADED',
            'BATCH_STAGE2_APPLIED',
            'EXTERNAL_ASSETS_COMPLETED'
        )
        ORDER BY updated_at DESC
        LIMIT 1
        """
    ).fetchone()

    queue = {
        "active": False,
        "status": "No active processing",
        "processing_mode": "No active processing",
        "current_lesson": "",
        "completed": 0,
        "total": 0,
        "percent": 0,
        "eta": "--"
    }

    if active_request:
        request_id = active_request["request_id"]
        request_status = str(active_request["status"] or "").upper()

        child_rows = conn.execute(
            """
            SELECT curriculum_code, status, stage, percent
            FROM build_request_items
            WHERE request_id = ?
            ORDER BY id
            """,
            (request_id,)
        ).fetchall()

        queue_total = len(child_rows)
        queue_completed = sum(
            1 for child in child_rows
            if str(child["status"] or "").upper() == "PUBLISHED"
        )

        current_row = next(
            (
                child for child in child_rows
                if str(child["status"] or "").upper() != "PUBLISHED"
            ),
            None
        )

        stage_percent = {
            "QUEUED": 2,
            "RUNNING": 5,
            "PROCESSING": 5,
            "BUILDING": 8,
            "BATCH_PROCESSING": 8,
            "BATCH_STAGE1_READY": 10,
            "BATCH_STAGE1_SUBMITTED": 20,
            "BATCH_STAGE1_DOWNLOADED": 30,
            "BATCH_STAGE1_APPLIED": 40,
            "BATCH_STAGE2_READY": 50,
            "BATCH_STAGE2_SUBMITTED": 60,
            "BATCH_STAGE2_DOWNLOADED": 70,
            "BATCH_STAGE2_APPLIED": 80,
            "EXTERNAL_ASSETS_COMPLETED": 90,
            "PUBLISHING": 95,
        }.get(request_status, 5)

        item_percent = 0
        if child_rows:
            item_percent = int(
                sum(int(child["percent"] or 0) for child in child_rows)
                / len(child_rows)
            )

        queue_percent = max(stage_percent, item_percent)

        stage_label = {
            "QUEUED": "Waiting to start",
            "RUNNING": "Preparing lessons",
            "PROCESSING": "Preparing lessons",
            "BUILDING": "Generating lessons",
            "BATCH_PROCESSING": "Preparing batch",
            "BATCH_STAGE1_READY": "Preparing lesson content",
            "BATCH_STAGE1_SUBMITTED": "Generating lesson content",
            "BATCH_STAGE1_DOWNLOADED": "Lesson content received",
            "BATCH_STAGE1_APPLIED": "Lesson content prepared",
            "BATCH_STAGE2_READY": "Preparing learning activities",
            "BATCH_STAGE2_SUBMITTED": "Generating learning activities",
            "BATCH_STAGE2_DOWNLOADED": "Learning activities received",
            "BATCH_STAGE2_APPLIED": "Learning activities prepared",
            "EXTERNAL_ASSETS_COMPLETED": "Publishing lessons",
            "PUBLISHING": "Publishing lessons",
        }.get(request_status, "Batch processing")

        eta = "Calculating"
        started_value = (
            active_request["started_at"]
            or active_request["created_at"]
        )

        if started_value and 0 < queue_percent < 100:
            try:
                started_text = str(started_value).replace("Z", "+00:00")
                started = datetime.fromisoformat(started_text)
                if started.tzinfo is None:
                    started = started.replace(tzinfo=timezone.utc)

                elapsed_seconds = max(
                    1,
                    int((datetime.now(timezone.utc) - started).total_seconds())
                )
                remaining_seconds = int(
                    elapsed_seconds
                    * (100 - queue_percent)
                    / queue_percent
                )

                if remaining_seconds < 60:
                    eta = "Less than 1 min"
                elif remaining_seconds < 3600:
                    eta = f"About {(remaining_seconds + 59) // 60} min"
                else:
                    hours = remaining_seconds // 3600
                    minutes = (remaining_seconds % 3600) // 60
                    eta = f"About {hours}h {minutes}m"
            except (TypeError, ValueError):
                eta = "Calculating"

        queue = {
            "active": True,
            "status": stage_label,
            "processing_mode": (
                "Batch Processing"
                if active_request["processing_mode"] == "QUEUE_BATCH"
                else "Queue Processing"
            ),
            "current_lesson": (
                current_row["curriculum_code"]
                if current_row else "Finalising"
            ),
            "completed": queue_completed,
            "total": queue_total,
            "percent": queue_percent,
            "eta": eta
        }

    conn.close()

    return {
        "course": {
            "subject": subject,
            "year_level": year_level,
            "label": f"{subject} · {year_level}",
            "total": total,
            "published": published,
            "remaining": remaining,
            "failed": failed,
            "update_ready": update_ready,
            "progress": progress,
            "last_completed": last_completed,
            "next_lesson": next_lesson
        },
        "queue": queue
    }




@app.get("/api/curriculum/default")
def curriculum_default():
    return dashboard_default_course()



@app.get("/api/dashboard/activity")
def dashboard_activity():
    conn = get_connection()
    import sqlite3
    conn.row_factory = sqlite3.Row

    failed_count = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM elaboration_builds
        WHERE status LIKE '%FAIL%'
           OR status LIKE '%ERROR%'
        """
    ).fetchone()["count"]

    update_count = conn.execute(
        """
        SELECT COUNT(*) AS count
        FROM elaboration_builds
        WHERE status = 'UPDATE_READY'
        """
    ).fetchone()["count"]

    latest_batch = conn.execute(
        """
        SELECT
            request_id,
            processing_mode,
            status,
            lesson_numbers,
            completed_at,
            updated_at
        FROM build_requests
        WHERE status IN ('COMPLETED', 'SUCCESS', 'PUBLISHED')
        ORDER BY COALESCE(completed_at, updated_at) DESC
        LIMIT 1
        """
    ).fetchone()

    recent_publications = conn.execute(
        """
        SELECT
            subject,
            year_level,
            COUNT(*) AS lesson_count,
            MAX(updated_at) AS latest_published
        FROM elaboration_builds
        WHERE status = 'PUBLISHED'
           OR moodle_course_id IS NOT NULL
        GROUP BY subject, year_level
        ORDER BY latest_published DESC
        LIMIT 3
        """
    ).fetchall()

    notifications = []

    if latest_batch:
        lessons = [
            item.strip()
            for item in str(latest_batch["lesson_numbers"]).split(",")
            if item.strip()
        ]

        notifications.append({
            "type": "success",
            "title": f"Batch completed — {len(lessons)} lessons published",
            "time": "Recently"
        })

    notifications.append({
        "type": "info",
        "title": "Curriculum framework selection is available",
        "time": "Today"
    })

    if update_count:
        notifications.append({
            "type": "warning",
            "title": f"{update_count} lessons can be updated with new features",
            "time": "Today"
        })

    if failed_count:
        notifications.append({
            "type": "danger",
            "title": f"{failed_count} lessons failed — review required",
            "time": "Today"
        })

    conn.close()

    return {
        "notifications": notifications[:4],
        "recent_publications": [
            {
                "course": f"{row['subject']} {row['year_level']}",
                "lessons": row["lesson_count"],
                "status": "Published"
            }
            for row in recent_publications
        ],
        "platform_status": [
            {
                "name": "Lesson Generation",
                "status": "Operational"
            },
            {
                "name": "Images",
                "status": "Operational"
            },
            {
                "name": "Queue Dashboard",
                "status": "Operational"
            }
        ]
    }


@app.get("/api/year-levels")
async def get_year_levels():

    reader.reload()

    return reader.get_year_levels()
# ==========================================================
# Build Request
# ==========================================================

@app.post("/api/build")
async def build(request: Request):

    payload = await request.json()

    processing_mode = str(
        payload.get(
            "processing_mode",
            "IMMEDIATE"
        )
    ).strip().upper()

    if processing_mode in (
        "QUEUE_STANDARD",
        "QUEUE_BATCH"
    ):

        items = payload.get(
            "items",
            []
        )

        if items:

            request_id = create_multi_build_request(
                requested_by=payload.get(
                    "requested_by",
                    ""
                ),
                processing_mode=processing_mode,
                learning_area=payload.get(
                    "learning_area",
                    ""
                ),
                subject=payload.get(
                    "subject",
                    ""
                ),
                year_level=payload.get(
                    "year_level",
                    ""
                ),
                strand=payload.get(
                    "strand",
                    ""
                ),
                sub_strand=payload.get(
                    "sub_strand",
                    ""
                ),
                items=items
            )

            return {
                "status": "QUEUED",
                "request_id": request_id,
                "processing_mode": processing_mode,
                "item_count": len(items),
                "message":
                    "Multi-content build request queued successfully."
            }

        request_id = create_build_request(
            requested_by=payload.get(
                "requested_by",
                ""
            ),
            processing_mode=processing_mode,
            learning_area=payload.get(
                "learning_area",
                ""
            ),
            subject=payload.get(
                "subject",
                ""
            ),
            year_level=payload.get(
                "year_level",
                ""
            ),
            strand=payload.get(
                "strand",
                ""
            ),
            sub_strand=payload.get(
                "sub_strand",
                ""
            ),
            parent_code=payload.get(
                "parent_code",
                ""
            ),
            lesson_numbers=payload.get(
                "lesson_numbers",
                []
            )
        )

        return {
            "status": "QUEUED",
            "request_id": request_id,
            "processing_mode": processing_mode,
            "message":
                "Build request queued successfully."
        }

    if processing_mode != "IMMEDIATE":

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid processing_mode. "
                "Expected IMMEDIATE, "
                "QUEUE_STANDARD or QUEUE_BATCH."
            )
        )

    job_id = uuid.uuid4().hex

    build_jobs[job_id] = {
        "job_id": job_id,
        "status": "QUEUED",
        "stage": "PREPARING",
        "message": "Preparing curriculum build...",
        "percent": 10,
        "result": None,
        "error": None,
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }

    asyncio.create_task(
        run_build_job(
            job_id,
            payload
        )
    )

    return {
        "status": "ACCEPTED",
        "job_id": job_id,
        "percent": 10,
        "message": "Build accepted."
    }

# ==========================================================
# Pipeline Progress Callback
# ==========================================================

@app.post("/api/build-progress/{job_id}")
async def build_progress(
        job_id: str,
        request: Request
):

    job = build_jobs.get(job_id)

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Build job not found."
        )

    data = await request.json()

    stage = data.get("stage")
    message = data.get("message")
    percent = data.get("percent")

    if percent is not None:

        percent = max(
            0,
            min(
                99,
                int(percent)
            )
        )

    update_job(
        job_id,
        status="RUNNING",
        stage=stage,
        message=message,
        percent=percent
    )

    print(
        "BUILD PROGRESS:",
        job_id,
        percent,
        stage,
        message
    )

    return {
        "status": "OK",
        "job_id": job_id
    }


@app.get("/api/build-status/{job_id}")
async def build_status(job_id: str):

    job = build_jobs.get(job_id)

    if not job:

        raise HTTPException(
            status_code=404,
            detail="Build job not found."
        )

    return job


# ==========================================================
# Publish Generated Lesson
# ==========================================================

@app.post("/api/publish-generated")
async def publish_generated(request: Request):

    payload = await request.json()

    return await publish_generated_lesson(
        payload
    )


# ==========================================================
# Curriculum Build Selection Proxy
# ==========================================================

@app.get("/api/build-selection")
async def build_selection_proxy(
        learning_area: str,
        subject: str,
        year_level: str,
        strand: str,
        sub_strand: str = ""
):

    params = {
        "learning_area": learning_area,
        "subject": subject,
        "year_level": year_level,
        "strand": strand,
    }

    if sub_strand:
        params["sub_strand"] = sub_strand

    async with httpx.AsyncClient(
        timeout=60
    ) as client:

        response = await client.get(
            "http://curriculum-normalizer:8001/build-selection",
            params=params
        )

    if response.status_code != 200:

        raise HTTPException(
            status_code=response.status_code,
            detail=(
                "Curriculum Normalizer returned "
                f"HTTP {response.status_code}: "
                + response.text
            )
        )

    return response.json()
