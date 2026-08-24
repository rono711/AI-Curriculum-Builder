"""Learning analytics database access."""

import sqlite3
from datetime import datetime, timezone

from learning_analytics.config import ANALYTICS_DB, DATA_DIR


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def get_connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    db = sqlite3.connect(
        ANALYTICS_DB,
        timeout=30
    )

    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")

    return db


def initialize_database():
    with get_connection() as db:

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                moodle_attempt_id INTEGER NOT NULL UNIQUE,
                moodle_quiz_id INTEGER NOT NULL,
                moodle_user_id INTEGER NOT NULL,
                attempt_number INTEGER NOT NULL,
                state TEXT NOT NULL,
                raw_score REAL,
                max_score REAL,
                percentage REAL,
                time_started INTEGER,
                time_finished INTEGER,
                build_id TEXT,
                lesson_package_id TEXT,
                curriculum_code TEXT,
                processed_at TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS question_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                moodle_attempt_id INTEGER NOT NULL,
                moodle_user_id INTEGER NOT NULL,
                moodle_quiz_id INTEGER NOT NULL,
                moodle_slot INTEGER NOT NULL,
                question_key TEXT NOT NULL,
                moodle_question_id INTEGER,
                moodle_question_bank_entry_id INTEGER,
                question_type TEXT,
                status TEXT,
                mark REAL,
                max_mark REAL,
                question_text TEXT,
                student_response TEXT,
                correct_response TEXT,
                raw_review_json TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE (moodle_attempt_id, question_key)
            )
            """
        )

        db.commit()


def save_attempt(attempt):
    """Insert or update one normalized Moodle attempt."""

    now = utc_now()

    with get_connection() as db:
        db.execute(
            """
            INSERT INTO quiz_attempts (
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
                processed_at,
                created_at,
                updated_at
            )
            VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?
            )
            ON CONFLICT(moodle_attempt_id)
            DO UPDATE SET
                moodle_quiz_id = excluded.moodle_quiz_id,
                moodle_user_id = excluded.moodle_user_id,
                attempt_number = excluded.attempt_number,
                state = excluded.state,
                raw_score = excluded.raw_score,
                max_score = excluded.max_score,
                percentage = excluded.percentage,
                time_started = excluded.time_started,
                time_finished = excluded.time_finished,
                build_id = excluded.build_id,
                lesson_package_id = excluded.lesson_package_id,
                curriculum_code = excluded.curriculum_code,
                processed_at = excluded.processed_at,
                updated_at = excluded.updated_at
            """,
            (
                attempt["moodle_attempt_id"],
                attempt["moodle_quiz_id"],
                attempt["moodle_user_id"],
                attempt["attempt_number"],
                attempt["state"],
                attempt["raw_score"],
                attempt["max_score"],
                attempt["percentage"],
                attempt.get("time_started"),
                attempt.get("time_finished"),
                attempt.get("build_id"),
                attempt.get("lesson_package_id"),
                attempt.get("curriculum_code"),
                now,
                now,
                now,
            )
        )

        db.commit()


def save_question_responses(responses):
    """Insert or update normalized question-level evidence."""

    import json

    now = utc_now()

    with get_connection() as db:

        for response in responses:
            db.execute(
                """
                INSERT INTO question_responses (
                    moodle_attempt_id,
                    moodle_user_id,
                    moodle_quiz_id,
                    moodle_slot,
                    question_key,
                    moodle_question_id,
                    moodle_question_bank_entry_id,
                    question_type,
                    status,
                    mark,
                    max_mark,
                    question_text,
                    student_response,
                    correct_response,
                    raw_review_json,
                    created_at,
                    updated_at
                )
                VALUES (
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?,
                    ?, ?
                )
                ON CONFLICT(
                    moodle_attempt_id,
                    question_key
                )
                DO UPDATE SET
                    status = excluded.status,
                    mark = excluded.mark,
                    max_mark = excluded.max_mark,
                    question_text = excluded.question_text,
                    student_response = excluded.student_response,
                    correct_response = excluded.correct_response,
                    raw_review_json = excluded.raw_review_json,
                    updated_at = excluded.updated_at
                """,
                (
                    response["moodle_attempt_id"],
                    response["moodle_user_id"],
                    response["moodle_quiz_id"],
                    response["moodle_slot"],
                    response["question_key"],
                    response.get("moodle_question_id"),
                    response.get(
                        "moodle_question_bank_entry_id"
                    ),
                    response.get("question_type"),
                    response.get("status"),
                    response.get("mark"),
                    response.get("max_mark"),
                    response.get("question_text"),
                    response.get("student_response"),
                    response.get("correct_response"),
                    json.dumps(
                        response.get(
                            "raw_review",
                            {}
                        ),
                        ensure_ascii=False
                    ),
                    now,
                    now,
                )
            )

        db.commit()
