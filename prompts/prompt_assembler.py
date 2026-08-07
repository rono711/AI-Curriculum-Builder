import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(

        0,

        str(PROJECT_ROOT)

    )

from shared.build_paths import BuildPaths
from workbook_reader import WorkbookReader
from template_loader import TemplateLoader
from placeholder_replacer import PlaceholderReplacer


# ==========================================================
# Prompt Assembler
# ==========================================================

class PromptAssembler:

    def __init__(

            self,

            workbook_path

    ):

        self.reader = WorkbookReader(

            workbook_path

        )

        self.templates = TemplateLoader()

    # ======================================================
    # Common Context
    # ======================================================

    def context(

            self,

            lesson_package_id

    ):

        metadata = self.reader.build_metadata()

        lesson = self.reader.lesson(

            lesson_package_id

        )

        context = {}

        #
        # Workbook Metadata
        #

        context.update(

            metadata

        )

        #
        # Lesson DB
        #

        context.update(

            lesson

        )

        #
        # Lesson Content
        #


        paths = BuildPaths(

            self.reader.workbook_path

        )

        lesson_file = (

                paths.content_folder

                / "lesson_output.md"

        )

        if lesson_file.exists():

            lesson_markdown = lesson_file.read_text(

                encoding="utf-8"

            )

        else:

            lesson_markdown = ""

        #
        # Additional Context
        #

        context["LESSON_CONTENT"] = lesson_markdown

        context["CURRICULUM_CODE"] = lesson.get(

            "curriculum_code",

            ""

        )

        context["YEAR_LEVEL"] = lesson.get(

            "year_level",

            ""

        )

        context["SUBJECT"] = lesson.get(

            "subject",

            ""

        )

        context["TOPIC"] = lesson.get(

            "lesson_title",

            ""

        )

        context["CONTENT_DESCRIPTION"] = lesson.get(

            "content_description",

            ""

        )

        context["ELABORATION"] = lesson.get(

            "elaboration",

            ""

        )

        return context

    # ======================================================
    # Assemble Prompt
    # ======================================================

    def assemble(

            self,

            lesson_package_id,

            prompt_type

    ):

        context = self.context(

            lesson_package_id

        )

        replacer = PlaceholderReplacer(

            context

        )

        prompt_type = prompt_type.upper()

        #
        # Base templates
        #

        templates = [

            self.templates.common(

                "system.md"

            ),

            self.templates.common(

                "branding.md"

            ),

            self.templates.common(

                "accessibility.md"

            ),

            self.templates.curriculum(

                "australian_v9.md"

            )

        ]

        #
        # Teaching Model
        #

        teaching_model = (

                context.get(

                    "teaching_model",

                    "explicit"

                )

                .lower()

                .replace(

                    " ",

                    "_"

                )

                + ".md"

        )

        templates.append(

            self.templates.pedagogy(

                teaching_model

            )

        )

        #
        # Year Level
        #

        year = str(

            context["year_level"]

        ).lower()

        if "foundation" in year:

            templates.append(

                self.templates.year_level(

                    "foundation.md"

                )

            )

        elif "year 1" in year or "year 2" in year:

            templates.append(

                self.templates.year_level(

                    "primary.md"

                )

            )

        else:

            templates.append(

                self.templates.year_level(

                    "secondary.md"

                )

            )

        #
        # Subject
        #

        subject = (

                str(

                    context["subject"]

                )

                .lower()

                .replace(

                    " ",

                    "_"

                )

                + ".md"

        )

        templates.append(

            self.templates.subject(

                subject

            )

        )

        #
        # Output Template
        #
        if prompt_type == "LESSON_CONTENT":

            templates.append(

                self.templates.teacher(

                    "lesson.md"

                )
            )
        elif prompt_type == "DISPLAY_TITLE":

            templates.append(

                self.templates.display_title(

                    "display_title.md"

                )

            )
        elif prompt_type == "MISSION":

            templates.append(
                self.templates.descriptions(
                    "mission_of_the_day.md"
            )
        )
        elif prompt_type == "GAMMA_SLIDES":

            templates.append(

                self.templates.gamma(

                    "gamma_slides.md"

                )

            )

        elif prompt_type == "DID_YOU_KNOW":

            templates.append(

                self.templates.descriptions(

                    "did_you_know.md"

                )
            )
        elif prompt_type == "QUIZ":

            templates.append(

                self.templates.quiz(

                    "quiz.md"

                )
            )
        elif prompt_type == "CHECKING_YOUR_THINKING":

            templates.append(

                self.templates.descriptions(

                    "checking_your_thinking.md"

                )
            )
        elif prompt_type == "ACTIVITIES":

            templates.append(

                self.templates.activities(

                    "activities.md"
                )
            )
        elif prompt_type == "LETS_DO_IT":

            templates.append(

                self.templates.descriptions(

                    "lets_do_it.md"
                )
            )
        elif prompt_type == "RECAP":

            templates.append(

                self.templates.recap(

                    "recap.md"

                )
            )
        elif prompt_type == "WHAT_WE_DISCOVERED":

            templates.append(

                self.templates.descriptions(

                    "what_we_discovered.md"

                )
            )
        elif prompt_type == "WORKSHEET":

            templates.append(

                self.templates.worksheet(

                    "worksheet.md"

                )
            )

        elif prompt_type == "NOTEBOOKLM":

            templates.append(

                self.templates.notebooklm(

                    "notebooklm.md"

                )
            )

        #
        # Build Prompt
        #
        print("=" * 60)
        print("PROMPT CONTEXT")
        print("Year Level :", context.get("year_level"))
        print("Subject    :", context.get("subject"))
        print("Topic      :", context.get("lesson_title"))
        print("Code       :", context.get("curriculum_code"))
        print("Content    :", context.get("content_description"))
        print("Elaboration:", context.get("elaboration"))
        print("=" * 60)

        lesson = context.get("LESSON_CONTENT", "")

        print("LESSON LENGTH:", len(lesson))

        print("LESSON PREVIEW")
        print(lesson[:1000])

        print("=" * 60)
        prompt = replacer.assemble(

            templates

        )

        return prompt

    # ======================================================
    # Close
    # ======================================================

    def close(self):

        self.reader.close()
