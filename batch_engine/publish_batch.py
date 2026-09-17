import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from build_registry import (
    get_build_request,
    get_build_request_items,
    checkpoint_moodle_identity,
    register_quiz_questions,
    mark_published,
    mark_failed_if_incomplete,
    complete_build_request_item,
    fail_build_request_item,
    refresh_build_request_from_items,
    update_build_request_item,
)

from pipeline_engine.builder import PipelineBuilder


CURRICULUM_NORMALIZER_INTERNAL_URL = os.getenv(
    "CURRICULUM_NORMALIZER_INTERNAL_URL",
    "http://curriculum-normalizer:8001"
).rstrip("/")

PUBLISHER_ENGINE_URL = os.getenv(
    "PUBLISHER_ENGINE_URL",
    "http://publisher-engine:8012/publish"
)

PUBLISHER_ENGINE_BASE_URL = (
    PUBLISHER_ENGINE_URL.rsplit(
        "/publish",
        1
    )[0]
    if PUBLISHER_ENGINE_URL.endswith("/publish")
    else PUBLISHER_ENGINE_URL.rstrip("/")
)


def read_json(path):
    return json.loads(
        Path(path).read_text(
            encoding="utf-8"
        )
    )


def build_publish_plan(rid):
    request = get_build_request(rid)

    if request is None:
        raise RuntimeError(
            "Request not found: " + rid
        )

    if request["status"] != "EXTERNAL_ASSETS_COMPLETED":
        raise RuntimeError(
            "Expected EXTERNAL_ASSETS_COMPLETED, found "
            + str(request["status"])
        )

    batch_dir = (
        ROOT / "data" / "batches" / rid
    )

    prepare = read_json(
        batch_dir / "prepare_state.json"
    )

    children = {
        int(row["id"]): row
        for row in get_build_request_items(rid)
    }

    plan = []

    for prepared in prepare["prepared_lessons"]:
        item_id = int(
            prepared["item_id"]
        )

        child = children.get(item_id)

        if child is None:
            raise RuntimeError(
                "Child item missing: "
                + str(item_id)
            )

        rows = (
            prepared.get("lesson_rows")
            or []
        )

        if len(rows) != 1:
            raise RuntimeError(
                "Expected one lesson row for item "
                + str(item_id)
            )

        package = str(
            rows[0]["lesson_package_id"]
        ).strip()

        workbook = Path(
            prepared["workbook_path"]
        )

        if not workbook.is_file():
            raise RuntimeError(
                "Workbook missing: "
                + str(workbook)
            )

        build_name = workbook.stem
        build_root = workbook.parent.parent

        plan.append({
            "request_id":
                rid,
            "item_id":
                item_id,
            "item_status":
                str(
                    child["status"]
                ).strip().upper(),
            "build_id":
                str(
                    prepared["build_id"]
                ),
            "lesson_package_id":
                package,
            "curriculum_code":
                str(
                    child["curriculum_code"]
                ).strip(),
            "workbook":
                str(workbook),
            "build_root":
                str(build_root),
            "build_name":
                build_name,
        })

    if len(plan) != 2:
        raise RuntimeError(
            "Expected 2 lessons, found "
            + str(len(plan))
        )

    return plan


