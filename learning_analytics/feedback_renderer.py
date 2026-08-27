"""Render validated analytics into student and teacher feedback."""

from html import escape


def _text(value):
    if value is None:
        return ""

    return str(value).strip()


def _paragraph(value):
    value = _text(value)

    if not value:
        return ""

    return (
        "<p>"
        + escape(value)
        + "</p>"
    )


def _list(items):
    clean = [
        _text(item)
        for item in (items or [])
        if _text(item)
    ]

    if not clean:
        return ""

    body = "".join(
        "<li>"
        + escape(item)
        + "</li>"
        for item in clean
    )

    return "<ul>" + body + "</ul>"


def _section(title, body):
    if not body:
        return ""

    return (
        "<section>"
        "<h2>"
        + escape(title)
        + "</h2>"
        + body
        + "</section>"
    )


def _practice_block(
        title,
        practice,
        *,
        show_answer=False
):
    practice = practice or {}

    question = _text(
        practice.get("question")
    )

    if not question:
        return ""

    parts = [
        "<div class=\"practice\">",
        "<h3>",
        escape(title),
        "</h3>",
        "<p><strong>Question:</strong> ",
        escape(question),
        "</p>",
    ]

    hint = _text(
        practice.get("hint")
    )

    if hint:
        parts.extend([
            "<p><strong>Hint:</strong> ",
            escape(hint),
            "</p>",
        ])

    if show_answer:
        answer = _text(
            practice.get("answer")
        )

        explanation = _text(
            practice.get("explanation")
        )

        if answer:
            parts.extend([
                "<p><strong>Answer:</strong> ",
                escape(answer),
                "</p>",
            ])

        if explanation:
            parts.extend([
                "<p><strong>Explanation:</strong> ",
                escape(explanation),
                "</p>",
            ])

    parts.append("</div>")

    return "".join(parts)


def _worked_example(example):
    example = example or {}

    problem = _text(
        example.get("problem")
    )

    if not problem:
        return ""

    steps = example.get(
        "steps",
        []
    )

    answer = _text(
        example.get("answer")
    )

    parts = [
        "<div class=\"worked-example\">",
        "<h3>Worked example</h3>",
        "<p><strong>Problem:</strong> ",
        escape(problem),
        "</p>",
    ]

    if steps:
        parts.append("<ol>")

        for step in steps:
            if _text(step):
                parts.extend([
                    "<li>",
                    escape(_text(step)),
                    "</li>",
                ])

        parts.append("</ol>")

    if answer:
        parts.extend([
            "<p><strong>Answer:</strong> ",
            escape(answer),
            "</p>",
        ])

    parts.append("</div>")

    return "".join(parts)


def render_student_feedback(
        *,
        student_name,
        diagnostic,
        evidence_packet
):
    """Create student-facing HTML without grading-review details."""

    summary = diagnostic.get(
        "student_summary",
        {}
    )

    concerns = diagnostic.get(
        "concerns",
        []
    )

    improved = evidence_packet.get(
        "improved_evidence",
        []
    )

    parts = [
        "<article class=\"student-feedback\">",
        "<h1>Your learning feedback</h1>",
        "<p>Hi ",
        escape(_text(student_name)),
        ",</p>",
    ]

    interpretation = _text(
        summary.get(
            "overall_interpretation"
        )
    )

    if interpretation:
        parts.append(
            _paragraph(
                interpretation
            )
        )

    strengths = summary.get(
        "strengths",
        []
    )

    if strengths:
        parts.append(
            _section(
                "What you did well",
                _list(strengths)
            )
        )

    if improved:
        improvement_items = []

        for item in improved:
            history = item.get(
                "history",
                []
            )

            if history:
                latest = history[-1]

                question = _text(
                    latest.get(
                        "question_text"
                    )
                )

                if question:
                    improvement_items.append(
                        "You improved on: "
                        + question
                    )
                    continue

            improvement_items.append(
                "You corrected an earlier "
                "question on a later attempt."
            )

        parts.append(
            _section(
                "Your progress",
                _list(
                    improvement_items
                )
            )
        )

    if concerns:
        parts.append(
            "<section>"
            "<h2>Ideas to strengthen</h2>"
        )

        for concern in concerns:
            parts.append(
                _render_student_concern(
                    concern
                )
            )

        parts.append(
            "</section>"
        )

    else:
        parts.append(
            _section(
                "Your next challenge",
                _paragraph(
                    "Your current evidence does not "
                    "show a validated learning gap. "
                    "Keep explaining your thinking "
                    "and trying different ways to "
                    "represent what you know."
                )
            )
        )

    next_steps = diagnostic.get(
        "next_steps",
        []
    )

    if next_steps:
        parts.append(
            _section(
                "What to do next",
                _list(next_steps)
            )
        )

    parts.extend([
        "<p>Keep building on what you know.</p>",
        "</article>",
    ])

    return "".join(parts)


