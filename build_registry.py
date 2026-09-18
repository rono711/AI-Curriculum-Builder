"""
Rono's School AI Curriculum Builder
Persistent Elaboration Build Registry

Purpose:
- Track elaborations successfully published across different build requests.
- Prevent accidental duplicate builds.
- Allow an explicit UPDATE build later.
"""

import sqlite3
import json
import uuid
from pathlib import Path
from datetime import datetime, timezone


# ==========================================================
# Registry Location
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"

REGISTRY_DB = DATA_DIR / "build_registry.db"


# ==========================================================
# Database Connection
# ==========================================================

def get_connection():

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        REGISTRY_DB,
        timeout=30
    )

    connection.row_factory = sqlite3.Row

    return connection


# ==========================================================
# Initialize Registry
# ==========================================================

def initialize_registry():

    with get_connection() as connection:

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS elaboration_builds (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                elaboration_key TEXT NOT NULL,

                learning_area TEXT NOT NULL,
                subject TEXT NOT NULL,
                year_level TEXT NOT NULL,

                strand TEXT NOT NULL,
                sub_strand TEXT,

                parent_code TEXT NOT NULL,
                topic_id TEXT,

                curriculum_code TEXT,

                content_description TEXT,
                elaboration TEXT NOT NULL,

                build_id TEXT,

                lesson_package_id TEXT,

                build_mode TEXT NOT NULL DEFAULT 'NEW',

                status TEXT NOT NULL,

                moodle_course_id INTEGER,
                moodle_section_id INTEGER,

                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_elaboration_builds_key

            ON elaboration_builds (
                elaboration_key
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_elaboration_builds_status

            ON elaboration_builds (
                status
            )
            """
        )
        # ==================================================
        # Non-destructive Registry Schema Migration
        # ==================================================

        existing_columns = {
            row["name"]
            for row in connection.execute(
                "PRAGMA table_info(elaboration_builds)"
            ).fetchall()
        }

        additional_columns = {

            # Moodle structure identity.

            "moodle_subsection_cmid":
                "INTEGER",

            "moodle_subsection_section_id":
                "INTEGER",

            "moodle_content_description_cmid":
                "INTEGER",

            # Lesson component identity.

            "moodle_lesson_content_cmid":
                "INTEGER",

            "moodle_did_you_know_cmid":
                "INTEGER",

            "moodle_quiz_id":
                "INTEGER",

            "moodle_quiz_cmid":
                "INTEGER",

            "moodle_activities_cmid":
                "INTEGER",

            "moodle_recap_cmid":
                "INTEGER",

            # Selective UPDATE history.

            "update_components":
                "TEXT"

        }

        for column_name, column_type in additional_columns.items():

            if column_name in existing_columns:
                continue

            connection.execute(
                f"""
                ALTER TABLE elaboration_builds
                ADD COLUMN {column_name} {column_type}
                """
            )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS build_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT NOT NULL UNIQUE,
                requested_by TEXT NOT NULL,
                processing_mode TEXT NOT NULL,
                learning_area TEXT NOT NULL,
                subject TEXT NOT NULL,
                year_level TEXT NOT NULL,
                strand TEXT NOT NULL,
                sub_strand TEXT,
                parent_code TEXT NOT NULL,
                lesson_numbers TEXT NOT NULL,
                status TEXT NOT NULL,
                openai_batch_id TEXT,
                error TEXT,
                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                updated_at TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_build_requests_status
            ON build_requests (status)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_build_requests_requested_by
            ON build_requests (requested_by)
            """
        )

        # ==================================================
        # External Batch Execution History
        # ==================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS batch_runs (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                request_id TEXT NOT NULL,
                stage INTEGER NOT NULL,
                provider TEXT NOT NULL,
                attempt INTEGER NOT NULL DEFAULT 1,

                external_batch_id TEXT,
                input_file_id TEXT,
                output_file_id TEXT,

                status TEXT NOT NULL,
                error TEXT,

                created_at TEXT NOT NULL,
                submitted_at TEXT,
                completed_at TEXT,
                updated_at TEXT NOT NULL,

                UNIQUE (
                    request_id,
                    stage,
                    provider,
                    attempt
                ),

                FOREIGN KEY (request_id)
                    REFERENCES build_requests (request_id)
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_batch_runs_request
            ON batch_runs (
                request_id,
                stage,
                provider
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_batch_runs_external
            ON batch_runs (
                external_batch_id
            )
            """
        )

        # ==================================================
        # Queue V1 - Individual Selected Lesson Items
        # ==================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS build_request_items (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                request_id TEXT NOT NULL,

                parent_code TEXT NOT NULL,
                curriculum_code TEXT,
                content_description TEXT,

                lesson_number INTEGER NOT NULL,
                topic_id TEXT,
                lesson_text TEXT,

                status TEXT NOT NULL DEFAULT 'QUEUED',
                stage TEXT,
                message TEXT,
                percent INTEGER NOT NULL DEFAULT 0,
                error TEXT,

                build_id TEXT,
                lesson_package_id TEXT,

                created_at TEXT NOT NULL,
                started_at TEXT,
                completed_at TEXT,
                updated_at TEXT NOT NULL,

                UNIQUE (
                    request_id,
                    parent_code,
                    lesson_number
                ),

                FOREIGN KEY (request_id)
                    REFERENCES build_requests (request_id)
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_build_request_items_request
            ON build_request_items (request_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_build_request_items_status
            ON build_request_items (status)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_build_request_items_parent
            ON build_request_items (
                request_id,
                parent_code
            )
            """
        )
                # ==================================================
        # Quiz Question Identity Registry
        # ==================================================

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_questions (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                question_key TEXT NOT NULL,

                build_id TEXT,
                lesson_package_id TEXT NOT NULL,
                curriculum_code TEXT,

                moodle_course_id INTEGER,
                moodle_quiz_id INTEGER NOT NULL,
                moodle_quiz_cmid INTEGER,

                moodle_question_id INTEGER NOT NULL UNIQUE,

                moodle_question_bank_entry_id
                    INTEGER NOT NULL UNIQUE,

                moodle_slot INTEGER,

                question_type TEXT,

                source TEXT NOT NULL,

                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,

                UNIQUE (
                    moodle_quiz_id,
                    question_key
                )
            )
            """
        )

        # ==================================================
        # Quiz Question Identity Schema Migration
        # ==================================================

        quiz_questions_schema_row = connection.execute(
            """
            SELECT sql
            FROM sqlite_master
            WHERE type = 'table'
              AND name = 'quiz_questions'
            """
        ).fetchone()

        quiz_questions_schema = (
            str(quiz_questions_schema_row["sql"])
            if quiz_questions_schema_row
            else ""
        )

        legacy_question_key_unique = (
            "question_key TEXT NOT NULL UNIQUE"
            in quiz_questions_schema
        )

        if legacy_question_key_unique:

            duplicate_scoped_keys = connection.execute(
                """
                SELECT
                    moodle_quiz_id,
                    question_key,
                    COUNT(*) AS total
                FROM quiz_questions
                GROUP BY
                    moodle_quiz_id,
                    question_key
                HAVING COUNT(*) > 1
                LIMIT 1
                """
            ).fetchone()

            if duplicate_scoped_keys:
                raise RuntimeError(
                    "Cannot migrate quiz_questions: "
                    "duplicate scoped question identity "
                    f"quiz={duplicate_scoped_keys['moodle_quiz_id']} "
                    f"key={duplicate_scoped_keys['question_key']}."
                )

            connection.execute(
                """
                CREATE TABLE quiz_questions_migrated (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_key TEXT NOT NULL,
                    build_id TEXT,
                    lesson_package_id TEXT NOT NULL,
                    curriculum_code TEXT,
                    moodle_course_id INTEGER,
                    moodle_quiz_id INTEGER NOT NULL,
                    moodle_quiz_cmid INTEGER,
                    moodle_question_id INTEGER NOT NULL UNIQUE,
                    moodle_question_bank_entry_id
                        INTEGER NOT NULL UNIQUE,
                    moodle_slot INTEGER,
                    question_type TEXT,
                    source TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE (
                        moodle_quiz_id,
                        question_key
                    )
                )
                """
            )

            connection.execute(
                """
                INSERT INTO quiz_questions_migrated (
                    id,
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
                    question_type,
                    source,
                    created_at,
                    updated_at
                )
                SELECT
                    id,
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
                    question_type,
                    source,
                    created_at,
                    updated_at
                FROM quiz_questions
                ORDER BY id
                """
            )

            old_count = connection.execute(
                "SELECT COUNT(*) FROM quiz_questions"
            ).fetchone()[0]

            new_count = connection.execute(
                "SELECT COUNT(*) FROM quiz_questions_migrated"
            ).fetchone()[0]

            if old_count != new_count:
                raise RuntimeError(
                    "quiz_questions migration row-count "
                    f"mismatch: old={old_count}, "
                    f"new={new_count}."
                )

            connection.execute(
                "DROP TABLE quiz_questions"
            )

            connection.execute(
                """
                ALTER TABLE quiz_questions_migrated
                RENAME TO quiz_questions
                """
            )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_quiz_questions_lesson_package

            ON quiz_questions (
                lesson_package_id
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_quiz_questions_quiz

            ON quiz_questions (
                moodle_quiz_id
            )
            """
        )

        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_quiz_questions_quiz_slot

            ON quiz_questions (
                moodle_quiz_id,
                moodle_slot
            )
            """
        )
        connection.commit()


# ==========================================================
# Normalization
# ==========================================================

def normalize(value):

    if value is None:
        return ""

    return " ".join(
        str(value)
        .strip()
        .lower()
        .split()
    )


# ==========================================================
# Elaboration Key
# ==========================================================

def make_elaboration_key(
        year_level,
        subject,
        parent_code,
        topic_id,
        elaboration
):

    """
    Produce a stable curriculum identity for an elaboration.

    IMPORTANT:
    build_id and lesson_package_id are intentionally NOT
    included because they identify a particular build,
    not the curriculum elaboration itself.
    """

    parts = [

        normalize(year_level),

        normalize(subject),

        normalize(parent_code),

        normalize(topic_id),

        normalize(elaboration)

    ]

    return "|".join(parts)


# ==========================================================
# Current Published Build
# ==========================================================

def get_published_build(elaboration_key):

    initialize_registry()

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT *
            FROM elaboration_builds

            WHERE elaboration_key = ?
              AND status = 'PUBLISHED'

            ORDER BY id DESC

            LIMIT 1
            """,
            (
                elaboration_key,
            )
        ).fetchone()

        if row is None:
            return None

        return dict(row)

