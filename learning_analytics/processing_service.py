"""Run the complete validated learning-analytics workflow."""

from learning_analytics.attempt_finalizer import (
    finalize_attempt_cycle,
)
from learning_analytics.attempt_processor import (
    normalize_attempt,
)
from learning_analytics.database import (
    get_attempt_processing_state,
    get_feedback_report,
    get_student_quiz_responses,
    save_attempt,
    save_feedback_report,
    save_question_responses,
)
from learning_analytics.feedback_renderer import (
    render_student_feedback,
    render_teacher_feedback,
)
from learning_analytics.feedback_validator import (
    require_valid_student_feedback,
)
from learning_analytics.orchestrator import (
    LearningAnalyticsOrchestrator,
)
from learning_analytics.moodle_client import (
    MoodleAnalyticsClient,
)


class LearningAnalyticsProcessingService:

    def __init__(self, moodle_client=None):
        self.moodle_client = (
            moodle_client
            if moodle_client is not None
            else MoodleAnalyticsClient()
        )

    def _apply_attempt_control(
            self,
            *,
            moodle_user_id,
            moodle_quiz_id,
            finalization
    ):
        """Close further Quiz attempts after early mastery."""

        if (
            not finalization["mastered"]
            or finalization["attempt_count"] >= 3
        ):
            return None

        return self.moodle_client.set_quiz_attempt_limit(
            quiz_id=moodle_quiz_id,
            user_id=moodle_user_id,
            attempts=finalization["attempt_count"]
        )

    def process_review(
            self,
            *,
            review,
            moodle_user_id,
            student_name,
            year_level
    ):
        """Process one Moodle review through validated persistence."""

        normalized = normalize_attempt(
            review,
            user_id=moodle_user_id
        )

        attempt = normalized["attempt"]
        responses = normalized["responses"]

        processing_state = get_attempt_processing_state(
            moodle_user_id=moodle_user_id,
            moodle_quiz_id=attempt["moodle_quiz_id"],
            moodle_attempt_id=attempt["moodle_attempt_id"]
        )

        if processing_state["fully_processed"]:
            report = get_feedback_report(
                moodle_user_id=moodle_user_id,
                moodle_quiz_id=attempt["moodle_quiz_id"],
                latest_moodle_attempt_id=
                    attempt["moodle_attempt_id"]
            )

            return {
                "status":
                    "ALREADY_PROCESSED",

                "report_id":
                    processing_state["report_id"],

                "moodle_user_id":
                    int(moodle_user_id),

                "moodle_quiz_id":
                    int(
                        attempt["moodle_quiz_id"]
                    ),

                "moodle_attempt_id":
                    int(
                        attempt["moodle_attempt_id"]
                    ),

                "curriculum_code":
                    attempt["curriculum_code"],

                "attempt_count":
                    report["attempt_count"],

                "validation":
                    report["validation"],

                "student_html":
                    report["student_html"],

                "teacher_html":
                    report["teacher_html"],

                "actually_processed":
                    False,
            }

        if int(
            attempt["moodle_user_id"]
        ) != int(moodle_user_id):
            raise RuntimeError(
                "Normalized attempt user does not "
                "match requested Moodle user."
            )

        save_attempt(
            attempt
        )

        save_question_responses(
            responses
        )

        moodle_quiz_id = int(
            attempt["moodle_quiz_id"]
        )

        curriculum_code = attempt[
            "curriculum_code"
        ]

        rows = get_student_quiz_responses(
            moodle_user_id=moodle_user_id,
            moodle_quiz_id=moodle_quiz_id
        )

        analysis_result = (
            LearningAnalyticsOrchestrator()
            .analyse(
                student_name=student_name,
                year_level=year_level,
                curriculum_code=curriculum_code,
                rows=rows
            )
        )

        diagnostic = analysis_result[
            "diagnostic"
        ]

        evidence_packet = analysis_result[
            "evidence_packet"
        ]

        semantic_reviews = analysis_result[
            "semantic_reviews"
        ]

        student_html = render_student_feedback(
            student_name=student_name,
            diagnostic=diagnostic,
            evidence_packet=evidence_packet
        )

        teacher_html = render_teacher_feedback(
            student_name=student_name,
            diagnostic=diagnostic,
            evidence_packet=evidence_packet,
            semantic_reviews=semantic_reviews
        )

        student_validation = (
            require_valid_student_feedback(
                student_html,
                student_name=student_name,
                diagnostic=diagnostic
            )
        )

        report_validation = {
            "valid":
                (
                    analysis_result[
                        "diagnostic_validation"
                    ]["valid"]
                    and student_validation["valid"]
                ),

            "diagnostic":
                analysis_result[
                    "diagnostic_validation"
                ],

            "student_feedback":
                student_validation,
        }

        if not report_validation["valid"]:
            raise RuntimeError(
                "Combined feedback report validation failed."
            )

        attempt_ids = {
            int(
                row["moodle_attempt_id"]
            )
            for row in rows
        }

        report_id = save_feedback_report({
            "moodle_user_id":
                int(moodle_user_id),

            "moodle_quiz_id":
                moodle_quiz_id,

            "latest_moodle_attempt_id":
                max(attempt_ids),

            "attempt_count":
                len(attempt_ids),

            "curriculum_code":
                curriculum_code,

            "lesson_package_id":
                attempt.get(
                    "lesson_package_id"
                ),

            "diagnostic":
                diagnostic,

            "semantic_reviews":
                semantic_reviews,

            "validation":
                report_validation,

            "student_html":
                student_html,

            "teacher_html":
                teacher_html,

            "model":
                analysis_result.get(
                    "model"
                ),

            "total_tokens":
                analysis_result.get(
                    "total_tokens"
                ),

            "status":
                "VALIDATED",
        })

        finalization = finalize_attempt_cycle(
            moodle_user_id=moodle_user_id,
            moodle_quiz_id=moodle_quiz_id,
            curriculum_code=curriculum_code,
            rows=rows
        )

        attempt_control = self._apply_attempt_control(
            moodle_user_id=moodle_user_id,
            moodle_quiz_id=moodle_quiz_id,
            finalization=finalization
        )

        return {
            "report_id":
                report_id,

            "moodle_user_id":
                int(moodle_user_id),

            "moodle_quiz_id":
                moodle_quiz_id,

            "curriculum_code":
                curriculum_code,

            "attempt_count":
                len(attempt_ids),

            "diagnostic":
                diagnostic,

            "semantic_reviews":
                semantic_reviews,

            "validation":
                report_validation,

            "finalization":
                finalization,

            "attempt_control":
                attempt_control,

            "student_html":
                student_html,

            "teacher_html":
                teacher_html,
        }
