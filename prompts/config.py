from pathlib import Path
import os

# ==========================================================
# Project Root
# ==========================================================

PROJECT_ROOT = Path("/volume1/docker/curriculum-builder")

# ==========================================================
# Shared Folders
# ==========================================================

BUILDS_FOLDER = PROJECT_ROOT / "builds"

OUTPUT_FOLDER = PROJECT_ROOT / "output"

LOG_FOLDER = PROJECT_ROOT / "logs"

# ==========================================================
# Prompt Engine
# ==========================================================

PROMPT_ENGINE_FOLDER = PROJECT_ROOT / "prompts"

TEMPLATES_FOLDER = PROMPT_ENGINE_FOLDER / "templates"

OUTPUT_PROMPTS_FOLDER = PROMPT_ENGINE_FOLDER / "output"

# ==========================================================
# CONTENT Engine
# ==========================================================

CONTENT_ENGINE_URL = os.getenv(
    "CONTENT_ENGINE_URL",
    "http://192.168.1.108:8006/generate"
)

# ==========================================================
# Workbook Worksheets
# ==========================================================

SHEET_BUILD_METADATA = "Build_Metadata"

SHEET_LESSON_DB = "Lesson_DB"

SHEET_LESSON_METADATA = "Lesson_Metadata"

SHEET_LESSON_CONTENT = "Lesson_Content"

SHEET_GOOGLE_SLIDES = "Gamma_Slides"

SHEET_QUIZ = "Quiz"

SHEET_ACTIVITIES = "Activities"

SHEET_RECAP = "Recap"

SHEET_RESOURCES = "Resources"

SHEET_PROMPT_QUEUE = "Prompt_Queue"

SHEET_PROMPT_LIBRARY = "Prompt_Library"

SHEET_PROMPT_DEFINITIONS = "Prompt_Definitions"

SHEET_AI_GENERATION = "AI_Generation"

# ==========================================================
# Prompt Types
# ==========================================================

PROMPT_TYPES = [

    "LESSON_CONTENT",

    "GOOGLE_SLIDES",

    "QUIZ",

    "ACTIVITIES",

    "RECAP",

    "TEACHER_GUIDE",

    "WORKSHEET",

    "NOTEBOOKLM"

]

# ==========================================================
# AI Providers
# ==========================================================

AI_PROVIDER_GAMMA = "GAMMA"

AI_PROVIDER_CHATGPT = "CHATGPT"

AI_PROVIDER_GEMINI = "GEMINI"

AI_PROVIDER_NOTEBOOKLM = "NOTEBOOKLM"

# ==========================================================
# Status
# ==========================================================

STATUS_PENDING = "PENDING"

STATUS_RUNNING = "RUNNING"

STATUS_COMPLETED = "COMPLETED"

STATUS_FAILED = "FAILED"

# ==========================================================
# Output Files
# ==========================================================

GAMMA_PROMPT = "gamma_prompt.md"

LESSON_PROMPT = "lesson_prompt.md"

QUIZ_PROMPT = "quiz_prompt.md"

ACTIVITIES_PROMPT = "activities_prompt.md"

RECAP_PROMPT = "recap_prompt.md"

WORKSHEET_PROMPT = "worksheet_prompt.md"

TEACHER_GUIDE_PROMPT = "teacher_guide_prompt.md"

NOTEBOOKLM_PROMPT = "notebooklm_prompt.md"

# ==========================================================
# Date Formats
# ==========================================================

DATE_FORMAT = "%Y-%m-%d"

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# ==========================================================
# Rono's School Defaults
# ==========================================================

DEFAULT_CURRICULUM = "Australian Curriculum v9"

DEFAULT_BRAND = "Rono's School"

DEFAULT_LANGUAGE = "English"

DEFAULT_PRESENTATION_STYLE = "Primary"

DEFAULT_TEACHING_MODEL = "Explicit Instruction"

DEFAULT_VISUAL_STYLE = "Modern Colourful"

DEFAULT_ACCESSIBILITY = "WCAG 2.2"

# ==========================================================
# Prompt Version
# ==========================================================

PROMPT_ENGINE_VERSION = "1.0.0"
