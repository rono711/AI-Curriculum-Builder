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
# Activities Engine
# ==========================================================

ACTIVITIES_ENGINE_FOLDER = (

    PROJECT_ROOT

    / "activities_engine"

)

LOG_FOLDER = (

    ACTIVITIES_ENGINE_FOLDER

    / "logs"

)

OUTPUT_FOLDER = (

    ACTIVITIES_ENGINE_FOLDER

    / "output"

)

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

SHEET_ACTIVITIES = "Activities"

SHEET_DESCRIPTIONS = "Descriptions"

SHEET_ASSET_REGISTER = "Asset_Register"

SHEET_BUILD_LOG = "Build_Log"

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

ACTIVITIES_MARKDOWN_FILE = "activities.md"

ACTIVITIES_HTML_FILE = "activities.html"

ACTIVITIES_JSON_FILE = "activities.json"

ACTIVITIES_RESPONSE_FILE = "activities_response.json"

# ==========================================================
# Version
# ==========================================================

ACTIVITIES_ENGINE_VERSION = "1.0.0"
