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

    / "recap_engine"

    / ".env"

)

# ==========================================================
# Recap Engine
# ==========================================================

RECAP_ENGINE_FOLDER = (

    PROJECT_ROOT

    / "recap_engine"

)

LOG_FOLDER = (

    RECAP_ENGINE_FOLDER

    / "logs"

)

OUTPUT_FOLDER = (

    RECAP_ENGINE_FOLDER

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

SHEET_RECAP = "Recap"

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

RECAP_MARKDOWN_FILE = "../prompts/templates/recap.md"

RECAP_HTML_FILE = "recap.html"

RECAP_JSON_FILE = "recap.json"

RECAP_RESPONSE_FILE = "recap_response.json"

# ==========================================================
# Version
# ==========================================================

RECAP_ENGINE_VERSION = "1.0.0"