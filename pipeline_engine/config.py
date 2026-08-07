from pathlib import Path

# ==========================================================
# Project
# ==========================================================

PROJECT_ROOT = Path("/volume1/docker/curriculum-builder")

# ==========================================================
# Build Folder
# ==========================================================

BUILDS_FOLDER = PROJECT_ROOT / "builds"

# ==========================================================
# Engine URLs
# ==========================================================

PROMPT_ENGINE_URL = "http://127.0.0.1:8005/prompt"

GAMMA_ENGINE_URL = "http://localhost:8006/generate"

QUIZ_ENGINE_URL = "http://localhost:8002/generate"

ACTIVITIES_ENGINE_URL = "http://localhost:8010/generate"

RECAP_ENGINE_URL = "http://localhost:8011/generate"

PUBLISHER_ENGINE_URL = "http://localhost:8012/publish"

# ==========================================================
# Timeouts (seconds)
# ==========================================================

PROMPT_TIMEOUT = 600

ENGINE_TIMEOUT = 1800