# ==========================================================
# Current Generated Build Awaiting Publication
# ==========================================================

def get_generated_build(elaboration_key):

    initialize_registry()

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT *
            FROM elaboration_builds

            WHERE elaboration_key = ?
              AND status = 'GENERATED'

            ORDER BY id DESC

            LIMIT 1
            """,
            (
                elaboration_key,
            )
        ).fetchone()

        if row is None:
            return None

        return dict(row)

# ==========================================================
# Previous Published Build With Moodle Identity
# ==========================================================

def get_previous_published_build(
        elaboration_key,
        before_record_id
):

    initialize_registry()

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT *
            FROM elaboration_builds

            WHERE elaboration_key = ?
              AND status = 'PUBLISHED'
              AND id < ?
              AND moodle_course_id IS NOT NULL
              AND moodle_lesson_content_cmid IS NOT NULL

            ORDER BY id DESC

            LIMIT 1
            """,
            (
                elaboration_key,
                before_record_id,
            )
        ).fetchone()

        if row is None:
            return None

        return dict(row)


# ==========================================================
# Is Published?
# ==========================================================

def is_elaboration_published(elaboration_key):

    return (
        get_published_build(
            elaboration_key
        )
        is not None
    )


# ==========================================================
# Start Build
# ==========================================================

def start_build(
        *,
        elaboration_key,
        learning_area,
        subject,
        year_level,
        strand,
        sub_strand,
        parent_code,
        topic_id,
        curriculum_code,
        content_description,
        elaboration,
        build_id,
        lesson_package_id,
        build_mode="NEW",
        update_components=None
):

    initialize_registry()

    if update_components:

        update_components_value = ",".join(
            str(component).strip().lower()
            for component in update_components
            if str(component).strip()
        )

    else:

        update_components_value = None
    now = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as connection:

        cursor = connection.execute(
            """
            INSERT INTO elaboration_builds (

                elaboration_key,
                learning_area,
                subject,
                year_level,
                strand,
                sub_strand,
                parent_code,
                topic_id,
                curriculum_code,
                content_description,
                elaboration,
                build_id,
                lesson_package_id,
                build_mode,
                update_components,
                status,
                created_at,
                updated_at

            )

            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                elaboration_key,

                learning_area,
                subject,
                year_level,

                strand,
                sub_strand,

                parent_code,
                topic_id,

                curriculum_code,

                content_description,
                elaboration,

                str(build_id),
                lesson_package_id,

                str(build_mode).upper(),

                update_components_value,

                "BUILDING",

                now,
                now
            )
        )

        connection.commit()

        return cursor.lastrowid


# ==========================================================
# Update Status
# ==========================================================

def update_status(
        record_id,
        status,
        moodle_course_id=None,
        moodle_section_id=None,
        moodle_subsection_cmid=None,
        moodle_subsection_section_id=None,
        moodle_content_description_cmid=None,
        moodle_lesson_content_cmid=None,
        moodle_did_you_know_cmid=None,
        moodle_quiz_id=None,
        moodle_quiz_cmid=None,
        moodle_activities_cmid=None,
        moodle_recap_cmid=None,
        update_components=None
):

    initialize_registry()

    now = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as connection:

        connection.execute(
            """
            UPDATE elaboration_builds

            SET status = ?,

                moodle_course_id =
                    COALESCE(?, moodle_course_id),

                moodle_section_id =
                    COALESCE(?, moodle_section_id),

                moodle_subsection_cmid =
                    COALESCE(?, moodle_subsection_cmid),

                moodle_subsection_section_id =
                    COALESCE(
                        ?,
                        moodle_subsection_section_id
                    ),

                moodle_content_description_cmid =
                    COALESCE(
                        ?,
                        moodle_content_description_cmid
                    ),

                moodle_lesson_content_cmid =
                    COALESCE(
                        ?,
                        moodle_lesson_content_cmid
                    ),

                moodle_did_you_know_cmid =
                    COALESCE(
                        ?,
                        moodle_did_you_know_cmid
                    ),

                moodle_quiz_id =
                    COALESCE(?, moodle_quiz_id),

                moodle_quiz_cmid =
                    COALESCE(?, moodle_quiz_cmid),

                moodle_activities_cmid =
                    COALESCE(
                        ?,
                        moodle_activities_cmid
                    ),

                moodle_recap_cmid =
                    COALESCE(?, moodle_recap_cmid),

                update_components =
                    COALESCE(?, update_components),

                updated_at = ?

            WHERE id = ?
            """,
            (
                str(status).upper(),

                moodle_course_id,
                moodle_section_id,
                moodle_subsection_cmid,
                moodle_subsection_section_id,
                moodle_content_description_cmid,
                moodle_lesson_content_cmid,
                moodle_did_you_know_cmid,
                moodle_quiz_id,
                moodle_quiz_cmid,
                moodle_activities_cmid,
                moodle_recap_cmid,
                update_components,

                now,
                record_id
            )
        )

        connection.commit()
# ==========================================================
# Mark Published
# ==========================================================

def validate_analytics_publication_readiness(
        *,
        record_id,
        moodle_course_id,
        moodle_quiz_id,
        moodle_quiz_cmid
):
    """Validate Analytics requirements before PUBLISHED status."""

    initialize_registry()

    problems = []

    if not moodle_course_id:
        problems.append(
            "MISSING_COURSE_ID"
        )

    if not moodle_quiz_id:
        problems.append(
            "MISSING_QUIZ_ID"
        )

    if not moodle_quiz_cmid:
        problems.append(
            "MISSING_QUIZ_CMID"
        )

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                curriculum_code,
                lesson_package_id
            FROM elaboration_builds
            WHERE id = ?
            """,
            (
                int(record_id),
            )
        ).fetchone()

        if row is None:
            raise ValueError(
                f"Registry record {record_id} "
                "does not exist."
            )

        question_count = 0

        if moodle_quiz_id:
            question_count = int(
                connection.execute(
                    """
                    SELECT COUNT(*)
                    FROM quiz_questions
                    WHERE moodle_quiz_id = ?
                    """,
                    (
                        int(moodle_quiz_id),
                    )
                ).fetchone()[0]
                or 0
            )

    if moodle_quiz_id and question_count < 1:
        problems.append(
            "NO_REGISTERED_QUESTIONS"
        )

    if problems:
        raise RuntimeError(
            "Registry record "
            + str(record_id)
            + " cannot become PUBLISHED: "
            + ",".join(problems)
        )

    return {
        "record_id":
            int(record_id),

        "curriculum_code":
            row["curriculum_code"],

        "lesson_package_id":
            row["lesson_package_id"],

        "moodle_course_id":
            int(moodle_course_id),

        "moodle_quiz_id":
            int(moodle_quiz_id),

        "moodle_quiz_cmid":
            int(moodle_quiz_cmid),

        "registered_question_count":
            question_count,

        "analytics_ready":
            True,

        "analytics_status":
            "ANALYTICS_READY",
    }


