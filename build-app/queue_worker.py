import os
import sys

import httpx


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from build_registry import (
    claim_build_request,
    complete_build_request,
    fail_build_request,
    get_queued_requests,
    get_build_request_items,
    claim_build_request_item,
    update_build_request_item,
    complete_build_request_item,
    fail_build_request_item,
    refresh_build_request_from_items,
)


LESSON_PACKAGE_BUILDER_URL = os.getenv(
    "LESSON_PACKAGE_BUILDER_URL",
    "http://lesson-package-builder:8003/build",
)


def process_multi_standard_request(request):
    request_id = request["request_id"]

    if not claim_build_request(request_id):
        print(
            "SKIP:",
            request_id,
            "was already claimed.",
        )
        return False

    items = get_build_request_items(
        request_id
    )

    if not items:
        fail_build_request(
            request_id,
            "Multi-content request has no child items.",
        )
        return False

    print("=" * 60)
    print("STANDARD MULTI-CONTENT QUEUE REQUEST")
    print("Request:", request_id)
    print("Items:", len(items))
    print("=" * 60)

    for item in items:
        item_id = item["id"]

        if item["status"] == "PUBLISHED":
            print(
                "ALREADY PUBLISHED:",
                item["curriculum_code"],
            )
            continue

        if not claim_build_request_item(item_id):
            print(
                "SKIP ITEM:",
                item_id,
                item["curriculum_code"],
                "could not be claimed.",
            )
            continue

        update_build_request_item(
            item_id,
            "BUILDING",
            "Preparing lesson package...",
            10,
        )

        payload = {
            "requested_by":
                request["requested_by"],

            "learning_area":
                request["learning_area"],

            "subject":
                request["subject"],

            "year_level":
                request["year_level"],

            "strand":
                request["strand"],

            "sub_strand":
                request["sub_strand"] or "",

            "parent_code":
                item["parent_code"],

            "lesson_numbers":
                [item["lesson_number"]],

            "build_mode":
                "NEW",

            "update_components":
                [],

            "publication_mode":
                "IMMEDIATE",

            "progress_job_id":
                "",

            "progress_url":
                "",
        }

        print(
            "PROCESSING ITEM:",
            item["curriculum_code"],
            "| Parent:",
            payload["parent_code"],
            "| Lesson:",
            payload["lesson_numbers"],
        )

        try:
            update_build_request_item(
                item_id,
                "GENERATING",
                "Generating and publishing lesson...",
                25,
            )

            with httpx.Client(
                timeout=1800
            ) as client:
                response = client.post(
                    LESSON_PACKAGE_BUILDER_URL,
                    json=payload,
                )

            if response.status_code != 200:
                try:
                    detail = response.json()
                except Exception:
                    detail = response.text

                raise RuntimeError(
                    "Lesson Package Builder returned HTTP "
                    f"{response.status_code}: {detail}"
                )

            result = response.json()

            if result.get("status") != "SUCCESS":
                raise RuntimeError(
                    "Lesson Package Builder did not "
                    "return SUCCESS: "
                    + str(result)
                )

            lesson_results = result.get(
                "lessons",
                []
            )

            if len(lesson_results) != 1:
                raise RuntimeError(
                    "Expected exactly one lesson result, "
                    f"received {len(lesson_results)}."
                )

            lesson_result = lesson_results[0]

            if lesson_result.get("status") != "SUCCESS":
                raise RuntimeError(
                    "Lesson pipeline did not return "
                    "SUCCESS: "
                    + str(lesson_result)
                )

            returned_package_id = str(
                lesson_result.get(
                    "lesson_package_id",
                    ""
                )
            ).strip()

            if not returned_package_id:
                raise RuntimeError(
                    "Lesson pipeline did not return "
                    "lesson_package_id."
                )

            build_id = result.get(
                "build_id"
            )

            complete_build_request_item(
                item_id,
                build_id=build_id,
                lesson_package_id=returned_package_id,
            )

            summary = (
                refresh_build_request_from_items(
                    request_id
                )
            )

            print(
                "PUBLISHED ITEM:",
                item["curriculum_code"],
                "| Build:",
                build_id,
                "| Package:",
                returned_package_id,
            )

            print(
                "REQUEST STATUS:",
                summary
            )

        except Exception as exc:
            fail_build_request_item(
                item_id,
                str(exc),
            )

            summary = (
                refresh_build_request_from_items(
                    request_id
                )
            )

            print(
                "FAILED ITEM:",
                item["curriculum_code"],
                str(exc),
            )

            print(
                "REQUEST STATUS:",
                summary
            )

    summary = refresh_build_request_from_items(
        request_id
    )

    print("=" * 60)
    print("MULTI-CONTENT REQUEST FINISHED")
    print("Request:", request_id)
    print("Summary:", summary)
    print("=" * 60)

    return (
        summary is not None
        and summary["status"] == "PUBLISHED"
    )


def process_standard_request(request):
    request_id = request["request_id"]

    if not claim_build_request(request_id):
        print(
            "SKIP:",
            request_id,
            "was already claimed.",
        )
        return False

    print("=" * 60)
    print("STANDARD QUEUE REQUEST")
    print("Request:", request_id)
    print("Parent:", request["parent_code"])
    print("Lessons:", request["lesson_numbers"])
    print("=" * 60)

    payload = {
        "requested_by":
            request["requested_by"],

        "learning_area":
            request["learning_area"],

        "subject":
            request["subject"],

        "year_level":
            request["year_level"],

        "strand":
            request["strand"],

        "sub_strand":
            request["sub_strand"] or "",

        "parent_code":
            request["parent_code"],

        "lesson_numbers":
            request["lesson_numbers"],

        "build_mode":
            "NEW",

        "update_components":
            [],

        "publication_mode":
            "IMMEDIATE",

        "progress_job_id":
            "",

        "progress_url":
            "",
    }

    try:
        with httpx.Client(timeout=1800) as client:
            response = client.post(
                LESSON_PACKAGE_BUILDER_URL,
                json=payload,
            )

        if response.status_code != 200:
            try:
                detail = response.json()
            except Exception:
                detail = response.text

            raise RuntimeError(
                "Lesson Package Builder returned HTTP "
                f"{response.status_code}: {detail}"
            )

        result = response.json()

        if result.get("status") != "SUCCESS":
            raise RuntimeError(
                "Lesson Package Builder did not return SUCCESS: "
                + str(result)
            )

        complete_build_request(request_id)

        print(
            "PUBLISHED:",
            request_id,
        )

        return True

    except Exception as exc:
        fail_build_request(
            request_id,
            str(exc),
        )

        print(
            "FAILED:",
            request_id,
            str(exc),
        )

        return False


def run_once():
    queued = get_queued_requests(
        processing_mode="QUEUE_STANDARD",
        limit=1,
    )

    if not queued:
        print("No QUEUE_STANDARD requests waiting.")
        return 0

    request = queued[0]

    items = get_build_request_items(
        request["request_id"]
    )

    if items:
        print(
            "ROUTING TO MULTI-CONTENT WORKER:",
            request["request_id"],
            "| Items:",
            len(items),
        )

        success = process_multi_standard_request(
            request
        )

    else:
        print(
            "ROUTING TO LEGACY STANDARD WORKER:",
            request["request_id"],
        )

        success = process_standard_request(
            request
        )

    if success:
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(run_once())
