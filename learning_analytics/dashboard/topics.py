"""Question-level difficulty analytics for dashboard."""

from collections import defaultdict

from learning_analytics.database import (
    get_connection,
)
from learning_analytics.dashboard.attempts import (
    course_attempts,
)
from learning_analytics.dashboard.roles import (
    course_students,
)


CORRECT_STATUSES = {
    "correct",
    "mright",
    "gaveup_correct",
}


def is_correct_response(row):
    status = str(
        row.get("status") or ""
    ).strip().lower()

    if status in CORRECT_STATUSES:
        return True

    mark = row.get("mark")
    max_mark = row.get("max_mark")

    if mark is None or max_mark in (
        None,
        0,
        0.0,
    ):
        return False

    return float(mark) >= float(max_mark)


def course_question_responses(
        course_id,
        *,
        date_from=None,
        date_to=None
):
    attempts = course_attempts(
        course_id,
        date_from=date_from,
        date_to=date_to,
    )

    if not attempts:
        return []

    attempt_ids = {
        int(row["moodle_attempt_id"])
        for row in attempts
    }

    attempt_lookup = {
        int(row["moodle_attempt_id"]):
            row
        for row in attempts
    }

    placeholders = ",".join(
        "?"
        for _ in attempt_ids
    )

    sql = f"""
        SELECT
            id,
            moodle_attempt_id,
            moodle_user_id,
            moodle_quiz_id,
            question_key,
            moodle_slot,
            moodle_question_id,
            moodle_question_bank_entry_id,
            question_type,
            status,
            mark,
            max_mark,
            question_text,
            student_response,
            correct_response,
            updated_at
        FROM question_responses
        WHERE moodle_attempt_id
              IN ({placeholders})
        ORDER BY
            moodle_user_id,
            moodle_quiz_id,
            moodle_attempt_id,
            moodle_slot
    """

    with get_connection() as db:
        rows = [
            dict(row)
            for row in db.execute(
                sql,
                tuple(sorted(attempt_ids))
            ).fetchall()
        ]

    for row in rows:
        attempt = attempt_lookup.get(
            int(row["moodle_attempt_id"]),
            {}
        )

        row["curriculum_code"] = (
            attempt.get("curriculum_code")
        )

        row["lesson_package_id"] = (
            attempt.get("lesson_package_id")
        )

        row["attempt_number"] = (
            attempt.get("attempt_number")
        )

        row["time_finished"] = (
            attempt.get("time_finished")
        )

        row["correct"] = (
            is_correct_response(row)
        )

    return rows


def question_difficulty(
        course_id,
        *,
        date_from=None,
        date_to=None
):
    responses = course_question_responses(
        course_id,
        date_from=date_from,
        date_to=date_to,
    )

    students = {
        int(row["moodle_user_id"]):
            row
        for row in course_students(course_id)
    }

    grouped = defaultdict(list)

    for row in responses:
        key = (
            int(row["moodle_quiz_id"]),
            str(row["question_key"]),
        )

        grouped[key].append(row)

    result = []

    for (
        quiz_id,
        question_key
    ), rows in grouped.items():

        # Latest evidence for each student
        # prevents repeated attempts from
        # overweighting one learner.
        latest = {}

        for row in rows:
            user_id = int(
                row["moodle_user_id"]
            )

            previous = latest.get(user_id)

            if (
                previous is None
                or int(
                    row["moodle_attempt_id"]
                )
                > int(
                    previous[
                        "moodle_attempt_id"
                    ]
                )
            ):
                latest[user_id] = row

        attempted = len(latest)

        struggling = [
            row
            for row in latest.values()
            if not row["correct"]
        ]

        struggling_ids = {
            int(row["moodle_user_id"])
            for row in struggling
        }

        rate = (
            (
                len(struggling)
                / attempted
            ) * 100
            if attempted
            else 0.0
        )

        sample = rows[-1]

        result.append({
            "moodle_quiz_id":
                quiz_id,

            "curriculum_code":
                sample.get(
                    "curriculum_code"
                ),

            "question_key":
                question_key,

            "question_text":
                sample.get(
                    "question_text"
                ),

            "qtype":
                sample.get("question_type"),

            "students_attempted":
                attempted,

            "students_struggling":
                len(struggling),

            "difficulty_rate":
                round(rate, 2),


            "struggling_students": [
                {
                    "moodle_user_id":
                        user_id,

                    "fullname":
                        students.get(
                            user_id,
                            {}
                        ).get(
                            "fullname",
                            ""
                        ),
                }
                for user_id
                in sorted(struggling_ids)
            ],
        })

    result.sort(
        key=lambda row: (
            -row["difficulty_rate"],
            -row["students_struggling"],
            str(row["curriculum_code"]),
            str(row["question_key"]),
        )
    )

    return result
