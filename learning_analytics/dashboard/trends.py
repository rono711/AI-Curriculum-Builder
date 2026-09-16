"""Historical difficulty trends for dashboard."""

from datetime import datetime, timedelta, timezone

from learning_analytics.dashboard.topics import (
    question_difficulty,
)


def parse_datetime(value):
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.fromisoformat(
            str(value).replace(
                "Z",
                "+00:00"
            )
        )

    if dt.tzinfo is None:
        dt = dt.replace(
            tzinfo=timezone.utc
        )

    return dt


def classify_trend(change):
    if change <= -5:
        return "IMPROVING"

    if change >= 5:
        return "WORSENING"

    return "STABLE"


def compare_question_periods(
        course_id,
        *,
        current_from,
        current_to
):
    current_from = parse_datetime(
        current_from
    )

    current_to = parse_datetime(
        current_to
    )

    duration = (
        current_to
        - current_from
    )

    previous_to = (
        current_from
        - timedelta(seconds=1)
    )

    previous_from = (
        previous_to
        - duration
    )

    current = question_difficulty(
        course_id,
        date_from=current_from.isoformat(),
        date_to=current_to.isoformat(),
    )

    previous = question_difficulty(
        course_id,
        date_from=previous_from.isoformat(),
        date_to=previous_to.isoformat(),
    )

    current_map = {
        (
            int(row["moodle_quiz_id"]),
            str(row["question_key"]),
        ): row
        for row in current
    }

    previous_map = {
        (
            int(row["moodle_quiz_id"]),
            str(row["question_key"]),
        ): row
        for row in previous
    }

    keys = (
        set(current_map)
        | set(previous_map)
    )

    result = []

    for key in keys:
        now = current_map.get(key)
        before = previous_map.get(key)

        if now is None:
            continue

        current_rate = float(
            now["difficulty_rate"]
        )

        previous_rate = (
            float(
                before["difficulty_rate"]
            )
            if before is not None
            else None
        )

        change = (
            round(
                current_rate
                - previous_rate,
                2
            )
            if previous_rate is not None
            else None
        )

        result.append({
            **now,

            "current_rate":
                current_rate,

            "previous_rate":
                previous_rate,

            "change_percentage_points":
                change,

            "trend":
                (
                    classify_trend(change)
                    if change is not None
                    else "NO_COMPARISON"
                ),
        })

    result.sort(
        key=lambda row: (
            0
            if row["trend"] == "WORSENING"
            else 1,
            -row["current_rate"],
            str(row["curriculum_code"]),
            str(row["question_key"]),
        )
    )

    return {
        "current_period": {
            "from":
                current_from.isoformat(),

            "to":
                current_to.isoformat(),
        },

        "previous_period": {
            "from":
                previous_from.isoformat(),

            "to":
                previous_to.isoformat(),
        },

        "questions":
            result,
    }
