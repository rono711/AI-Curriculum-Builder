"""Validate semantic-review AI output."""

ALLOWED_OUTCOMES = {
    "VALID_EQUIVALENT",
    "INVALID",
    "AMBIGUOUS",
    "REVIEW_REQUIRED",
}


def validate_semantic_review(
        review,
        *,
        expected_question_key
):
    errors = []

    question_key = review.get(
        "question_key"
    )

    outcome = review.get(
        "outcome"
    )

    mathematically_valid = review.get(
        "mathematically_valid"
    )

    matches_requested_format = review.get(
        "matches_requested_format"
    )

    if question_key != expected_question_key:
        errors.append(
            "Semantic review question key mismatch: "
            f"expected {expected_question_key}, "
            f"received {question_key}"
        )

    if outcome not in ALLOWED_OUTCOMES:
        errors.append(
            f"Invalid semantic outcome: {outcome}"
        )

    if not isinstance(
        mathematically_valid,
        bool
    ):
        errors.append(
            "mathematically_valid must be boolean"
        )

    if not isinstance(
        matches_requested_format,
        bool
    ):
        errors.append(
            "matches_requested_format must be boolean"
        )

    if (
        outcome == "VALID_EQUIVALENT"
        and mathematically_valid is not True
    ):
        errors.append(
            "VALID_EQUIVALENT requires "
            "mathematically_valid=true"
        )

    if (
        outcome == "INVALID"
        and mathematically_valid is not False
    ):
        errors.append(
            "INVALID requires "
            "mathematically_valid=false"
        )

    if not review.get("reason"):
        errors.append(
            "Semantic review has no reason"
        )

    if not review.get("recommendation"):
        errors.append(
            "Semantic review has no recommendation"
        )

    return {
        "valid":
            not errors,

        "errors":
            errors,

        "question_key":
            question_key,

        "outcome":
            outcome,
    }
