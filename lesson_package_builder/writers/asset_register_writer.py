from config import SHEET_ASSET_REGISTER


# ==========================================================
# Worksheet Header Map
# ==========================================================

def header_map(sheet):
    headers = {}

    for cell in sheet[1]:

        if cell.value:
            headers[str(cell.value).strip()] = cell.column

    return headers


# ==========================================================
# Default Asset Types
# ==========================================================

ASSET_TYPES = [

    "PPTX",

    "GAMMA_SLIDES",

    "PDF",

    "THUMBNAIL",

    "WORKSHEET",

    "QUIZ_EXPORT",

    "ACTIVITY_FILES"

]


# ==========================================================
# Populate Asset Register
# ==========================================================

def write_asset_register(

        workbook,

        lesson_rows

):
    sheet = workbook[SHEET_ASSET_REGISTER]

    headers = header_map(sheet)

    row_number = 2

    asset_number = 1

    for lesson in lesson_rows:

        for asset_type in ASSET_TYPES:

            values = {

                "build_id":

                    lesson["build_id"],

                "lesson_package_id":

                    lesson["lesson_package_id"],

                "lesson_number":

                    lesson["lesson_number"],

                "curriculum_code":

                    lesson["curriculum_code"],

                "asset_number":

                    asset_number,

                "asset_type":

                    asset_type,

                "asset_name":

                    "",

                "asset_filename":

                    "",

                "asset_path":

                    "",

                "asset_url":

                    "",

                "mime_type":

                    "",

                "generation_status":

                    "PENDING",

                "review_status":

                    "NOT_STARTED"

            }

            for column, value in values.items():

                if column in headers:
                    sheet.cell(

                        row=row_number,

                        column=headers[column]

                    ).value = value

            row_number += 1

            asset_number += 1

    return row_number - 2
