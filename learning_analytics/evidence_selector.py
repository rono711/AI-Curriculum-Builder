"""Prepare longitudinal evidence for diagnostic analysis."""


def performance_ratio(row):
    maximum = float(
        row.get("max_mark") or 0
    )

    if maximum <= 0:
        return 0.0

    return (
        float(row.get("mark") or 0)
        / maximum
    )


def classify_response(row):
    ratio = performance_ratio(row)

    if ratio >= 1.0:
        return "CORRECT"

    if ratio > 0.0:
        return "PARTIAL"

    return "INCORRECT"


def build_diagnostic_evidence(
        rows,
        semantic_review_keys=None
):
    semantic_review_keys = set(
        semantic_review_keys or []
    )

    histories = {}

    for source in rows:
        item = dict(source)

        item["evidence_classification"] = (
            classify_response(item)
        )

        histories.setdefault(
            item["question_key"],
            []
        ).append(item)

    current_correct = []
    diagnostic_candidates = []
    improved = []
    persistent = []
    semantic_review = []

    for question_key, history in histories.items():

        history.sort(
            key=lambda item: (
                int(
                    item.get(
                        "moodle_attempt_id"
                    )
                    or 0
                )
            )
        )

        latest = history[-1]

        previous = history[:-1]

        latest_class = latest[
            "evidence_classification"
        ]

        if question_key in semantic_review_keys:
            semantic_review.append({
                "question_key":
                    question_key,

                "outcome":
                    "SEMANTIC_REVIEW_REQUIRED",

                "history":
                    history,
            })

            continue

        previous_noncorrect = any(
            item["evidence_classification"]
            != "CORRECT"
            for item in previous
        )

        all_noncorrect = all(
            item["evidence_classification"]
            != "CORRECT"
            for item in history
        )

        if (
            latest_class == "CORRECT"
            and previous_noncorrect
        ):
            improved.append({
                "question_key":
                    question_key,

                "outcome":
                    "IMPROVED",

                "history":
                    history,
            })

            current_correct.append(
                latest
            )

            continue

        if latest_class == "CORRECT":
            current_correct.append(
                latest
            )

            continue

        diagnostic_candidates.append(
            latest
        )

        if (
            len(history) >= 2
            and all_noncorrect
        ):
            persistent.append({
                "question_key":
                    question_key,

                "outcome":
                    "REPEATED_NONCORRECT",

                "history":
                    history,
            })

    return {
        "correct_evidence":
            current_correct,

        "diagnostic_candidates":
            diagnostic_candidates,

        "improved_evidence":
            improved,

        "persistent_evidence":
            persistent,

        "semantic_review_evidence":
            semantic_review,

        "question_histories":
            histories,
    }
