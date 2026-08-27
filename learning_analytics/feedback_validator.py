"""Validate student-facing feedback before delivery."""

import re

from bs4 import BeautifulSoup


FORBIDDEN_PATTERNS = [
    r"\bCB_\d",
    r"\bVALID_EQUIVALENT\b",
    r"\bPOSSIBLE_GRADING",
    r"\bsemantic review\b",
    r"\bgrading review\b",
    r"\bgrading issue\b",
    r"\bmarking error\b",
    r"\bmarking issue\b",
    r"\bmarking anomaly\b",
    r"\bflagged answer\b",
    r"\bassessment-quality\b",
]


TEACHER_DIRECTED_PATTERNS = [
    r"\breinforce\b",
    r"\bteach\b",
    r"\bask the student\b",
    r"\ballow mathematically\b",
    r"\bcheck whether short-answer\b",
]


def validate_student_feedback(
        html,
        *,
        student_name,
        diagnostic
):
    errors = []

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    text = soup.get_text(
        " ",
        strip=True
    )

    lowered = text.lower()

    if not text:
        errors.append(
            "Student feedback is empty."
        )

    if not soup.select_one(
        ".student-feedback"
    ):
        errors.append(
            "Student feedback root is missing."
        )

    greeting = (
        "hi "
        + str(student_name).strip().lower()
    )

    if greeting not in lowered:
        errors.append(
            "Student greeting is missing."
        )

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        ):
            errors.append(
                "Forbidden student-facing content: "
                + pattern
            )

    for pattern in TEACHER_DIRECTED_PATTERNS:
        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        ):
            errors.append(
                "Teacher-directed language exposed: "
                + pattern
            )

    third_person_patterns = [
        rf"\b{re.escape(student_name)}\s+shows\b",
        rf"\b{re.escape(student_name)}\s+needs\b",
        rf"\b{re.escape(student_name)}\s+understands\b",
        r"\bthe student shows\b",
        r"\bthe student needs\b",
    ]

    for pattern in third_person_patterns:
        if re.search(
            pattern,
            text,
            flags=re.IGNORECASE
        ):
            errors.append(
                "Third-person student summary found: "
                + pattern
            )

    practice_blocks = soup.select(
        ".practice"
    )

    for index, block in enumerate(
        practice_blocks,
        start=1
    ):
        block_text = block.get_text(
            " ",
            strip=True
        )

        if "Answer:" in block_text:
            errors.append(
                f"Practice block {index} "
                "exposes an answer."
            )

        if "Explanation:" in block_text:
            errors.append(
                f"Practice block {index} "
                "exposes an explanation."
            )

    concerns = diagnostic.get(
        "concerns",
        []
    )

    rendered_concerns = soup.select(
        ".learning-concern"
    )

    if concerns:
        if len(rendered_concerns) != len(
            concerns
        ):
            errors.append(
                "Rendered concern count does not "
                "match validated concern count."
            )

        for index, block in enumerate(
            rendered_concerns,
            start=1
        ):
            if not block.select_one(
                ".worked-example"
            ):
                errors.append(
                    f"Concern {index} has no "
                    "worked example."
                )

            blocks = block.select(
                ".practice"
            )

            if len(blocks) < 2:
                errors.append(
                    f"Concern {index} does not have "
                    "both guided and independent practice."
                )

    else:
        if rendered_concerns:
            errors.append(
                "Student feedback contains remediation "
                "despite no validated concerns."
            )

    return {
        "valid":
            not errors,

        "errors":
            errors,

        "validated_concerns":
            len(concerns),

        "rendered_concerns":
            len(rendered_concerns),

        "practice_blocks":
            len(practice_blocks),
    }


def require_valid_student_feedback(
        html,
        *,
        student_name,
        diagnostic
):
    result = validate_student_feedback(
        html,
        student_name=student_name,
        diagnostic=diagnostic
    )

    if not result["valid"]:
        raise RuntimeError(
            "Student feedback validation failed: "
            + "; ".join(
                result["errors"]
            )
        )

    return result
