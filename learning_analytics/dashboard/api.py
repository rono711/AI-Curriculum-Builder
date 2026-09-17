"""Read-only FastAPI routes for Learning Analytics dashboard."""

from fastapi import APIRouter, HTTPException, Query

from learning_analytics.dashboard.roles import (
    course_students,
    course_staff,
)
from learning_analytics.dashboard.attempts import (
    course_attempts,
    course_quizzes,
)
from learning_analytics.dashboard.parent_topics import (
    parent_topic_difficulty,
)
from learning_analytics.dashboard.topic_trends import (
    parent_topic_history,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Learning Analytics Dashboard"],
)


@router.get("/course/{course_id}/overview")
def course_overview(
        course_id: int,
        date_from: str | None = Query(None),
        date_to: str | None = Query(None)
):
    students = course_students(course_id)
    staff = course_staff(course_id)

    attempts = course_attempts(
        course_id,
        date_from=date_from,
        date_to=date_to,
    )

    quizzes = course_quizzes(course_id)

    active_student_ids = {
        int(row["moodle_user_id"])
        for row in attempts
    }

    percentages = [
        float(row["percentage"])
        for row in attempts
        if row.get("percentage") is not None
    ]

    average_score = (
        round(
            sum(percentages)
            / len(percentages),
            2
        )
        if percentages
        else None
    )

    return {
        "course_id":
            int(course_id),

        "date_from":
            date_from,

        "date_to":
            date_to,

        "enrolled_students":
            len(students),

        "students_with_activity":
            len(active_student_ids),

        "staff_count":
            len(staff),

        "quiz_count":
            len(quizzes),

        "attempt_count":
            len(attempts),

        "average_attempt_score":
            average_score,
    }


@router.get("/course/{course_id}/students")
def students(course_id: int):
    return {
        "course_id":
            int(course_id),

        "students":
            course_students(course_id),

        "staff":
            course_staff(course_id),
    }


@router.get("/course/{course_id}/topics")
def topics(
        course_id: int,
        date_from: str | None = Query(None),
        date_to: str | None = Query(None)
):
    rows = parent_topic_difficulty(
        course_id,
        date_from=date_from,
        date_to=date_to,
    )

    return {
        "course_id":
            int(course_id),

        "date_from":
            date_from,

        "date_to":
            date_to,

        "topic_count":
            len(rows),

        "topics":
            rows,
    }


@router.get("/course/{course_id}/topics/history")
def topic_history(
        course_id: int,
        date_from: str = Query(...),
        date_to: str = Query(...),
        bucket_days: int = Query(
            7,
            ge=1,
            le=365,
        )
):
    try:
        result = parent_topic_history(
            course_id,
            date_from=date_from,
            date_to=date_to,
            bucket_days=bucket_days,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return result
