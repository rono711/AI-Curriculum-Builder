from pathlib import Path


# ==========================================================
# Project
# ==========================================================

PROJECT_ROOT = Path("/volume1/docker/curriculum-builder")

# ==========================================================
# Shared Folders
# ==========================================================

INPUT_FOLDER = PROJECT_ROOT / "input"

DATA_FOLDER = PROJECT_ROOT / "data"

TEMPLATE_FOLDER = PROJECT_ROOT / "templates"

BUILDS_FOLDER = PROJECT_ROOT / "builds"

LOG_FOLDER = PROJECT_ROOT / "logs"

# ==========================================================
# Shared Files
# ==========================================================

MASTER_LESSON_DB = (
        DATA_FOLDER /
        "Master_Lesson_DB.xlsx"
)

WORKBOOK_TEMPLATE = (
        TEMPLATE_FOLDER /
        "AI_Curriculum_Workbook_v4.0_Production.xlsx"
)

# ==========================================================
# Build
# ==========================================================

BUILD_PREFIX = "BLD"

BUILD_NUMBER_WIDTH = 6

WORKBOOK_VERSION = "4.0"

CURRICULUM_VERSION = "Australian Curriculum v9"

# ==========================================================
# Date Formats
# ==========================================================

DATE_FOLDER_FORMAT = "%Y/%m"

DATE_FILENAME_FORMAT = "%Y%m%d"

DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# ==========================================================
# Worksheet Names
# ==========================================================

SHEET_BUILD_METADATA = "Build_Metadata"

SHEET_LESSON_DB = "Lesson_DB"

SHEET_LESSON_CONTENT = "Lesson_Content"

SHEET_LESSON_METADATA = "Lesson_Metadata"

SHEET_SLIDES = "Gamma_Slides"

SHEET_QUIZ = "Quiz"

SHEET_ACTIVITIES = "Activities"

SHEET_RECAP = "Recap"

SHEET_DESCRIPTIONS = "Descriptions"

SHEET_RESOURCES = "Resources"

SHEET_PROMPT_DEFINITIONS = "Prompt_Definitions"

SHEET_PROMPT_QUEUE = "Prompt_Queue"

SHEET_PROMPT_LIBRARY = "Prompt_Library"

SHEET_AI_GENERATION = "AI_Generation"

SHEET_ASSET_REGISTER = "Asset_Register"

SHEET_MOODLE_PUBLISH = "Moodle_Publish"

SHEET_BUILD_LOG = "Build_Log"

SHEET_INSTRUCTIONS = "Instructions"

# ==========================================================
#  Engine URLs
# ==========================================================


PROMPT_ENGINE_URL = "http://127.0.0.1:8005/prompt"

GAMMA_ENGINE_URL = "http://localhost:8006/generate"

QUIZ_ENGINE_URL = "http://localhost:8002/generate"

ACTIVITIES_ENGINE_URL = "http://localhost:8010/generate"

RECAP_ENGINE_URL = "http://localhost:8011/generate"

PUBLISHER_ENGINE_URL = "http://localhost:8012/publish"

PIPELINE_ENGINE_URL = "http://localhost:8013/run"

# ==========================================================
# Build Status
# ==========================================================

STATUS_CREATED = "CREATED"

STATUS_AI_PENDING = "AI_PENDING"

STATUS_AI_COMPLETED = "AI_COMPLETED"

STATUS_REVIEW_PENDING = "REVIEW_PENDING"

STATUS_APPROVED = "APPROVED"

STATUS_PUBLISHED = "PUBLISHED"

QUIZ_STRUCTURE = {

    "MCQ": 10,

    "TRUE_FALSE": 5,

    "SHORT_ANSWER": 3,

    "EXTENDED_RESPONSE": 2

}

# ==========================================================
# Default Activity Types
# ==========================================================

ACTIVITY_TYPES = {

    "WARM_UP",

    "GUIDED_PRACTICE",

    "INDEPENDENT_PRACTICE",

    "EXTENSION",

    "DIFFERENTIATION"

}
