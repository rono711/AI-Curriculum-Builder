"""Resolve a Moodle student identity from course enrollment."""

from learning_analytics.moodle_client import (
    MoodleAnalyticsClient,
)


class MoodleStudentResolver:

    def __init__(self):
        self.client = MoodleAnalyticsClient()

    def resolve(
            self,
            *,
            moodle_course_id,
            moodle_user_id
    ):
        users = self.client.get_enrolled_users(
            moodle_course_id
        )

        matches = [
            user
            for user in users
            if int(
                user.get(
                    "id",
                    0
                )
            ) == int(moodle_user_id)
        ]

        if not matches:
            raise RuntimeError(
                "Moodle user "
                f"{moodle_user_id} is not enrolled "
                f"in course {moodle_course_id}."
            )

        if len(matches) != 1:
            raise RuntimeError(
                "Expected exactly one Moodle user "
                f"{moodle_user_id}; found "
                f"{len(matches)}."
            )

        user = matches[0]

        email = str(
            user.get(
                "email",
                ""
            )
        ).strip()

        fullname = str(
            user.get(
                "fullname",
                ""
            )
        ).strip()

        firstname = str(
            user.get(
                "firstname",
                ""
            )
        ).strip()

        lastname = str(
            user.get(
                "lastname",
                ""
            )
        ).strip()

        username = str(
            user.get(
                "username",
                ""
            )
        ).strip()

        if not fullname:
            raise RuntimeError(
                f"Moodle user {moodle_user_id} "
                "has no full name."
            )

        if not email:
            raise RuntimeError(
                f"Moodle user {moodle_user_id} "
                "has no accessible email address."
            )

        if "@" not in email:
            raise RuntimeError(
                f"Moodle user {moodle_user_id} "
                "has an invalid email address."
            )

        return {
            "moodle_user_id":
                int(moodle_user_id),

            "moodle_course_id":
                int(moodle_course_id),

            "fullname":
                fullname,

            "firstname":
                firstname,

            "lastname":
                lastname,

            "username":
                username,

            "email":
                email,
        }
