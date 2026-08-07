from typing import Any
from config import SHEET_AI_GENERATION

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
# AI Generation Queue
# ==========================================================

AI_STAGES = [

    ("LESSON_CONTENT", "CHATGPT"),

    ("MISSION", "CHATGPT"),

    ("GAMMA_SLIDES", "GAMMA"),

    ("DID_YOU_KNOW", "CHATGPT"),

    ("QUIZ", "CHATGPT"),

    ("CHECKING_YOUR_THINKING", "CHATGPT"),

    ("ACTIVITIES", "CHATGPT"),

    ("LETS_DO_IT", "CHATGPT"),

    ("RECAP", "CHATGPT"),

    ("WHAT_WE_DISCOVERED", "CHATGPT"),

    ("WORKSHEET", "CHATGPT"),

    ("NOTEBOOKLM", "NOTEBOOKLM")

]


# ==========================================================
# Populate AI Generation Worksheet
# ==========================================================

def write_ai_generation(

        workbook: object,

        lesson_rows: object

) -> Any:

    sheet = workbook[

        SHEET_AI_GENERATION

    ]

    headers = header_map(

        sheet

    )

    row_number = 2

    job_number = 1

    for lesson in lesson_rows:

        for prompt_type, provider in AI_STAGES:

            values = {

                "job_id":

                    f"AI_{job_number:05d}",

                "lesson_package_id":

                    lesson["lesson_package_id"],

                "lesson_number":

                    lesson["lesson_number"],

                "curriculum_code":

                    lesson["curriculum_code"],

                "prompt_type":

                    prompt_type,

                "provider":

                    provider,

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

            job_number += 1

    return row_number - 2