def mark_published(
        record_id,
        moodle_course_id=None,
        moodle_section_id=None,
        moodle_subsection_cmid=None,
        moodle_subsection_section_id=None,
        moodle_content_description_cmid=None,
        moodle_lesson_content_cmid=None,
        moodle_did_you_know_cmid=None,
        moodle_quiz_id=None,
        moodle_quiz_cmid=None,
        moodle_activities_cmid=None,
        moodle_recap_cmid=None,
        update_components=None
):

    validate_analytics_publication_readiness(
        record_id=record_id,
        moodle_course_id=moodle_course_id,
        moodle_quiz_id=moodle_quiz_id,
        moodle_quiz_cmid=moodle_quiz_cmid,
    )

    update_status(
        record_id=record_id,
        status="PUBLISHED",

        moodle_course_id=moodle_course_id,
        moodle_section_id=moodle_section_id,

        moodle_subsection_cmid=
            moodle_subsection_cmid,

        moodle_subsection_section_id=
            moodle_subsection_section_id,

        moodle_content_description_cmid=
            moodle_content_description_cmid,

        moodle_lesson_content_cmid=
            moodle_lesson_content_cmid,

        moodle_did_you_know_cmid=
            moodle_did_you_know_cmid,

        moodle_quiz_id=
            moodle_quiz_id,

        moodle_quiz_cmid=
            moodle_quiz_cmid,

        moodle_activities_cmid=
            moodle_activities_cmid,

        moodle_recap_cmid=
            moodle_recap_cmid,

        update_components=
            update_components
    )


# ==========================================================
# Checkpoint Moodle Identity
# ==========================================================

