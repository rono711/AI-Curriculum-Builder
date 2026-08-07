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
# Shared
# ==========================================================

SHARED_FOLDER = PROJECT_ROOT / "shared"

# ==========================================================
# CONTENT Engine
# ==========================================================

CONTENT_ENGINE_FOLDER = PROJECT_ROOT / "content_engine"

LOG_FOLDER = CONTENT_ENGINE_FOLDER / "logs"
OUTPUT_FOLDER = CONTENT_ENGINE_FOLDER / "output"


# ==========================================================
# Prompt Engine
# ==========================================================

PROMPT_ENGINE_URL = os.getenv(
    "PROMPT_ENGINE_URL",
    "http://192.168.1.108:8005/prompt"
)

# ==========================================================
# Gamma Engine
# ==========================================================

GAMMA_ENGINE_URL = os.getenv(
    "GAMMA_ENGINE_URL",
    "http://192.168.1.108:8007/generate"
)

# ==========================================================
# Future AI Engines
# ==========================================================

CHATGPT_ENGINE_URL = ""

GEMINI_ENGINE_URL = ""

NOTEBOOKLM_ENGINE_URL = ""

# ==========================================================
# Providers
# ==========================================================

PROVIDER_CHATGPT = "CHATGPT"

PROVIDER_GEMINI = "GEMINI"

PROVIDER_GAMMA = "GAMMA"

PROVIDER_NOTEBOOKLM = "NOTEBOOKLM"

# ==========================================================
# Prompt Types
# ==========================================================

PROMPT_LESSON = "LESSON_CONTENT"

PROMPT_SLIDES = "GAMMA_SLIDES"

PROMPT_QUIZ = "QUIZ"

PROMPT_ACTIVITIES = "ACTIVITIES"

PROMPT_RECAP = "RECAP"

PROMPT_WORKSHEET = "WORKSHEET"

PROMPT_TEACHER = "TEACHER_GUIDE"

PROMPT_NOTEBOOKLM = "NOTEBOOKLM"

# ==========================================================
# Status
# ==========================================================

STATUS_PENDING = "PENDING"

STATUS_RUNNING = "RUNNING"

STATUS_COMPLETED = "COMPLETED"

STATUS_FAILED = "FAILED"

# ==========================================================
# Workbook
# ==========================================================

SHEET_LESSON_CONTENT = "Lesson_Content"

SHEET_GAMMA_SLIDES = "Gamma_Slides"

SHEET_DESCRIPTIONS = "Descriptions"

SHEET_QUIZ = "Quiz"

SHEET_ACTIVITIES = "Activities"

SHEET_RECAP = "Recap"

SHEET_RESOURCES = "Resources"

SHEET_AI_GENERATION = "AI_Generation"

SHEET_ASSET_REGISTER = "Asset_Register"

SHEET_MOODLE_PUBLISH = "Moodle_Publish"

SHEET_BUILD_LOG = "Build_Log"

# ==========================================================
# Version
# ==========================================================

CONTENT_ENGINE_VERSION = "1.0.0"
