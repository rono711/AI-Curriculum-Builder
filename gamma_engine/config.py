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
    PROJECT_ROOT / ".env"
)

# ==========================================================
# Shared
# ==========================================================

SHARED_FOLDER = PROJECT_ROOT / "shared"

# ==========================================================
# Gamma Engine
# ==========================================================

GAMMA_ENGINE_FOLDER = PROJECT_ROOT / "gamma_engine"

LOG_FOLDER = GAMMA_ENGINE_FOLDER / "logs"

OUTPUT_FOLDER = GAMMA_ENGINE_FOLDER / "output"

# ==========================================================
# Gamma API
# ==========================================================

GAMMA_API_URL = os.getenv(

    "GAMMA_API_URL",

    "https://public-api.gamma.app/v1.0"

)

GAMMA_API_KEY = os.getenv(

    "GAMMA_API_KEY"

)

# ==========================================================
# Google Drive
# ==========================================================

GOOGLE_DRIVE_FOLDER = (

    "Rono's School AI Curriculum"

)

GAMMA_SLIDES_FOLDER = (

    "Lesson Slides"

)

# ==========================================================
# Workbook
# ==========================================================

SHEET_GAMMA_SLIDES = "Gamma_Slides"

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

# ==========================================================
# Default Presentation
# ==========================================================

DEFAULT_SLIDES = 12

DEFAULT_TEXT_MODE = "generate"

DEFAULT_FORMAT = "presentation"

DEFAULT_EXPORT = "pptx"

# ==========================================================
# Version
# ==========================================================

GAMMA_ENGINE_VERSION = "2.0.0"
