"""Resolve analytics curriculum hierarchy from build registry."""

import sqlite3

from build_registry import (
    REGISTRY_DB,
)


def resolve_curriculum_identity(
        curriculum_code
):
    """Resolve an elaboration to its parent Content Description."""

    with sqlite3.connect(
        REGISTRY_DB
    ) as db:
        db.row_factory = sqlite3.Row

        row = db.execute(
            """
            SELECT
                learning_area,
                subject,
                year_level,
                strand,
                sub_strand,
                parent_code,
                curriculum_code,
                content_description,
                elaboration,
                topic_id
            FROM elaboration_builds
            WHERE curriculum_code = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                curriculum_code,
            )
        ).fetchone()

    if row is None:
        raise RuntimeError(
            "No curriculum identity exists for "
            f"{curriculum_code}."
        )

    if not row["parent_code"]:
        raise RuntimeError(
            "Curriculum identity has no parent "
            f"Content Description: {curriculum_code}"
        )

    return dict(row)


def get_content_description_lessons(
        parent_code
):
    """Return known lessons under one Content Description."""

    with sqlite3.connect(
        REGISTRY_DB
    ) as db:
        db.row_factory = sqlite3.Row

        rows = db.execute(
            """
            SELECT
                curriculum_code,
                topic_id,
                elaboration,
                content_description,
                moodle_quiz_id,
                status
            FROM elaboration_builds
            WHERE parent_code = ?
            ORDER BY
                curriculum_code,
                id DESC
            """,
            (
                parent_code,
            )
        ).fetchall()

    unique = {}

    for row in rows:
        code = row["curriculum_code"]

        if code not in unique:
            unique[code] = dict(row)

    return list(
        unique.values()
    )
