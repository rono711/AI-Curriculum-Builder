"""Discover finished Moodle attempts requiring analytics processing."""

from learning_analytics.attempt_processor import (
    quiz_identity,
)
from learning_analytics.database import (
    get_attempt_processing_state,
    get_feedback_report,
    get_stored_quiz_attempts,
    mark_attempt_reset,
    get_active_quiz_attempt_control,
    mark_quiz_attempt_control_cleared,
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

    def reconcile_user_attempts(
            self,
            *,
            moodle_quiz_id,
            moodle_user_id,
            moodle_attempts
    ):
        """Mark analytics attempts RESET when they no longer exist in Moodle."""

        moodle_ids = {
            int(attempt["id"])
            for attempt in moodle_attempts
            if attempt.get("id")
        }

        stored = get_stored_quiz_attempts(
            moodle_user_id=moodle_user_id,
            moodle_quiz_id=moodle_quiz_id,
            lifecycle_status="ACTIVE"
        )

        reset_attempts = []

        for attempt in stored:
            attempt_id = int(
                attempt["moodle_attempt_id"]
            )

            if attempt_id in moodle_ids:
                continue

            result = mark_attempt_reset(
                moodle_attempt_id=attempt_id,
                reason="MISSING_FROM_MOODLE"
            )

            if result and result.get("changed"):
                reset_attempts.append(result)

        override_clear = None

        if reset_attempts:
            control = get_active_quiz_attempt_control(
                moodle_user_id=moodle_user_id,
                moodle_quiz_id=moodle_quiz_id
            )

            if control is not None:
                override_clear = (
                    self.client.clear_quiz_attempt_limit(
                        quiz_id=moodle_quiz_id,
                        user_id=moodle_user_id
                    )
                )

                mark_quiz_attempt_control_cleared(
                    moodle_user_id=moodle_user_id,
                    moodle_quiz_id=moodle_quiz_id
                )

        return {
            "reset_attempts": reset_attempts,
            "reset_count": len(reset_attempts),
            "override_clear": override_clear,
        }


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
        reconciliations = []

        for user in users:

            user_id = int(
                user.get("id", 0)
            )

            if not user_id:
                continue

            data = self.client.get_user_quiz_attempts(
                quiz_id=moodle_quiz_id,
                user_id=user_id,
                status="all"
            )

            all_attempts = data.get(
                "attempts",
                []
            )

            reconciliation = self.reconcile_user_attempts(
                moodle_quiz_id=moodle_quiz_id,
                moodle_user_id=user_id,
                moodle_attempts=all_attempts
            )

            reset_attempts = reconciliation[
                "reset_attempts"
            ]

            if reconciliation["reset_count"]:
                reconciliations.append({
                    "moodle_user_id": user_id,
                    "reset_attempt_ids": [
                        int(item["moodle_attempt_id"])
                        for item in reset_attempts
                    ],
                    "override_cleared": (
                        reconciliation["override_clear"]
                        is not None
                    ),
                })

            attempts = [
                attempt
                for attempt in all_attempts
                if attempt.get("state") == "finished"
            ]

            if not attempts and not reset_attempts:
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

            "reconciliations":
                reconciliations,

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
