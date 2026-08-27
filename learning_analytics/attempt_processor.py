"""Process and normalise Moodle quiz attempts."""

import sqlite3

from learning_analytics.config import BUILD_REGISTRY_DB


def question_registry_for_quiz(quiz_id):
    db = sqlite3.connect(BUILD_REGISTRY_DB)
    db.row_factory = sqlite3.Row

    try:
        rows = db.execute(
            """
            SELECT
                question_key,
                build_id,
                lesson_package_id,
                curriculum_code,
                moodle_course_id,
                moodle_quiz_id,
                moodle_quiz_cmid,
                moodle_question_id,
                moodle_question_bank_entry_id,
                moodle_slot,
                question_type
            FROM quiz_questions
            WHERE moodle_quiz_id = ?
            ORDER BY moodle_slot
            """,
            (int(quiz_id),)
        ).fetchall()

        return {
            int(row["moodle_slot"]): dict(row)
            for row in rows
        }

    finally:
        db.close()


def normalize_attempt(review, user_id):
    """Map one Moodle attempt review to stable CB question identities."""

    from learning_analytics.review_parser import parse_question

    attempt = review.get("attempt", {})

    if not attempt:
        raise RuntimeError(
            "Moodle review contains no attempt."
        )

    attempt_id = int(attempt["id"])
    quiz_id = int(attempt["quiz"])

    mappings = question_registry_for_quiz(
        quiz_id
    )

    questions = review.get(
        "questions",
        []
    )

    if len(mappings) != len(questions):
        raise RuntimeError(
            f"Quiz {quiz_id}: registry has "
            f"{len(mappings)} questions but "
            f"attempt {attempt_id} has "
            f"{len(questions)} questions."
        )

    responses = []

    for question in questions:
        evidence = parse_question(
            question
        )

        slot = evidence["slot"]

        mapping = mappings.get(
            slot
        )

        if not mapping:
            raise RuntimeError(
                f"Quiz {quiz_id} slot {slot} "
                "has no CB question mapping."
            )

        responses.append({
            "moodle_attempt_id":
                attempt_id,

            "moodle_user_id":
                int(user_id),

            "moodle_quiz_id":
                quiz_id,

            "moodle_slot":
                slot,

            "question_key":
                mapping["question_key"],

            "moodle_question_id":
                mapping["moodle_question_id"],

            "moodle_question_bank_entry_id":
                mapping[
                    "moodle_question_bank_entry_id"
                ],

            "question_type":
                evidence["question_type"],

            "status":
                evidence["status"],

            "mark":
                evidence["mark"],

            "max_mark":
                evidence["max_mark"],

            "question_text":
                evidence["question_text"],

            "student_response":
                evidence["student_response"],

            "correct_response":
                evidence["correct_response"],

            "raw_review":
                question,
        })

    raw_score = sum(
        item["mark"]
        for item in responses
    )

    max_score = sum(
        item["max_mark"]
        for item in responses
    )

    first = mappings[
        min(mappings)
    ]

    return {
        "attempt": {
            "moodle_attempt_id":
                attempt_id,

            "moodle_quiz_id":
                quiz_id,

            "moodle_user_id":
                int(user_id),

            "attempt_number":
                int(
                    attempt.get(
                        "attempt",
                        0
                    )
                    or 0
                ),

            "state":
                str(
                    attempt.get(
                        "state",
                        ""
                    )
                ),

            "raw_score":
                raw_score,

            "max_score":
                max_score,

            "percentage":
                (
                    raw_score
                    / max_score
                    * 100
                    if max_score
                    else 0.0
                ),

            "time_started":
                attempt.get("timestart"),

            "time_finished":
                attempt.get("timefinish"),

            "build_id":
                first["build_id"],

            "lesson_package_id":
                first["lesson_package_id"],

            "curriculum_code":
                first["curriculum_code"],
        },

        "responses":
            responses,
    }


def quiz_identity(quiz_id):
    """Return the single curriculum identity registered to a quiz."""

    mappings = question_registry_for_quiz(
        quiz_id
    )

    if not mappings:
        raise RuntimeError(
            f"Quiz {quiz_id} has no registered questions."
        )

    curriculum_codes = {
        row["curriculum_code"]
        for row in mappings.values()
    }

    course_ids = {
        int(row["moodle_course_id"])
        for row in mappings.values()
    }

    if len(curriculum_codes) != 1:
        raise RuntimeError(
            f"Quiz {quiz_id} maps to multiple "
            f"curriculum codes: "
            f"{sorted(curriculum_codes)}"
        )

    if len(course_ids) != 1:
        raise RuntimeError(
            f"Quiz {quiz_id} maps to multiple "
            f"Moodle courses: "
            f"{sorted(course_ids)}"
        )

    return {
        "curriculum_code":
            next(iter(curriculum_codes)),

        "moodle_course_id":
            next(iter(course_ids)),
    }
