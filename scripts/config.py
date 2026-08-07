from pathlib import Path

# =====================================================
# Project Paths
# =====================================================

PROJECT_ROOT = Path("/volume1/docker/curriculum-builder")

INPUT_FOLDER = PROJECT_ROOT / "input"
OUTPUT_FOLDER = PROJECT_ROOT / "output"
TEMPLATE_FOLDER = PROJECT_ROOT / "templates"
LOG_FOLDER = PROJECT_ROOT / "logs"
PROMPTS_FOLDER = PROJECT_ROOT / "prompts"

# =====================================================
# Files
# =====================================================

CURRICULUM_WORKBOOK = INPUT_FOLDER / "curriculum-workbook.xlsx"

TEMPLATE_WORKBOOK = (
        TEMPLATE_FOLDER /
        "AI_Curriculum_Workbook_v3.0_Production.xlsx"
)

OUTPUT_WORKBOOK = (
        OUTPUT_FOLDER /
        "AI_Curriculum_Workbook_v3.0_Production.xlsx"
)
