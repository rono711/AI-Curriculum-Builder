import os
import sys

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )

import httpx

from fastapi import HTTPException

from build_registry import (
    get_connection,
    mark_published
)


PUBLISHER_ENGINE_URL = os.getenv(
    "PUBLISHER_ENGINE_URL",
    "http://publisher-engine:8012/publish"
)


async def publish_generated_lesson(payload):

    lesson_package_id = str(
        payload.get(
            "lesson_package_id",
            ""
        )
    ).strip()

    if not lesson_package_id:

        raise HTTPException(
            status_code=400,
            detail="lesson_package_id is required"
        )

    # ======================================================
    # Find GENERATED registry record
    # ======================================================

    with get_connection() as connection:

        row = connection.execute(
            """
            SELECT *
            FROM elaboration_builds
            WHERE lesson_package_id = ?
              AND status = 'GENERATED'
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                lesson_package_id,
            )
        ).fetchone()

    if row is None:

        raise HTTPException(
            status_code=409,
            detail=(
                "No GENERATED registry record found for "
                + lesson_package_id
            )
        )

    record = dict(row)

    record_id = record["id"]
    build_id = str(
        record["build_id"]
    )

    # ======================================================
    # Locate existing workbook
    # ======================================================

    project_root = str(
        PROJECT_ROOT
    )

    builds_root = os.path.join(
        project_root,
        "builds"
    )

    build_token = (
        "_"
        + build_id.zfill(6)
        + "_"
    )

    matches = []

    for root, dirs, files in os.walk(
        builds_root
    ):

        if os.path.basename(root) != "Workbook":
            continue

        for filename in files:

            if (
                filename.startswith("BLD_")
                and
                build_token in filename
                and
                filename.endswith(".xlsx")
            ):

                matches.append(
                    os.path.join(
                        root,
                        filename
                    )
                )

    if len(matches) != 1:

        raise HTTPException(
            status_code=409,
            detail=(
                "Expected exactly one workbook for Build "
                + build_id
                + ", found "
                + str(len(matches))
            )
        )

    workbook_path = matches[0]

    workbook_dir = os.path.dirname(
        workbook_path
    )

    build_name = os.path.splitext(
        os.path.basename(
            workbook_path
        )
    )[0]

    build_root = os.path.dirname(
        workbook_dir
    )

    # ======================================================
    # Publish existing generated package
    # ======================================================

    publisher_payload = {
        "build_root":
            build_root,

        "build_name":
            build_name,

        "lesson_package_id":
            lesson_package_id
    }

    print("=" * 60)
    print("PUBLISH GENERATED LESSON")
    print("Registry Record :", record_id)
    print("Build ID        :", build_id)
    print("Build Name      :", build_name)
    print("Lesson Package  :", lesson_package_id)
    print("=" * 60)

    try:

        async with httpx.AsyncClient(
            timeout=300.0
        ) as client:

            response = await client.post(
                PUBLISHER_ENGINE_URL,
                json=publisher_payload
            )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=(
                "Publisher Engine request failed: "
                + str(exc)
            )
        )

    if response.status_code != 200:

        raise HTTPException(
            status_code=502,
            detail=(
                "Publisher Engine returned "
                + str(response.status_code)
                + ": "
                + response.text[:1000]
            )
        )

    try:

        publisher_result = response.json()

    except ValueError:

        raise HTTPException(
            status_code=502,
            detail=(
                "Publisher Engine returned invalid JSON"
            )
        )

    if (
        publisher_result.get("status")
        != "SUCCESS"
    ):

        raise HTTPException(
            status_code=502,
            detail=(
                "Publisher Engine did not return SUCCESS: "
                + str(publisher_result)
            )
        )

    # ======================================================
    # Extract Moodle result returned inside Publisher result
    # ======================================================

    moodle_result = publisher_result.get(
        "publisher",
        {}
    )

    if (
        moodle_result.get("status")
        != "success"
    ):

        raise HTTPException(
            status_code=502,
            detail=(
                "Moodle Publisher result was not successful: "
                + str(moodle_result)
            )
        )

    # ======================================================
    # Registry -> PUBLISHED
    # ======================================================

    mark_published(
        record_id=record_id,

        moodle_course_id=
            moodle_result.get(
                "courseid"
            ),

        moodle_section_id=
            moodle_result.get(
                "strandsectionid"
            ),

        moodle_subsection_cmid=
            moodle_result.get(
                "subsectioncmid"
            ),

        moodle_subsection_section_id=
            moodle_result.get(
                "subsectionsectionid"
            ),

        moodle_content_description_cmid=
            moodle_result.get(
                "contentdescriptioncmid"
            ),

        moodle_lesson_content_cmid=
            moodle_result.get(
                "lessoncontentcmid"
            ),

        moodle_did_you_know_cmid=
            moodle_result.get(
                "didyouknowcmid"
            ),

        moodle_quiz_id=
            moodle_result.get(
                "quizid"
            ),

        moodle_quiz_cmid=
            moodle_result.get(
                "quizcmid"
            ),

        moodle_activities_cmid=
            moodle_result.get(
                "activitiescmid"
            ),

        moodle_recap_cmid=
            moodle_result.get(
                "recapcmid"
            )
    )

    print(
        "REGISTRY RECORD:",
        record_id,
        "STATUS: PUBLISHED"
    )

    return {
        "status":
            "SUCCESS",

        "lesson_package_id":
            lesson_package_id,

        "build_id":
            build_id,

        "publisher":
            publisher_result
    }
