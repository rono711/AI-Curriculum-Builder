from pathlib import Path

# ==========================================================
# Description Engine
# ==========================================================

ENGINE_NAME = "Description Engine"

ENGINE_VERSION = "1.0.0"

# ==========================================================
# Project
# ==========================================================

PROJECT_ROOT = Path("/volume1/docker/curriculum-builder")

# ==========================================================
# Build Folders
# ==========================================================

BUILD_FOLDER = PROJECT_ROOT / "builds"

PROMPTS_FOLDER = PROJECT_ROOT / "prompts"

# ==========================================================
# Prompt Templates
# ==========================================================

DESCRIPTION_TEMPLATE_FOLDER = (

    PROMPTS_FOLDER

    / "templates"

    / "descriptions"

)

# ==========================================================
# Output Folder
# ==========================================================

DESCRIPTION_FOLDER = "Descriptions"

DESCRIPTION_JSON = "descriptions.json"

DESCRIPTION_MARKDOWN = "descriptions.md"