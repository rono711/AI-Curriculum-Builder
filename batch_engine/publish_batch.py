import argparse
import json
import sqlite3
import sys
from pathlib import Path

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
            + ": Moodle identity already exists. "
            + "Refusing duplicate publication."
        )

    update_build_request_item(
        item["item_id"],
        "MOODLE_PUBLISH",
        "Publishing lesson to Moodle...",
        90
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
