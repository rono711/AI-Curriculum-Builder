"""Regression tests for numeric GIFT short-answer normalization."""

import unittest

from quiz_engine.quiz_runner import QuizRunner


class QuizShortAnswerNormalizationTests(unittest.TestCase):

    def test_integer_numeral_variants(self):
        cases = {
            "415 602": {"415 602", "415602", "415,602"},
            "1,234": {"1,234", "1234", "1 234"},
            "-1,250": {"-1,250", "-1250", "-1 250"},
        }

        for answer, expected in cases.items():
            result = set(
                QuizRunner._numeric_shortanswer_variants(answer)
            )
            self.assertTrue(expected.issubset(result))

    def test_non_integer_answers_remain_unchanged(self):
        answers = [
            "12.5",
            "1/4",
            "place value",
            "Year 3",
            "AC9M3N01",
            "60 004, 60 040, 60 400",
            "13 hundreds, 7 tens and 5 ones",
            "3 x 4 = 12",
        ]

        for answer in answers:
            self.assertEqual(
                QuizRunner._numeric_shortanswer_variants(answer),
                [answer],
            )

    def test_arshil_numeral_regression(self):
        gift = (
            '::SA1::Write the numeral for '
            '"four hundred and fifteen thousand, '
            'six hundred and two". {\n'
            '=415 602\n'
            '}'
        )

        result = (
            QuizRunner._expand_numeric_shortanswer_variants(gift)
        )

        self.assertIn("=415 602", result)
        self.assertIn("=415602", result)
        self.assertIn("=415,602", result)

        QuizRunner._validate_gift(result)

    def test_numeric_multiple_choice_is_not_modified(self):
        gift = (
            "::Q1::Which numeral is correct? {\n"
            "=415 602\n"
            "~451 602\n"
            "~415 620\n"
            "}"
        )

        result = (
            QuizRunner._expand_numeric_shortanswer_variants(gift)
        )

        self.assertEqual(result, gift)

    def test_matching_question_is_not_modified(self):
        gift = (
            "::M1::Match the numbers. {\n"
            "=415 602 -> four hundred and fifteen thousand\n"
            "=20 000 -> twenty thousand\n"
            "}"
        )

        result = (
            QuizRunner._expand_numeric_shortanswer_variants(gift)
        )

        self.assertEqual(result, gift)

    def test_text_shortanswer_is_not_modified(self):
        gift = (
            "::SA1::What is the place value word? {\n"
            "=hundreds\n"
            "}"
        )

        result = (
            QuizRunner._expand_numeric_shortanswer_variants(gift)
        )

        self.assertEqual(result, gift)

    def test_traceable_shortanswer_is_supported(self):
        gift = (
            "::CB_000999_001_SA001::Write the numeral. {\n"
            "=1,234\n"
            "}"
        )

        result = (
            QuizRunner._expand_numeric_shortanswer_variants(gift)
        )

        self.assertIn("=1,234", result)
        self.assertIn("=1234", result)
        self.assertIn("=1 234", result)

        QuizRunner._validate_gift(result)


if __name__ == "__main__":
    unittest.main()
