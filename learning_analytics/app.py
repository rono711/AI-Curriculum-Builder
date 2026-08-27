"""Learning analytics service entry point."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from learning_analytics.attempt_processor import (
    quiz_identity,
)
from learning_analytics.curriculum_resolver import (
    resolve_curriculum_identity,
)
from learning_analytics.moodle_client import (
    MoodleAnalyticsClient,
)
from learning_analytics.processing_service import (
    LearningAnalyticsProcessingService,
)
from learning_analytics.student_resolver import (
    MoodleStudentResolver,
)


app = FastAPI(
    title="Rono's School Learning Analytics",
    version="1.0.0",
)


class ProcessAttemptRequest(BaseModel):
    moodle_attempt_id: int
    moodle_user_id: int


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "learning-analytics",
    }


@app.post("/attempts/process")
def process_attempt(
        request: ProcessAttemptRequest
):
    try:
        client = MoodleAnalyticsClient()

        review = client.get_attempt_review(
            request.moodle_attempt_id
        )

        attempt = review.get(
            "attempt",
            {}
        )

        if not attempt:
            raise RuntimeError(
                "Moodle review contains no attempt."
            )

        actual_attempt_id = int(
            attempt["id"]
        )

        if actual_attempt_id != \
                request.moodle_attempt_id:
            raise RuntimeError(
                "Returned Moodle attempt ID does "
                "not match requested attempt."
            )

        moodle_quiz_id = int(
            attempt["quiz"]
        )

        client.verify_attempt_owner(
            quiz_id=moodle_quiz_id,
            user_id=request.moodle_user_id,
            attempt_id=request.moodle_attempt_id
        )

        identity = quiz_identity(
            moodle_quiz_id
        )

        student = MoodleStudentResolver().resolve(
            moodle_course_id=
                identity["moodle_course_id"],
            moodle_user_id=
                request.moodle_user_id
        )

        curriculum = resolve_curriculum_identity(
            identity["curriculum_code"]
        )

        student_name = (
            student.get("firstname")
            or student["fullname"]
        )

        result = (
            LearningAnalyticsProcessingService()
            .process_review(
                review=review,
                moodle_user_id=
                    request.moodle_user_id,
                student_name=
                    student_name,
                year_level=
                    curriculum["year_level"]
            )
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc


@app.get("/quizzes/{moodle_quiz_id}/attempts")
def scan_quiz_attempts(
        moodle_quiz_id: int
):
    """Read-only discovery of finished Moodle attempts."""

    try:
        from learning_analytics.attempt_detector import (
            FinishedAttemptDetector,
        )

        return (
            FinishedAttemptDetector()
            .scan_quiz(
                moodle_quiz_id=
                    moodle_quiz_id
            )
        )

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc
