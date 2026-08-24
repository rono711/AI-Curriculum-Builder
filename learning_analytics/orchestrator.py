"""Coordinate longitudinal, semantic and diagnostic analysis."""

from learning_analytics.diagnostic_engine import (
    DiagnosticEngine,
)
from learning_analytics.diagnostic_validator import (
    validate_diagnostic,
)
from learning_analytics.evidence_selector import (
    build_diagnostic_evidence,
)
from learning_analytics.semantic_review_engine import (
    SemanticReviewEngine,
)
from learning_analytics.semantic_review_validator import (
    validate_semantic_review,
)


SEMANTIC_REVIEW_TYPES = {
    "shortanswer",
}


class LearningAnalyticsOrchestrator:

    def __init__(self):
        self.semantic = SemanticReviewEngine()
        self.diagnostic = DiagnosticEngine()

    def analyse(
            self,
            *,
            student_name,
            year_level,
            curriculum_code,
            rows
    ):
        # First pass establishes longitudinal state.
        initial = build_diagnostic_evidence(
            rows
        )

        semantic_results = []
        semantic_review_keys = set()

        for candidate in initial[
            "diagnostic_candidates"
        ]:
            question_type = str(
                candidate.get(
                    "question_type",
                    ""
                )
            ).lower()

            if question_type not in \
                    SEMANTIC_REVIEW_TYPES:
                continue

            result = self.semantic.review(
                year_level=year_level,
                curriculum_code=curriculum_code,
                question_key=candidate[
                    "question_key"
                ],
                question_text=candidate[
                    "question_text"
                ],
                student_response=candidate[
                    "student_response"
                ],
                reference_response=candidate[
                    "correct_response"
                ]
            )

            review = result["review"]

            validation = (
                validate_semantic_review(
                    review,
                    expected_question_key=
                        candidate["question_key"]
                )
            )

            if not validation["valid"]:
                raise RuntimeError(
                    "Semantic review validation failed: "
                    + "; ".join(
                        validation["errors"]
                    )
                )

            semantic_results.append(
                review
            )

            if review["outcome"] in {
                "VALID_EQUIVALENT",
                "AMBIGUOUS",
                "REVIEW_REQUIRED",
            }:
                semantic_review_keys.add(
                    candidate[
                        "question_key"
                    ]
                )

        # Rebuild packet with semantic-review questions
        # removed from diagnostic candidates.
        packet = build_diagnostic_evidence(
            rows,
            semantic_review_keys=
                semantic_review_keys
        )

        result = self.diagnostic.analyse(
            student_name=student_name,
            year_level=year_level,
            curriculum_code=curriculum_code,
            attempts=packet
        )

        analysis = result["analysis"]

        validation = validate_diagnostic(
            analysis,
            packet
        )

        if not validation["valid"]:
            raise RuntimeError(
                "Diagnostic validation failed: "
                + "; ".join(
                    validation["errors"]
                )
            )

        return {
            "evidence_packet":
                packet,

            "semantic_reviews":
                semantic_results,

            "diagnostic":
                analysis,

            "diagnostic_validation":
                validation,

            "model":
                result["model"],

            "total_tokens":
                result["total_tokens"],
        }
