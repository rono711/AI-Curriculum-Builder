"""Validate AI diagnostic output against deterministic evidence."""

ALLOWED_CLASSIFICATIONS = {
    "SUPPORTED_CONCERN",
    "POSSIBLE_CONCERN",
    "IMPROVED",
    "PERSISTENT_GAP",
    "POSSIBLE_GRADING_ISSUE",
    "INSUFFICIENT_EVIDENCE",
}

ALLOWED_CONFIDENCE = {
    "low",
    "medium",
    "high",
}


def validate_diagnostic(
        analysis,
        evidence_packet
):
    correct_keys = {
        row["question_key"]
        for row in evidence_packet[
            "correct_evidence"
        ]
    }

    candidate_keys = {
        row["question_key"]
        for row in evidence_packet[
            "diagnostic_candidates"
        ]
    }

    improved_keys = {
        row["question_key"]
        for row in evidence_packet.get(
            "improved_evidence",
            []
        )
    }

    semantic_review_keys = {
        row["question_key"]
        for row in evidence_packet.get(
            "semantic_review_evidence",
            []
        )
    }

    all_keys = (
        correct_keys
        | candidate_keys
        | improved_keys
        | semantic_review_keys
    )

    errors = []

    grading_keys = set()

    for review in analysis.get(
        "grading_reviews",
        []
    ):
        key = review.get(
            "question_key"
        )

        classification = review.get(
            "classification"
        )

        if key not in all_keys:
            errors.append(
                f"Unknown grading-review key: {key}"
            )

        if classification != \
                "POSSIBLE_GRADING_ISSUE":
            errors.append(
                f"Invalid grading classification "
                f"for {key}: {classification}"
            )

        grading_keys.add(
            key
        )

    for concern in analysis.get(
        "concerns",
        []
    ):
        classification = concern.get(
            "classification"
        )

        confidence = concern.get(
            "confidence"
        )

        keys = concern.get(
            "question_keys",
            []
        )

        if classification not in \
                ALLOWED_CLASSIFICATIONS:
            errors.append(
                f"Invalid concern classification: "
                f"{classification}"
            )

        if confidence not in \
                ALLOWED_CONFIDENCE:
            errors.append(
                f"Invalid confidence: {confidence}"
            )

        for key in keys:

            if key not in all_keys:
                errors.append(
                    f"Unknown concern key: {key}"
                )

            if key in correct_keys:
                errors.append(
                    f"Correct question used as "
                    f"concern evidence: {key}"
                )

            if key not in candidate_keys:
                errors.append(
                    f"Non-candidate question used "
                    f"as concern evidence: {key}"
                )

            if key in grading_keys:
                errors.append(
                    f"Grading-review question also "
                    f"used as concern evidence: {key}"
                )

            if key in improved_keys:
                errors.append(
                    f"Improved question used as "
                    f"current concern evidence: {key}"
                )

            if key in semantic_review_keys:
                errors.append(
                    f"Semantic-review question used as "
                    f"current concern evidence: {key}"
                )

    return {
        "valid":
            not errors,

        "errors":
            errors,

        "correct_keys":
            sorted(correct_keys),

        "candidate_keys":
            sorted(candidate_keys),

        "grading_review_keys":
            sorted(grading_keys),

        "semantic_review_keys":
            sorted(semantic_review_keys),
    }
