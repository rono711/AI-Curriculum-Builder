from config import (
    SHEET_ACTIVITIES,
    ACTIVITY_TYPES
)


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
# Create Activities Worksheet
# ==========================================================

def write_activities(

        workbook,

        lesson_rows

):
    sheet = workbook[SHEET_ACTIVITIES]

    headers = header_map(sheet)

    row_number = 2

    activity_number = 1

    for lesson in lesson_rows:

        for activity_type in ACTIVITY_TYPES:

            values = {

                "lesson_package_id":

                    lesson["lesson_package_id"],

                "lesson_number":

                    lesson["lesson_number"],

                "activity_number":

                    activity_number,

                "activity_type":

                    activity_type,

                "title": "",

                "instructions": "",

                "resources": "",

                "answer_key": "",

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

            activity_number += 1

    return row_number - 2