def checkpoint_moodle_identity(
        record_id,
        moodle_course_id=None,
        moodle_section_id=None,
        moodle_subsection_cmid=None,
        moodle_subsection_section_id=None,
        moodle_content_description_cmid=None,
        moodle_lesson_content_cmid=None,
        moodle_did_you_know_cmid=None,
        moodle_quiz_id=None,
        moodle_quiz_cmid=None,
        moodle_activities_cmid=None,
        moodle_recap_cmid=None
):

    initialize_registry()

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT status
            FROM elaboration_builds
            WHERE id = ?
            """,
            (record_id,)
        ).fetchone()

    if row is None:
        raise ValueError(
            f"Registry record {record_id} does not exist."
        )

    update_status(
        record_id=record_id,
        status=row["status"],

        moodle_course_id=moodle_course_id,
        moodle_section_id=moodle_section_id,

        moodle_subsection_cmid=
            moodle_subsection_cmid,

        moodle_subsection_section_id=
            moodle_subsection_section_id,

        moodle_content_description_cmid=
            moodle_content_description_cmid,

        moodle_lesson_content_cmid=
            moodle_lesson_content_cmid,

        moodle_did_you_know_cmid=
            moodle_did_you_know_cmid,

        moodle_quiz_id=
            moodle_quiz_id,

        moodle_quiz_cmid=
            moodle_quiz_cmid,

        moodle_activities_cmid=
            moodle_activities_cmid,

        moodle_recap_cmid=
            moodle_recap_cmid
    )


# ==========================================================
# Inherit Published Moodle Identity
# ==========================================================

def inherit_moodle_identity(
        record_id,
        published_build
):

    if not published_build:
        raise ValueError(
            "Published build is required to inherit "
            "Moodle identity."
        )

    required = [
        "moodle_course_id",
        "moodle_recap_cmid",
    ]

    for field in required:

        if not published_build.get(field):

            raise ValueError(
                "Previous published build is missing "
                f"required Moodle identity: {field}"
            )

    initialize_registry()

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT status
            FROM elaboration_builds
            WHERE id = ?
            """,
            (
                record_id,
            )
        ).fetchone()

    if row is None:

        raise ValueError(
            f"Registry record {record_id} does not exist."
        )

    current_status = row["status"]
    update_status(
        record_id=record_id,
        status=current_status,

        moodle_course_id=
            published_build.get(
                "moodle_course_id"
            ),

        moodle_section_id=
            published_build.get(
                "moodle_section_id"
            ),

        moodle_subsection_cmid=
            published_build.get(
                "moodle_subsection_cmid"
            ),

        moodle_subsection_section_id=
            published_build.get(
                "moodle_subsection_section_id"
            ),

        moodle_content_description_cmid=
            published_build.get(
                "moodle_content_description_cmid"
            ),

        moodle_lesson_content_cmid=
            published_build.get(
                "moodle_lesson_content_cmid"
            ),

        moodle_did_you_know_cmid=
            published_build.get(
                "moodle_did_you_know_cmid"
            ),

        moodle_quiz_id=
            published_build.get(
                "moodle_quiz_id"
            ),

        moodle_quiz_cmid=
            published_build.get(
                "moodle_quiz_cmid"
            ),

        moodle_activities_cmid=
            published_build.get(
                "moodle_activities_cmid"
            ),

        moodle_recap_cmid=
            published_build.get(
                "moodle_recap_cmid"
            )
    )

# ==========================================================
# Mark Generated - Awaiting Publication
# ==========================================================

def mark_generated(record_id):

    update_status(
        record_id=record_id,
        status="GENERATED"
    )


# ==========================================================
# Mark Failed
# ==========================================================

def mark_failed(record_id):

    update_status(
        record_id,
        "FAILED"
    )


# ==========================================================
# Mark Failed If Incomplete
# ==========================================================

def mark_failed_if_incomplete(record_id):
    """
    Mark an in-progress registry record FAILED without
    overwriting a successfully completed terminal state.

    Returns the resulting/preserved status.
    """

    initialize_registry()

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT status
            FROM elaboration_builds
            WHERE id = ?
            """,
            (record_id,)
        ).fetchone()

    if row is None:
        raise ValueError(
            f"Registry record {record_id} does not exist."
        )

    current_status = str(
        row["status"] or ""
    ).strip().upper()

    # Never downgrade successfully completed states.
    if current_status in (
            "PUBLISHED",
            "GENERATED"
    ):
        return current_status

    if current_status == "FAILED":
        return current_status

    update_status(
        record_id=record_id,
        status="FAILED"
    )

    return "FAILED"


# ==========================================================
# Mark Update Ready
# ==========================================================

def mark_update_ready(
        record_id,
        update_components=None
):

    update_status(
        record_id=record_id,
        status="UPDATE_READY",
        update_components=update_components
    )

# ==========================================================
# Build History
# ==========================================================

def get_build_history(elaboration_key):

    initialize_registry()

    with get_connection() as connection:

        rows = connection.execute(
            """
            SELECT *
            FROM elaboration_builds

            WHERE elaboration_key = ?

            ORDER BY id DESC
            """,
            (
                elaboration_key,
            )
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]


# ==========================================================
# Initialize When Imported
# ==========================================================

initialize_registry()


# ==========================================================
# Persistent Build Request Queue
# ==========================================================

def create_build_request(
        requested_by,
        processing_mode,
        learning_area,
        subject,
        year_level,
        strand,
        sub_strand,
        parent_code,
        lesson_numbers
):

    initialize_registry()

    mode = str(processing_mode).strip().upper()

    if mode not in (
        "QUEUE_STANDARD",
        "QUEUE_BATCH"
    ):
        raise ValueError(
            "Invalid queued processing mode."
        )

    lessons = [
        int(value)
        for value in lesson_numbers
    ]

    if not lessons:
        raise ValueError(
            "At least one lesson number is required."
        )

    request_id = (
        "REQ_"
        + datetime.now(timezone.utc).strftime(
            "%Y%m%d_%H%M%S_"
        )
        + uuid.uuid4().hex[:8].upper()
    )

    now = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as connection:

        connection.execute(
            """
            INSERT INTO build_requests (
                request_id,
                requested_by,
                processing_mode,
                learning_area,
                subject,
                year_level,
                strand,
                sub_strand,
                parent_code,
                lesson_numbers,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_id,
                str(requested_by).strip(),
                mode,
                str(learning_area).strip(),
                str(subject).strip(),
                str(year_level).strip(),
                str(strand).strip(),
                str(sub_strand or "").strip(),
                str(parent_code).strip(),
                json.dumps(lessons),
                "QUEUED",
                now,
                now
            )
        )

        connection.commit()

    return request_id


