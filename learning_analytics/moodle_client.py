"""Retrieve quiz attempt data from Moodle."""

import requests

from learning_analytics.config import (
    MOODLE_ANALYTICS_TOKEN,
    MOODLE_ANALYTICS_URL,
    validate_moodle_config,
)


class MoodleAnalyticsClient:

    def __init__(self):

        validate_moodle_config()

        self.endpoint = (
            MOODLE_ANALYTICS_URL
            + "/webservice/rest/server.php"
        )

        self.token = MOODLE_ANALYTICS_TOKEN

    def call(
            self,
            function,
            **params
    ):

        payload = {
            "wstoken":
                self.token,

            "wsfunction":
                function,

            "moodlewsrestformat":
                "json",

            **params,
        }

        response = requests.get(
            self.endpoint,
            params=payload,
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        if (
            isinstance(data, dict)
            and "exception" in data
        ):
            raise RuntimeError(
                f"{function}: "
                f"{data.get('errorcode')} - "
                f"{data.get('message')}"
            )

        return data

    def get_enrolled_users(
            self,
            course_id
    ):

        return self.call(
            "core_enrol_get_enrolled_users",
            courseid=int(course_id)
        )

    def get_user_quiz_attempts(
            self,
            quiz_id,
            user_id,
            status="finished"
    ):

        return self.call(
            "mod_quiz_get_user_quiz_attempts",
            quizid=int(quiz_id),
            userid=int(user_id),
            status=status,
            includepreviews=0
        )

    def get_attempt_review(
            self,
            attempt_id
    ):

        return self.call(
            "mod_quiz_get_attempt_review",
            attemptid=int(attempt_id)
        )

    def get_quiz_questions(
            self,
            quiz_id
    ):

        return self.call(
            "local_rono_publisher_get_quiz_questions",
            quizid=int(quiz_id)
        )


    def set_quiz_attempt_limit(
            self,
            *,
            quiz_id,
            user_id,
            attempts
    ):
        """Set the effective Moodle Quiz attempt limit for one user."""

        attempts = int(attempts)

        if attempts < 1 or attempts > 3:
            raise ValueError(
                "Quiz attempt limit must be between 1 and 3."
            )

        return self.call(
            "local_rono_publisher_set_quiz_attempt_limit",
            quizid=int(quiz_id),
            userid=int(user_id),
            attempts=attempts
        )


    def verify_attempt_owner(
            self,
            *,
            quiz_id,
            user_id,
            attempt_id
    ):
        """Verify that a Moodle attempt belongs to the supplied user."""

        data = self.get_user_quiz_attempts(
            quiz_id=quiz_id,
            user_id=user_id,
            status="all"
        )

        attempts = data.get(
            "attempts",
            []
        )

        matches = [
            attempt
            for attempt in attempts
            if int(
                attempt.get(
                    "id",
                    0
                )
            ) == int(attempt_id)
        ]

        if len(matches) != 1:
            raise RuntimeError(
                f"Moodle attempt {attempt_id} does not "
                f"belong to Moodle user {user_id} "
                f"for quiz {quiz_id}."
            )

        return matches[0]
