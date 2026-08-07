from pathlib import Path
import json
from datetime import datetime


# ==========================================================
# Prompt Asset Writer
# ==========================================================

class PromptAssetWriter:

    def __init__(

            self,

            output_folder

    ):
        self.output_folder = Path(

            output_folder

        )

        self.output_folder.mkdir(

            parents=True,

            exist_ok=True

        )

    # ======================================================
    # Markdown
    # ======================================================

    def markdown(

            self,

            filename,

            prompt

    ):
        file = self.output_folder / filename

        file.write_text(

            prompt,

            encoding="utf-8"

        )

        return file

    # ======================================================
    # JSON Metadata
    # ======================================================

    def metadata(

            self,

            filename,

            lesson,

            prompt_type,

            prompt_file

    ):
        file = self.output_folder / filename

        data = {

            "generated_at":

                datetime.now().isoformat(),

            "lesson_package_id":

                lesson["lesson_package_id"],

            "curriculum_code":

                lesson["curriculum_code"],

            "lesson_title":

                lesson["lesson_title"],

            "subject":

                lesson["subject"],

            "year_level":

                lesson["year_level"],

            "prompt_type":

                prompt_type,

            "prompt_file":

                str(prompt_file)

        }

        file.write_text(

            json.dumps(

                data,

                indent=4,

                ensure_ascii=False

            ),

            encoding="utf-8"

        )

        return file
