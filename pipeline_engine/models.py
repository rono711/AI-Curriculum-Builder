from typing import Any, Dict, List, Optional

from pydantic import BaseModel


# ==========================================================
# Pipeline Request
# ==========================================================

class PipelineRequest(BaseModel):

    build_root: str

    build_name: str

    lesson_rows: List[Dict[str, Any]]


    progress_job_id: str = ""

    progress_url: str = ""

# ==========================================================
# Lesson Result
# ==========================================================

class LessonResult(BaseModel):

    lesson_package_id: str

    curriculum_code: Optional[str] = None

    status: str


# ==========================================================
# Pipeline Response
# ==========================================================

class PipelineResponse(BaseModel):

    status: str

    build_root: str

    build_name: str

    lesson_count: int

    lessons: List[LessonResult] = []
