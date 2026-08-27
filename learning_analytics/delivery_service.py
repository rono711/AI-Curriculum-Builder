"""Deliver previously validated learning feedback."""

from pathlib import Path

from learning_analytics.database import (
    get_feedback_report,
    record_feedback_delivery,
    update_feedback_delivery,
    utc_now,
)
from learning_analytics.feedback_validator import (
    require_valid_student_feedback,
)
from learning_analytics.mail_sender import (
    FeedbackMailSender,
)
from learning_analytics.student_resolver import (
    MoodleStudentResolver,
)
from build_registry import (
    get_quiz_course_id,
)


ALLOWED_MODES = {
    "PREVIEW",
    "TEST",
    "LIVE",
}


class FeedbackDeliveryService:

    def _load_validated_report(
            self,
            *,
            moodle_user_id,
            moodle_quiz_id
    ):
        report = get_feedback_report(
            moodle_user_id=moodle_user_id,
            moodle_quiz_id=moodle_quiz_id
        )

        if report is None:
            raise RuntimeError(
                "No persisted feedback report exists."
            )

        if report.get("status") != "VALIDATED":
            raise RuntimeError(
                "Feedback report is not VALIDATED."
            )

        validation = report.get(
            "validation",
            {}
        )

        if validation.get("valid") is not True:
            raise RuntimeError(
                "Persisted feedback validation "
                "is not valid."
            )

        return report

    def preview(
            self,
            *,
            moodle_user_id,
            moodle_quiz_id,
            student_name,
            output_dir=
                "data/delivery_previews"
    ):
        report = self._load_validated_report(
            moodle_user_id=moodle_user_id,
            moodle_quiz_id=moodle_quiz_id
        )

        # Validate the persisted HTML again immediately
        # before producing a delivery artifact.
        validation = require_valid_student_feedback(
            report["student_html"],
            student_name=student_name,
            diagnostic=report["diagnostic"]
        )

        output_dir = Path(
            output_dir
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        filename = (
            f"report_{report['id']}_"
            f"user_{moodle_user_id}_"
            f"quiz_{moodle_quiz_id}_"
            "PREVIEW.html"
        )

        path = (
            output_dir
            / filename
        )

        path.write_text(
            report["student_html"],
            encoding="utf-8"
        )

        delivery_id = record_feedback_delivery(
            feedback_report_id=
                report["id"],
            recipient="PREVIEW_ONLY",
            delivery_mode="PREVIEW",
            status="PENDING"
        )

        update_feedback_delivery(
            delivery_id,
            status="COMPLETED"
        )

        return {
            "delivery_id":
                delivery_id,

            "report_id":
                report["id"],

            "mode":
                "PREVIEW",

            "path":
                str(path),

            "validation":
                validation,
        }

    def send_test(
            self,
            *,
            moodle_user_id,
            moodle_quiz_id,
            student_name
    ):
        """Send persisted feedback only to TEST mailbox."""

        report = self._load_validated_report(
            moodle_user_id=moodle_user_id,
            moodle_quiz_id=moodle_quiz_id
        )

        validation = (
            require_valid_student_feedback(
                report["student_html"],
                student_name=student_name,
                diagnostic=report["diagnostic"]
            )
        )

        sender = FeedbackMailSender()

        recipient = sender.test_email

        delivery_id = record_feedback_delivery(
            feedback_report_id=
                report["id"],
            recipient=recipient,
            delivery_mode="TEST",
            status="PENDING"
        )

        curriculum_code = (
            report.get("curriculum_code")
            or "Curriculum"
        )

        subject = (
            "[TEST] Rono's School Learning Feedback | "
            f"{curriculum_code}"
        )

        try:
            sent = sender.send_test(
                subject=subject,
                html=report["student_html"]
            )

            update_feedback_delivery(
                delivery_id,
                status="SENT",
                sent_at=utc_now()
            )

        except Exception as exc:
            update_feedback_delivery(
                delivery_id,
                status="FAILED",
                error_message=str(exc)
            )

            raise

        return {
            "delivery_id":
                delivery_id,

            "report_id":
                report["id"],

            "mode":
                "TEST",

            "recipient":
                sent["recipient"],

            "subject":
                sent["subject"],

            "validation":
                validation,
        }

    def resolve_live_delivery(
            self,
            *,
            moodle_user_id,
            moodle_quiz_id
    ):
        """Resolve LIVE routing without sending anything."""

        moodle_course_id = get_quiz_course_id(
            moodle_quiz_id
        )

        report = self._load_validated_report(
            moodle_user_id=moodle_user_id,
            moodle_quiz_id=moodle_quiz_id
        )

        if int(
            report["moodle_user_id"]
        ) != int(moodle_user_id):
            raise RuntimeError(
                "Report Moodle user does not match "
                "requested Moodle user."
            )

        student = MoodleStudentResolver().resolve(
            moodle_course_id=moodle_course_id,
            moodle_user_id=moodle_user_id
        )

        student_name = (
            student.get("firstname")
            or student["fullname"]
        )

        validation = require_valid_student_feedback(
            report["student_html"],
            student_name=student_name,
            diagnostic=report["diagnostic"]
        )

        sender = FeedbackMailSender()

        curriculum_code = (
            report.get("curriculum_code")
            or "Curriculum"
        )

        subject = (
            "Rono's School Learning Feedback | "
            f"{curriculum_code}"
        )

        return {
            "report_id":
                report["id"],

            "moodle_user_id":
                int(moodle_user_id),

            "moodle_course_id":
                int(moodle_course_id),

            "moodle_quiz_id":
                int(moodle_quiz_id),

            "student_name":
                student["fullname"],

            "recipient":
                student["email"],

            "curriculum_code":
                curriculum_code,

            "subject":
                subject,

            "validation":
                validation,

            "live_enabled":
                sender.live_enabled,

            "would_send":
                True,

            "actually_sent":
                False,
        }

    def send_live(
            self,
            *,
            moodle_user_id,
            moodle_quiz_id
    ):
        """Send validated feedback to Moodle-resolved student."""

        routing = self.resolve_live_delivery(
            moodle_user_id=moodle_user_id,
            moodle_quiz_id=moodle_quiz_id
        )

        sender = FeedbackMailSender()

        # Hard configuration kill switch.
        # This check happens before an audit PENDING row
        # and before any SMTP connection is opened.
        if not sender.live_enabled:
            raise RuntimeError(
                "LIVE feedback delivery is disabled."
            )

        report = self._load_validated_report(
            moodle_user_id=moodle_user_id,
            moodle_quiz_id=moodle_quiz_id
        )

        if int(report["id"]) != int(
            routing["report_id"]
        ):
            raise RuntimeError(
                "Resolved report changed during "
                "LIVE delivery preparation."
            )

        delivery_id = record_feedback_delivery(
            feedback_report_id=
                report["id"],
            recipient=
                routing["recipient"],
            delivery_mode="LIVE",
            status="PENDING"
        )

        try:
            sent = sender.send_live(
                recipient=
                    routing["recipient"],
                subject=
                    routing["subject"],
                html=
                    report["student_html"]
            )

            update_feedback_delivery(
                delivery_id,
                status="SENT",
                sent_at=utc_now()
            )

        except Exception as exc:
            update_feedback_delivery(
                delivery_id,
                status="FAILED",
                error_message=str(exc)
            )

            raise

        return {
            "delivery_id":
                delivery_id,

            "report_id":
                report["id"],

            "mode":
                "LIVE",

            "moodle_user_id":
                routing["moodle_user_id"],

            "moodle_course_id":
                routing["moodle_course_id"],

            "moodle_quiz_id":
                routing["moodle_quiz_id"],

            "student_name":
                routing["student_name"],

            "recipient":
                sent["recipient"],

            "curriculum_code":
                routing["curriculum_code"],

            "subject":
                sent["subject"],

            "validation":
                routing["validation"],

            "actually_sent":
                True,
        }