def get_queued_requests(
        processing_mode=None,
        limit=50
):

    initialize_registry()

    params = []

    sql = """
        SELECT *
        FROM build_requests
        WHERE status = 'QUEUED'
    """

    if processing_mode:

        sql += """
            AND processing_mode = ?
        """

        params.append(
            str(processing_mode)
            .strip()
            .upper()
        )

    sql += """
        ORDER BY id ASC
        LIMIT ?
    """

    params.append(
        int(limit)
    )

    with get_connection() as connection:

        rows = connection.execute(
            sql,
            params
        ).fetchall()

    results = []

    for row in rows:

        item = dict(row)

        item["lesson_numbers"] = json.loads(
            item["lesson_numbers"]
        )

        results.append(item)

    return results


def claim_build_request(request_id):

    initialize_registry()

    now = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as connection:

        cursor = connection.execute(
            """
            UPDATE build_requests

            SET status = 'PROCESSING',
                started_at = ?,
                updated_at = ?,
                error = NULL

            WHERE request_id = ?
              AND status = 'QUEUED'
            """,
            (
                now,
                now,
                request_id
            )
        )

        connection.commit()

        return cursor.rowcount == 1


def complete_build_request(request_id):

    initialize_registry()

    now = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as connection:

        connection.execute(
            """
            UPDATE build_requests

            SET status = 'PUBLISHED',
                completed_at = ?,
                updated_at = ?,
                error = NULL

            WHERE request_id = ?
            """,
            (
                now,
                now,
                request_id
            )
        )

        connection.commit()



def fail_build_request(request_id, error):

    initialize_registry()

    now = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as connection:

        connection.execute(
            """
            UPDATE build_requests
            SET status = 'FAILED',
                completed_at = ?,
                updated_at = ?,
                error = ?
            WHERE request_id = ?
            """,
            (
                now,
                now,
                str(error),
                request_id
            )
        )

        connection.commit()


def get_build_request(request_id):

    initialize_registry()

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT *
            FROM build_requests
            WHERE request_id = ?
            """,
            (
                request_id,
            )
        ).fetchone()

    if row is None:
        return None

    result = dict(row)

    result["lesson_numbers"] = json.loads(
        result["lesson_numbers"]
    )

    return result


def create_batch_run(
        request_id,
        stage,
        provider="OPENAI",
        attempt=1
):
    initialize_registry()

    now = datetime.now(
        timezone.utc
    ).isoformat()

    request_id = str(request_id).strip()
    provider = str(provider).strip().upper()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO batch_runs (
                request_id,
                stage,
                provider,
                attempt,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request_id,
                int(stage),
                provider,
                int(attempt),
                "CREATED",
                now,
                now,
            )
        )

        connection.commit()

        return cursor.lastrowid


def update_batch_run(
        run_id,
        status,
        external_batch_id=None,
        input_file_id=None,
        output_file_id=None,
        error=None
):
    initialize_registry()

    now = datetime.now(
        timezone.utc
    ).isoformat()

    status = str(status).strip().upper()

    submitted_at = (
        now
        if status in (
            "SUBMITTED",
            "VALIDATING",
            "IN_PROGRESS"
        )
        else None
    )

    completed_at = (
        now
        if status in (
            "COMPLETED",
            "FAILED",
            "CANCELLED",
            "EXPIRED"
        )
        else None
    )

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE batch_runs

            SET status = ?,
                external_batch_id =
                    COALESCE(?, external_batch_id),
                input_file_id =
                    COALESCE(?, input_file_id),
                output_file_id =
                    COALESCE(?, output_file_id),
                error = ?,
                submitted_at =
                    COALESCE(submitted_at, ?),
                completed_at =
                    COALESCE(completed_at, ?),
                updated_at = ?

            WHERE id = ?
            """,
            (
                status,
                external_batch_id,
                input_file_id,
                output_file_id,
                error,
                submitted_at,
                completed_at,
                now,
                int(run_id),
            )
        )

        connection.commit()

        return cursor.rowcount == 1


def get_batch_runs(
        request_id,
        stage=None,
        provider=None
):
    initialize_registry()

    sql = """
        SELECT *
        FROM batch_runs
        WHERE request_id = ?
    """

    params = [
        str(request_id).strip()
    ]

    if stage is not None:
        sql += " AND stage = ?"
        params.append(int(stage))

    if provider is not None:
        sql += " AND provider = ?"
        params.append(
            str(provider).strip().upper()
        )

    sql += " ORDER BY stage, attempt, id"

    with get_connection() as connection:
        rows = connection.execute(
            sql,
            tuple(params)
        ).fetchall()

    return [
        dict(row)
        for row in rows
    ]


