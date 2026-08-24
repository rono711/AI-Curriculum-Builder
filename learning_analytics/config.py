"""Learning analytics configuration."""

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(
    dotenv_path=ENV_FILE,
    override=False
)

DATA_DIR = PROJECT_ROOT / "data"

ANALYTICS_DB = (
    DATA_DIR
    / "learning_analytics.db"
)

BUILD_REGISTRY_DB = (
    DATA_DIR
    / "build_registry.db"
)

MOODLE_ANALYTICS_URL = os.getenv(
    "MOODLE_ANALYTICS_URL",
    ""
).strip().rstrip("/")

MOODLE_ANALYTICS_TOKEN = os.getenv(
    "MOODLE_ANALYTICS_TOKEN",
    ""
).strip()

MAX_QUIZ_ATTEMPTS = int(
    os.getenv(
        "ANALYTICS_MAX_QUIZ_ATTEMPTS",
        "3"
    )
)

FEEDBACK_EMAIL_MODE = os.getenv(
    "ANALYTICS_EMAIL_MODE",
    "PREVIEW"
).strip().upper()


def validate_moodle_config():
    if not MOODLE_ANALYTICS_URL:
        raise RuntimeError(
            "MOODLE_ANALYTICS_URL is not configured."
        )

    if not MOODLE_ANALYTICS_TOKEN:
        raise RuntimeError(
            "MOODLE_ANALYTICS_TOKEN is not configured."
        )
