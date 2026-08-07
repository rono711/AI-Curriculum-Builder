import sys
from pathlib import Path

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

from gamma_runner import GammaRunner


from presentation_writer import PresentationWriter
# ==========================================================
# Gamma Builder
# ==========================================================

class GammaBuilder:

    def __init__(self):

        self.runner = GammaRunner()

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
        # Workbook Writer
        #

        writer = PresentationWriter(

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

                / "gamma_slides.md"

        )

        description_file = (

                paths.content_folder

                / "did_you_know.md"

        )
        metadata_file = (

                paths.prompts_folder

                / "gamma_slides.json"

        )

        #
        # Slides Folder
        #

        slides_folder = paths.slides_folder

        slides_folder.mkdir(

            parents=True,

            exist_ok=True

        )

        print("=" * 60)
        print("PROMPT FILE")
        print(prompt_file)
        print("METADATA FILE")
        print(metadata_file)
        print("SLIDES FOLDER")
        print(slides_folder)
        print("=" * 60)

        #
        # Generate Slides
        #

        result = self.runner.generate(

            prompt_file=str(prompt_file),

            description_prompt_file=str(description_file),

            metadata_file=str(metadata_file)

        )
        #
        # Read Did You Know description
        #

        did_you_know_description = description_file.read_text(

            encoding="utf-8"

        ).strip()

        #
        # Save Gamma Response
        #

        import json

        response_json = (

                slides_folder

                / "gamma_response.json"

        )

        response_json.write_text(

            json.dumps(

                result,

                indent=4,

                ensure_ascii=False

            ),

            encoding="utf-8"

        )

        #
        # Save URLs
        #

        urls = {

            "presentation_url":

                result["presentation_url"],

            "gamma_embed_url":

                result["gamma_embed_url"],

            "pptx_url":

                result["pptx_url"]

        }

        (

                slides_folder

                / "slides_urls.json"

        ).write_text(

            json.dumps(

                urls,

                indent=4,

                ensure_ascii=False

            ),

            encoding="utf-8"

        )

        #
        # Workbook Writer
        #

        writer = PresentationWriter(

            str(workbook_path)

        )
        #
        # Update Gamma_Slides Worksheet
        #
        writer.update_gamma_slides(

            lesson_package_id=lesson_package_id,

            deck_id=result["generation_id"],

            slides_id=result["presentation_id"],

            slides_url=result["presentation_url"],

            gamma_embed_url=result["gamma_embed_url"],

            slide_title=result["slide_title"],

            slide_number=1,

            speaker_notes=""

        )
        #
        # Update Descriptions Worksheet
        #
        print("=" * 60)
        print("CALLING update_descriptions")
        print("=" * 60)

        writer.update_descriptions(

            lesson_package_id=lesson_package_id,

            slides_title=result["title"],

            slides_description=did_you_know_description,

            generation_status="COMPLETED",

            review_status="PENDING"

        )

        #
        # Asset Register
        #
        writer.update_asset_register(

            lesson_package_id=lesson_package_id,

            asset_type="GAMMA_SLIDES",

            filename="gamma_response.json",

            url=result["presentation_url"],

            status="COMPLETED"

        )

        #
        # Build Log
        #
        writer.log(

            component="Gamma Engine",

            action="Generate Presentation",

            status="SUCCESS",

            details=result["presentation_url"]

        )
        #
        # Save Workbook
        #
        writer.save()
        #
        # Finished
        #
        return result