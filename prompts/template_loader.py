from pathlib import Path

from config import TEMPLATES_FOLDER


# ==========================================================
# Template Loader
# ==========================================================

class TemplateLoader:

    def __init__(self):

        self.root = TEMPLATES_FOLDER

    # ======================================================
    # Read Markdown File
    # ======================================================

    @staticmethod
    def read(file_path):

        file_path = Path(file_path)

        if not file_path.exists():

            raise FileNotFoundError(

                f"Template not found: {file_path}"

            )

        return file_path.read_text(

            encoding="utf-8"

        )

    # ======================================================
    # Load Relative Template
    # ======================================================

    def load(

            self,

            *parts

    ):

        file_path = self.root.joinpath(

            *parts

        )

        return self.read(

            file_path

        )

    # ======================================================
    # Common
    # ======================================================

    def common(

            self,

            name

    ):

        return self.load(

            "common",

            name

        )

    # ======================================================
    # Pedagogy
    # ======================================================

    def pedagogy(

            self,

            name

    ):

        return self.load(

            "pedagogy",

            name

        )

    # ======================================================
    # Curriculum
    # ======================================================

    def curriculum(

            self,

            name

    ):

        return self.load(

            "curriculum",

            name

        )

    # ======================================================
    # Year Level
    # ======================================================

    def year_level(

            self,

            name

    ):

        return self.load(

            "year_level",

            name

        )

    # ======================================================
    # Subject
    # ======================================================

    def subject(

            self,

            name

    ):

        return self.load(

            "subject",

            name

        )

    # ======================================================
    # Gamma
    # ======================================================

    def gamma(

            self,

            name

    ):

        return self.load(

            "gamma",

            name

        )

    # ======================================================
    # Teacher
    # ======================================================

    def teacher(

            self,

            name

    ):

        return self.load(

            "teacher",

            name

        )

    # ======================================================
    # Quiz
    # ======================================================

    def quiz(

            self,

            name

    ):

        return self.load(

            "quiz",

            name

        )

    # ======================================================
    # Activities
    # ======================================================

    def activities(

            self,

            name

    ):

        return self.load(

            "activities",

            name

        )

    # ======================================================
    # Recap
    # ======================================================

    def recap(

            self,

            name

    ):

        return self.load(

            "recap",

            name

        )

    # ======================================================
    # Display Title
    # ======================================================

    def display_title(

            self,

            name

    ):
        return self.load(

            "display_title",

            name

        )

    # ======================================================
    # Descriptions
    # ======================================================

    def descriptions(

            self,

            name

    ):

        return self.load(

            "descriptions",

            name

        )

    # ======================================================
    # Image
    # ======================================================

    def image(

            self,

            name

    ):

        return self.load(

            "image",

            name

        )

    # ======================================================
    # Worksheet
    # ======================================================

    def worksheet(

            self,

            name

    ):

        return self.load(

            "worksheet",

            name

        )

    # ======================================================
    # NotebookLM
    # ======================================================

    def notebooklm(

            self,

            name

    ):

        return self.load(

            "notebooklm",

            name

        )