def get_registry_record(build_id, package):
    db = sqlite3.connect(
        ROOT / "data" / "build_registry.db"
    )
    db.row_factory = sqlite3.Row

    try:
        row = db.execute(
            """
            SELECT *
            FROM elaboration_builds
            WHERE build_id = ?
              AND lesson_package_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (
                str(build_id),
                str(package),
            )
        ).fetchone()

        if row is None:
            raise RuntimeError(
                "Elaboration registry record missing for "
                + str(build_id)
                + " / "
                + str(package)
            )

        return dict(row)

    finally:
        db.close()


def get_published_subsection_lessons(
        moodle_course_id,
        moodle_subsection_section_id
):
    db = sqlite3.connect(
        ROOT / "data" / "build_registry.db"
    )
    db.row_factory = sqlite3.Row

    try:
        rows = db.execute(
            """
            SELECT *
            FROM elaboration_builds
            WHERE status = 'PUBLISHED'
              AND moodle_course_id = ?
              AND moodle_subsection_section_id = ?
            ORDER BY id DESC
            """,
            (
                int(moodle_course_id),
                int(moodle_subsection_section_id),
            )
        ).fetchall()
    finally:
        db.close()

    # Newest published row wins for duplicate
    # historical curriculum records.
    lessons = {}

    for row in rows:
        record = dict(row)

        code = str(
            record.get("curriculum_code") or ""
        ).strip()

        if not code:
            continue

        if code not in lessons:
            lessons[code] = record

    return lessons


def get_canonical_curriculum_order(
        curriculum_codes
):
    if not curriculum_codes:
        return []

    params = [
        ("curriculum_code", code)
        for code in curriculum_codes
    ]

    response = requests.get(
        CURRICULUM_NORMALIZER_INTERNAL_URL
        + "/canonical-order",
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    result = response.json()

    if not isinstance(result, list):
        raise RuntimeError(
            "Canonical-order service returned "
            "an invalid response."
        )

    returned = [
        str(
            row.get("curriculum_code") or ""
        ).strip()
        for row in result
        if isinstance(row, dict)
    ]

    expected = set(curriculum_codes)
    actual = set(returned)

    if len(returned) != len(actual):
        raise RuntimeError(
            "Canonical-order service returned "
            "duplicate curriculum codes: "
            + repr(returned)
        )

    if (
        expected != actual
        or len(returned) != len(curriculum_codes)
    ):
        raise RuntimeError(
            "Canonical-order mismatch. Expected "
            + repr(sorted(expected))
            + ", received "
            + repr(sorted(actual))
        )

    return returned


def build_owned_cmid_sequence(
        ordered_codes,
        lessons
):
    component_columns = (
        "moodle_content_description_cmid",
        "moodle_lesson_content_cmid",
        "moodle_did_you_know_cmid",
        "moodle_quiz_cmid",
        "moodle_activities_cmid",
        "moodle_recap_cmid",
    )

    cmids = []
    seen = set()

    for code in ordered_codes:
        record = lessons[code]

        for column in component_columns:
            value = record.get(column)

            if value is None:
                continue

            cmid = int(value)

            if cmid <= 0 or cmid in seen:
                continue

            seen.add(cmid)
            cmids.append(cmid)

    return cmids


def reconcile_published_subsection(
        moodle_course_id,
        moodle_subsection_section_id
):
    lessons = get_published_subsection_lessons(
        moodle_course_id,
        moodle_subsection_section_id,
    )

    if len(lessons) <= 1:
        return {
            "status": "SKIPPED_SINGLE_LESSON",
            "lesson_count": len(lessons),
        }

    ordered_codes = get_canonical_curriculum_order(
        list(lessons.keys())
    )

    cmids = build_owned_cmid_sequence(
        ordered_codes,
        lessons,
    )

    if not cmids:
        raise RuntimeError(
            "No Moodle CMIDs available for "
            "order reconciliation."
        )

    response = requests.post(
        PUBLISHER_ENGINE_BASE_URL
        + "/reconcile-order",
        json={
            "courseid":
                int(moodle_course_id),

            "sectionid":
                int(moodle_subsection_section_id),

            "cmids":
                cmids,

            "dryrun":
                False,
        },
        timeout=60,
    )

    response.raise_for_status()

    result = response.json()

    if result.get("status") != "SUCCESS":
        raise RuntimeError(
            "Publisher reconciliation did not "
            "return SUCCESS: "
            + repr(result)
        )

    reconciliation = result.get(
        "reconciliation"
    )

    if not isinstance(reconciliation, dict):
        raise RuntimeError(
            "Publisher reconciliation response "
            "is missing reconciliation data."
        )

    if reconciliation.get("changed"):
        raise RuntimeError(
            "Moodle order remains incorrect after "
            "reconciliation."
        )

    return {
        "status": "SUCCESS",
        "lesson_count": len(lessons),
        "curriculum_codes": ordered_codes,
        "cmids": cmids,
        "reconciliation": reconciliation,
    }


def call_moodle(pipeline, item):
    package = item["lesson_package_id"]

    registry = get_registry_record(
        item["build_id"],
        package
    )

    if item["item_status"] == "PUBLISHED":
        return {
            "skip": True,
            "registry": registry,
        }

    if (
        registry.get("status") == "PUBLISHED"
        and registry.get("moodle_course_id")
        and registry.get(
            "moodle_subsection_section_id"
        )
    ):
        print(
            "ORDER-ONLY RECOVERY:",
            package
        )

        return {
            "skip": False,
            "order_only": True,
            "registry": registry,
        }

    workbook_status = (
        pipeline._get_publication_status(
            item["workbook"],
            package
        )
    )

    if workbook_status == "PUBLISHED":
        raise RuntimeError(
            package
            + ": workbook already PUBLISHED."
        )

    if registry.get("moodle_course_id"):
        raise RuntimeError(
            package
            + ": Moodle identity already exists but "
            + "registry is not safely PUBLISHED. "
            + "Refusing duplicate publication."
        )

    update_build_request_item(
        item["item_id"],
        "PUBLISHING",
        "Publishing lesson to Moodle...",
        95
    )

    pipeline._set_publication_status(
        item["workbook"],
        package,
        "PUBLISHING",
        "YES"
    )

    print("PUBLISHING:", package)

    publish_call = (
        pipeline._call_publisher_safely(
            item["build_root"],
            item["build_name"],
            package
        )
    )

    if not publish_call["success"]:
        pipeline._set_publication_status(
            item["workbook"],
            package,
            "FAILED",
            "YES"
        )

        raise RuntimeError(
            package
            + ": Moodle publisher failed: "
            + str(publish_call["result"])
        )

    moodle = publish_call["result"].get(
        "publisher"
    )

    if (
        not isinstance(moodle, dict)
        or moodle.get("status") != "success"
    ):
        pipeline._set_publication_status(
            item["workbook"],
            package,
            "FAILED",
            "YES"
        )

        raise RuntimeError(
            package
            + ": invalid Moodle result."
        )

    return {
        "skip": False,
        "registry": registry,
        "moodle": moodle,
    }


def finalize_moodle(pipeline, item, call_result):
    package = item["lesson_package_id"]
    registry = call_result["registry"]

    if call_result["skip"]:
        print("FINALIZE SKIP:", package)
        return True

    if call_result.get("order_only"):
        print(
            "FINALIZE ORDER-ONLY:",
            package
        )

        reconciliation = (
            reconcile_published_subsection(
                moodle_course_id=registry[
                    "moodle_course_id"
                ],
                moodle_subsection_section_id=registry[
                    "moodle_subsection_section_id"
                ],
            )
        )

        print(
            "MOODLE ORDER RECOVERY:",
            reconciliation.get("status"),
            "lessons=",
            reconciliation.get("lesson_count"),
        )

        pipeline._set_publication_status(
            item["workbook"],
            package,
            "PUBLISHED",
            "NO"
        )

        complete_build_request_item(
            item["item_id"],
            build_id=item["build_id"],
            lesson_package_id=package,
        )

        print(
            "BATCH CHILD RECOVERED:",
            package
        )

        return True

    moodle = call_result["moodle"]

    checkpoint_moodle_identity(
        record_id=registry["id"],
        moodle_course_id=moodle.get("courseid"),
        moodle_section_id=moodle.get("strandsectionid"),
        moodle_subsection_cmid=moodle.get("subsectioncmid"),
        moodle_subsection_section_id=moodle.get(
            "subsectionsectionid"
        ),
        moodle_content_description_cmid=moodle.get(
            "contentdescriptioncmid"
        ),
        moodle_lesson_content_cmid=moodle.get(
            "lessoncontentcmid"
        ),
        moodle_did_you_know_cmid=moodle.get(
            "didyouknowcmid"
        ),
        moodle_quiz_id=moodle.get("quizid"),
        moodle_quiz_cmid=moodle.get("quizcmid"),
        moodle_activities_cmid=moodle.get(
            "activitiescmid"
        ),
        moodle_recap_cmid=moodle.get("recapcmid"),
    )

    print(
        "MOODLE IDENTITY CHECKPOINTED:",
        registry["id"]
    )

    questions = moodle.get("questions")

    if not questions:
        mark_failed_if_incomplete(
            registry["id"]
        )
        raise RuntimeError(
            package
            + ": Moodle returned no question mappings."
        )

    register_quiz_questions(
        build_id=item["build_id"],
        lesson_package_id=package,
        curriculum_code=item["curriculum_code"],
        moodle_course_id=moodle.get("courseid"),
        moodle_quiz_id=moodle.get("quizid"),
        moodle_quiz_cmid=moodle.get("quizcmid"),
        questions=questions,
        source="BATCH_PUBLISH",
    )

    print(
        "QUIZ QUESTIONS REGISTERED:",
        len(questions)
    )

    mark_published(
        record_id=registry["id"],
        moodle_course_id=moodle.get("courseid"),
        moodle_section_id=moodle.get("strandsectionid"),
        moodle_subsection_cmid=moodle.get("subsectioncmid"),
        moodle_subsection_section_id=moodle.get(
            "subsectionsectionid"
        ),
        moodle_content_description_cmid=moodle.get(
            "contentdescriptioncmid"
        ),
        moodle_lesson_content_cmid=moodle.get(
            "lessoncontentcmid"
        ),
        moodle_did_you_know_cmid=moodle.get(
            "didyouknowcmid"
        ),
        moodle_quiz_id=moodle.get("quizid"),
        moodle_quiz_cmid=moodle.get("quizcmid"),
        moodle_activities_cmid=moodle.get(
            "activitiescmid"
        ),
        moodle_recap_cmid=moodle.get("recapcmid"),
    )

    reconciliation = reconcile_published_subsection(
        moodle_course_id=moodle.get("courseid"),
        moodle_subsection_section_id=moodle.get(
            "subsectionsectionid"
        ),
    )

    print(
        "MOODLE ORDER RECONCILIATION:",
        reconciliation.get("status"),
        "lessons=",
        reconciliation.get("lesson_count"),
    )

    pipeline._set_publication_status(
        item["workbook"],
        package,
        "PUBLISHED",
        "NO"
    )

    complete_build_request_item(
        item["item_id"],
        build_id=item["build_id"],
        lesson_package_id=package,
    )

    print("BATCH CHILD PUBLISHED:", package)

    return True


def validate(rid):
    plan = build_publish_plan(rid)

    pipeline = PipelineBuilder()

    print("=" * 70)
    print("BATCH MOODLE PUBLICATION VALIDATION")
    print("REQUEST:", rid)
    print("=" * 70)

    for item in plan:
        status = pipeline._get_publication_status(
            item["workbook"],
            item["lesson_package_id"]
        )

        registry = get_registry_record(
            item["build_id"],
            item["lesson_package_id"]
        )

        print()
        print(
            "ITEM:",
            item["item_id"]
        )
        print(
            "PACKAGE:",
            item["lesson_package_id"]
        )
        print(
            "CURRICULUM:",
            item["curriculum_code"]
        )
        print(
            "BUILD ID:",
            item["build_id"]
        )
        print(
            "CHILD STATUS:",
            item["item_status"]
        )
        print(
            "REGISTRY RECORD:",
            registry["id"]
        )
        print(
            "REGISTRY STATUS:",
            registry["status"]
        )
        print(
            "MOODLE COURSE:",
            registry["moodle_course_id"]
        )
        print(
            "WORKBOOK STATUS:",
            status or "NOT PUBLISHED"
        )
        print(
            "BUILD ROOT:",
            item["build_root"]
        )
        print(
            "BUILD NAME:",
            item["build_name"]
        )

    print()
    print("=" * 70)
    print("VALIDATION: PASS")
    print("NO MOODLE PUBLICATION CALLS MADE")
    print("=" * 70)

    return 0


def publish(rid):
    plan = build_publish_plan(rid)
    pipeline = PipelineBuilder()

    print("=" * 70)
    print("BATCH MOODLE PUBLICATION")
    print("REQUEST:", rid)
    print("=" * 70)

    for item in plan:
        try:
            result = call_moodle(
                pipeline,
                item
            )

            finalize_moodle(
                pipeline,
                item,
                result
            )

        except Exception as exc:
            print(
                "PUBLICATION FAILED:",
                item["lesson_package_id"]
            )
            print("ERROR:", exc)

            refresh_build_request_from_items(
                rid
            )

            raise

    parent = refresh_build_request_from_items(
        rid
    )

    print()
    print("PARENT STATUS:", parent)
    print("BATCH MOODLE PUBLICATION COMPLETE")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "request_id"
    )

    parser.add_argument(
        "--publish",
        action="store_true"
    )

    args = parser.parse_args()

    if args.publish:
        raise SystemExit(
            publish(args.request_id)
        )

    raise SystemExit(
        validate(args.request_id)
    )
