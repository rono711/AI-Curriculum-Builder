from pathlib import Path


# ==========================================================
# Build Paths
# ==========================================================

class BuildPaths:

    def __init__(self, workbook_path):

        self.workbook = Path(workbook_path)

        #
        # Example:
        # BLD_20260712_000079.xlsx
        #

        self.build_name = self.workbook.stem

        #
        # builds/YYYY/MM
        #

        self.build_root = self.workbook.parent.parent

    # ======================================================
    # Workbook
    # ======================================================

    @property
    def workbook_folder(self):
        return self.build_root / "Workbook"

    # ======================================================
    # Prompts
    # ======================================================

    @property
    def prompts_folder(self):
        return self.build_root / "Prompts" / self.build_name

    # ======================================================
    # AI
    # ======================================================

    @property
    def content_folder(self):
        return self.build_root / "Content" / self.build_name

    # ======================================================
    # Slides
    # ======================================================

    @property
    def slides_folder(self):
        return self.build_root / "Slides" / self.build_name

    # ======================================================
    # Quiz
    # ======================================================

    @property
    def quiz_folder(self):
        return self.build_root / "Quiz" / self.build_name

    # ======================================================
    # Activities
    # ======================================================

    @property
    def activities_folder(self):
        return self.build_root / "Activities" / self.build_name

    # ======================================================
    # Recap
    # ======================================================

    @property
    def recap_folder(self):
        return self.build_root / "Recap" / self.build_name

    # ======================================================
    # Moodle
    # ======================================================

    @property
    def moodle_folder(self):
        return self.build_root / "Moodle" / self.build_name

    # ======================================================
    # Logs
    # ======================================================

    @property
    def logs_folder(self):
        return self.build_root / "Logs"

    # ======================================================
    # Temp
    # ======================================================

    @property
    def temp_folder(self):
        return self.build_root / "Temp"