def get_latest_batch_run(
        request_id,
        stage,
        provider="OPENAI"
):
    initialize_registry()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM batch_runs

            WHERE request_id = ?
              AND stage = ?
              AND provider = ?

            ORDER BY attempt DESC, id DESC
            LIMIT 1
            """,
            (
                str(request_id).strip(),
                int(stage),
                str(provider).strip().upper(),
            )
        ).fetchone()

    return (
        dict(row)
        if row is not None
        else None
    )


def mark_batch_ready(request_id):

    initialize_registry()

    now = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as connection:

        cursor = connection.execute(
            """
            UPDATE build_requests

            SET status = 'BATCH_READY',
                completed_at = NULL,
                updated_at = ?,
                error = NULL

            WHERE request_id = ?
              AND processing_mode = 'QUEUE_BATCH'
              AND status IN (
                  'PROCESSING',
                  'FAILED'
              )
            """,
            (
                now,
                request_id
            )
        )

        connection.commit()

        return cursor.rowcount == 1


def mark_batch_submitted(
        request_id,
        openai_batch_id
):

    initialize_registry()

    now = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as connection:

        cursor = connection.execute(
            """
            UPDATE build_requests

            SET status = 'BATCH_SUBMITTED',
                openai_batch_id = ?,
                updated_at = ?,
                error = NULL

            WHERE request_id = ?
              AND processing_mode = 'QUEUE_BATCH'
              AND status = 'BATCH_READY'
            """,
            (
                str(openai_batch_id),
                now,
                request_id
            )
        )

        connection.commit()

        return cursor.rowcount == 1


def set_batch_status(
        request_id,
        status,
        error=None
):

    initialize_registry()

    now = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as connection:

        cursor = connection.execute(
            """
            UPDATE build_requests

            SET status = ?,
                updated_at = ?,
                error = ?

            WHERE request_id = ?
              AND processing_mode = 'QUEUE_BATCH'
            """,
            (
                str(status).strip().upper(),
                now,
                error,
                request_id
            )
        )

        connection.commit()

        return cursor.rowcount == 1

# ==========================================================
# Register Quiz Questions
# ==========================================================

def register_quiz_questions(
        *,
        build_id,
        lesson_package_id,
        curriculum_code,
        moodle_course_id,
        moodle_quiz_id,
        moodle_quiz_cmid,
        questions,
        source="PUBLISH"
):

    initialize_registry()

    if not lesson_package_id:
        raise ValueError(
            "lesson_package_id is required "
            "for quiz question registration."
        )

    if not moodle_quiz_id:
        raise ValueError(
            "moodle_quiz_id is required "
            "for quiz question registration."
        )

    if not questions:
        raise ValueError(
            "questions are required "
            "for quiz question registration."
        )

    now = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as connection:

        for slot, question in enumerate(
                questions,
                start=1
        ):

            question_key = str(
                question.get(
                    "questionkey",
                    ""
                )
            ).strip()

            moodle_question_id = question.get(
                "questionid"
            )

            question_bank_entry_id = question.get(
                "questionbankentryid"
            )

            question_type = str(
                question.get(
                    "qtype",
                    ""
                )
            ).strip()

            if not question_key:
                raise ValueError(
                    f"Missing questionkey at slot {slot}."
                )

            if not moodle_question_id:
                raise ValueError(
                    f"Missing Moodle question ID "
                    f"for {question_key}."
                )

            if not question_bank_entry_id:
                raise ValueError(
                    f"Missing Question Bank entry ID "
                    f"for {question_key}."
                )

            connection.execute(
                """
                INSERT INTO quiz_questions (

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
                    question_type,

                    source,
                    created_at,
                    updated_at

                )

                VALUES (
                    ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?,
                    ?, ?,
                    ?, ?, ?
                )

                ON CONFLICT(
                    moodle_quiz_id,
                    question_key
                )
                DO UPDATE SET

                    build_id =
                        excluded.build_id,

                    lesson_package_id =
                        excluded.lesson_package_id,

                    curriculum_code =
                        excluded.curriculum_code,

                    moodle_course_id =
                        excluded.moodle_course_id,

                    moodle_quiz_id =
                        excluded.moodle_quiz_id,

                    moodle_quiz_cmid =
                        excluded.moodle_quiz_cmid,

                    moodle_question_id =
                        excluded.moodle_question_id,

                    moodle_question_bank_entry_id =
                        excluded.moodle_question_bank_entry_id,

                    moodle_slot =
                        excluded.moodle_slot,

                    question_type =
                        excluded.question_type,

                    source =
                        excluded.source,

                    updated_at =
                        excluded.updated_at
                """,
                (
                    question_key,
                    str(build_id),
                    str(lesson_package_id),
                    curriculum_code,

                    moodle_course_id,
                    int(moodle_quiz_id),
                    moodle_quiz_cmid,

                    int(moodle_question_id),
                    int(question_bank_entry_id),

                    slot,
                    question_type,

                    str(source).upper(),
                    now,
                    now
                )
            )

        connection.commit()



def get_quiz_course_id(
        moodle_quiz_id
):
    """Return the single Moodle course owning a registered quiz."""

    initialize_registry()

    with sqlite3.connect(
        REGISTRY_DB
    ) as db:
        rows = db.execute(
            """
            SELECT DISTINCT moodle_course_id
            FROM quiz_questions
            WHERE moodle_quiz_id = ?
              AND moodle_course_id IS NOT NULL
            """,
            (
                int(moodle_quiz_id),
            )
        ).fetchall()

    course_ids = {
        int(row[0])
        for row in rows
    }

    if not course_ids:
        raise RuntimeError(
            "No registered Moodle course exists "
            f"for Quiz {moodle_quiz_id}."
        )

    if len(course_ids) != 1:
        raise RuntimeError(
            "Quiz "
            f"{moodle_quiz_id} maps to multiple "
            f"Moodle courses: "
            f"{sorted(course_ids)}"
        )

    return next(
        iter(course_ids)
    )


def get_analytics_readiness():
    """Return Analytics readiness for latest published quiz builds."""

    initialize_registry()

    with sqlite3.connect(REGISTRY_DB) as db:
        db.row_factory = sqlite3.Row

        rows = db.execute(
            """
            SELECT
                e.id,
                e.curriculum_code,
                e.parent_code,
                e.year_level,
                e.subject,
                e.build_id,
                e.lesson_package_id,
                e.status,
                e.moodle_course_id,
                e.moodle_quiz_id,
                e.moodle_quiz_cmid,
                e.updated_at,

                (
                    SELECT COUNT(*)
                    FROM quiz_questions q
                    WHERE q.moodle_quiz_id =
                          e.moodle_quiz_id
                ) AS registered_question_count

            FROM elaboration_builds e

            INNER JOIN (
                SELECT
                    curriculum_code,
                    MAX(id) AS latest_id
                FROM elaboration_builds
                GROUP BY curriculum_code
            ) latest
                ON latest.latest_id = e.id

            WHERE e.status = 'PUBLISHED'

            ORDER BY
                e.curriculum_code
            """
        ).fetchall()

    results = []

    for row in rows:
        item = dict(row)

        problems = []

        if not item.get("moodle_course_id"):
            problems.append(
                "MISSING_COURSE_ID"
            )

        if not item.get("moodle_quiz_id"):
            problems.append(
                "MISSING_QUIZ_ID"
            )

        if not item.get("moodle_quiz_cmid"):
            problems.append(
                "MISSING_QUIZ_CMID"
            )

        if (
            item.get("moodle_quiz_id")
            and int(
                item.get(
                    "registered_question_count",
                    0
                )
                or 0
            ) < 1
        ):
            problems.append(
                "NO_REGISTERED_QUESTIONS"
            )

        item["analytics_ready"] = (
            len(problems) == 0
        )

        item["analytics_problems"] = (
            problems
        )

        item["analytics_status"] = (
            "ANALYTICS_READY"
            if not problems
            else problems[0]
        )

        results.append(item)

    return results


def get_analytics_readiness_summary():
    """Return aggregate Analytics readiness counts."""

    rows = get_analytics_readiness()

    ready = [
        row
        for row in rows
        if row["analytics_ready"]
    ]

    problems = [
        row
        for row in rows
        if not row["analytics_ready"]
    ]

    return {
        "published_quizzes":
            len(rows),

        "analytics_ready":
            len(ready),

        "problems":
            len(problems),

        "missing_course_id":
            sum(
                "MISSING_COURSE_ID"
                in row["analytics_problems"]
                for row in rows
            ),

        "missing_quiz_id":
            sum(
                "MISSING_QUIZ_ID"
                in row["analytics_problems"]
                for row in rows
            ),

        "missing_quiz_cmid":
            sum(
                "MISSING_QUIZ_CMID"
                in row["analytics_problems"]
                for row in rows
            ),

        "missing_questions":
            sum(
                "NO_REGISTERED_QUESTIONS"
                in row["analytics_problems"]
                for row in rows
            ),
    }


def get_active_analytics_quizzes():
    """Return current published quizzes only when Analytics-ready."""

    rows = get_analytics_readiness()

    problems = [
        row
        for row in rows
        if not row["analytics_ready"]
    ]

    if problems:
        details = "; ".join(
            (
                str(row["curriculum_code"])
                + ":"
                + ",".join(
                    row["analytics_problems"]
                )
            )
            for row in problems
        )

        raise RuntimeError(
            "Current published quizzes are not "
            "Analytics-ready: "
            + details
        )

    quizzes = []
    seen_quiz_ids = set()

    for row in rows:
        quiz_id = int(
            row["moodle_quiz_id"]
        )

        if quiz_id in seen_quiz_ids:
            raise RuntimeError(
                "Active Moodle quiz is mapped to "
                "multiple current curriculum builds: "
                f"{quiz_id}"
            )

        seen_quiz_ids.add(quiz_id)

        quizzes.append({
            "curriculum_code":
                row["curriculum_code"],

            "parent_code":
                row["parent_code"],

            "year_level":
                row["year_level"],

            "subject":
                row["subject"],

            "moodle_course_id":
                row["moodle_course_id"],

            "moodle_quiz_id":
                row["moodle_quiz_id"],

            "lesson_package_id":
                row["lesson_package_id"],

            "status":
                row["status"],

            "updated_at":
                row["updated_at"],
        })

    quizzes.sort(
        key=lambda row: (
            int(row["moodle_course_id"]),
            int(row["moodle_quiz_id"]),
        )
    )

    return quizzes


# Queue V1 - Read request items

def get_build_request_items(request_id):
    initialize_registry()
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM build_request_items WHERE request_id = ? ORDER BY parent_code, lesson_number, id",
            (str(request_id).strip(),)
        ).fetchall()
    return [dict(row) for row in rows]


# Queue V1 - Create multi-content request

def create_multi_build_request(requested_by, processing_mode, learning_area, subject, year_level, strand, sub_strand, items):
    initialize_registry()
    mode = str(processing_mode).strip().upper()
    if mode not in ("QUEUE_STANDARD", "QUEUE_BATCH"):
        raise ValueError("Invalid queued processing mode.")
    if not isinstance(items, list) or not items:
        raise ValueError("At least one selected lesson is required.")
    normalized = []
    seen = set()
    for raw in items:
        if not isinstance(raw, dict):
            raise ValueError("Each selected lesson must be an object.")
        parent_code = str(raw.get("parent_code") or "").strip()
        if not parent_code:
            raise ValueError("parent_code is required for every lesson.")
        try:
            lesson_number = int(raw.get("lesson_number"))
        except (TypeError, ValueError):
            raise ValueError("A valid lesson_number is required.")
        key = (parent_code, lesson_number)
        if key in seen:
            continue
        seen.add(key)
        normalized.append((parent_code, lesson_number, raw))
    if not normalized:
        raise ValueError("No valid selected lessons were supplied.")
    request_id = "REQ_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_") + uuid.uuid4().hex[:8].upper()
    now = datetime.now(timezone.utc).isoformat()
    parent_codes = list(dict.fromkeys(item[0] for item in normalized))
    summary_parent = parent_codes[0] if len(parent_codes) == 1 else "MULTI"
    summary_lessons = [item[1] for item in normalized]
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO build_requests (request_id, requested_by, processing_mode, learning_area, subject, year_level, strand, sub_strand, parent_code, lesson_numbers, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (request_id, str(requested_by).strip(), mode, str(learning_area).strip(), str(subject).strip(), str(year_level).strip(), str(strand).strip(), str(sub_strand or "").strip(), summary_parent, json.dumps(summary_lessons), "QUEUED", now, now)
        )
        for parent_code, lesson_number, raw in normalized:
            connection.execute(
                "INSERT INTO build_request_items (request_id, parent_code, curriculum_code, content_description, lesson_number, topic_id, lesson_text, status, stage, message, percent, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (request_id, parent_code, str(raw.get("curriculum_code") or parent_code).strip(), str(raw.get("content_description") or "").strip(), lesson_number, str(raw.get("topic_id") or "").strip(), str(raw.get("lesson_text") or "").strip(), "QUEUED", "QUEUED", "Waiting to be processed.", 0, now, now)
            )
        connection.commit()
    return request_id



# ==========================================================
# Queue V1 - Child Item Lifecycle
# ==========================================================

def claim_build_request_item(item_id):
    initialize_registry()

    now = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE build_request_items
            SET status = 'PROCESSING',
                stage = 'PROCESSING',
                message = 'Processing lesson...',
                percent = 5,
                started_at = COALESCE(started_at, ?),
                updated_at = ?,
                error = NULL
            WHERE id = ?
              AND status = 'QUEUED'
            """,
            (
                now,
                now,
                int(item_id)
            )
        )

        connection.commit()

        return cursor.rowcount == 1



