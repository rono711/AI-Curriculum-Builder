"""
==========================================================
Rono's School AI Curriculum Builder
Shared Service Registry
==========================================================

Every service URL is defined here.

No other module should hardcode ports or URLs.
"""

# ==========================================================
# Local Host
# ==========================================================

HOST = "127.0.0.1"

# ==========================================================
# Ports
# ==========================================================

BUILD_APP_PORT = 8001

CURRICULUM_SERVICE_PORT = 8003

LESSON_PACKAGE_BUILDER_PORT = 8004

PROMPT_ENGINE_PORT = 8005

GAMMA_ENGINE_PORT = 8006

AI_ENGINE_PORT = 8007

MOODLE_PUBLISHER_PORT = 8008

WORKBOOK_SERVICE_PORT = 8009

# ==========================================================
# Service URLs
# ==========================================================

BUILD_APP_URL = (

    f"http://{HOST}:{BUILD_APP_PORT}"

)

CURRICULUM_SERVICE_URL = (

    f"http://{HOST}:{CURRICULUM_SERVICE_PORT}"

)

LESSON_PACKAGE_BUILDER_URL = (

    f"http://{HOST}:{LESSON_PACKAGE_BUILDER_PORT}"

)

PROMPT_ENGINE_URL = (

    f"http://{HOST}:{PROMPT_ENGINE_PORT}"

)

WORKBOOK_SERVICE_URL = (

    f"http://{HOST}:{WORKBOOK_SERVICE_PORT}"

)

GAMMA_ENGINE_URL = (

    f"http://{HOST}:{GAMMA_ENGINE_PORT}"

)

CONTENT_ENGINE_URL = (

    f"http://{HOST}:{AI_ENGINE_PORT}"

)

MOODLE_PUBLISHER_URL = (

    f"http://{HOST}:{MOODLE_PUBLISHER_PORT}"

)

# ==========================================================
# API Endpoints
# ==========================================================

BUILD_HEALTH = (

        BUILD_APP_URL +

        "/health"

)

CURRICULUM_HEALTH = (

        CURRICULUM_SERVICE_URL +

        "/health"

)

NORMALIZE = (

        CURRICULUM_SERVICE_URL +

        "/normalize"

)

BUILD_WORKBOOK = (

        LESSON_PACKAGE_BUILDER_URL +

        "/build"

)

GENERATE_PROMPT = (

        PROMPT_ENGINE_URL +

        "/prompt"

)

# ==========================================================
# Workbook Service
# ==========================================================

READ_WORKBOOK = (

        WORKBOOK_SERVICE_URL +

        "/read"

)

UPDATE_WORKBOOK = (

        WORKBOOK_SERVICE_URL +

        "/update"

)

UPDATE_MARKDOWN = (
    WORKBOOK_SERVICE_URL +
    "/update_markdown"
)

GENERATE_PRESENTATION = (

        GAMMA_ENGINE_URL +

        "/generate"

)

GENERATE_AI = (

        CONTENT_ENGINE_URL +

        "/generate"

)

PUBLISH_MOODLE = (

        MOODLE_PUBLISHER_URL +

        "/publish"

)

# ==========================================================
# Future Public URLs
# ==========================================================

PUBLIC_BUILD_APP = "https://build.ronosschool.com"

PUBLIC_API = "https://api.ronosschool.com"

PUBLIC_MOODLE = "https://ronosschool.com"

PUBLIC_GOOGLE_DRIVE = ""

PUBLIC_GOOGLE_SLIDES = ""
