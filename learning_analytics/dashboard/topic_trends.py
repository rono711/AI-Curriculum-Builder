"""Historical parent-topic trends for dashboard."""

from datetime import datetime, timedelta, timezone

from learning_analytics.dashboard.parent_topics import (
    parent_topic_difficulty,
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
    if change is None:
        return "NO_COMPARISON"

    if change <= -5:
        return "IMPROVING"

    if change >= 5:
        return "WORSENING"

    return "STABLE"


def parent_topic_period_comparison(
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

    duration = current_to - current_from

    previous_to = (
        current_from
        - timedelta(seconds=1)
    )

    previous_from = (
        previous_to
        - duration
    )

    current = parent_topic_difficulty(
        course_id,
        date_from=current_from.isoformat(),
        date_to=current_to.isoformat(),
    )

    previous = parent_topic_difficulty(
        course_id,
        date_from=previous_from.isoformat(),
        date_to=previous_to.isoformat(),
    )

    previous_map = {
        row["parent_code"]: row
        for row in previous
    }

    result = []

    for row in current:
        before = previous_map.get(
            row["parent_code"]
        )

        current_rate = float(
            row["difficulty_rate"]
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
            **row,

            "current_rate":
                current_rate,

            "previous_rate":
                previous_rate,

            "change_percentage_points":
                change,

            "trend":
                classify_trend(change),
        })

    return {
        "current_period": {
            "from": current_from.isoformat(),
            "to": current_to.isoformat(),
        },

        "previous_period": {
            "from": previous_from.isoformat(),
            "to": previous_to.isoformat(),
        },

        "topics": result,
    }


def parent_topic_history(
        course_id,
        *,
        date_from,
        date_to,
        bucket_days=7
):
    """Return parent-topic difficulty in consecutive time buckets."""

    start = parse_datetime(date_from)
    end = parse_datetime(date_to)

    if end < start:
        raise ValueError(
            "date_to must not be earlier than date_from."
        )

    bucket_days = int(bucket_days)

    if bucket_days < 1:
        raise ValueError(
            "bucket_days must be at least 1."
        )

    buckets = []

    cursor = start
    bucket_number = 1

    while cursor <= end:
        bucket_end = min(
            cursor
            + timedelta(days=bucket_days)
            - timedelta(seconds=1),
            end,
        )

        rows = parent_topic_difficulty(
            course_id,
            date_from=cursor.isoformat(),
            date_to=bucket_end.isoformat(),
        )

        row_map = {
            row["parent_code"]: row
            for row in rows
        }

        buckets.append({
            "bucket":
                bucket_number,

            "from":
                cursor.isoformat(),

            "to":
                bucket_end.isoformat(),

            "topics":
                row_map,
        })

        cursor = (
            bucket_end
            + timedelta(seconds=1)
        )

        bucket_number += 1

    parent_codes = sorted({
        parent_code
        for bucket in buckets
        for parent_code in bucket["topics"]
    })

    topics = []

    for parent_code in parent_codes:
        points = []

        for bucket in buckets:
            row = bucket["topics"].get(
                parent_code
            )

            if row is None:
                points.append({
                    "bucket":
                        bucket["bucket"],

                    "from":
                        bucket["from"],

                    "to":
                        bucket["to"],

                    "difficulty_rate":
                        None,

                    "students_with_evidence":
                        0,

                    "students_struggling":
                        0,

                    "status":
                        "NO_DATA",
                })

                continue

            points.append({
                "bucket":
                    bucket["bucket"],

                "from":
                    bucket["from"],

                "to":
                    bucket["to"],

                "difficulty_rate":
                    float(
                        row["difficulty_rate"]
                    ),

                "students_with_evidence":
                    int(
                        row[
                            "students_with_evidence"
                        ]
                    ),

                "students_struggling":
                    int(
                        row[
                            "students_struggling"
                        ]
                    ),

                "status":
                    "HAS_DATA",
            })

        evidence_points = [
            point
            for point in points
            if point["difficulty_rate"]
            is not None
        ]

        first_rate = (
            evidence_points[0][
                "difficulty_rate"
            ]
            if evidence_points
            else None
        )

        latest_rate = (
            evidence_points[-1][
                "difficulty_rate"
            ]
            if evidence_points
            else None
        )

        change = (
            round(
                latest_rate - first_rate,
                2
            )
            if len(evidence_points) >= 2
            else None
        )

        topics.append({
            "parent_code":
                parent_code,

            "first_rate":
                first_rate,

            "latest_rate":
                latest_rate,

            "change_percentage_points":
                change,

            "trend":
                classify_trend(change),

            "evidence_bucket_count":
                len(evidence_points),

            "points":
                points,
        })

    return {
        "course_id":
            int(course_id),

        "date_from":
            start.isoformat(),

        "date_to":
            end.isoformat(),

        "bucket_days":
            bucket_days,

        "bucket_count":
            len(buckets),

        "topics":
            topics,
    }
