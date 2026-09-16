"""Moodle course-role helpers for Learning Analytics."""

from learning_analytics.moodle_client import (
    MoodleAnalyticsClient,
)


STUDENT_ROLES = {"student"}

TEACHER_ROLES = {
    "teacher",
    "editingteacher",
}

MANAGER_ROLES = {"manager"}


def role_names(user):
    return {
        str(
            role.get("shortname") or ""
        ).strip().lower()
        for role in user.get("roles", [])
        if role.get("shortname")
    }


def course_users(
        course_id,
        *,
        moodle_client=None
):
    client = (
        moodle_client
        or MoodleAnalyticsClient()
    )

    result = []

    for user in client.get_enrolled_users(
        int(course_id)
    ):
        roles = role_names(user)

        result.append({
            "moodle_user_id":
                int(user["id"]),

            "fullname":
                str(
                    user.get("fullname")
                    or ""
                ).strip(),

            "firstname":
                str(
                    user.get("firstname")
                    or ""
                ).strip(),

            "email":
                str(
                    user.get("email")
                    or ""
                ).strip(),

            "roles":
                sorted(roles),

            "is_student":
                bool(roles & STUDENT_ROLES),

            "is_teacher":
                bool(roles & TEACHER_ROLES),

            "is_manager":
                bool(roles & MANAGER_ROLES),
        })

    return result


def course_students(
        course_id,
        *,
        moodle_client=None
):
    return [
        user
        for user in course_users(
            course_id,
            moodle_client=moodle_client,
        )
        if user["is_student"]
    ]


def course_staff(
        course_id,
        *,
        moodle_client=None
):
    return [
        user
        for user in course_users(
            course_id,
            moodle_client=moodle_client,
        )
        if (
            user["is_teacher"]
            or user["is_manager"]
        )
    ]
