from datetime import datetime

from openpyxl import load_workbook


# ==========================================================
# Sync Writer
# ==========================================================

class SyncWriter:

    # ======================================================
    # Header Map
    # ======================================================

    @staticmethod
    def header_map(sheet):

        headers = {}

        for cell in sheet[1]:

            if cell.value:

                headers[str(cell.value).strip()] = cell.column

        return headers

    # ======================================================
    # Update Workbook
    # ======================================================

    def update(

            self,

            workbook_path,

            lesson_package_id,

            course,

            section,

            mission,

            quiz,

            activities,

            recap

    ):

        workbook = load_workbook(

            workbook_path

        )

        sheet = workbook[

            "Moodle_Publish"

        ]

        headers = self.header_map(

            sheet

        )

        row = 2

        while True:

            value = sheet.cell(

                row=row,

                column=headers["lesson_package_id"]

            ).value

            if not value:

                break

            if str(value) == str(

                    lesson_package_id

            ):

                #
                # Course
                #

                self.write(

                    sheet,

                    headers,

                    row,

                    "course_id",

                    course.get(

                        "courseid",

                        ""

                    )

                )

                #
                # Section
                #

                self.write(

                    sheet,

                    headers,

                    row,

                    "section_id",

                    section.get(

                        "sectionid",

                        ""

                    )

                )

                #
                # Mission
                #

                self.write(

                    sheet,

                    headers,

                    row,

                    "mission_pageid",

                    mission.get(

                        "pageid",

                        ""

                    )

                )

                self.write(

                    sheet,

                    headers,

                    row,

                    "mission_cmid",

                    mission.get(

                        "cmid",

                        ""

                    )

                )

                #
                # Quiz
                #

                self.write(

                    sheet,

                    headers,

                    row,

                    "quizid",

                    quiz.get(

                        "quizid",

                        ""

                    )

                )

                self.write(

                    sheet,

                    headers,

                    row,

                    "quiz_cmid",

                    quiz.get(

                        "cmid",

                        ""

                    )

                )

                #
                # Activities
                #

                self.write(

                    sheet,

                    headers,

                    row,

                    "activities_pageid",

                    activities.get(

                        "pageid",

                        ""

                    )

                )

                self.write(

                    sheet,

                    headers,

                    row,

                    "activities_cmid",

                    activities.get(

                        "cmid",

                        ""

                    )

                )

                #
                # Recap
                #

                self.write(

                    sheet,

                    headers,

                    row,

                    "recap_pageid",

                    recap.get(

                        "pageid",

                        ""

                    )

                )

                self.write(

                    sheet,

                    headers,

                    row,

                    "recap_cmid",

                    recap.get(

                        "cmid",

                        ""

                    )

                )

                #
                # URL
                #

                self.write(

                    sheet,

                    headers,

                    row,

                    "activity_url",

                    mission.get(

                        "url",

                        ""

                    )

                )

                #
                # Publish
                #

                self.write(

                    sheet,

                    headers,

                    row,

                    "publication_status",

                    "PUBLISHED"

                )

                self.write(

                    sheet,

                    headers,

                    row,

                    "last_synced",

                    datetime.now()

                )

                self.write(

                    sheet,

                    headers,

                    row,

                    "needs_sync",

                    "NO"

                )

                break

            row += 1

        workbook.save(

            workbook_path

        )

        workbook.close()

    # ======================================================
    # Write
    # ======================================================

    def write(

            self,

            sheet,

            headers,

            row,

            field,

            value

    ):

        if field in headers:

            sheet.cell(

                row=row,

                column=headers[field]

            ).value = value