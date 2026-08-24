"""AI-assisted diagnostic analysis of student quiz evidence."""

import json

from shared.ai_client import AIClient


class DiagnosticEngine:

    def __init__(self):
        self.ai = AIClient()

    def analyse(
            self,
            *,
            student_name,
            year_level,
            curriculum_code,
            attempts
    ):
        prompt = self._build_prompt(
            student_name=student_name,
            year_level=year_level,
            curriculum_code=curriculum_code,
            attempts=attempts
        )

        result = self.ai.generate(
            prompt
        )

        content = result["content"].strip()

        if content.startswith("```"):
            lines = content.splitlines()

            if lines:
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            content = "\n".join(lines).strip()

        analysis = json.loads(
            content
        )

        return {
            "analysis":
                analysis,

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
            student_name,
            year_level,
            curriculum_code,
            attempts
    ):
        evidence_json = json.dumps(
            attempts,
            ensure_ascii=False,
            indent=2
        )

        return f"""
You are an educational diagnostic tutor analysing
a student's mathematics quiz evidence.

STUDENT
Name: {student_name}
Year level: {year_level}
Curriculum code: {curriculum_code}

IMPORTANT RULES

1. Moodle marks and scores are evidence, but do not
   automatically assume every Moodle-marked incorrect
   answer proves a misconception.

2. Evaluate the mathematical meaning of the student's
   actual response.

3. If a response may be mathematically equivalent to
   the reference answer, classify it as
   POSSIBLE_GRADING_ISSUE rather than a learning gap.

4. One wrong response is not enough to confidently
   diagnose a persistent misconception.

5. Use repeated related evidence to increase diagnostic
   confidence.

6. If an earlier error becomes correct on a later
   attempt, recognise the improvement.

7. Group related incorrect responses into learning
   concerns. Do not create repetitive lessons for every
   individual question.

8. Do not change or recalculate Moodle's official grade.

9. Teaching must be appropriate for {year_level}.

10. For every genuine learning concern, teach the
    underlying idea rather than merely telling the
    student which answer was correct.

11. A mini-lesson must include:
    - a simple explanation;
    - one worked example;
    - one guided practice question with a hint;
    - one new independent practice question;
    - the answer and explanation for internal checking.

12. New practice questions must test the same concept
    but must not copy the original question.

13. Be careful with vocabulary errors versus conceptual
    errors.

14. Return ONLY valid JSON. No Markdown fences.

15. Never include a question classified CORRECT as
    evidence supporting a learning concern.

16. Correct questions may be used only as counter-evidence,
    strengths, or evidence that understanding is mixed.

17. Before treating a short-answer response as a learning
    concern, check whether the student's mathematics is
    actually valid even if wording/form differs from the
    reference answer.

18. A Moodle-marked incorrect response that demonstrates
    the correct mathematical value must not be used as
    evidence of conceptual failure.

19. Put questionable marking, alternate valid answers,
    ambiguous questions, or overly restrictive expected
    answers in grading_reviews.

20. Do not tell the student that a grading issue is their
    misconception.

21. The question_keys of each concern must contain only
    non-correct diagnostic candidates that actually support
    that concern.

22. If a question is placed in grading_reviews, that
    question MUST NOT appear in the question_keys of any
    learning concern and MUST NOT increase the confidence
    or remediation priority of a learning concern.

23. A grading-review question may be mentioned separately
    as an assessment-quality issue, but never as evidence
    that the student lacks the concept.

24. improved_evidence is deterministic longitudinal
    evidence. Treat those question keys as IMPROVED, not
    as current learning concerns.

25. A question in improved_evidence MUST NOT appear in
    the question_keys of a current learning concern unless
    later evidence shows the student became non-correct
    again.

26. persistent_evidence means Moodle recorded repeated
    non-correct performance. It does NOT automatically
    prove a persistent conceptual gap. Check semantic
    validity and grading issues first.

27. Give explicit positive recognition when a student
    corrected an earlier misunderstanding on a later
    attempt.

ALLOWED CLASSIFICATIONS

SUPPORTED_CONCERN
POSSIBLE_CONCERN
IMPROVED
PERSISTENT_GAP
POSSIBLE_GRADING_ISSUE
INSUFFICIENT_EVIDENCE

OUTPUT FORMAT

{{
  "student_summary": {{
    "overall_interpretation": "...",
    "strengths": ["..."],
    "improvements": ["..."]
  }},
  "concerns": [
    {{
      "title": "...",
      "classification": "SUPPORTED_CONCERN",
      "confidence": "low|medium|high",
      "question_keys": ["..."],
      "evidence": "...",
      "diagnosis": "...",
      "mini_lesson": "...",
      "worked_example": {{
        "problem": "...",
        "steps": ["...", "..."],
        "answer": "..."
      }},
      "guided_practice": {{
        "question": "...",
        "hint": "...",
        "answer": "..."
      }},
      "independent_practice": {{
        "question": "...",
        "answer": "...",
        "explanation": "..."
      }},
      "remediation_priority": "low|medium|high"
    }}
  ],
  "grading_reviews": [
    {{
      "question_key": "...",
      "classification": "POSSIBLE_GRADING_ISSUE",
      "reason": "...",
      "student_response": "...",
      "reference_response": "...",
      "recommendation": "..."
    }}
  ],
  "next_steps": ["..."]
}}

QUIZ EVIDENCE

{evidence_json}
""".strip()
