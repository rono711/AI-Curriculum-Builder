import html
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )

from workbook_reader import WorkbookReader
from moodle_client import MoodleClient
from sync_writer import SyncWriter


# ==========================================================
# Publisher Builder
# ==========================================================

class PublisherBuilder:

    def __init__(self):

        self.reader = WorkbookReader()

        self.moodle = MoodleClient()

        self.sync = SyncWriter()

    # ======================================================
    # Helpers
    # ======================================================

    @staticmethod
    def _text(value):

        if value is None:
            return ""

        return str(value).strip()

    @staticmethod
    def _read_text_file(path):

        path = Path(path)

        if not path.exists():
            return ""

        return path.read_text(
            encoding="utf-8"
        )

    # ======================================================
    # Lesson Content
    # ======================================================

    def _build_lesson_content(
            self,
            build_root,
            build_name
    ):

        lesson_file = (
            Path(build_root)
            / "Content"
            / build_name
            / "lesson_output.md"
        )

        lesson_markdown = self._read_text_file(
            lesson_file
        )

        if not lesson_markdown:
            return ""

        #
        # Preserve the existing Publisher behaviour for the
        # first production integration test.
        #

        return (
                "<pre>\n"
                + html.escape(lesson_markdown)
                + "\n</pre>"
        )

        return (
            "<pre>\n"
            + html.escape(lesson_markdown)
            + "\n</pre>"
        )

    # ======================================================
    # Did You Know / Gamma
    # ======================================================

    def _build_did_you_know(
            self,
            build_root,
            build_name,
            slides
    ):

        slides_folder = (
            Path(build_root)
            / "Slides"
            / build_name
        )

        urls_file = (
            slides_folder
            / "slides_urls.json"
        )

        embed_url = ""

        if urls_file.exists():

            data = json.loads(
                urls_file.read_text(
                    encoding="utf-8"
                )
            )

            embed_url = self._text(
                data.get("gamma_embed_url")
            )
        #
        # Workbook fallback.
        #

        if not lesson_markdown:
            return ""


        return (
            "<pre>\n"
            + html.escape(lesson_markdown)
            + "\n</pre>"
        )
        if not embed_url:

            embed_url = self._text(
                slides.get("gamma_embed_url")
            )

        #
        # If the workbook already contains complete embed HTML,
        # use it as a second fallback.
        #
        if not embed_url:

            embed_html = self._text(
                slides.get("slides_embed_html")
            )

            if embed_html:
                return embed_html

        if not embed_url:
            return ""

        safe_url = html.escape(
            embed_url,
            quote=True
        )

        return (
            '<iframe '
            f'src="{safe_url}" '
            'width="100%" '
            'height="720" '
            'allowfullscreen>'
            '</iframe>'
        )

    # ======================================================
    # Activities
    # ======================================================

    def _build_activities(
            self,
            build_root,
            build_name,
            activities
    ):

        activities_file = (
            Path(build_root)
            / "Activities"
            / build_name
            / "activities.html"
        )

        content = self._read_text_file(
            activities_file
        )

        if content:
            return content

        return self._text(
            activities.get("activities_html")
        )

    # ======================================================
    # Recap
    # ======================================================

    def _build_recap(
            self,
            build_root,
            build_name,
            recap
    ):

        recap_file = (
            Path(build_root)
            / "Recap"
            / build_name
            / "recap.html"
        )

        content = self._read_text_file(
            recap_file
        )

        if content:
            return content

        return self._text(
            recap.get("recap_html")
        )

    # ======================================================
    # Quiz Content
    # ======================================================

    def _build_quiz_content(
            self,
            build_root,
            build_name,
            quiz
    ):

        #
        # Prefer the GIFT content already stored in the workbook.
        #
        gift_content = self._text(
            quiz.get("gift_content")
        )

        if gift_content:
            return gift_content

        #
        # Fallback to generated .gift file.
        #
        gift_filename = self._text(
            quiz.get("gift_filename")
        )

        if not gift_filename:
            return ""

        gift_file = (
            Path(build_root)
            / "Quiz"
            / build_name
            / gift_filename
        )

        return self._read_text_file(
            gift_file
        )
    # ======================================================
    # Moodle Course Mapping
    # ======================================================

    def _resolve_course(
            self,
            subject,
            year_level
    ):

        mapping_file = (
            PROJECT_ROOT
            / "data"
            / "moodle_course_mapping.xlsx"
        )

        if not mapping_file.exists():
            raise RuntimeError(
                "Moodle course mapping file not found: "
                f"{mapping_file}"
            )

        from openpyxl import load_workbook

        workbook = load_workbook(
            mapping_file,
            read_only=True,
            data_only=True
        )

        try:

            if "Course_Mapping" not in workbook.sheetnames:
                raise RuntimeError(
                    "Course_Mapping worksheet not found in "
                    "moodle_course_mapping.xlsx"
                )

            sheet = workbook["Course_Mapping"]

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

            required_headers = [
                "subject",
                "year",
                "moodle_course_id",
            ]

            for field in required_headers:

                if field not in headers:
                    raise RuntimeError(
                        "Missing Moodle course mapping column: "
                        f"{field}"
                    )

            wanted_subject = self._text(
                subject
            ).casefold()

            wanted_year = self._text(
                year_level
            ).casefold()

            matches = []

            for row in range(
                    2,
                    sheet.max_row + 1
            ):

                mapped_subject = self._text(
                    sheet.cell(
                        row=row,
                        column=headers["subject"]
                    ).value
                )

                mapped_year = self._text(
                    sheet.cell(
                        row=row,
                        column=headers["year"]
                    ).value
                )

                if (
                    mapped_subject.casefold()
                    == wanted_subject
                    and
                    mapped_year.casefold()
                    == wanted_year
                ):

                    courseid = sheet.cell(
                        row=row,
                        column=headers[
                            "moodle_course_id"
                        ]
                    ).value

                    course_name = ""

                    if "moodle_course_name" in headers:

                        course_name = self._text(
                            sheet.cell(
                                row=row,
                                column=headers[
                                    "moodle_course_name"
                                ]
                            ).value
                        )

                    matches.append({
                        "courseid": int(courseid),
                        "name": course_name,
                    })

            if not matches:

                raise RuntimeError(
                    "No Moodle course mapping found for "
                    f"subject={subject!r}, "
                    f"year_level={year_level!r}"
                )

            if len(matches) > 1:

                raise RuntimeError(
                    "Multiple Moodle course mappings found for "
                    f"subject={subject!r}, "
                    f"year_level={year_level!r}"
                )

            return matches[0]

        finally:

            workbook.close()

    # ======================================================
    # Publish
    # ======================================================

    def publish(
            self,
            build_root,
            build_name,
            lesson_package_id
    ):

        workbook = (
            Path(build_root)
            / "Workbook"
            / f"{build_name}.xlsx"
        )

        print("=" * 60)
        print("PUBLISHER WORKBOOK")
        print(workbook)
        print("=" * 60)

        lesson = self.reader.read(
            workbook,
            lesson_package_id
        )

        metadata = lesson["metadata"]
        descriptions = lesson["descriptions"]
        slides = lesson["slides"]
        quiz = lesson["quiz"]
        activities = lesson["activities"]
        recap = lesson["recap"]

        print("=" * 60)
        print("LESSON METADATA")
        print(metadata)
        print("=" * 60)

        # ==================================================
        # Resolve existing Moodle course
        # ==================================================

        course = self._resolve_course(
            metadata["subject"],
            metadata["year_level"]
        )

        courseid = int(
            course["courseid"]
        )

        print("=" * 60)
        print("MOODLE COURSE MAPPING")
        print(
            "Subject:",
            metadata["subject"]
        )
        print(
            "Year:",
            metadata["year_level"]
        )
        print(
            "Course ID:",
            courseid
        )
        print(
            "Course Name:",
            course.get("name", "")
        )
        print("=" * 60)

        # ==================================================
        # Build generated lesson assets
        # ==================================================

        lesson_content = self._build_lesson_content(
            build_root,
            build_name
        )

        did_you_know = self._build_did_you_know(
            build_root,
            build_name,
            slides
        )

        quiz_content = self._build_quiz_content(
            build_root,
            build_name,
            quiz
        )

        activities_content = self._build_activities(
            build_root,
            build_name,
            activities
        )

        recap_content = self._build_recap(
            build_root,
            build_name,
            recap
        )

        # ==================================================
        # Validation
        # ==================================================

        if not lesson_content:
            raise RuntimeError(
                "Lesson Content is empty."
            )

        if not quiz_content:
            raise RuntimeError(
                "Quiz GIFT content is empty."
            )

        if not activities_content:
            raise RuntimeError(
                "Activities content is empty."
            )

        if not recap_content:
            raise RuntimeError(
                "Recap content is empty."
            )

        # ==================================================
        # Lesson title
        # ==================================================

        display_title = self._text(
            descriptions.get("display_title")
        )

        if not display_title:
            display_title = self._text(
                metadata.get("lesson_title")
            )

        if not display_title:
            display_title = self._text(
                metadata.get("elaboration")
            )

        curriculum_code = self._text(
            metadata.get("curriculum_code")
        )

        if curriculum_code:
            lesson_title = (
                f"{curriculum_code} - {display_title}"
            )
        else:
            lesson_title = display_title

        # ==================================================
        # Complete Moodle lesson payload
        # ==================================================

        payload = {

            "courseid":
                courseid,

            "strand":
                self._text(
                    metadata.get("strand")
                ),

            "substrand":
                self._text(
                    metadata.get("sub_strand")
                ),

            "contentdescription":
                self._text(
                    metadata.get(
                        "content_description"
                    )
                ),

            "lesson[title]":
                lesson_title,

            "lesson[lessoncontent]":
                lesson_content,

            "lesson[lessondescription]":
                self._text(
                    descriptions.get(
                        "mission_description"
                    )
                ),

            "lesson[didyouknow]":
                did_you_know,

            "lesson[didyouknowdescription]":
                self._text(
                    descriptions.get(
                        "slides_description"
                    )
                ),

            "lesson[quiztitle]":
                self._text(
                    quiz.get("quiz_title")
                )
                or
                self._text(
                    descriptions.get(
                        "quiz_title"
                    )
                )
                or
                "Checking Your Thinking",

            "lesson[quizdescription]":
                self._text(
                    descriptions.get(
                        "quiz_description"
                    )
                )
                or
                self._text(
                    quiz.get(
                        "quiz_description"
                    )
                ),

            "lesson[quizformat]":
                "gift",

            "lesson[quizcontent]":
                quiz_content,

            "lesson[activities]":
                activities_content,

            "lesson[activitiesdescription]":
                self._text(
                    descriptions.get(
                        "activities_description"
                    )
                )
                or
                self._text(
                    activities.get(
                        "activities_description"
                    )
                ),

            "lesson[recap]":
                recap_content,

            "lesson[recapdescription]":
                self._text(
                    descriptions.get(
                        "recap_description"
                    )
                )
                or
                self._text(
                    recap.get(
                        "recap_description"
                    )
                ),
        }

        # ==================================================
        # Validate structural metadata
        # ==================================================

        for required in [
            "strand",
            "substrand",
            "contentdescription",
            "lesson[title]",
        ]:

            if not payload[required]:

                raise RuntimeError(
                    f"Required Moodle field is empty: "
                    f"{required}"
                )

        print("=" * 60)
        print("RONO PUBLISHER PAYLOAD")
        print(
            {
                **payload,
                "lesson[quizcontent]":
                    f"<GIFT {len(quiz_content)} chars>",
                "lesson[lessoncontent]":
                    f"<CONTENT {len(lesson_content)} chars>",
                "lesson[activities]":
                    f"<ACTIVITIES {len(activities_content)} chars>",
                "lesson[recap]":
                    f"<RECAP {len(recap_content)} chars>",
            }
        )
        print("=" * 60)

        # ==================================================
        # ONE atomic Moodle lesson publication
        # ==================================================

        published = self.moodle.publish_lesson(
            payload
        )

        print("=" * 60)
        print("RONO PUBLISHER RESULT")
        print(published)
        print("=" * 60)

        # ==================================================
        # Verify Moodle result
        # ==================================================

        if (
            published.get("status")
            != "success"
        ):

            raise RuntimeError(
                "Moodle lesson publishing did not "
                "return success."
            )

        if int(
            published.get(
                "questioncount",
                0
            )
        ) <= 0:

            raise RuntimeError(
                "Moodle published the lesson but "
                "reported zero imported questions."
            )

        if int(
            published.get(
                "slotcount",
                0
            )
        ) <= 0:

            raise RuntimeError(
                "Moodle published the Quiz but "
                "reported zero Quiz slots."
            )

        # ==================================================
        # Update Moodle_Publish worksheet
        # ==================================================

        self.sync.update(
            workbook,
            lesson_package_id,
            published
        )

        print("=" * 60)
        print("MOODLE_PUBLISH WORKBOOK UPDATED")
        print(lesson_package_id)
        print("=" * 60)

        # ==================================================
        # Return
        # ==================================================

        return {

            "status":
                "SUCCESS",

            "lesson_package_id":
                lesson_package_id,

            "course":
                course,

            "publisher":
                published,

            "quiz": {

                "quizid":
                    published.get(
                        "quizid"
                    ),

                "cmid":
                    published.get(
                        "quizcmid"
                    ),

                "contextid":
                    published.get(
                        "quizcontextid"
                    ),

                "questioncount":
                    published.get(
                        "questioncount"
                    ),

                "slotcount":
                    published.get(
                        "slotcount"
                    ),

                "sumgrades":
                    published.get(
                        "quizsumgrades"
                    ),
            },

            "mission": {

                "cmid":
                    published.get(
                        "lessoncontentcmid"
                    )
            },

            "did_you_know": {

                "cmid":
                    published.get(
                        "didyouknowcmid"
                    )
            },

            "activities": {

                "cmid":
                    published.get(
                        "activitiescmid"
                    )
            },

            "recap": {

                "cmid":
                    published.get(
                        "recapcmid"
                    )
            },
        }