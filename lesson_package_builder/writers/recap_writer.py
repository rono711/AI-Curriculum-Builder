from config import SHEET_RECAP


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
# Create Recap Worksheet
# ==========================================================

def write_recap(

        workbook,

        lesson_rows

):
    sheet = workbook[SHEET_RECAP]

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

            "lesson_summary": "",

            "exit_ticket": "",

            "homework": "",

            "extension": "",

            "reflection": "",

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

    return row_number - 1
