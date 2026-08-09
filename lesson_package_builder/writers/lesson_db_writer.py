import pandas as pd

from config import (
    MASTER_LESSON_DB,
    SHEET_LESSON_DB
)

# ==========================================================
# Master Lesson DB  -> Workbook Column Mapping
# ==========================================================

COLUMN_MAP = {

    "Learning Area": "learning_area",

    "Subject": "subject",

    "Year Level": "year_level",

    "Strand": "strand",

    "Sub-Strand": "sub_strand",

    "Parent Code": "parent_code",

    "Topic ID": "topic_id",

    "Curriculum Code": "curriculum_code",

    "Content Description": "content_description",

    "Topic Lesson Number": "lesson_number",

    "Topics": "lesson_title",

    "Elaboration": "elaboration"

}


# ==========================================================
# Worksheet Header Map
# ==========================================================

def header_map(sheet):
    headers = {}

    for cell in sheet[1]:

        if not cell.value:
            continue

        key = (
            str(cell.value)
            .strip()
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

        headers[key] = cell.column

    return headers


# ==========================================================
# Read Master Lesson DB
# ==========================================================

def read_master_db():

    df = pd.read_excel(
        MASTER_LESSON_DB,
        dtype=object
    )

    df = df.fillna("")

    return df

# ==========================================================
# Selected Lessons
# ==========================================================

def selected_lessons(request):
    df = read_master_db()

    df = df[

        (df["Learning Area"] == request["learning_area"])

        &

        (df["Subject"] == request["subject"])

        &

        (df["Year Level"] == request["year_level"])

        &

        (df["Strand"] == request["strand"])

        &

        (df["Parent Code"] == request["parent_code"])

        &

        (

            df["Topic Lesson Number"]

            .isin(

                request["lesson_numbers"]

            )

        )

        ]

    df = df.sort_values(

        "Topic Lesson Number"

    )

    print("=" * 60)
    print("SELECTED LESSONS")
    print("Rows:", len(df))
    print("Columns:")
    print(df.columns.tolist())
    print(df.head())
    print("=" * 60)

    return df


# ==========================================================
# Populate Lesson_DB Worksheet
# ==========================================================

def write_lesson_db(

        workbook,

        request

):
    sheet = workbook[SHEET_LESSON_DB]

    headers = header_map(sheet)

    lessons = selected_lessons(request)

    lesson_rows = []

    row_number = 2

    sequence = 1

    for _, lesson in lessons.iterrows():

        #
        # Generate Lesson Package ID
        #

        lesson_package_id = (

            f"LP_"

            f"{request['build_id']:06d}_"

            f"{sequence:03d}"

        )

        #
        # Builder-generated values
        #

        generated = {

            "build_id":
                request["build_id"],

            "lesson_package_id":
                lesson_package_id,

            "lesson_status":
                "CREATED",

            "review_status":
                "NOT_STARTED"

        }

        #
        # Copy curriculum fields
        #

        for source_column, target_column in COLUMN_MAP.items():

            if target_column not in headers:
                continue

            sheet.cell(

                row=row_number,

                column=headers[target_column]

            ).value = lesson[source_column]

        #
        # Copy generated fields
        #

        for column, value in generated.items():

            if column not in headers:
                continue

            sheet.cell(

                row=row_number,

                column=headers[column]

            ).value = value

        #
        # Build lesson object
        # for remaining writers
        #

        lesson_rows.append({

            #
            # Build
            #

            "build_id":

                request["build_id"],

            "lesson_package_id":

                lesson_package_id,

            #
            # Curriculum
            #

            "learning_area":

                lesson["Learning Area"],

            "subject":

                lesson["Subject"],

            "year_level":

                lesson["Year Level"],

            "school_level":

                lesson["School Level"],

            "strand":

                lesson["Strand"],

            "sub_strand":

                lesson["Sub-Strand"],

            "parent_code":

                lesson["Parent Code"],

            "topic_id":

                lesson["Topic ID"],

            "curriculum_code":

                lesson["Curriculum Code"],

            #
            # Lesson
            #

            "lesson_number":

                int(

                    lesson["Topic Lesson Number"]

                ),

            "lesson_title":

                lesson["Topics"],

            "content_description":

                lesson["Content Description"],

            "elaboration":

                lesson["Elaboration"],

            #
            # Workflow
            #

            "generation_status":

                "PENDING",

            "review_status":

                "NOT_STARTED",

            "publication_status":

                "NOT_PUBLISHED"

        })

        row_number += 1
        sequence += 1

    #
    # Return lesson rows for downstream writers
    #

    return lesson_rows
