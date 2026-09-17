"""Curriculum metadata resolver for Analytics dashboard."""

import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

REGISTRY_DB = (
    ROOT
    / "data"
    / "build_registry.db"
)


def get_connection():
    db = sqlite3.connect(
        REGISTRY_DB
    )

    db.row_factory = sqlite3.Row

    return db


def lesson_metadata(
        *,
        moodle_quiz_id
):
    with get_connection() as db:
        row = db.execute(
            """
            SELECT
                id,
                curriculum_code,
                parent_code,
                topic_id,
                elaboration,
                content_description,
                learning_area,
                subject,
                year_level,
                strand,
                sub_strand,
                lesson_package_id,
                moodle_course_id,
                moodle_quiz_id,
                moodle_quiz_cmid,
                status,
                updated_at
            FROM elaboration_builds
            WHERE moodle_quiz_id = ?
              AND status = 'PUBLISHED'
            ORDER BY
                updated_at DESC,
                id DESC
            LIMIT 1
            """,
            (
                int(moodle_quiz_id),
            )
        ).fetchone()

    if row is None:
        return None

    return dict(row)


def course_lessons(course_id):
    with get_connection() as db:
        rows = db.execute(
            """
            SELECT *
            FROM (
                SELECT
                    id,
                    curriculum_code,
                    parent_code,
                    topic_id,
                    elaboration,
                    content_description,
                    learning_area,
                    subject,
                    year_level,
                    strand,
                    sub_strand,
                    lesson_package_id,
                    moodle_course_id,
                    moodle_quiz_id,
                    moodle_quiz_cmid,
                    status,
                    updated_at,

                    ROW_NUMBER() OVER (
                        PARTITION BY moodle_quiz_id
                        ORDER BY
                            updated_at DESC,
                            id DESC
                    ) AS rn

                FROM elaboration_builds

                WHERE moodle_course_id = ?
                  AND status = 'PUBLISHED'
                  AND moodle_quiz_id IS NOT NULL
            )
            WHERE rn = 1
            ORDER BY
                parent_code,
                curriculum_code
            """,
            (
                int(course_id),
            )
        ).fetchall()

    return [
        dict(row)
        for row in rows
    ]
