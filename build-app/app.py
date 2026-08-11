import os
import asyncio
import uuid

from datetime import datetime, timezone

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from api.workbook_reader import WorkbookReader
import httpx
from fastapi.responses import FileResponse

# ==========================================================
# Service URLs
# ==========================================================

LESSON_PACKAGE_BUILDER_URL = os.getenv(
    "LESSON_PACKAGE_BUILDER_URL",
    "http://192.168.1.108:8003/build"
)

# ==========================================================
# FastAPI App
# ==========================================================

app = FastAPI(title="Rono AI Curriculum Builder")


# ==========================================================
# Static Files
# ==========================================================

app.mount("/static", StaticFiles(directory="static"), name="static")


# ==========================================================
# HTML Templates
# ==========================================================

templates = Jinja2Templates(directory="templates")


# ==========================================================
# Workbook
# ==========================================================

reader = WorkbookReader()
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
        name="index.html",
        context={
            "title": "Rono AI Curriculum Builder"
        }
    )

# ==========================================================
# Health Check
# ==========================================================

@app.get("/health")
async def health():

    return {
        "status": "OK",
        "service": "Build App"
    }

# ==========================================================
# Year Levels
# ==========================================================

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
