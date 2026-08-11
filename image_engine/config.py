import os
from pathlib import Path

from dotenv import load_dotenv


# ==========================================================
# Project
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(
    PROJECT_ROOT / ".env"
)


# ==========================================================
# OpenAI
# ==========================================================

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.4-mini"
)

OPENAI_IMAGE_MODEL = os.getenv(
    "OPENAI_IMAGE_MODEL",
    "gpt-image-1.5"
)


# ==========================================================
# Image Generation
# ==========================================================

IMAGE_SIZE = os.getenv(
    "OPENAI_IMAGE_SIZE",
    "1536x1024"
)

IMAGE_QUALITY = os.getenv(
    "OPENAI_IMAGE_QUALITY",
    "medium"
)

IMAGE_FORMAT = os.getenv(
    "OPENAI_IMAGE_FORMAT",
    "png"
)
