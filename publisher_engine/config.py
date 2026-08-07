from pathlib import Path
import os

from dotenv import load_dotenv

# ==========================================================
# Project
# ==========================================================

PROJECT_ROOT = Path(

    "/volume1/docker/curriculum-builder"

)

load_dotenv(

    PROJECT_ROOT

    /  ".env"

)

# ==========================================================
# Moodle
# ==========================================================

MOODLE_URL = os.getenv(

    "MOODLE_URL"

)

MOODLE_TOKEN = os.getenv(

    "MOODLE_TOKEN"

)

MOODLE_SERVICE = os.getenv(

    "MOODLE_SERVICE"

)

VERIFY_SSL = os.getenv(

    "VERIFY_SSL",

    "true"

).lower() == "true"

PUBLISH_TIMEOUT = int(

    os.getenv(

        "PUBLISH_TIMEOUT",

        "300"

    )

)

# ==========================================================
# Workbook
# ==========================================================

WORKBOOK_SHEET_METADATA = "Lesson_Metadata"

WORKBOOK_SHEET_SLIDES = "Gamma_Slides"

WORKBOOK_SHEET_QUIZ = "Quiz"

WORKBOOK_SHEET_ACTIVITIES = "Activities"

WORKBOOK_SHEET_RECAP = "Recap"

WORKBOOK_SHEET_DESCRIPTIONS = "Descriptions"

WORKBOOK_SHEET_PUBLISH = "Moodle_Publish"
