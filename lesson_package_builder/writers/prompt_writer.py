from config import SHEET_PROMPT_QUEUE


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
# Prompt Types
# ==========================================================

PROMPT_TYPES = [

    "LESSON_CONTENT",

    "DISPLAY_TITLE",

    "GAMMA_SLIDES",

    "QUIZ",

    "ACTIVITIES",

    "RECAP",

    "WORKSHEET",

    "TEACHER_GUIDE",

    "NOTEBOOKLM"

]


# ==========================================================
# Populate Prompt Queue
# ==========================================================

def write_prompt_queue(

        workbook,

        lesson_rows

):
    sheet = workbook[SHEET_PROMPT_QUEUE]

    headers = header_map(sheet)

    row_number = 2

    prompt_number = 1

    for lesson in lesson_rows:

        for prompt_type in PROMPT_TYPES:

            values = {

                #
                # Build
                #

                "build_id":

                    lesson["build_id"],

                #
                # Lesson
                #

                "lesson_package_id":

                    lesson["lesson_package_id"],

                "learning_area":

                    lesson["learning_area"],

                "subject":

                    lesson["subject"],

                "year_level":

                    lesson["year_level"],

                "school_level":

                    lesson["school_level"],

                "strand":

                    lesson["strand"],

                "sub_strand":

                    lesson["sub_strand"],

                "parent_code":

                    lesson["parent_code"],

                "topic_id":

                    lesson["topic_id"],

                "curriculum_code":

                    lesson["curriculum_code"],

                "lesson_number":

                    lesson["lesson_number"],

                "lesson_title":

                    lesson["lesson_title"],

                "content_description":

                    lesson["content_description"],

                "elaboration":

                    lesson["elaboration"],

                #
                # Prompt
                #

                "prompt_id":

                    f"PR_{prompt_number:06d}",

                "prompt_type":

                    prompt_type,

                "prompt_definition_id":

                    "",

                "prompt_library_id":

                    "",

                "prompt":

                    "",

                "response":

                    "",

                #
                # Workflow
                #

                "status":

                    "PENDING",

                "generation_status":

                    "PENDING",

                "review_status":

                    "NOT_STARTED",

                "started_at":

                    "",

                "completed_at":

                    "",

                "completed_by":

                    "",

                "error":

                    ""

            }

            for column, value in values.items():

                if column in headers:
                    sheet.cell(

                        row=row_number,

                        column=headers[column]

                    ).value = value

            row_number += 1

            prompt_number += 1

    return row_number - 2
