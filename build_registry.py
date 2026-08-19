"""
Rono's School AI Curriculum Builder
Persistent Elaboration Build Registry

Purpose:
- Track elaborations successfully published across different build requests.
- Prevent accidental duplicate builds.
- Allow an explicit UPDATE build later.
"""

import sqlite3
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
