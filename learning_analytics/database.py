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

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                moodle_user_id INTEGER NOT NULL,
                moodle_quiz_id INTEGER NOT NULL,
                latest_moodle_attempt_id INTEGER NOT NULL,

                attempt_count INTEGER NOT NULL,

                curriculum_code TEXT,
                lesson_package_id TEXT,

                diagnostic_json TEXT NOT NULL,
                semantic_reviews_json TEXT NOT NULL,
                validation_json TEXT NOT NULL,

                student_html TEXT NOT NULL,
                teacher_html TEXT NOT NULL,

                model TEXT,
                total_tokens INTEGER,

                status TEXT NOT NULL,

                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                UNIQUE (
                    moodle_user_id,
                    moodle_quiz_id,
                    latest_moodle_attempt_id
                )
            )
            """
        )

        db.execute(
            """
            CREATE INDEX IF NOT EXISTS
                idx_feedback_reports_student_quiz
            ON feedback_reports (
                moodle_user_id,
                moodle_quiz_id
            )
            """
        )

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback_deliveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                feedback_report_id INTEGER NOT NULL,

                recipient TEXT NOT NULL,
                delivery_mode TEXT NOT NULL,
                status TEXT NOT NULL,

                sent_at TEXT,
                error_message TEXT,

                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                FOREIGN KEY (
                    feedback_report_id
                )
                REFERENCES feedback_reports(id)
                ON DELETE CASCADE
            )
            """
        )

        db.execute(
            """
            CREATE INDEX IF NOT EXISTS
                idx_feedback_deliveries_report
            ON feedback_deliveries (
                feedback_report_id
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


def save_feedback_report(report):
    """Insert or update one validated feedback report."""

    import json

    now = utc_now()

    with get_connection() as db:
        db.execute(
            """
            INSERT INTO feedback_reports (
                moodle_user_id,
                moodle_quiz_id,
                latest_moodle_attempt_id,
                attempt_count,
                curriculum_code,
                lesson_package_id,
                diagnostic_json,
                semantic_reviews_json,
                validation_json,
                student_html,
                teacher_html,
                model,
                total_tokens,
                status,
                created_at,
                updated_at
            )
            VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?,
                ?
            )
            ON CONFLICT(
                moodle_user_id,
                moodle_quiz_id,
                latest_moodle_attempt_id
            )
            DO UPDATE SET
                attempt_count = excluded.attempt_count,
                curriculum_code = excluded.curriculum_code,
                lesson_package_id = excluded.lesson_package_id,
                diagnostic_json = excluded.diagnostic_json,
                semantic_reviews_json =
                    excluded.semantic_reviews_json,
                validation_json = excluded.validation_json,
                student_html = excluded.student_html,
                teacher_html = excluded.teacher_html,
                model = excluded.model,
                total_tokens = excluded.total_tokens,
                status = excluded.status,
                updated_at = excluded.updated_at
            """,
            (
                report["moodle_user_id"],
                report["moodle_quiz_id"],
                report["latest_moodle_attempt_id"],
                report["attempt_count"],
                report.get("curriculum_code"),
                report.get("lesson_package_id"),
                json.dumps(
                    report["diagnostic"],
                    ensure_ascii=False
                ),
                json.dumps(
                    report.get(
                        "semantic_reviews",
                        []
                    ),
                    ensure_ascii=False
                ),
                json.dumps(
                    report["validation"],
                    ensure_ascii=False
                ),
                report["student_html"],
                report["teacher_html"],
                report.get("model"),
                report.get("total_tokens"),
                report.get(
                    "status",
                    "VALIDATED"
                ),
                now,
                now,
            )
        )

        row = db.execute(
            """
            SELECT id
            FROM feedback_reports
            WHERE moodle_user_id = ?
              AND moodle_quiz_id = ?
              AND latest_moodle_attempt_id = ?
            """,
            (
                report["moodle_user_id"],
                report["moodle_quiz_id"],
                report["latest_moodle_attempt_id"],
            )
        ).fetchone()

        db.commit()

        return int(row["id"])


def get_feedback_report(
        *,
        moodle_user_id,
        moodle_quiz_id,
        latest_moodle_attempt_id=None
):
    """Retrieve a persisted feedback report."""

    import json

    with get_connection() as db:

        if latest_moodle_attempt_id is None:
            row = db.execute(
                """
                SELECT *
                FROM feedback_reports
                WHERE moodle_user_id = ?
                  AND moodle_quiz_id = ?
                ORDER BY
                    latest_moodle_attempt_id DESC,
                    id DESC
                LIMIT 1
                """,
                (
                    moodle_user_id,
                    moodle_quiz_id,
                )
            ).fetchone()

        else:
            row = db.execute(
                """
                SELECT *
                FROM feedback_reports
                WHERE moodle_user_id = ?
                  AND moodle_quiz_id = ?
                  AND latest_moodle_attempt_id = ?
                LIMIT 1
                """,
                (
                    moodle_user_id,
                    moodle_quiz_id,
                    latest_moodle_attempt_id,
                )
            ).fetchone()

        if row is None:
            return None

        result = dict(row)

        result["diagnostic"] = json.loads(
            result.pop(
                "diagnostic_json"
            )
        )

        result["semantic_reviews"] = json.loads(
            result.pop(
                "semantic_reviews_json"
            )
        )

        result["validation"] = json.loads(
            result.pop(
                "validation_json"
            )
        )

        return result


def record_feedback_delivery(
        *,
        feedback_report_id,
        recipient,
        delivery_mode,
        status,
        sent_at=None,
        error_message=None
):
    """Record one feedback delivery event."""

    allowed_modes = {
        "PREVIEW",
        "TEST",
        "LIVE",
    }

    allowed_statuses = {
        "PENDING",
        "COMPLETED",
        "SENT",
        "FAILED",
    }

    if delivery_mode not in allowed_modes:
        raise ValueError(
            "Invalid delivery mode: "
            f"{delivery_mode}"
        )

    if status not in allowed_statuses:
        raise ValueError(
            "Invalid delivery status: "
            f"{status}"
        )

    now = utc_now()

    with get_connection() as db:
        cursor = db.execute(
            """
            INSERT INTO feedback_deliveries (
                feedback_report_id,
                recipient,
                delivery_mode,
                status,
                sent_at,
                error_message,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                feedback_report_id,
                recipient,
                delivery_mode,
                status,
                sent_at,
                error_message,
                now,
                now,
            )
        )

        db.commit()

        return int(
            cursor.lastrowid
        )


def update_feedback_delivery(
        delivery_id,
        *,
        status,
        sent_at=None,
        error_message=None
):
    """Update an existing feedback delivery audit event."""

    allowed_statuses = {
        "PENDING",
        "COMPLETED",
        "SENT",
        "FAILED",
    }

    if status not in allowed_statuses:
        raise ValueError(
            f"Invalid delivery status: {status}"
        )

    now = utc_now()

    with get_connection() as db:
        cursor = db.execute(
            """
            UPDATE feedback_deliveries
            SET
                status = ?,
                sent_at = ?,
                error_message = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                status,
                sent_at,
                error_message,
                now,
                delivery_id,
            )
        )

        if cursor.rowcount != 1:
            raise RuntimeError(
                f"Delivery {delivery_id} does not exist."
            )

        db.commit()
