"""Regression tests for Analytics publication readiness."""

import unittest
from unittest.mock import patch

import build_registry


class FakeCursor:

    def __init__(self, value):
        self.value = value

    def fetchone(self):
        return self.value


class FakeConnection:

    def __init__(
            self,
            *,
            record=None,
            question_count=0
    ):
        self.record = record
        self.question_count = question_count

    def execute(self, sql, params=()):
        normalized = " ".join(
            sql.split()
        ).lower()

        if (
            "from elaboration_builds"
            in normalized
        ):
            return FakeCursor(
                self.record
            )

        if (
            "from quiz_questions"
            in normalized
        ):
            return FakeCursor(
                (self.question_count,)
            )

        raise AssertionError(
            "Unexpected SQL: " + normalized
        )

    def __enter__(self):
        return self

    def __exit__(
            self,
            exc_type,
            exc_value,
            traceback
    ):
        return False


class AnalyticsPublicationReadinessTests(
        unittest.TestCase
):

    def setUp(self):
        self.record = {
            "id": 999,
            "curriculum_code": "TEST_E1",
            "lesson_package_id": "LP_TEST_001",
        }

    def validate(
            self,
            *,
            course=48,
            quiz=100,
            cmid=1114,
            question_count=15
    ):
        connection = FakeConnection(
            record=self.record,
            question_count=question_count,
        )

        with patch.object(
            build_registry,
            "initialize_registry",
            return_value=None,
        ), patch.object(
            build_registry,
            "get_connection",
            return_value=connection,
        ):
            return (
                build_registry
                .validate_analytics_publication_readiness(
                    record_id=999,
                    moodle_course_id=course,
                    moodle_quiz_id=quiz,
                    moodle_quiz_cmid=cmid,
                )
            )

    def test_complete_quiz_is_ready(self):
        result = self.validate()

        self.assertTrue(
            result["analytics_ready"]
        )

        self.assertEqual(
            result[
                "registered_question_count"
            ],
            15,
        )

    def test_missing_course_is_rejected(self):
        with self.assertRaisesRegex(
            RuntimeError,
            "MISSING_COURSE_ID",
        ):
            self.validate(
                course=None
            )

    def test_missing_quiz_is_rejected(self):
        with self.assertRaisesRegex(
            RuntimeError,
            "MISSING_QUIZ_ID",
        ):
            self.validate(
                quiz=None
            )

    def test_missing_quiz_cmid_is_rejected(self):
        with self.assertRaisesRegex(
            RuntimeError,
            "MISSING_QUIZ_CMID",
        ):
            self.validate(
                cmid=None
            )

    def test_missing_questions_is_rejected(self):
        with self.assertRaisesRegex(
            RuntimeError,
            "NO_REGISTERED_QUESTIONS",
        ):
            self.validate(
                question_count=0
            )

    def test_reused_quiz_identity_is_allowed(self):
        result = self.validate(
            question_count=15
        )

        self.assertEqual(
            result["moodle_quiz_id"],
            100,
        )

        self.assertTrue(
            result["analytics_ready"]
        )

    def test_missing_registry_record_is_rejected(self):
        connection = FakeConnection(
            record=None,
            question_count=15,
        )

        with patch.object(
            build_registry,
            "initialize_registry",
            return_value=None,
        ), patch.object(
            build_registry,
            "get_connection",
            return_value=connection,
        ):
            with self.assertRaisesRegex(
                ValueError,
                "does not exist",
            ):
                build_registry.validate_analytics_publication_readiness(
                    record_id=999,
                    moodle_course_id=48,
                    moodle_quiz_id=100,
                    moodle_quiz_cmid=1114,
                )


if __name__ == "__main__":
    unittest.main()