def update_build_request_item(
        item_id,
        stage,
        message,
        percent
):
    initialize_registry()

    now = datetime.now(
        timezone.utc
    ).isoformat()

    value = max(
        0,
        min(
            100,
            int(percent)
        )
    )

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE build_request_items
            SET stage = ?,
                message = ?,
                percent = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                str(stage).strip().upper(),
                str(message),
                value,
                now,
                int(item_id)
            )
        )

        connection.commit()



def complete_build_request_item(
        item_id,
        build_id=None,
        lesson_package_id=None
):
    initialize_registry()

    now = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE build_request_items
            SET status = 'PUBLISHED',
                stage = 'PUBLISHED',
                message = 'Lesson published successfully.',
                percent = 100,
                build_id = ?,
                lesson_package_id = ?,
                completed_at = ?,
                updated_at = ?,
                error = NULL
            WHERE id = ?
            """,
            (
                (
                    None
                    if build_id is None
                    else str(build_id)
                ),
                (
                    None
                    if lesson_package_id is None
                    else str(lesson_package_id)
                ),
                now,
                now,
                int(item_id)
            )
        )

        connection.commit()



def fail_build_request_item(
        item_id,
        error
):
    initialize_registry()

    now = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            UPDATE build_request_items
            SET status = 'FAILED',
                stage = 'FAILED',
                message = 'Lesson processing failed.',
                completed_at = ?,
                updated_at = ?,
                error = ?
            WHERE id = ?
            """,
            (
                now,
                now,
                str(error),
                int(item_id)
            )
        )

        connection.commit()



