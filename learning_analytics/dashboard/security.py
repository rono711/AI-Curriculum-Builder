"""Authentication and authorization for dashboard API."""

import hashlib
import hmac
import time

from fastapi import Header, HTTPException, Request

from learning_analytics.config import (
    DASHBOARD_API_SECRET,
    DASHBOARD_SIGNATURE_MAX_AGE,
)
from learning_analytics.dashboard.roles import (
    course_users,
)


def _reject(status_code, detail):
    raise HTTPException(
        status_code=status_code,
        detail=detail,
    )


def verify_dashboard_request(
        request: Request,
        x_rono_user_id: str = Header(...),
        x_rono_timestamp: str = Header(...),
        x_rono_signature: str = Header(...),
):
    if not DASHBOARD_API_SECRET:
        _reject(
            503,
            "Dashboard API authentication "
            "is not configured.",
        )

    try:
        user_id = int(x_rono_user_id)
        timestamp = int(x_rono_timestamp)

    except (TypeError, ValueError):
        _reject(
            401,
            "Invalid dashboard authentication headers.",
        )

    now = int(time.time())

    if abs(now - timestamp) > int(
        DASHBOARD_SIGNATURE_MAX_AGE
    ):
        _reject(
            401,
            "Dashboard request has expired.",
        )

    message = "\n".join([
        request.method.upper(),
        request.url.path,
        request.url.query,
        str(user_id),
        str(timestamp),
    ])

    expected = hmac.new(
        DASHBOARD_API_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(
        expected,
        str(x_rono_signature).strip().lower(),
    ):
        _reject(
            401,
            "Invalid dashboard request signature.",
        )

    return {
        "moodle_user_id": user_id,
    }


def authorize_course_staff(
        *,
        course_id,
        moodle_user_id
):
    matches = [
        user
        for user in course_users(course_id)
        if int(
            user["moodle_user_id"]
        ) == int(moodle_user_id)
    ]

    if len(matches) != 1:
        _reject(
            403,
            "User does not have access "
            "to this course.",
        )

    user = matches[0]

    if not (
        user["is_teacher"]
        or user["is_manager"]
    ):
        _reject(
            403,
            "Teacher or manager access required.",
        )

    return user
