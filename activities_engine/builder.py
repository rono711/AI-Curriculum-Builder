import sys
from pathlib import Path
import json

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from shared.build_paths import BuildPaths

from activities_runner import ActivitiesRunner
from activities_writer import ActivitiesWriter


# ==========================================================
# Activities Builder
# ==========================================================

class ActivitiesBuilder:

    def __init__(self):
        self.runner = ActivitiesRunner()

    # ======================================================
    # Generate Activities
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
        # Workbook Writer
        #

        writer = ActivitiesWriter(

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

            / "activities.md"

        )

        description_prompt_file = (

            paths.prompts_folder

            / "lets_do_it.md"

        )

        metadata_file = (

            paths.prompts_folder

            / "activities.json"

        )

        #
        # Activities Folder
        #

        activities_folder = (

            paths.build_root

            / "Activities"

            / build_name

        )

        activities_folder.mkdir(

            parents=True,

            exist_ok=True

        )

        print("=" * 60)
        print("ACTIVITIES PROMPT")
        print(prompt_file)
        print("=" * 60)

        #
        # Generate
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

            activities_folder

            / "activities.md"

        )

        markdown_file.write_text(

            result["markdown"],

            encoding="utf-8"

        )

        #
        # Save HTML
        #

        html_file = (

            activities_folder

            / "activities.html"

        )

        html_file.write_text(

            result["html"],

            encoding="utf-8"

        )

        #
        # Save JSON
        #

        json_file = (

            activities_folder

            / "activities.json"

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

        writer = ActivitiesWriter(

            str(workbook_path)

        )

        #
        # Update Activities Worksheet
        #

        writer.update_activities(

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

            activity_title=result["title"],

            activity_description=result["description"],

            generation_status="COMPLETED",

            review_status="PENDING"

        )

        #
        # Asset Register
        #

        writer.update_asset_register(

            lesson_package_id=lesson_package_id,

            asset_type="ACTIVITIES",

            filename=html_file.name,

            url=""

        )

        #
        # Build Log
        #

        writer.log(

            component="Activities Engine",

            action="Generate Activities",

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