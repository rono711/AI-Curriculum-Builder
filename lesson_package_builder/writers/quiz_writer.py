from config import (
    SHEET_QUIZ,
    QUIZ_STRUCTURE
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
# Create Quiz Worksheet
# ==========================================================

def write_quiz(

        workbook,

        lesson_rows

):
    sheet = workbook[SHEET_QUIZ]

    headers = header_map(sheet)

    row_number = 2

    question_number = 1

    for lesson in lesson_rows:

        for question_type, quantity in QUIZ_STRUCTURE.items():

            for _ in range(quantity):

                values = {

                    "lesson_package_id":

                        lesson["lesson_package_id"],

                    "lesson_number":

                        lesson["lesson_number"],

                    "question_number":

                        question_number,

                    "question_type":

                        question_type,

                    "difficulty":

                        "",

                    "question":

                        "",

                    "option_a":

                        "",

                    "option_b":

                        "",

                    "option_c":

                        "",

                    "option_d":

                        "",

                    "correct_answer":

                        "",

                    "feedback":

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

                question_number += 1

    return row_number - 2
