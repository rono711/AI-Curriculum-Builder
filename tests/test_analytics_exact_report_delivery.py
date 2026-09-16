"""Regression tests for exact-report Analytics delivery."""

import unittest
from unittest.mock import patch

import learning_analytics.worker as worker


class FakeDelivery:

    def __init__(self):
        self.calls = []

    def send_live(
            self,
            *,
            moodle_user_id,
            moodle_quiz_id,
            feedback_report_id=None
    ):
        self.calls.append({
            "user": moodle_user_id,
            "quiz": moodle_quiz_id,
            "report": feedback_report_id,
        })

        return {
            "report_id": feedback_report_id,
            "actually_sent": True,
            "already_delivered": False,
            "delivery_ids": [feedback_report_id],
        }


class ExactReportDeliveryTests(unittest.TestCase):

    def test_processed_attempt_uses_exact_report(self):
        delivery = FakeDelivery()

        with patch.object(
            worker,
            "FEEDBACK_EMAIL_MODE",
            "LIVE",
        ):
            worker.deliver_processed_attempt(
                delivery=delivery,
                processed_item={
                    "moodle_attempt_id": 501,
                    "moodle_user_id": 1009,
                    "student_name": "Student One",
                    "result": {
                        "report_id": 101
                    },
                },
                moodle_quiz_id=999,
            )

        self.assertEqual(
            delivery.calls[0]["report"],
            101,
        )

    def test_three_reports_get_three_deliveries(self):

        items = [
            {
                "moodle_attempt_id": 501,
                "moodle_user_id": 1009,
                "student_name": "Student One",
                "curriculum_code": "TEST_E1",
                "result": {"report_id": 101},
            },
            {
                "moodle_attempt_id": 502,
                "moodle_user_id": 1009,
                "student_name": "Student One",
                "curriculum_code": "TEST_E1",
                "result": {"report_id": 102},
            },
            {
                "moodle_attempt_id": 503,
                "moodle_user_id": 1009,
                "student_name": "Student One",
                "curriculum_code": "TEST_E1",
                "result": {"report_id": 103},
            },
        ]

        class Detector:

            def process_new(
                    self,
                    *,
                    moodle_quiz_id
            ):
                return {
                    "new_attempts_found": 3,
                    "processed_count": 3,
                    "results": items,
                    "scan_summary": {},
                }

        delivery = FakeDelivery()

        with patch.object(
            worker,
            "get_active_analytics_quizzes",
            return_value=[
                {
                    "moodle_quiz_id": 999,
                    "curriculum_code": "TEST_E1",
                }
            ],
        ), patch.object(
            worker,
            "FinishedAttemptDetector",
            return_value=Detector(),
        ), patch.object(
            worker,
            "FeedbackDeliveryService",
            return_value=delivery,
        ), patch.object(
            worker,
            "FEEDBACK_EMAIL_MODE",
            "LIVE",
        ):
            summary = worker.run_cycle()

        self.assertEqual(
            summary["new_attempts"],
            3,
        )
        self.assertEqual(
            summary["processed"],
            3,
        )
        self.assertEqual(
            summary["delivered"],
            3,
        )

        self.assertEqual(
            [
                call["report"]
                for call in delivery.calls
            ],
            [101, 102, 103],
        )

    def test_missing_report_id_is_rejected(self):
        delivery = FakeDelivery()

        with patch.object(
            worker,
            "FEEDBACK_EMAIL_MODE",
            "LIVE",
        ):
            with self.assertRaisesRegex(
                RuntimeError,
                "no feedback report ID",
            ):
                worker.deliver_processed_attempt(
                    delivery=delivery,
                    processed_item={
                        "moodle_attempt_id": 501,
                        "moodle_user_id": 1009,
                        "student_name": "Student One",
                        "result": {},
                    },
                    moodle_quiz_id=999,
                )


if __name__ == "__main__":
    unittest.main()
