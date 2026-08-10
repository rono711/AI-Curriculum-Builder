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
        build_mode="NEW"
):

    initialize_registry()

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

                status,

                created_at,
                updated_at

            )

            VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?
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
        moodle_section_id=None
):

    now = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as connection:

        connection.execute(
            """
            UPDATE elaboration_builds

            SET status = ?,
                moodle_course_id =
                    COALESCE(
                        ?,
                        moodle_course_id
                    ),
                moodle_section_id =
                    COALESCE(
                        ?,
                        moodle_section_id
                    ),
                updated_at = ?

            WHERE id = ?
            """,
            (
                str(status).upper(),

                moodle_course_id,

                moodle_section_id,

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
        moodle_section_id=None
):

    update_status(
        record_id,
        "PUBLISHED",
        moodle_course_id,
        moodle_section_id
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