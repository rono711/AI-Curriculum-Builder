from config import SHEET_LESSON_METADATA


# ==========================================================
# Header Map
# ==========================================================

def header_map(sheet):

    headers = {}

    for cell in sheet[1]:

        if cell.value:
            headers[str(cell.value).strip()] = cell.column

    return headers


# ==========================================================
# Write Lesson Metadata
# ==========================================================

def write_lesson_metadata(
        workbook,
        lesson_rows,
        request
):

    sheet = workbook[SHEET_LESSON_METADATA]

    headers = header_map(sheet)

    row = 2

    for lesson in lesson_rows:

        values = {

            "lesson_package_id":
                lesson["lesson_package_id"],

            "build_id":
                request["build_id"],

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
                lesson["elaboration"]

        }

        for field, value in values.items():

            if field not in headers:
                continue

            sheet.cell(
                row=row,
                column=headers[field]
            ).value = value

        row += 1