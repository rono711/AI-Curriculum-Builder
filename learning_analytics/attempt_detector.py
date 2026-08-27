"""Discover finished Moodle attempts requiring analytics processing."""

from learning_analytics.attempt_processor import (
    quiz_identity,
)
from learning_analytics.database import (
    get_attempt_processing_state,
    get_feedback_report,
)
from learning_analytics.moodle_client import (
    MoodleAnalyticsClient,
)
from learning_analytics.curriculum_resolver import (
    resolve_curriculum_identity,
)
from learning_analytics.processing_service import (
    LearningAnalyticsProcessingService,
)


class FinishedAttemptDetector:

    def __init__(self):
        self.client = MoodleAnalyticsClient()

    def scan_quiz(
            self,
            *,
            moodle_quiz_id
    ):
        """Discover finished attempts without processing them."""

        identity = quiz_identity(
            moodle_quiz_id
        )

        course_id = identity[
            "moodle_course_id"
        ]

        users = self.client.get_enrolled_users(
            course_id
        )

        discovered = []

        for user in users:

            user_id = int(
                user.get("id", 0)
            )

            if not user_id:
                continue

            data = self.client.get_user_quiz_attempts(
                quiz_id=moodle_quiz_id,
                user_id=user_id,
                status="finished"
            )

            attempts = data.get(
                "attempts",
                []
            )

            if not attempts:
                continue

            latest_report = get_feedback_report(
                moodle_user_id=user_id,
                moodle_quiz_id=moodle_quiz_id
            )

            latest_report_attempt = (
                int(
                    latest_report[
                        "latest_moodle_attempt_id"
                    ]
                )
                if latest_report
                else None
            )

            for attempt in attempts:

                attempt_id = int(
                    attempt["id"]
                )

                state = get_attempt_processing_state(
                    moodle_user_id=user_id,
                    moodle_quiz_id=moodle_quiz_id,
                    moodle_attempt_id=attempt_id
                )

                if state["fully_processed"]:
                    detector_state = "PROCESSED"

                elif (
                    latest_report_attempt is not None
                    and latest_report_attempt > attempt_id
                ):
                    detector_state = "SUPERSEDED"

                else:
                    detector_state = "NEW"

                discovered.append({
                    "moodle_attempt_id":
                        attempt_id,

                    "moodle_user_id":
                        user_id,

                    "student_name":
                        user.get(
                            "fullname",
                            ""
                        ),

                    "moodle_quiz_id":
                        int(moodle_quiz_id),

                    "moodle_course_id":
                        int(course_id),

                    "curriculum_code":
                        identity[
                            "curriculum_code"
                        ],

                    "attempt_number":
                        attempt.get(
                            "attempt"
                        ),

                    "state":
                        detector_state,

                    "report_id":
                        state[
                            "report_id"
                        ],

                    "report_validated":
                        state[
                            "report_validated"
                        ],

                    "remediation_complete":
                        state[
                            "remediation_complete"
                        ],
                })

        discovered.sort(
            key=lambda item: (
                item["moodle_user_id"],
                item["moodle_attempt_id"],
            )
        )

        return {
            "moodle_quiz_id":
                int(moodle_quiz_id),

            "moodle_course_id":
                int(course_id),

            "curriculum_code":
                identity[
                    "curriculum_code"
                ],

            "attempts":
                discovered,

            "summary":
                {
                    state: sum(
                        item["state"] == state
                        for item in discovered
                    )
                    for state in [
                        "PROCESSED",
                        "SUPERSEDED",
                        "NEW",
                    ]
                },
        }

    def process_new(
            self,
            *,
            moodle_quiz_id
    ):
        """Process only attempts currently classified as NEW."""

        scan = self.scan_quiz(
            moodle_quiz_id=moodle_quiz_id
        )

        new_attempts = [
            item
            for item in scan["attempts"]
            if item["state"] == "NEW"
        ]

        results = []

        for item in new_attempts:

            self.client.verify_attempt_owner(
                quiz_id=moodle_quiz_id,
                user_id=item["moodle_user_id"],
                attempt_id=item["moodle_attempt_id"]
            )

            review = self.client.get_attempt_review(
                item["moodle_attempt_id"]
            )

            curriculum = resolve_curriculum_identity(
                item["curriculum_code"]
            )

            student_name = str(
                item["student_name"]
            ).strip().split(
                " ",
                1
            )[0]

            processed = (
                LearningAnalyticsProcessingService()
                .process_review(
                    review=review,
                    moodle_user_id=
                        item["moodle_user_id"],
                    student_name=
                        student_name,
                    year_level=
                        curriculum["year_level"]
                )
            )

            results.append({
                "moodle_attempt_id":
                    item["moodle_attempt_id"],

                "moodle_user_id":
                    item["moodle_user_id"],

                "student_name":
                    item["student_name"],

                "curriculum_code":
                    item["curriculum_code"],

                "result":
                    processed,
            })

        return {
            "moodle_quiz_id":
                int(moodle_quiz_id),

            "new_attempts_found":
                len(new_attempts),

            "processed_count":
                len(results),

            "results":
                results,

            "scan_summary":
                scan["summary"],
        }
