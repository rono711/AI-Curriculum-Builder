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
)


LESSON_PACKAGE_BUILDER_URL = os.getenv(
    "LESSON_PACKAGE_BUILDER_URL",
    "http://lesson-package-builder:8003/build",
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

    success = process_standard_request(
        queued[0]
    )

    if success:
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(run_once())
