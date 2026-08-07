from pathlib import Path
import json

from models import DescriptionRequest


# ==========================================================
# Description Builder
# ==========================================================

class DescriptionBuilder:

    def __init__(

            self,

            build_root,

            build_name,

            lesson_package_id

    ):

        self.build_root = Path(build_root)

        self.build_name = build_name

        self.lesson_package_id = lesson_package_id

        self.build_folder = (

            self.build_root

            / build_name

        )

        self.lesson_folder = (

            self.build_folder

            / "Lesson"

        )

        self.output_folder = (

            self.build_folder

            / "Descriptions"

        )

        self.output_folder.mkdir(

            parents=True,

            exist_ok=True

        )

    # ======================================================
    # Build
    # ======================================================

    def build(

            self

    ):

        lesson_json = self.read_json(

            self.lesson_folder

            / "lesson_content.json"

        )

        descriptions = {

            "text_and_media": {

                "title":

                    lesson_json.get(

                        "content_description",

                        ""

                    ),

                "description": ""

            },

            "mission": {

                "title":

                    "Mission of the Day",

                "description": ""

            },

            "did_you_know": {

                "title":

                    "Did You Know?",

                "description": ""

            },

            "quiz": {

                "title":

                    "Checking Your Thinking",

                "description": ""

            },

            "activities": {

                "title":

                    "Let's Do It",

                "description": ""

            },

            "recap": {

                "title":

                    "What We Discovered",

                "description": ""

            }

        }

        self.write_json(

            descriptions

        )

        self.write_markdown(

            descriptions

        )

        return descriptions

    # ======================================================
    # Read JSON
    # ======================================================

    def read_json(

            self,

            filename

    ):

        if not filename.exists():

            return {}

        with open(

                filename,

                "r",

                encoding="utf-8"

        ) as f:

            return json.load(

                f

            )

    # ======================================================
    # Write JSON
    # ======================================================

    def write_json(

            self,

            data

    ):

        with open(

                self.output_folder

                / "descriptions.json",

                "w",

                encoding="utf-8"

        ) as f:

            json.dump(

                data,

                f,

                indent=4,

                ensure_ascii=False

            )

    # ======================================================
    # Write Markdown
    # ======================================================

    def write_markdown(

            self,

            descriptions

    ):

        md = f"""

# Text & Media

{descriptions["text_and_media"]["description"]}

# Mission

{descriptions["mission"]["description"]}

# Did You Know?

{descriptions["did_you_know"]["description"]}

# Quiz

{descriptions["quiz"]["description"]}

# Activities

{descriptions["activities"]["description"]}

# Recap

{descriptions["recap"]["description"]}

"""

        with open(

                self.output_folder

                / "descriptions.md",

                "w",

                encoding="utf-8"

        ) as f:

            f.write(

                md

            )