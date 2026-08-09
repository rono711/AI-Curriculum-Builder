from config import SHEET_MOODLE_PUBLISH


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
# Populate Moodle Publish Worksheet
# ==========================================================

def write_moodle_publish(

        workbook,

        lesson_rows

):
    sheet = workbook[SHEET_MOODLE_PUBLISH]

    headers = header_map(sheet)

    row_number = 2

    for lesson in lesson_rows:

        values = {

            "build_id":

                lesson["build_id"],

            "lesson_package_id":

                lesson["lesson_package_id"],

            "learning_area":

                lesson["learning_area"],

            "subject":

                lesson["subject"],

            "year_level":

                lesson["year_level"],

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

            "course_id":

                "",

            "section_id":

                "",

            "page_id":

                "",

            "cmid":

                "",

            "activity_url":

                "",

            "publish_version":

                "1.0",

            "publication_status":

                "PENDING",

            "needs_sync":

                 "YES",

            "payload_hash":

                "",

            "published_at":

                "",

            "last_synced":

                ""

        }

        for column, value in values.items():

            if column in headers:
                sheet.cell(

                    row=row_number,

                    column=headers[column]

                ).value = value

        row_number += 1

    return row_number - 2