def _render_student_concern(
        concern
):
    title = _text(
        concern.get("title")
    )

    mini_lesson = _text(
        concern.get("mini_lesson")
    )

    parts = [
        "<div class=\"learning-concern\">",
        "<h3>",
        escape(title),
        "</h3>",
    ]

    if mini_lesson:
        parts.append(
            _paragraph(
                mini_lesson
            )
        )

    parts.append(
        _worked_example(
            concern.get(
                "worked_example"
            )
        )
    )

    parts.append(
        _practice_block(
            "Try this with a hint",
            concern.get(
                "guided_practice"
            ),
            show_answer=False
        )
    )

    # Deliberately hide the answer from the student.
    parts.append(
        _practice_block(
            "Now try this yourself",
            concern.get(
                "independent_practice"
            ),
            show_answer=False
        )
    )

    parts.append("</div>")

    return "".join(parts)


def render_teacher_feedback(
        *,
        student_name,
        diagnostic,
        evidence_packet,
        semantic_reviews
):
    """Create teacher-facing review with assessment details."""

    parts = [
        "<article class=\"teacher-feedback\">",
        "<h1>Learning analytics review</h1>",
        "<p><strong>Student:</strong> ",
        escape(_text(student_name)),
        "</p>",
    ]

    concerns = diagnostic.get(
        "concerns",
        []
    )

    if concerns:
        parts.append(
            "<section>"
            "<h2>Validated learning concerns</h2>"
        )

        for concern in concerns:
            parts.extend([
                "<div class=\"teacher-concern\">",
                "<h3>",
                escape(
                    _text(
                        concern.get(
                            "title"
                        )
                    )
                ),
                "</h3>",
                "<p><strong>Classification:</strong> ",
                escape(
                    _text(
                        concern.get(
                            "classification"
                        )
                    )
                ),
                "</p>",
                "<p><strong>Confidence:</strong> ",
                escape(
                    _text(
                        concern.get(
                            "confidence"
                        )
                    )
                ),
                "</p>",
            ])

            diagnosis = _text(
                concern.get(
                    "diagnosis"
                )
            )

            if diagnosis:
                parts.append(
                    _paragraph(
                        diagnosis
                    )
                )

            keys = concern.get(
                "question_keys",
                []
            )

            if keys:
                parts.append(
                    _list(keys)
                )

            parts.append(
                _practice_block(
                    "Independent practice",
                    concern.get(
                        "independent_practice"
                    ),
                    show_answer=True
                )
            )

            parts.append("</div>")

        parts.append("</section>")

    else:
        parts.append(
            _section(
                "Validated learning concerns",
                _paragraph(
                    "No current validated learning "
                    "concerns were identified."
                )
            )
        )

    improved = evidence_packet.get(
        "improved_evidence",
        []
    )

    if improved:
        parts.append(
            _section(
                "Improved evidence",
                _list([
                    item.get(
                        "question_key"
                    )
                    for item in improved
                ])
            )
        )

    if semantic_reviews:
        parts.append(
            "<section>"
            "<h2>Assessment / semantic review</h2>"
        )

        for review in semantic_reviews:
            parts.extend([
                "<div class=\"semantic-review\">",
                "<h3>",
                escape(
                    _text(
                        review.get(
                            "question_key"
                        )
                    )
                ),
                "</h3>",
                "<p><strong>Outcome:</strong> ",
                escape(
                    _text(
                        review.get(
                            "outcome"
                        )
                    )
                ),
                "</p>",
            ])

            reason = _text(
                review.get("reason")
            )

            recommendation = _text(
                review.get(
                    "recommendation"
                )
            )

            if reason:
                parts.append(
                    _paragraph(reason)
                )

            if recommendation:
                parts.extend([
                    "<p><strong>Recommendation:</strong> ",
                    escape(recommendation),
                    "</p>",
                ])

            parts.append("</div>")

        parts.append("</section>")

    parts.append("</article>")

    return "".join(parts)
