"""
Rono's School AI Curriculum Builder
Shared Service Registry

The root .env file is the single source of truth for
service ports and service URLs.

No module should hardcode service ports or URLs.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


# ==========================================================
# Project
# ==========================================================

PROJECT_ROOT = Path(
    os.getenv(
        "PROJECT_ROOT",
        "/volume1/docker/curriculum-builder"
    )
)

load_dotenv(PROJECT_ROOT / ".env")


# ==========================================================
# Network
# ==========================================================

NAS_HOST = os.getenv(
    "NAS_HOST",
    "192.168.1.108"
)


# ==========================================================
# Service Ports
# ==========================================================

CURRICULUM_NORMALIZER_PORT = int(
    os.getenv("CURRICULUM_NORMALIZER_PORT", "8001")
)

BUILD_APP_PORT = int(
    os.getenv("BUILD_APP_PORT", "8002")
)

LESSON_PACKAGE_BUILDER_PORT = int(
    os.getenv("LESSON_PACKAGE_BUILDER_PORT", "8003")
)

PIPELINE_ENGINE_PORT = int(
    os.getenv("PIPELINE_ENGINE_PORT", "8004")
)

PROMPT_ENGINE_PORT = int(
    os.getenv("PROMPT_ENGINE_PORT", "8005")
)

CONTENT_ENGINE_PORT = int(
    os.getenv("CONTENT_ENGINE_PORT", "8006")
)

GAMMA_ENGINE_PORT = int(
    os.getenv("GAMMA_ENGINE_PORT", "8007")
)

ACTIVITIES_ENGINE_PORT = int(
    os.getenv("ACTIVITIES_ENGINE_PORT", "8008")
)

QUIZ_ENGINE_PORT = int(
    os.getenv("QUIZ_ENGINE_PORT", "8009")
)

RECAP_ENGINE_PORT = int(
    os.getenv("RECAP_ENGINE_PORT", "8010")
)

WORKBOOK_SERVICE_PORT = int(
    os.getenv("WORKBOOK_SERVICE_PORT", "8011")
)

PUBLISHER_ENGINE_PORT = int(
    os.getenv("PUBLISHER_ENGINE_PORT", "8012")
)


# ==========================================================
# Service Base URLs
# ==========================================================

CURRICULUM_NORMALIZER_URL = os.getenv(
    "CURRICULUM_NORMALIZER_URL",
    f"http://{NAS_HOST}:{CURRICULUM_NORMALIZER_PORT}"
)

BUILD_APP_URL = os.getenv(
    "BUILD_APP_URL",
    f"http://{NAS_HOST}:{BUILD_APP_PORT}"
)

LESSON_PACKAGE_BUILDER_URL = os.getenv(
    "LESSON_PACKAGE_BUILDER_URL",
    f"http://{NAS_HOST}:{LESSON_PACKAGE_BUILDER_PORT}/build"
)

WORKBOOK_SERVICE_URL = os.getenv(
    "WORKBOOK_SERVICE_URL",
    f"http://{NAS_HOST}:{WORKBOOK_SERVICE_PORT}"
)


# ==========================================================
# Engine Endpoints
# ==========================================================

PIPELINE_ENGINE_URL = os.getenv(
    "PIPELINE_ENGINE_URL",
    f"http://{NAS_HOST}:{PIPELINE_ENGINE_PORT}/run"
)

PROMPT_ENGINE_URL = os.getenv(
    "PROMPT_ENGINE_URL",
    f"http://{NAS_HOST}:{PROMPT_ENGINE_PORT}/prompt"
)

CONTENT_ENGINE_URL = os.getenv(
    "CONTENT_ENGINE_URL",
    f"http://{NAS_HOST}:{CONTENT_ENGINE_PORT}/generate"
)

GAMMA_ENGINE_URL = os.getenv(
    "GAMMA_ENGINE_URL",
    f"http://{NAS_HOST}:{GAMMA_ENGINE_PORT}/generate"
)

ACTIVITIES_ENGINE_URL = os.getenv(
    "ACTIVITIES_ENGINE_URL",
    f"http://{NAS_HOST}:{ACTIVITIES_ENGINE_PORT}/generate"
)

QUIZ_ENGINE_URL = os.getenv(
    "QUIZ_ENGINE_URL",
    f"http://{NAS_HOST}:{QUIZ_ENGINE_PORT}/generate"
)

RECAP_ENGINE_URL = os.getenv(
    "RECAP_ENGINE_URL",
    f"http://{NAS_HOST}:{RECAP_ENGINE_PORT}/generate"
)

PUBLISHER_ENGINE_URL = os.getenv(
    "PUBLISHER_ENGINE_URL",
    f"http://{NAS_HOST}:{PUBLISHER_ENGINE_PORT}/publish"
)


# ==========================================================
# Compatibility API Endpoints
# ==========================================================
#
# Existing modules import these names.
# Keep them until those modules are migrated directly to
# the centralized service URL variables.
#

GENERATE_PROMPT = PROMPT_ENGINE_URL

GENERATE_PRESENTATION = GAMMA_ENGINE_URL

GENERATE_AI = CONTENT_ENGINE_URL

BUILD_WORKBOOK = LESSON_PACKAGE_BUILDER_URL

PUBLISH_MOODLE = PUBLISHER_ENGINE_URL


# ==========================================================
# Workbook Service Endpoints
# ==========================================================

READ_WORKBOOK = (
    f"{WORKBOOK_SERVICE_URL}/read"
)

UPDATE_WORKBOOK = (
    f"{WORKBOOK_SERVICE_URL}/update"
)

UPDATE_MARKDOWN = (
    f"{WORKBOOK_SERVICE_URL}/update_markdown"
)


# ==========================================================
# Health Endpoints
# ==========================================================

BUILD_HEALTH = (
    f"{BUILD_APP_URL}/health"
)

CURRICULUM_HEALTH = (
    f"{CURRICULUM_NORMALIZER_URL}/health"
)

NORMALIZE = (
    f"{CURRICULUM_NORMALIZER_URL}/normalize"
)


# ==========================================================
# Public URLs
# ==========================================================

PUBLIC_BUILD_APP = "https://build.ronosschool.com"

PUBLIC_API = "https://api.ronosschool.com"

PUBLIC_MOODLE = "https://ronosschool.com"

PUBLIC_GOOGLE_DRIVE = ""

PUBLIC_GOOGLE_SLIDES = ""
