from datetime import datetime
from pathlib import Path

from config import (
    BUILDS_FOLDER,
    BUILD_PREFIX,
    BUILD_NUMBER_WIDTH,
    DATE_FOLDER_FORMAT,
    DATE_FILENAME_FORMAT
)

# ==========================================================
# Build Counter File
# ==========================================================

BUILD_COUNTER = Path(__file__).parent / "build_number.txt"


# ==========================================================
# Next Build Number
# ==========================================================

def next_build_number():
    if not BUILD_COUNTER.exists():
        BUILD_COUNTER.write_text("000000")

    number = int(

        BUILD_COUNTER.read_text().strip()

    )

    number += 1

    BUILD_COUNTER.write_text(

        f"{number:0{BUILD_NUMBER_WIDTH}d}"

    )

    return number


# ==========================================================
# Build Folder
# ==========================================================

def build_folder():
    now = datetime.now()

    month_folder = (

            BUILDS_FOLDER

            / now.strftime("%Y")

            / now.strftime("%m")

    )

    #
    # Standard folders
    #

    for folder in [

        "Workbook",

        "Prompts",

        "AI",

        "Slides",

        "Moodle",

        "Logs",

        "Temp"

    ]:
        (

                month_folder / folder

        ).mkdir(

            parents=True,

            exist_ok=True

        )

    return month_folder / "Workbook"


# ==========================================================
# Safe Filename
# ==========================================================

def safe_name(value):
    value = str(value)

    value = value.replace("&", "and")

    value = value.replace("/", "-")

    value = value.replace("\\", "-")

    value = value.replace(" ", "")

    value = value.replace(":", "")

    return value


# ==========================================================
# Workbook Filename
# ==========================================================

def workbook_filename(

        subject,

        year_level,

        strand

):
    build_number = next_build_number()

    build_date = datetime.now().strftime(

        DATE_FILENAME_FORMAT

    )

    filename = (

        f"{BUILD_PREFIX}_"

        f"{build_date}_"

        f"{build_number:0{BUILD_NUMBER_WIDTH}d}_"

        f"{safe_name(subject)}_"

        f"{safe_name(year_level)}_"

        f"{safe_name(strand)}"

        ".xlsx"

    )

    return {

        "build_id":

            build_number,

        "filename":

            filename,

        "path":

            build_folder() / filename

    }
