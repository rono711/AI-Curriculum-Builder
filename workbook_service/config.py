from pathlib import Path
import os

from dotenv import load_dotenv

# ==========================================================
# Project
# ==========================================================

PROJECT_ROOT = Path("/volume1/docker/curriculum-builder")
#
# Load environment variables
#

load_dotenv(

    PROJECT_ROOT / ".env"

)


# ==========================================================
# Workbook Service
# ==========================================================

WORKBOOK_FOLDER = PROJECT_ROOT / "shared" / "workbook"

LOG_FOLDER = WORKBOOK_FOLDER / "logs"

# ==========================================================
# Workbook Worksheets
# ==========================================================

SHEET_BUILD_METADATA = "Build_Metadata"

SHEET_LESSON_DB = "Lesson_DB"

SHEET_LESSON_CONTENT = "Lesson_Content"

SHEET_GAMMA_SLIDES = "Gamma_Slides"

SHEET_QUIZ = "Quiz"

SHEET_ACTIVITIES = "Activities"

SHEET_RECAP = "Recap"

SHEET_RESOURCES = "Resources"

SHEET_PROMPT_QUEUE = "Prompt_Queue"

SHEET_PROMPT_LIBRARY = "Prompt_Library"

SHEET_PROMPT_DEFINITIONS = "Prompt_Definitions"

SHEET_AI_GENERATION = "AI_Generation"

SHEET_ASSET_REGISTER = "Asset_Register"

SHEET_MOODLE_PUBLISH = "Moodle_Publish"

SHEET_BUILD_LOG = "Build_Log"

# ==========================================================
# Worksheet Registry
# ==========================================================

WORKSHEETS = {

    SHEET_BUILD_METADATA,

    SHEET_LESSON_DB,

    SHEET_LESSON_CONTENT,

    SHEET_GAMMA_SLIDES,

    SHEET_QUIZ,

    SHEET_ACTIVITIES,

    SHEET_RECAP,

    SHEET_RESOURCES,

    SHEET_PROMPT_QUEUE,

    SHEET_PROMPT_LIBRARY,

    SHEET_PROMPT_DEFINITIONS,

    SHEET_AI_GENERATION,

    SHEET_ASSET_REGISTER,

    SHEET_MOODLE_PUBLISH,

    SHEET_BUILD_LOG

}

# ==========================================================
# Workflow Status
# ==========================================================

STATUS_PENDING = "PENDING"

STATUS_READY = "READY"

STATUS_RUNNING = "RUNNING"

STATUS_COMPLETED = "COMPLETED"

STATUS_FAILED = "FAILED"

STATUS_NOT_STARTED = "NOT_STARTED"

STATUS_REVIEW_PENDING = "REVIEW_PENDING"

STATUS_REVIEWED = "REVIEWED"

STATUS_NOT_PUBLISHED = "NOT_PUBLISHED"

STATUS_PUBLISHED = "PUBLISHED"

# ==========================================================
# Date Formats
# ==========================================================

DATE_FORMAT = "%Y-%m-%d"

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# ==========================================================
# Workbook Service
# ==========================================================

WORKBOOK_SERVICE_VERSION = "1.0.0"
# ==========================================================
# n8n
# ==========================================================

N8N_WEBHOOK = os.getenv(

    "N8N_WEBHOOK"

)
