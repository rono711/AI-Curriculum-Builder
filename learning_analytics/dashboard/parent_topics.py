"""Parent-topic difficulty aggregation for dashboard."""

from collections import defaultdict

from learning_analytics.dashboard.lessons import (
    lesson_difficulty,
)


def parent_topic_difficulty(
        course_id,
        *,
        date_from=None,
        date_to=None
):
    lessons = lesson_difficulty(
        course_id,
        date_from=date_from,
        date_to=date_to,
    )

    grouped = defaultdict(list)

    for lesson in lessons:
        parent_code = str(
            lesson.get("parent_code")
            or ""
        ).strip()

        if parent_code:
            grouped[parent_code].append(
                lesson
            )

    result = []

    for parent_code, rows in grouped.items():
        evidence_students = {}
        struggling_students = {}

        for lesson in rows:
            for question in lesson["questions"]:
                for student in question.get(
                    "latest_students",
                    []
                ):
                    user_id = int(
                        student["moodle_user_id"]
                    )

                    evidence_students[user_id] = {
                        "moodle_user_id":
                            user_id,

                        "fullname":
                            student["fullname"],
                    }

            for student in lesson[
                "struggling_students"
            ]:
                user_id = int(
                    student["moodle_user_id"]
                )

                struggling_students[user_id] = {
                    "moodle_user_id":
                        user_id,

                    "fullname":
                        student["fullname"],
                }

        evidence_count = len(
            evidence_students
        )

        struggling_count = len(
            struggling_students
        )

        rate = (
            struggling_count
            / evidence_count
            * 100
            if evidence_count
            else 0.0
        )

        problem_lessons = [
            lesson
            for lesson in rows
            if lesson[
                "students_struggling"
            ] > 0
        ]

        result.append({
            "parent_code":
                parent_code,

            "subject":
                rows[0]["subject"],

            "year_level":
                rows[0]["year_level"],

            "lesson_count":
                len(rows),

            "problem_lesson_count":
                len(problem_lessons),

            "students_with_evidence":
                evidence_count,

            "students_struggling":
                struggling_count,

            "difficulty_rate":
                round(rate, 2),

            "struggling_students":
                sorted(
                    struggling_students.values(),
                    key=lambda item:
                        item["fullname"],
                ),

            "problem_lessons":
                problem_lessons,

            "lessons":
                rows,
        })

    result.sort(
        key=lambda row: (
            -row["difficulty_rate"],
            -row["students_struggling"],
            row["parent_code"],
        )
    )

    return result
