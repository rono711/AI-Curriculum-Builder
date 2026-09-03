"""Finalize longitudinal quiz evidence after the attempt cycle."""

from collections import defaultdict

from learning_analytics.config import (
    MAX_QUIZ_ATTEMPTS,
)
from learning_analytics.curriculum_resolver import (
    resolve_curriculum_identity,
)
from learning_analytics.database import (
    get_feedback_report,
    save_final_quiz_pool_item,
    save_remediation_evidence,
)


MAX_ATTEMPTS = MAX_QUIZ_ATTEMPTS


def _is_correct(row):
    mark = float(row.get("mark") or 0)
    max_mark = float(row.get("max_mark") or 0)

    return (
        max_mark > 0
        and mark >= max_mark
    )


def _history_state(history):
    latest = history[-1]

    if _is_correct(latest):
        if any(
            not _is_correct(row)
            for row in history[:-1]
        ):
            return "IMPROVED"

        return "CURRENT_CORRECT"

    if len(history) >= MAX_ATTEMPTS:
        return "UNRESOLVED_AFTER_MAX_ATTEMPTS"

    return "CURRENT_NONCORRECT"


def classify_attempt_histories(
        rows,
        *,
        semantic_keys=None,
        semantic_mastered_keys=None
):
    """Classify question histories without writing to the database."""

    semantic_keys = set(
        semantic_keys
        or []
    )

    semantic_mastered_keys = set(
        semantic_mastered_keys
        or []
    )

    histories = defaultdict(list)
    attempt_ids = set()

    for source in rows:
        row = dict(source)

        attempt_id = int(
            row["moodle_attempt_id"]
        )

        attempt_ids.add(
            attempt_id
        )

        histories[
            row["question_key"]
        ].append(row)

    for history in histories.values():
        history.sort(
            key=lambda item:
                int(
                    item["moodle_attempt_id"]
                )
        )

    attempt_count = len(
        attempt_ids
    )

    latest_attempt_id = max(
        attempt_ids
    )

    # Mastery must cover every question observed in the quiz
    # history, not only questions appearing in the latest attempt.
    #
    # If a previously unresolved question disappears from a later
    # attempt, its most recent available evidence must remain in the
    # mastery denominator. Otherwise a partial later attempt could
    # incorrectly produce MASTERED.
    latest_rows = {
        question_key: history[-1]
        for question_key, history
        in histories.items()
    }

    latest_mastery = {}

    for question_key, row in latest_rows.items():
        latest_mastery[
            question_key
        ] = (
            _is_correct(row)
            or question_key
            in semantic_mastered_keys
        )

    mastered = (
        bool(latest_mastery)
        and all(
            latest_mastery.values()
        )
    )

    cycle_complete = (
        mastered
        or attempt_count >= MAX_ATTEMPTS
    )

    if mastered:
        completion_reason = "MASTERED"

    elif attempt_count >= MAX_ATTEMPTS:
        completion_reason = "MAX_ATTEMPTS_REACHED"

    else:
        completion_reason = "IN_PROGRESS"

    classifications = {}

    for question_key, history in histories.items():

        if question_key in semantic_keys:
            state = "SEMANTIC_REVIEW"

        else:
            state = _history_state(
                history
            )

        classifications[
            question_key
        ] = {
            "state":
                state,

            "history":
                history,

            "attempts_observed":
                len(history),

            "promotable":
                (
                    not mastered
                    and attempt_count
                    >= MAX_ATTEMPTS
                    and state
                    == "UNRESOLVED_AFTER_MAX_ATTEMPTS"
                ),
        }

    return {
        "attempt_count":
            attempt_count,

        "latest_attempt_id":
            latest_attempt_id,

        "mastered":
            mastered,

        "completion_reason":
            completion_reason,

        "cycle_complete":
            cycle_complete,

        "latest_mastery":
            latest_mastery,

        "classifications":
            classifications,
    }


