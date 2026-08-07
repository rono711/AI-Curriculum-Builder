from pathlib import Path
import os


# ==========================================================
# Project
# ==========================================================

PROJECT_ROOT = Path(
    os.getenv(
        "PROJECT_ROOT",
        "/volume1/docker/curriculum-builder"
    )
)


# ==========================================================
# Build Folder
# ==========================================================

BUILDS_FOLDER = PROJECT_ROOT / "builds"


# ==========================================================
# Engine URLs
# ==========================================================

PROMPT_ENGINE_URL = os.getenv(
    "PROMPT_ENGINE_URL",
    "http://192.168.1.108:8005/prompt"
)

GAMMA_ENGINE_URL = os.getenv(
    "GAMMA_ENGINE_URL",
    "http://192.168.1.108:8007/generate"
)

QUIZ_ENGINE_URL = os.getenv(
    "QUIZ_ENGINE_URL",
    "http://192.168.1.108:8009/generate"
)

ACTIVITIES_ENGINE_URL = os.getenv(
    "ACTIVITIES_ENGINE_URL",
    "http://192.168.1.108:8008/generate"
)

RECAP_ENGINE_URL = os.getenv(
    "RECAP_ENGINE_URL",
    "http://192.168.1.108:8010/generate"
)

PUBLISHER_ENGINE_URL = os.getenv(
    "PUBLISHER_ENGINE_URL",
    "http://192.168.1.108:8012/publish"
)


# ==========================================================
# Timeouts (seconds)
# ==========================================================

PROMPT_TIMEOUT = 600

ENGINE_TIMEOUT = 1800
