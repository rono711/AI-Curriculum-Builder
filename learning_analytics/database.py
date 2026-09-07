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

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS remediation_evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                moodle_user_id INTEGER NOT NULL,
                moodle_quiz_id INTEGER NOT NULL,

                parent_code TEXT NOT NULL,
                curriculum_code TEXT NOT NULL,
                lesson_package_id TEXT,

                question_key TEXT NOT NULL,

                first_attempt_id INTEGER NOT NULL,
                latest_attempt_id INTEGER NOT NULL,
                attempts_observed INTEGER NOT NULL,

                evidence_state TEXT NOT NULL,
                confidence TEXT,

                question_text TEXT,
                latest_student_response TEXT,
                correct_response TEXT,

                diagnosis TEXT,
                concept_name TEXT,

                source_report_id INTEGER,

                promoted_to_final_pool INTEGER
                    NOT NULL DEFAULT 0,

                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                UNIQUE (
                    moodle_user_id,
                    moodle_quiz_id,
                    question_key
                ),

                FOREIGN KEY (
                    source_report_id
                )
                REFERENCES feedback_reports(id)
            )
            """
        )

        db.execute(
            """
            CREATE INDEX IF NOT EXISTS
                idx_remediation_parent_student
            ON remediation_evidence (
                moodle_user_id,
                parent_code
            )
            """
        )

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS final_quiz_pool (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                moodle_user_id INTEGER NOT NULL,

                parent_code TEXT NOT NULL,
                curriculum_code TEXT NOT NULL,

                source_question_key TEXT NOT NULL,

                concept_name TEXT,
                diagnosis TEXT,

                priority TEXT NOT NULL,
                source_attempt_count INTEGER NOT NULL,

                source_question_text TEXT,
                source_student_response TEXT,
                source_correct_response TEXT,

                generation_instruction TEXT NOT NULL,

                status TEXT NOT NULL,

                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                UNIQUE (
                    moodle_user_id,
                    parent_code,
                    source_question_key
                )
            )
            """
        )

        db.execute(
            """
            CREATE INDEX IF NOT EXISTS
                idx_final_quiz_pool_parent_student
            ON final_quiz_pool (
                moodle_user_id,
                parent_code,
                status
            )
            """
        )

        db.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_attempt_controls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                moodle_user_id INTEGER NOT NULL,
                moodle_quiz_id INTEGER NOT NULL,
                override_id INTEGER,
                attempt_limit INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'ACTIVE',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                cleared_at TEXT,
                UNIQUE (
                    moodle_user_id,
                    moodle_quiz_id
                )
            )
            """
        )

        db.execute(
            """
            CREATE INDEX IF NOT EXISTS
                idx_quiz_attempt_controls_status
            ON quiz_attempt_controls (
                moodle_user_id,
                moodle_quiz_id,
                status
            )
            """
        )

        # ---------------------------------------------------------
        # Schema migrations for existing analytics databases.
        # ---------------------------------------------------------
        #
        # Moodle remains authoritative for whether an attempt exists.
        # When a teacher deletes an attempt, analytics keeps the
        # historical evidence for audit but marks it RESET so it no
        # longer contributes to mastery or attempt counting.
        columns = {
            row["name"]
            for row in db.execute(
                "PRAGMA table_info(quiz_attempts)"
            ).fetchall()
        }

        if "lifecycle_status" not in columns:
            db.execute(
                """
                ALTER TABLE quiz_attempts
                ADD COLUMN lifecycle_status TEXT
                    NOT NULL DEFAULT 'ACTIVE'
                """
            )

        if "reset_at" not in columns:
            db.execute(
                """
                ALTER TABLE quiz_attempts
                ADD COLUMN reset_at TEXT
                """
            )

        if "reset_reason" not in columns:
            db.execute(
                """
                ALTER TABLE quiz_attempts
                ADD COLUMN reset_reason TEXT
                """
            )

        db.execute(
            """
            CREATE INDEX IF NOT EXISTS
                idx_quiz_attempts_lifecycle
            ON quiz_attempts (
                moodle_user_id,
                moodle_quiz_id,
                lifecycle_status
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
                updated_at = excluded.updated_at,
                lifecycle_status = 'ACTIVE',
                reset_at = NULL,
                reset_reason = NULL
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


def save_remediation_evidence(item):
    """Insert or update longitudinal remediation evidence."""

    now = utc_now()

    values = (
        item["moodle_user_id"],
        item["moodle_quiz_id"],
        item["parent_code"],
        item["curriculum_code"],
        item.get("lesson_package_id"),
        item["question_key"],
        item["first_attempt_id"],
        item["latest_attempt_id"],
        item["attempts_observed"],
        item["evidence_state"],
        item.get("confidence"),
        item.get("question_text"),
        item.get("latest_student_response"),
        item.get("correct_response"),
        item.get("diagnosis"),
        item.get("concept_name"),
        item.get("source_report_id"),
        int(bool(
            item.get(
                "promoted_to_final_pool",
                False
            )
        )),
        now,
        now,
    )

    with get_connection() as db:
        db.execute(
            """
            INSERT INTO remediation_evidence (
                moodle_user_id,
                moodle_quiz_id,
                parent_code,
                curriculum_code,
                lesson_package_id,
                question_key,
                first_attempt_id,
                latest_attempt_id,
                attempts_observed,
                evidence_state,
                confidence,
                question_text,
                latest_student_response,
                correct_response,
                diagnosis,
                concept_name,
                source_report_id,
                promoted_to_final_pool,
                created_at,
                updated_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            ON CONFLICT (
                moodle_user_id,
                moodle_quiz_id,
                question_key
            )
            DO UPDATE SET
                first_attempt_id =
                    excluded.first_attempt_id,
                latest_attempt_id =
                    excluded.latest_attempt_id,
                attempts_observed =
                    excluded.attempts_observed,
                evidence_state =
                    excluded.evidence_state,
                confidence =
                    excluded.confidence,
                question_text =
                    excluded.question_text,
                latest_student_response =
                    excluded.latest_student_response,
                correct_response =
                    excluded.correct_response,
                diagnosis =
                    excluded.diagnosis,
                concept_name =
                    excluded.concept_name,
                source_report_id =
                    excluded.source_report_id,
                promoted_to_final_pool =
                    excluded.promoted_to_final_pool,
                updated_at =
                    excluded.updated_at
            """,
            values
        )

        row = db.execute(
            """
            SELECT id
            FROM remediation_evidence
            WHERE moodle_user_id = ?
              AND moodle_quiz_id = ?
              AND question_key = ?
            """,
            (
                item["moodle_user_id"],
                item["moodle_quiz_id"],
                item["question_key"],
            )
        ).fetchone()

        db.commit()

        return int(row["id"])


def save_final_quiz_pool_item(item):
    """Insert or update one final-quiz remediation item."""

    now = utc_now()

    values = (
        item["moodle_user_id"],
        item["parent_code"],
        item["curriculum_code"],
        item["source_question_key"],
        item.get("concept_name"),
        item.get("diagnosis"),
        item["priority"],
        item["source_attempt_count"],
        item.get("source_question_text"),
        item.get("source_student_response"),
        item.get("source_correct_response"),
        item["generation_instruction"],
        item.get("status", "ACTIVE"),
        now,
        now,
    )

    with get_connection() as db:
        db.execute(
            """
            INSERT INTO final_quiz_pool (
                moodle_user_id,
                parent_code,
                curriculum_code,
                source_question_key,
                concept_name,
                diagnosis,
                priority,
                source_attempt_count,
                source_question_text,
                source_student_response,
                source_correct_response,
                generation_instruction,
                status,
                created_at,
                updated_at
            )
            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?
            )
            ON CONFLICT (
                moodle_user_id,
                parent_code,
                source_question_key
            )
            DO UPDATE SET
                curriculum_code =
                    excluded.curriculum_code,
                concept_name =
                    excluded.concept_name,
                diagnosis =
                    excluded.diagnosis,
                priority =
                    excluded.priority,
                source_attempt_count =
                    excluded.source_attempt_count,
                source_question_text =
                    excluded.source_question_text,
                source_student_response =
                    excluded.source_student_response,
                source_correct_response =
                    excluded.source_correct_response,
                generation_instruction =
                    excluded.generation_instruction,
                status =
                    excluded.status,
                updated_at =
                    excluded.updated_at
            """,
            values
        )

        row = db.execute(
            """
            SELECT id
            FROM final_quiz_pool
            WHERE moodle_user_id = ?
              AND parent_code = ?
              AND source_question_key = ?
            """,
            (
                item["moodle_user_id"],
                item["parent_code"],
                item["source_question_key"],
            )
        ).fetchone()

        db.commit()

        return int(row["id"])




def save_quiz_attempt_control(
        *,
        moodle_user_id,
        moodle_quiz_id,
        override_id,
        attempt_limit
):
    """Record a Moodle attempt override created by Learning Analytics."""

    now = utc_now()

    with get_connection() as db:
        db.execute(
            """
            INSERT INTO quiz_attempt_controls (
                moodle_user_id,
                moodle_quiz_id,
                override_id,
                attempt_limit,
                status,
                created_at,
                updated_at,
                cleared_at
            )
            VALUES (?, ?, ?, ?, 'ACTIVE', ?, ?, NULL)
            ON CONFLICT (
                moodle_user_id,
                moodle_quiz_id
            )
            DO UPDATE SET
                override_id = excluded.override_id,
                attempt_limit = excluded.attempt_limit,
                status = 'ACTIVE',
                updated_at = excluded.updated_at,
                cleared_at = NULL
            """,
            (
                int(moodle_user_id),
                int(moodle_quiz_id),
                (
                    int(override_id)
                    if override_id is not None
                    else None
                ),
                int(attempt_limit),
                now,
                now,
            )
        )

        db.commit()


def get_active_quiz_attempt_control(
        *,
        moodle_user_id,
        moodle_quiz_id
):
    """Return the active attempt override owned by Learning Analytics."""

    with get_connection() as db:
        row = db.execute(
            """
            SELECT *
            FROM quiz_attempt_controls
            WHERE moodle_user_id = ?
              AND moodle_quiz_id = ?
              AND status = 'ACTIVE'
            LIMIT 1
            """,
            (
                int(moodle_user_id),
                int(moodle_quiz_id),
            )
        ).fetchone()

    return dict(row) if row else None


def mark_quiz_attempt_control_cleared(
        *,
        moodle_user_id,
        moodle_quiz_id
):
    """Mark an Analytics-owned Moodle attempt override as cleared."""

    now = utc_now()

    with get_connection() as db:
        cursor = db.execute(
            """
            UPDATE quiz_attempt_controls
            SET status = 'CLEARED',
                updated_at = ?,
                cleared_at = ?
            WHERE moodle_user_id = ?
              AND moodle_quiz_id = ?
              AND status = 'ACTIVE'
            """,
            (
                now,
                now,
                int(moodle_user_id),
                int(moodle_quiz_id),
            )
        )

        db.commit()

        return cursor.rowcount > 0


def get_stored_quiz_attempts(
        *,
        moodle_user_id,
        moodle_quiz_id,
        lifecycle_status=None
):
    """Return stored analytics attempts for one student and Quiz."""

    sql = """
        SELECT
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
            curriculum_code,
            lifecycle_status,
            reset_at,
            reset_reason
        FROM quiz_attempts
        WHERE moodle_user_id = ?
          AND moodle_quiz_id = ?
    """

    params = [
        int(moodle_user_id),
        int(moodle_quiz_id),
    ]

    if lifecycle_status is not None:
        sql += " AND lifecycle_status = ?"
        params.append(str(lifecycle_status))

    sql += " ORDER BY moodle_attempt_id"

    with get_connection() as db:
        rows = db.execute(
            sql,
            tuple(params)
        ).fetchall()

    return [
        dict(row)
        for row in rows
    ]


def mark_attempt_reset(
        *,
        moodle_attempt_id,
        reason="TEACHER_DELETED_IN_MOODLE"
):
    """Retire one Moodle attempt from active analytics without deleting audit data."""

    now = utc_now()

    with get_connection() as db:
        row = db.execute(
            """
            SELECT
                moodle_attempt_id,
                moodle_quiz_id,
                moodle_user_id,
                lifecycle_status
            FROM quiz_attempts
            WHERE moodle_attempt_id = ?
            """,
            (
                int(moodle_attempt_id),
            )
        ).fetchone()

        if row is None:
            return None

        if row["lifecycle_status"] == "RESET":
            return {
                **dict(row),
                "changed": False,
            }

        db.execute(
            """
            UPDATE quiz_attempts
            SET lifecycle_status = 'RESET',
                reset_at = ?,
                reset_reason = ?,
                updated_at = ?
            WHERE moodle_attempt_id = ?
            """,
            (
                now,
                str(reason),
                now,
                int(moodle_attempt_id),
            )
        )

        db.commit()

    return {
        **dict(row),
        "lifecycle_status": "RESET",
        "reset_at": now,
        "reset_reason": str(reason),
        "changed": True,
    }


def get_quiz_attempt_number(moodle_attempt_id):
    """Return the stored Moodle attempt number for one attempt."""

    with get_connection() as db:
        row = db.execute(
            """
            SELECT attempt_number
            FROM quiz_attempts
            WHERE moodle_attempt_id = ?
            """,
            (
                int(moodle_attempt_id),
            )
        ).fetchone()

    if row is None:
        raise RuntimeError(
            f"Analytics attempt {moodle_attempt_id} "
            "is not stored."
        )

    return int(row["attempt_number"])



def get_student_quiz_responses(
        *,
        moodle_user_id,
        moodle_quiz_id
):
    """Return ACTIVE stored response history for one student Quiz."""

    with get_connection() as db:
        rows = db.execute(
            """
            SELECT
                qr.moodle_attempt_id,
                qr.moodle_user_id,
                qr.moodle_quiz_id,
                qr.moodle_slot,
                qr.question_key,
                qr.moodle_question_id,
                qr.moodle_question_bank_entry_id,
                qr.question_type,
                qr.status,
                qr.mark,
                qr.max_mark,
                qr.question_text,
                qr.student_response,
                qr.correct_response
            FROM question_responses qr
            JOIN quiz_attempts qa
              ON qa.moodle_attempt_id =
                    qr.moodle_attempt_id
            WHERE qr.moodle_user_id = ?
              AND qr.moodle_quiz_id = ?
              AND qa.lifecycle_status = 'ACTIVE'
            ORDER BY
                qr.moodle_attempt_id,
                qr.moodle_slot
            """,
            (
                int(moodle_user_id),
                int(moodle_quiz_id),
            )
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]


def get_attempt_processing_state(
        *,
        moodle_user_id,
        moodle_quiz_id,
        moodle_attempt_id
):
    """Return whether one attempt completed the analytics pipeline."""

    with get_connection() as db:

        attempt_lifecycle = db.execute(
            """
            SELECT lifecycle_status
            FROM quiz_attempts
            WHERE moodle_attempt_id = ?
              AND moodle_user_id = ?
              AND moodle_quiz_id = ?
            """,
            (
                int(moodle_attempt_id),
                int(moodle_user_id),
                int(moodle_quiz_id),
            )
        ).fetchone()

        report = db.execute(
            """
            SELECT
                id,
                status,
                latest_moodle_attempt_id,
                attempt_count
            FROM feedback_reports
            WHERE moodle_user_id = ?
              AND moodle_quiz_id = ?
              AND latest_moodle_attempt_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                int(moodle_user_id),
                int(moodle_quiz_id),
                int(moodle_attempt_id),
            )
        ).fetchone()

        expected = db.execute(
            """
            SELECT COUNT(DISTINCT question_key)
            FROM question_responses
            WHERE moodle_user_id = ?
              AND moodle_quiz_id = ?
              AND moodle_attempt_id = ?
            """,
            (
                int(moodle_user_id),
                int(moodle_quiz_id),
                int(moodle_attempt_id),
            )
        ).fetchone()[0]

        finalized = db.execute(
            """
            SELECT COUNT(DISTINCT r.question_key)
            FROM remediation_evidence r
            WHERE r.moodle_user_id = ?
              AND r.moodle_quiz_id = ?
              AND r.latest_attempt_id >= ?
              AND r.question_key IN (
                  SELECT question_key
                  FROM question_responses
                  WHERE moodle_user_id = ?
                    AND moodle_quiz_id = ?
                    AND moodle_attempt_id = ?
              )
            """,
            (
                int(moodle_user_id),
                int(moodle_quiz_id),
                int(moodle_attempt_id),
                int(moodle_user_id),
                int(moodle_quiz_id),
                int(moodle_attempt_id),
            )
        ).fetchone()[0]

    report_validated = (
        report is not None
        and report["status"] == "VALIDATED"
    )

    remediation_complete = (
        expected > 0
        and finalized == expected
    )

    lifecycle_status = (
        attempt_lifecycle["lifecycle_status"]
        if attempt_lifecycle
        else None
    )

    reset = lifecycle_status == "RESET"

    return {
        "moodle_attempt_id":
            int(moodle_attempt_id),

        "lifecycle_status":
            lifecycle_status,

        "reset":
            reset,

        "report_id":
            (
                int(report["id"])
                if report
                else None
            ),

        "report_validated":
            report_validated,

        "expected_questions":
            int(expected),

        "finalized_questions":
            int(finalized),

        "remediation_complete":
            remediation_complete,

        "fully_processed":
            (
                not reset
                and report_validated
                and remediation_complete
            ),
    }
