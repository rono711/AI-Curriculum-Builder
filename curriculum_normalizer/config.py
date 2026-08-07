from pathlib import Path

# ==========================================================
# Project Root
# ==========================================================

PROJECT_ROOT = Path("/volume1/docker/curriculum-builder")

# ==========================================================
# Shared Folders
# ==========================================================

INPUT_FOLDER = PROJECT_ROOT / "input"

DATA_FOLDER = PROJECT_ROOT / "data"

OUTPUT_FOLDER = PROJECT_ROOT / "output"

# ==========================================================
# Input Workbook
# ==========================================================

INPUT_WORKBOOK = (
        INPUT_FOLDER /
        "Australian_Curriculum_v9.xlsx"
)

# ==========================================================
# Master Lesson Database
# ==========================================================

MASTER_LESSON_DB = (
        DATA_FOLDER /
        "Master_Lesson_DB.xlsx"
)

# ==========================================================
# Curriculum
# ==========================================================

CURRICULUM_VERSION = "Australian Curriculum v9"

VERSION = "3.0.0"
