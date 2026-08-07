from pathlib import Path
import os

from dotenv import load_dotenv

# ==========================================================
# Project
# ==========================================================

PROJECT_ROOT = Path(

    "/volume1/docker/curriculum-builder"

)

#
# Environment
#

load_dotenv(

    PROJECT_ROOT

    / ".env"

)

# ==========================================================
# Shared
# ==========================================================

SHARED_FOLDER = PROJECT_ROOT / "shared"

# ==========================================================
# Quiz Engine
# ==========================================================

QUIZ_ENGINE_FOLDER = PROJECT_ROOT / "quiz_engine"

LOG_FOLDER = QUIZ_ENGINE_FOLDER / "logs"

OUTPUT_FOLDER = QUIZ_ENGINE_FOLDER / "output"

# ==========================================================
# OpenAI
# ==========================================================

OPENAI_API_KEY = os.getenv(

    "OPENAI_API_KEY"

)

OPENAI_MODEL = os.getenv(

    "OPENAI_MODEL",

    "gpt-5.5"

)

# ==========================================================
# Workbook
# ==========================================================

SHEET_QUIZ = "Quiz"

SHEET_ASSET_REGISTER = "Asset_Register"

SHEET_BUILD_LOG = "Build_Log"

SHEET_DESCRIPTIONS = "Descriptions"


# ==========================================================
# Status
# ==========================================================

STATUS_PENDING = "PENDING"

STATUS_RUNNING = "RUNNING"

STATUS_COMPLETED = "COMPLETED"

STATUS_FAILED = "FAILED"

STATUS_REVIEW_PENDING = "PENDING"

STATUS_REVIEWED = "REVIEWED"

# ==========================================================
# Output Files
# ==========================================================

QUIZ_GIFT_FILE = "lesson_quiz.gift"

QUIZ_JSON_FILE = "lesson_quiz.json"

QUIZ_RESPONSE_FILE = "quiz_response.json"

# ==========================================================
# Version
# ==========================================================

QUIZ_ENGINE_VERSION = "1.0.0"
