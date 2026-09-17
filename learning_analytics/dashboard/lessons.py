"""Lesson-level difficulty aggregation for dashboard."""

from collections import defaultdict

from learning_analytics.dashboard.topics import (
    question_difficulty,
)
from learning_analytics.dashboard.curriculum import (
    lesson_metadata,
)


def lesson_difficulty(
        course_id,
        *,
        date_from=None,
        date_to=None
):
    questions = question_difficulty(
        course_id,
        date_from=date_from,
        date_to=date_to,
    )

    grouped = defaultdict(list)

    for row in questions:
        code = str(
            row.get("curriculum_code")
            or ""
        ).strip()

        if not code:
            continue

        grouped[code].append(row)

    result = []

    for code, rows in grouped.items():
        quiz_ids = {
            int(row["moodle_quiz_id"])
            for row in rows
        }

        if len(quiz_ids) != 1:
            raise RuntimeError(
                "Lesson difficulty contains "
                "multiple Moodle quizzes for "
                + code
                + ": "
                + str(sorted(quiz_ids))
            )

        quiz_id = next(iter(quiz_ids))

        metadata = lesson_metadata(
            moodle_quiz_id=quiz_id
        )

        if metadata is None:
            raise RuntimeError(
                "No published curriculum metadata "
                "for Moodle quiz "
                + str(quiz_id)
            )

        student_evidence = {}

        for row in rows:
            for student in row[
                "struggling_students"
            ]:
                user_id = int(
                    student["moodle_user_id"]
                )

                student_evidence[user_id] = {
                    "moodle_user_id":
                        user_id,

                    "fullname":
                        student["fullname"],
                }

        attempted_ids = set()

        for row in rows:
            for student in row.get(
                "latest_students",
                []
            ):
                attempted_ids.add(
                    int(
                        student[
                            "moodle_user_id"
                        ]
                    )
                )

        attempted = len(
            attempted_ids
        )

        struggling = len(
            student_evidence
        )

        rate = (
            struggling
            / attempted
            * 100
            if attempted
            else 0.0
        )

        result.append({
            "curriculum_code":
                code,

            "moodle_quiz_id":
                quiz_id,

            "parent_code":
                metadata["parent_code"],

            "topic_id":
                metadata["topic_id"],

            "lesson_title":
                metadata["elaboration"],

            "content_description":
                metadata["content_description"],

            "subject":
                metadata["subject"],

            "year_level":
                metadata["year_level"],

            "question_count":
                len(rows),

            "students_with_evidence":
                attempted,

            "students_struggling":
                struggling,

            "difficulty_rate":
                round(rate, 2),

            "struggling_students":
                sorted(
                    student_evidence.values(),
                    key=lambda item:
                        item["fullname"],
                ),

            "questions":
                rows,

            "problem_questions": [
                row
                for row in rows
                if row[
                    "students_struggling"
                ] > 0
            ],
        })

    result.sort(
        key=lambda row: (
            -row["difficulty_rate"],
            -row["students_struggling"],
            row["curriculum_code"],
        )
    )

    return result
