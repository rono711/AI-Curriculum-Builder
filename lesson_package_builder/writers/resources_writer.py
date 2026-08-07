from config import SHEET_RESOURCES


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
# Default Resources
# ==========================================================

RESOURCE_TYPES = [

    "WORKSHEET",

    "PRESENTATION",

    "PDF",

    "IMAGE",

    "VIDEO",

    "AUDIO",

    "LINK"

]


# ==========================================================
# Populate Resources Worksheet
# ==========================================================

def write_resources(

        workbook,

        lesson_rows

):
    sheet = workbook[SHEET_RESOURCES]

    headers = header_map(sheet)

    row_number = 2

    resource_number = 1

    for lesson in lesson_rows:

        for resource_type in RESOURCE_TYPES:

            values = {

                "build_id":

                    lesson["build_id"],

                "lesson_package_id":

                    lesson["lesson_package_id"],

                "lesson_number":

                    lesson["lesson_number"],

                "curriculum_code":

                    lesson["curriculum_code"],

                "resource_number":

                    resource_number,

                "resource_type":

                    resource_type,

                "title":

                    "",

                "filename":

                    "",

                "filepath":

                    "",

                "url":

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

            resource_number += 1

    return row_number - 2
