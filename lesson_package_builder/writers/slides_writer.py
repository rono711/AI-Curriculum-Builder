from config import SHEET_SLIDES


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
# Create Slides Worksheet
# ==========================================================

def write_slides(

        workbook,

        lesson_rows

):
    sheet = workbook[SHEET_SLIDES]

    headers = header_map(sheet)

    row_number = 2

    for lesson in lesson_rows:

        values = {

            "lesson_package_id":

                lesson["lesson_package_id"],

            "lesson_number":

                lesson["lesson_number"],

            "lesson_title":

                lesson["lesson_title"],

            "curriculum_code":

                lesson["curriculum_code"],

            "slides_status":

                "PENDING",

            "gamma_slides_id":

                "",

            "gamma_slides_url":

                "",
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

    return len(lesson_rows)
