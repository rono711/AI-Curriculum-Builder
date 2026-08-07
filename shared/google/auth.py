from pathlib import Path

from google.oauth2.service_account import Credentials


# ==========================================================
# Project
# ==========================================================

PROJECT_ROOT = Path("/volume1/docker/curriculum-builder")

# ==========================================================
# Credentials
# ==========================================================

SERVICE_ACCOUNT_FILE = (

    PROJECT_ROOT /

    "credentials" /

    "google-service-account.json"

)

# ==========================================================
# Scopes
# ==========================================================

SCOPES = [

    "https://www.googleapis.com/auth/drive",

    "https://www.googleapis.com/auth/presentations"

]

# ==========================================================
# Google Credentials
# ==========================================================

def google_credentials():

    return Credentials.from_service_account_file(

        SERVICE_ACCOUNT_FILE,

        scopes=SCOPES

    )