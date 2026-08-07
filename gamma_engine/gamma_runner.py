from pathlib import Path
import json

from gamma_client import GammaClient


# ==========================================================
# Gamma Runner
# ==========================================================

class GammaRunner:

    def __init__(self):
        self.client = GammaClient()

    # ======================================================
    # Generate
    # ======================================================

    def generate(

            self,

            prompt_file,

            description_prompt_file,

            metadata_file

    ):
        #
        # Prompt
        #

        prompt = Path(

            prompt_file

        ).read_text(

            encoding="utf-8"

        )

        #
        # Description Prompt
        #

        description_prompt = Path(

            description_prompt_file

        ).read_text(

            encoding="utf-8"

        )

        #
        # Metadata
        #

        metadata = json.loads(

            Path(

                metadata_file

            ).read_text(

                encoding="utf-8"

            )

        )

        print("=" * 60)
        print("ACTIVITIES PROMPT")
        print(prompt_file)
        print("=" * 60)

        print("=" * 60)
        print("DESCRIPTION PROMPT")
        print(description_prompt_file)
        print("=" * 60)

        print("=" * 60)
        print("LESSON PACKAGE")
        print(metadata["lesson_package_id"])
        print("=" * 60)

        print("=" * 60)
        print("GAMMA METADATA")
        print(metadata)
        print("=" * 60)
        #
        # Description
        #

        # description = self.client.generate(

        #  description_prompt

        # )

        # Number of slides
        #

        cards = metadata.get(

            "number_of_slides",

            12

        )

        #
        # Submit
        #

        submit = self.client.submit(

            prompt=prompt,

            cards=cards

        )

        generation_id = submit[

            "generationId"

        ]

        print("=" * 60)
        print("Gamma Generation Submitted")
        print(generation_id)
        print("=" * 60)

        #
        # Wait
        #

        result = self.client.poll(

            generation_id

        )
        print(result)
        #
        # --------------------------------------------------
        # Presentation
        # --------------------------------------------------
        #

        presentation_url = result.get(
            "gammaUrl",
            ""
        )

        gamma_embed_url = ""

        if presentation_url:
            gamma_embed_url = presentation_url.replace(
                "/docs/",
                "/embed/"
            )

        presentation_title = result.get(
            "title",
            ""
        )

        if not presentation_title:
            presentation_title = metadata.get(
                "display_title",
                ""
            )

        if not presentation_title:
            presentation_title = metadata.get(
                "elaboration",
                ""
            )

        if not presentation_title:
            presentation_title = metadata.get(
                "lesson_title",
                "Lesson"
            )

        #
        # --------------------------------------------------
        # Return
        # --------------------------------------------------
        #

        return {

            "status":
                "SUCCESS",

            "title":
                presentation_title,

            "slide_title":
                presentation_title,

            "generation_id":
                generation_id,

            "presentation_id":
                result.get(
                    "presentationId",
                    ""
                ),

            "presentation_url":
                presentation_url,

            "gamma_embed_url":
                gamma_embed_url,

            "pptx_url":
                result.get(
                    "exportUrl",
                    ""
                )

        }