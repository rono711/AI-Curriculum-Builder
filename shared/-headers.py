"""
==========================================================
Workbook Header Utilities
==========================================================

Provides a single place to normalize worksheet header names
across all services.

Example:

    "Year Level"        -> year_level
    "Lesson Package ID" -> lesson_package_id
    "Sub-Strand"        -> sub_strand
"""

from typing import Any


def normalize_header(value: Any) -> str:
    """
    Convert an Excel worksheet header into a standard key.

    Examples:
        "Year Level"        -> year_level
        "Lesson Package ID" -> lesson_package_id
        "Sub-Strand"        -> sub_strand
        " Curriculum Code " -> curriculum_code
    """

    if value is None:
        return ""

    return (
        str(value)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


def normalize_headers(headers: dict) -> dict:
    """
    Normalize all keys in a dictionary.

    Example:

        {
            "Year Level": "Foundation Year",
            "Lesson Package ID": "LP001"
        }

    becomes

        {
            "year_level": "Foundation Year",
            "lesson_package_id": "LP001"
        }
    """

    return {
        normalize_header(key): value
        for key, value in headers.items()
    }