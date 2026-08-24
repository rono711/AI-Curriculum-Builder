"""Review potentially valid answers rejected by Moodle."""

import json

from shared.ai_client import AIClient


ALLOWED_OUTCOMES = {
    "VALID_EQUIVALENT",
    "INVALID",
    "AMBIGUOUS",
    "REVIEW_REQUIRED",
}


class SemanticReviewEngine:

    def __init__(self):
        self.ai = AIClient()

    def review(
            self,
            *,
            year_level,
            curriculum_code,
            question_key,
            question_text,
            student_response,
            reference_response
    ):
        prompt = self._build_prompt(
            year_level=year_level,
            curriculum_code=curriculum_code,
            question_key=question_key,
            question_text=question_text,
            student_response=student_response,
            reference_response=reference_response
        )

        result = self.ai.generate(prompt)

        content = result["content"].strip()

        if content.startswith("```"):
            lines = content.splitlines()
            lines = lines[1:]

            if (
                lines
                and lines[-1].strip() == "```"
            ):
                lines = lines[:-1]

            content = "\n".join(lines).strip()

        review = json.loads(content)

        outcome = review.get("outcome")

        if outcome not in ALLOWED_OUTCOMES:
            raise RuntimeError(
                f"Invalid semantic outcome: {outcome}"
            )

        return {
            "review":
                review,

            "model":
                result["model"],

            "prompt_tokens":
                result["prompt_tokens"],

            "completion_tokens":
                result["completion_tokens"],

            "total_tokens":
                result["total_tokens"],
        }

    def _build_prompt(
            self,
            *,
            year_level,
            curriculum_code,
            question_key,
            question_text,
            student_response,
            reference_response
    ):
        return f"""
You are reviewing a student's mathematics answer that
Moodle marked non-correct.

Your ONLY job is to determine whether the student's
actual mathematical response is equivalent to, compatible
with, or genuinely different from the expected answer.

Do NOT diagnose the student.
Do NOT write a lesson.
Do NOT change the Moodle grade.
Do NOT infer a misconception.

Student year level: {year_level}
Curriculum code: {curriculum_code}
Question key: {question_key}

Question:
{question_text}

Student response:
{student_response}

Reference response:
{reference_response}

Allowed outcomes:

VALID_EQUIVALENT
- The student's mathematics is valid and expresses the
  same mathematical value/meaning, even if its wording,
  notation, grouping, or form differs.

INVALID
- The student's response is mathematically different
  from the required answer.

AMBIGUOUS
- The question or response is too ambiguous to decide
  confidently.

REVIEW_REQUIRED
- There is a plausible issue requiring human assessment
  review.

Important:
A response may be mathematically correct but still fail
to follow a specifically requested representation.
Distinguish mathematical validity from compliance with
the requested format.

Return ONLY valid JSON:

{{
  "question_key": "{question_key}",
  "outcome": "VALID_EQUIVALENT",
  "mathematically_valid": true,
  "matches_requested_format": false,
  "reason": "...",
  "recommendation": "..."
}}
""".strip()