def finalize_attempt_cycle(
        *,
        moodle_user_id,
        moodle_quiz_id,
        curriculum_code,
        rows
):
    """Persist longitudinal evidence and final-pool promotions."""

    if not rows:
        raise RuntimeError(
            "No question-response evidence supplied."
        )

    identity = resolve_curriculum_identity(
        curriculum_code
    )

    report = get_feedback_report(
        moodle_user_id=moodle_user_id,
        moodle_quiz_id=moodle_quiz_id
    )

    source_report_id = (
        report["id"]
        if report
        else None
    )

    semantic_keys = set()
    semantic_mastered_keys = set()

    if report:
        semantic_reviews = report.get(
            "semantic_reviews",
            []
        )

        semantic_keys = {
            item.get("question_key")
            for item in semantic_reviews
            if item.get("outcome") in {
                "VALID_EQUIVALENT",
                "AMBIGUOUS",
                "REVIEW_REQUIRED",
            }
        }

        semantic_mastered_keys = {
            item.get("question_key")
            for item in semantic_reviews
            if item.get("outcome")
            == "VALID_EQUIVALENT"
        }

    concern_by_key = {}

    if report:
        for concern in report[
            "diagnostic"
        ].get(
            "concerns",
            []
        ):
            for key in concern.get(
                "question_keys",
                []
            ):
                concern_by_key[
                    key
                ] = concern

    classified = classify_attempt_histories(
        rows,
        semantic_keys=semantic_keys,
        semantic_mastered_keys=semantic_mastered_keys
    )

    attempt_count = classified[
        "attempt_count"
    ]

    classifications = classified[
        "classifications"
    ]

    attempt_ids = {
        int(
            dict(row)[
                "moodle_attempt_id"
            ]
        )
        for row in rows
    }

    latest_attempt_id = max(
        attempt_ids
    )

    evidence_rows = []
    promoted = []

    for question_key, classified_item in sorted(
        classifications.items()
    ):
        history = classified_item[
            "history"
        ]

        latest = history[-1]

        state = classified_item[
            "state"
        ]

        concern = concern_by_key.get(
            question_key,
            {}
        )

        should_promote = classified_item[
            "promotable"
        ]

        evidence = {
            "moodle_user_id":
                int(moodle_user_id),

            "moodle_quiz_id":
                int(moodle_quiz_id),

            "parent_code":
                identity["parent_code"],

            "curriculum_code":
                curriculum_code,

            "lesson_package_id":
                (
                    report.get("lesson_package_id")
                    if report
                    else None
                ),

            "question_key":
                question_key,

            "first_attempt_id":
                int(
                    history[0][
                        "moodle_attempt_id"
                    ]
                ),

            "latest_attempt_id":
                int(
                    latest[
                        "moodle_attempt_id"
                    ]
                ),

            "attempts_observed":
                len(history),

            "evidence_state":
                state,

            "confidence":
                concern.get("confidence"),

            "question_text":
                latest.get("question_text"),

            "latest_student_response":
                latest.get("student_response"),

            "correct_response":
                latest.get("correct_response"),

            "diagnosis":
                concern.get("diagnosis"),

            "concept_name":
                concern.get("title"),

            "source_report_id":
                source_report_id,

            "promoted_to_final_pool":
                should_promote,
        }

        save_remediation_evidence(
            evidence
        )

        evidence_rows.append(
            evidence
        )

        if should_promote:
            pool_item = {
                "moodle_user_id":
                    int(moodle_user_id),

                "parent_code":
                    identity["parent_code"],

                "curriculum_code":
                    curriculum_code,

                "source_question_key":
                    question_key,

                "concept_name":
                    concern.get("title"),

                "diagnosis":
                    concern.get("diagnosis"),

                "priority":
                    "HIGH",

                "source_attempt_count":
                    attempt_count,

                "source_question_text":
                    latest.get("question_text"),

                "source_student_response":
                    latest.get(
                        "student_response"
                    ),

                "source_correct_response":
                    latest.get(
                        "correct_response"
                    ),

                "generation_instruction":
                    (
                        "Generate a new analogous question "
                        "assessing the same underlying "
                        "concept and misconception pattern. "
                        "Do not copy the source question, "
                        "numbers, wording, answer choices "
                        "or exact response. Test transfer "
                        "of learning in a fresh context."
                    ),

                "status":
                    "ACTIVE",
            }

            save_final_quiz_pool_item(
                pool_item
            )

            promoted.append(
                pool_item
            )

    return {
        "moodle_user_id":
            int(moodle_user_id),

        "moodle_quiz_id":
            int(moodle_quiz_id),

        "parent_code":
            identity["parent_code"],

        "curriculum_code":
            curriculum_code,

        "attempt_count":
            attempt_count,

        "latest_attempt_id":
            latest_attempt_id,

        "mastered":
            classified["mastered"],

        "completion_reason":
            classified["completion_reason"],

        "cycle_complete":
            classified["cycle_complete"],

        "evidence":
            evidence_rows,

        "promoted":
            promoted,
    }
