from datetime import datetime

from config import (
    SHEET_BUILD_METADATA,
    CURRICULUM_VERSION,
    WORKBOOK_VERSION,
    STATUS_CREATED,
    DATE_TIME_FORMAT
)


# ==========================================================
# Header Map
# ==========================================================

def header_map(sheet):
    headers = {}

    for cell in sheet[1]:

        if cell.value:
            headers[str(cell.value).strip()] = cell.column

    return headers


# ==========================================================
# Write Build Metadata
# ==========================================================

def write_metadata(

        workbook,

        request,

        filename

):
    sheet = workbook[SHEET_BUILD_METADATA]

    headers = header_map(sheet)

    values = {

        "build_id":

            request["build_id"],

        "build_filename":

            filename,

        "requested_by":

            request["requested_by"],

        "learning_area":

            request["learning_area"],

        "subject":

            request["subject"],

        "year_level":

            request["year_level"],

        "strand":

            request["strand"],

        "parent_code":

            request["parent_code"],

        "selected_lessons":

            ",".join(

                map(

                    str,

                    request["lesson_numbers"]

                )

            ),

        "curriculum_version":

            CURRICULUM_VERSION,

        "workbook_version":

            WORKBOOK_VERSION,

        "created_at":

            datetime.now().strftime(

                DATE_TIME_FORMAT

            ),

        "build_status":

            STATUS_CREATED

    }

    #
    # Row 2 contains values
    #

    row = 2

    for field, value in values.items():

        if field not in headers:
            continue

        sheet.cell(

            row=row,

            column=headers[field]

        ).value = value
