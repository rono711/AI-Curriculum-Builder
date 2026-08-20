from pathlib import Path

from image_client import ImageClient
from image_writer import ImageWriter


# ==========================================================
# Image Runner
# ==========================================================

class ImageRunner:

    def __init__(self):

        self.client = ImageClient()

    # ======================================================
    # Generate
    # ======================================================

    def generate(

            self,

            prompt_file,

            output_folder,

            lesson_package_id,

            parent_code,

            curriculum_code,

            elaboration,

            force_regenerate=False

    ):

        prompt_file = Path(
            prompt_file
        )

        if not prompt_file.exists():

            raise FileNotFoundError(
                f"IMAGE prompt not found: "
                f"{prompt_file}"
            )

        assembled_prompt = (
            prompt_file.read_text(
                encoding="utf-8"
            )
        )

        if not assembled_prompt.strip():

            raise RuntimeError(
                "IMAGE prompt file is empty."
            )

        curriculum_code = (
            curriculum_code or ""
        ).strip()

        elaboration = (
            elaboration or ""
        ).strip()

        if not curriculum_code:

            raise RuntimeError(
                "curriculum_code cannot be empty."
            )

        if not elaboration:

            raise RuntimeError(
                "elaboration cannot be empty."
            )

        writer = ImageWriter(
            output_folder
        )

        # ==================================================
        # Reuse Existing Image
        # ==================================================

        if (
                not force_regenerate
                and
                writer.image_exists(
                    curriculum_code
                )
        ):

            existing_image = (
                writer.image_path(
                    curriculum_code
                )
            )

            existing_prompt = (
                writer.prompt_path(
                    curriculum_code
                )
            )

            print("=" * 60)
            print("IMAGE ALREADY EXISTS")
            print(existing_image)
            print("REUSING EXISTING IMAGE")
            print("=" * 60)

            return {

                "status":

                    "SUCCESS",

                "generation":

                    "REUSED",

                "lesson_package_id":

                    lesson_package_id,
                 
                "parent_code":
                    parent_code,

                "curriculum_code":
                    curriculum_code,

                "elaboration":
                    elaboration,

                "image_file":

                    str(existing_image),

                "prompt_file":

                    (
                        str(existing_prompt)
                        if existing_prompt.exists()
                        else ""
                    )

            }

        # ==================================================
        # Stage 1
        # Final Image Prompt
        # ==================================================

        lesson_image_context = f"""

CURRENT LESSON IDENTITY

Curriculum code:
{curriculum_code}

Specific Elaboration:
{elaboration}

Generate the image for this specific Elaboration.
"""

        prompt_result = (
            self.client.generate_image_prompt(
                assembled_prompt
                + lesson_image_context
            )
        )

        final_prompt = (
            prompt_result["prompt"]
        )

        saved_prompt = (
            writer.write_prompt(
                curriculum_code,
                final_prompt
            )
        )

        # ==================================================
        # Stage 2
        # Image
        # ==================================================

        image_result = (
            self.client.generate_image(
                final_prompt
            )
        )

        saved_image = (
            writer.write_image(
                curriculum_code,
                image_result["bytes"]
            )
        )

        print("=" * 60)
        print("IMAGE GENERATED")
        print("Lesson :", lesson_package_id)
        print("Prompt :", saved_prompt)
        print("Image  :", saved_image)
        print("=" * 60)

        return {

            "status":

                "SUCCESS",

            "generation":

                "GENERATED",

            "lesson_package_id":

                lesson_package_id,

            "parent_code":
                parent_code,

            "curriculum_code":
                curriculum_code,

            "elaboration":
                elaboration,

            "provider":

                image_result["provider"],

            "text_model":

                prompt_result["model"],

            "image_model":

                image_result["model"],

            "image_size":

                image_result["size"],

            "image_quality":

                image_result["quality"],

            "prompt_file":

                str(saved_prompt),

            "image_file":

                str(saved_image),

            "prompt_tokens":

                prompt_result["prompt_tokens"],

            "completion_tokens":

                prompt_result[
                    "completion_tokens"
                ],

            "total_tokens":

                prompt_result["total_tokens"]

        }