def refresh_build_request_from_items(
        request_id
):
    initialize_registry()

    request_id = str(
        request_id
    ).strip()

    now = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as connection:

        parent = connection.execute(
            """
            SELECT
                processing_mode,
                status
            FROM build_requests
            WHERE request_id = ?
            """,
            (request_id,)
        ).fetchone()

        if parent is None:
            return None

        batch_protected_states = {
            "PROCESSING",
            "BATCH_STAGE1_READY",
            "BATCH_STAGE1_SUBMITTED",
            "BATCH_STAGE1_DOWNLOADED",
            "BATCH_STAGE1_APPLIED",
            "BATCH_STAGE2_READY",
            "BATCH_STAGE2_SUBMITTED",
            "BATCH_STAGE2_DOWNLOADED",
            "BATCH_STAGE2_APPLIED",
            "EXTERNAL_ASSETS_COMPLETED",
        }

        if (
            str(parent["processing_mode"]).strip().upper()
            == "QUEUE_BATCH"
            and str(parent["status"]).strip().upper()
            in batch_protected_states
        ):
            return {
                "request_id": request_id,
                "status": str(
                    parent["status"]
                ).strip().upper(),
                "preserved": True,
            }

        rows = connection.execute(
            """
            SELECT
                status,
                percent,
                error
            FROM build_request_items
            WHERE request_id = ?
            ORDER BY id
            """,
            (
                request_id,
            )
        ).fetchall()

        if not rows:
            return None

        statuses = [
            str(row["status"]).strip().upper()
            for row in rows
        ]

        percentages = [
            int(row["percent"] or 0)
            for row in rows
        ]

        average_percent = int(
            sum(percentages)
            / len(percentages)
        )

        all_published = all(
            status == "PUBLISHED"
            for status in statuses
        )

        any_processing = any(
            status == "PROCESSING"
            for status in statuses
        )

        any_failed = any(
            status == "FAILED"
            for status in statuses
        )

        any_queued = any(
            status == "QUEUED"
            for status in statuses
        )

        if all_published:

            parent_status = "PUBLISHED"
            completed_at = now
            parent_error = None

        elif any_processing:

            parent_status = "PROCESSING"
            completed_at = None
            parent_error = None

        elif any_queued:

            parent_status = "QUEUED"
            completed_at = None

            errors = [
                str(row["error"])
                for row in rows
                if row["error"]
            ]

            parent_error = (
                "; ".join(errors)
                if errors
                else None
            )

        elif any_failed:

            parent_status = "FAILED"
            completed_at = now

            errors = [
                str(row["error"])
                for row in rows
                if row["error"]
            ]

            parent_error = (
                "; ".join(errors)
                if errors
                else "One or more lessons failed."
            )

        else:

            parent_status = "PROCESSING"
            completed_at = None
            parent_error = None

        connection.execute(
            """
            UPDATE build_requests
            SET status = ?,
                completed_at = ?,
                updated_at = ?,
                error = ?
            WHERE request_id = ?
            """,
            (
                parent_status,
                completed_at,
                now,
                parent_error,
                request_id
            )
        )

        connection.commit()

    return {
        "request_id": request_id,
        "status": parent_status,
        "percent": average_percent,
        "item_count": len(rows),
        "published_count": sum(
            status == "PUBLISHED"
            for status in statuses
        ),
        "failed_count": sum(
            status == "FAILED"
            for status in statuses
        ),
        "processing_count": sum(
            status == "PROCESSING"
            for status in statuses
        ),
        "queued_count": sum(
            status == "QUEUED"
            for status in statuses
        )
    }



# ==========================================================
# Queue V1 - Retry Failed Child Items
# ==========================================================

def retry_failed_build_request_items(request_id):
    initialize_registry()

    request_id = str(
        request_id
    ).strip()

    if not request_id:
        raise ValueError(
            "request_id is required."
        )

    now = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as connection:

        request_row = connection.execute(
            """
            SELECT
                request_id,
                processing_mode,
                status
            FROM build_requests
            WHERE request_id = ?
            """,
            (
                request_id,
            )
        ).fetchone()

        if request_row is None:
            raise ValueError(
                "Build request does not exist: "
                + request_id
            )

        failed_rows = connection.execute(
            """
            SELECT id
            FROM build_request_items
            WHERE request_id = ?
              AND status = 'FAILED'
            ORDER BY id
            """,
            (
                request_id,
            )
        ).fetchall()

        if not failed_rows:
            return {
                "request_id": request_id,
                "retried_count": 0,
                "status": str(
                    request_row["status"]
                ).strip().upper(),
            }

        failed_ids = [
            int(row["id"])
            for row in failed_rows
        ]

        placeholders = ",".join(
            "?"
            for _ in failed_ids
        )

        connection.execute(
            f"""
            UPDATE build_request_items

            SET status = 'QUEUED',
                stage = 'QUEUED',
                message = 'Waiting to be retried.',
                percent = 0,
                error = NULL,
                build_id = NULL,
                lesson_package_id = NULL,
                started_at = NULL,
                completed_at = NULL,
                updated_at = ?

            WHERE request_id = ?
              AND status = 'FAILED'
              AND id IN ({placeholders})
            """,
            (
                now,
                request_id,
                *failed_ids
            )
        )

        connection.execute(
            """
            UPDATE build_requests

            SET status = 'QUEUED',
                error = NULL,
                started_at = NULL,
                completed_at = NULL,
                updated_at = ?

            WHERE request_id = ?
            """,
            (
                now,
                request_id
            )
        )

        connection.commit()

    return {
        "request_id": request_id,
        "retried_count": len(failed_ids),
        "retried_item_ids": failed_ids,
        "status": "QUEUED",
    }
