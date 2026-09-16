"""Read-only attempt queries for the Analytics dashboard."""

from datetime import datetime, timezone

from build_registry import (
    get_active_analytics_quizzes,
)
from learning_analytics.database import (
    get_connection,
)
from learning_analytics.dashboard.roles import (
    course_students,
)


def unix_timestamp(value):
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return int(value)

    text = str(value).strip()

    if not text:
        return None

    try:
        return int(text)
    except ValueError:
        pass

    dt = datetime.fromisoformat(
        text.replace("Z", "+00:00")
    )

    if dt.tzinfo is None:
        dt = dt.replace(
            tzinfo=timezone.utc
        )

    return int(dt.timestamp())


def course_quizzes(course_id):
    course_id = int(course_id)

    return [
        row
        for row in get_active_analytics_quizzes()
        if int(
            row["moodle_course_id"]
        ) == course_id
    ]


def course_attempts(
        course_id,
        *,
        date_from=None,
        date_to=None,
        current_students_only=True
):
    course_id = int(course_id)

    quiz_ids = {
        int(row["moodle_quiz_id"])
        for row in course_quizzes(course_id)
    }

    if not quiz_ids:
        return []

    student_ids = {
        int(row["moodle_user_id"])
        for row in course_students(course_id)
    }

    from_ts = unix_timestamp(date_from)
    to_ts = unix_timestamp(date_to)

    placeholders = ",".join(
        "?"
        for _ in quiz_ids
    )

    sql = f"""
        SELECT
            id,
            moodle_attempt_id,
            moodle_quiz_id,
            moodle_user_id,
            attempt_number,
            state,
            raw_score,
            max_score,
            percentage,
            time_started,
            time_finished,
            build_id,
            lesson_package_id,
            curriculum_code,
            lifecycle_status,
            processed_at
        FROM quiz_attempts
        WHERE lifecycle_status = 'ACTIVE'
          AND moodle_quiz_id IN ({placeholders})
    """

    params = list(
        sorted(quiz_ids)
    )

    if from_ts is not None:
        sql += """
            AND COALESCE(
                time_finished,
                time_started
            ) >= ?
        """
        params.append(from_ts)

    if to_ts is not None:
        sql += """
            AND COALESCE(
                time_finished,
                time_started
            ) <= ?
        """
        params.append(to_ts)

    sql += """
        ORDER BY
            moodle_user_id,
            moodle_quiz_id,
            attempt_number,
            moodle_attempt_id
    """

    with get_connection() as db:
        rows = [
            dict(row)
            for row in db.execute(
                sql,
                tuple(params)
            ).fetchall()
        ]

    if current_students_only:
        rows = [
            row
            for row in rows
            if int(
                row["moodle_user_id"]
            ) in student_ids
        ]

    return rows
