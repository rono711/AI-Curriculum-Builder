import unittest
from unittest.mock import patch

from learning_analytics.attempt_finalizer import (
    classify_attempt_histories,
)
from learning_analytics.processing_service import (
    LearningAnalyticsProcessingService,
)


def row(attempt, question, correct):
    return {
        "moodle_attempt_id": attempt,
        "question_key": question,
        "mark": 1 if correct else 0,
        "max_mark": 1,
    }


class Moodle:

    def __init__(self):
        self.calls = []

    def set_quiz_attempt_limit(
        self, *, quiz_id, user_id, attempts
    ):
        self.calls.append(attempts)
        return {"overrideid": 999}


class Tests(unittest.TestCase):

    def test_mastery_attempt_one(self):
        result = classify_attempt_histories([
            row(101, "Q1", True),
            row(101, "Q2", True),
        ])
        self.assertTrue(result["mastered"])
        self.assertEqual(result["attempt_count"], 1)

    def test_no_mastery_attempt_one(self):
        result = classify_attempt_histories([
            row(101, "Q1", True),
            row(101, "Q2", False),
        ])
        self.assertFalse(result["mastered"])
        self.assertFalse(result["cycle_complete"])

    def test_mastery_attempt_two(self):
        result = classify_attempt_histories([
            row(101, "Q1", True),
            row(101, "Q2", False),
            row(102, "Q1", True),
            row(102, "Q2", True),
        ])
        self.assertTrue(result["mastered"])
        self.assertEqual(result["attempt_count"], 2)

    def test_max_three_attempts(self):
        result = classify_attempt_histories([
            row(101, "Q1", False),
            row(102, "Q1", False),
            row(103, "Q1", False),
        ])
        self.assertFalse(result["mastered"])
        self.assertTrue(result["cycle_complete"])
        self.assertEqual(
            result["completion_reason"],
            "MAX_ATTEMPTS_REACHED",
        )

    def test_mastery_limit_one(self):
        moodle = Moodle()
        service = LearningAnalyticsProcessingService(
            moodle_client=moodle
        )

        with patch(
            "learning_analytics.processing_service."
            "save_quiz_attempt_control"
        ):
            service._apply_attempt_control(
                moodle_user_id=1009,
                moodle_quiz_id=100,
                finalization={
                    "mastered": True,
                    "attempt_count": 1,
                },
            )

        self.assertEqual(moodle.calls, [1])

    def test_mastery_limit_two(self):
        moodle = Moodle()
        service = LearningAnalyticsProcessingService(
            moodle_client=moodle
        )

        with patch(
            "learning_analytics.processing_service."
            "save_quiz_attempt_control"
        ):
            service._apply_attempt_control(
                moodle_user_id=1009,
                moodle_quiz_id=100,
                finalization={
                    "mastered": True,
                    "attempt_count": 2,
                },
            )

        self.assertEqual(moodle.calls, [2])

    def test_nonmastery_no_block(self):
        moodle = Moodle()
        service = LearningAnalyticsProcessingService(
            moodle_client=moodle
        )

        result = service._apply_attempt_control(
            moodle_user_id=1009,
            moodle_quiz_id=100,
            finalization={
                "mastered": False,
                "attempt_count": 1,
            },
        )

        self.assertIsNone(result)
        self.assertEqual(moodle.calls, [])


if __name__ == "__main__":
    unittest.main()
