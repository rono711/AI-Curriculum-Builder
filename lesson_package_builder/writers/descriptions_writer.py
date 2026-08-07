from config import (
    SHEET_DESCRIPTIONS
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
# Create Descriptions Worksheet
# ==========================================================

def write_descriptions(

        workbook,

        lesson_rows

):

    sheet = workbook[

        SHEET_DESCRIPTIONS

    ]

    headers = header_map(

        sheet

    )

    row_number = 2

    for lesson in lesson_rows:

        values = {

            "lesson_package_id":

                lesson["lesson_package_id"],

            "curriculum_code":

                lesson["curriculum_code"],

            "topic_id":

                lesson["topic_id"],

            "lesson_title":

                lesson["lesson_title"],

            "display_title": "",

            "display_subtitle": "",

            "lesson_overview": "",

            "mission_title": "",

            "mission_description": "",

            "quiz_title": "",

            "quiz_description": "",

            "activities_title": "",

            "activities_description": "",

            "activities_json": "",

            "recap_title": "",

            "recap_description": "",

            "teacher_notes": "",

            "home_learning_description": "",

            "generation_status":

                "PENDING",

            "review_status":

                "NOT_STARTED",

            "description_hash": ""

        }

        for column, value in values.items():

            if column in headers:

                sheet.cell(

                    row=row_number,

                    column=headers[column]

                ).value = value

        row_number += 1

    return row_number - 2