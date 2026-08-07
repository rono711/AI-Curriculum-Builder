import sys
from pathlib import Path
import json

# ==========================================================
# Project Root
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(

        0,

        str(PROJECT_ROOT)

    )

from shared.build_paths import BuildPaths

from recap_runner import RecapRunner

from recap_writer import RecapWriter


# ==========================================================
# Recap Builder
# ==========================================================

class RecapBuilder:

    def __init__(self):

        self.runner = RecapRunner()

    # ======================================================
    # Generate
    # ======================================================

    def generate(

            self,

            build_root,

            build_name,

            lesson_package_id

    ):

        #
        # Workbook
        #

        workbook_path = (

            Path(build_root)

            / "Workbook"

            / f"{build_name}.xlsx"

        )
        #
        # Recap Writer
        #

        writer = RecapWriter(

            str(workbook_path)

        )
        #
        # Build Paths
        #

        paths = BuildPaths(

            str(workbook_path)

        )

        #
        # Prompt Assets
        #

        prompt_file = (

            paths.prompts_folder

            / "recap.md"

        )
        description_prompt_file = (

                paths.prompts_folder

                / "what_we_discovered.md"

        )

        metadata_file = (

            paths.prompts_folder

            / "recap.json"

        )

        #
        # Recap Folder
        #

        recap_folder = (

            paths.build_root

            / "Recap"

            / build_name

        )

        recap_folder.mkdir(

            parents=True,

            exist_ok=True

        )

        print("=" * 60)
        print("RECAP PROMPT")
        print(prompt_file)
        print("=" * 60)

        #
        # Generate Recap
        #

        result = self.runner.generate(

            prompt_file=str(prompt_file),
            description_prompt_file=str(description_prompt_file),
            metadata_file=str(metadata_file)

        )

        #
        # Save Markdown
        #

        markdown_file = (

            recap_folder

            / "recap.md"

        )

        markdown_file.write_text(

            result["markdown"],

            encoding="utf-8"

        )

        #
        # Save HTML
        #

        html_file = (

            recap_folder

            / "recap.html"

        )

        html_file.write_text(

            result["html"],

            encoding="utf-8"

        )

        #
        # Save JSON
        #

        json_file = (

            recap_folder

            / "recap.json"

        )

        json_file.write_text(

            json.dumps(

                result,

                indent=4,

                ensure_ascii=False

            ),

            encoding="utf-8"

        )

        #
        # Workbook Writer
        #

        writer = RecapWriter(

            str(workbook_path)

        )
        #
        # Update Recap Worksheet
        #
        writer.update_recap(

            lesson_package_id=lesson_package_id,

            markdown_filename=markdown_file.name,

            html_filename=html_file.name,

            generation_status="COMPLETED",

            review_status="PENDING"

        )
        #
        # Update Descriptions Worksheet
        #
        print("=" * 60)
        print("CALLING update_descriptions")
        print("=" * 60)

        writer.update_descriptions(

            lesson_package_id=lesson_package_id,

            recap_title=result["title"],

            recap_description=result["description"],

            generation_status="COMPLETED",

            review_status="PENDING"

        )

        #
        # Asset Register
        #

        writer.update_asset_register(

            lesson_package_id=lesson_package_id,

            asset_type="RECAP",

            filename=html_file.name,

            url=""

        )

        #
        # Build Log
        #

        writer.log(

            component="Recap Engine",

            action="Generate Recap",

            status="SUCCESS",

            details=html_file.name

        )

        #
        # Save Workbook
        #

        writer.save()

        #
        # Finished
        #

        return result