import base64
from pathlib import Path

from openai import OpenAI

from config import (
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OPENAI_IMAGE_MODEL,
    IMAGE_SIZE,
    IMAGE_QUALITY,
    IMAGE_FORMAT
)


# ==========================================================
# Image Client
# ==========================================================

class ImageClient:

    def __init__(self):

        if not OPENAI_API_KEY:

            raise RuntimeError(
                "OPENAI_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=OPENAI_API_KEY
        )

        self.text_model = OPENAI_MODEL

        self.image_model = OPENAI_IMAGE_MODEL

    # ======================================================
    # Generate Final Image Prompt
    # ======================================================

    def generate_image_prompt(

            self,

            assembled_prompt

    ):

        print("=" * 60)
        print("IMAGE PROMPT GENERATION")
        print("MODEL :", self.text_model)
        print("=" * 60)

        response = self.client.responses.create(

            model=self.text_model,

            input=assembled_prompt

        )

        final_prompt = (
            response.output_text or ""
        ).strip()

        if not final_prompt:

            raise RuntimeError(
                "OpenAI returned an empty image prompt."
            )

        usage = response.usage

        return {

            "prompt":

                final_prompt,

            "provider":

                "OPENAI",

            "model":

                self.text_model,

            "prompt_tokens":

                usage.input_tokens,

            "completion_tokens":

                usage.output_tokens,

            "total_tokens":

                usage.total_tokens

        }

    # ======================================================
    # Generate Image
    # ======================================================

    def generate_image(

            self,

            prompt,
            reference_images=None,
            reference_people=None

    ):

        print("=" * 60)
        print("IMAGE GENERATION")
        print("MODEL   :", self.image_model)
        print("SIZE    :", IMAGE_SIZE)
        print("QUALITY :", IMAGE_QUALITY)
        print("FORMAT  :", IMAGE_FORMAT)
        print("=" * 60)

        reference_images = [
            str(path)
            for path in (reference_images or [])
            if Path(path).is_file()
        ]

        reference_people = (
            reference_people or []
        )

        person_traits = []

        for person in reference_people:

            person_key = person.get(
                "person_key",
                ""
            )

            if person_key == "teacher_001":

                person_traits.append(
                    "For the referenced adult male teacher, "
                    "preserve a natural beard as a consistent "
                    "facial characteristic."
                )

        if reference_images:

            print("REFERENCE IMAGES:")
            for path in reference_images:
                print("  -", path)

            opened_files = []

            try:

                opened_files = [
                    open(path, "rb")
                    for path in reference_images
                ]

                reference_prompt = (
                    prompt
                    + "\n\nREFERENCE PEOPLE INSTRUCTIONS:\n"
                    + "The supplied image files are visual references for people, "
                    + "not source scenes to copy. Preserve the recognisable appearance "
                    + "of the referenced person or people when they are included in "
                    + "the educational scene. Create a new scene appropriate to the "
                    + "lesson prompt. Do not copy backgrounds, passport-photo framing, "
                    + "or unrelated objects from the reference photographs. "
                    + "Use natural poses, expressions, clothing and interactions "
                    + "appropriate to the educational context. Do not duplicate a "
                    + "referenced person to create multiple different people."
                    + (
                        "\n\nPERSON-SPECIFIC APPEARANCE REQUIREMENTS:\n"
                        + "\n".join(person_traits)
                        if person_traits
                        else ""
                    )
                )

                response = self.client.images.edit(

                    model=self.image_model,

                    image=opened_files,

                    prompt=reference_prompt,

                    size=IMAGE_SIZE,

                    quality=IMAGE_QUALITY,

                    output_format=IMAGE_FORMAT,

                    input_fidelity="high",

                    n=1

                )

                print("REFERENCE IMAGE GENERATION: SUCCESS")

            except Exception as exc:

                print("=" * 60)
                print("REFERENCE IMAGE GENERATION FAILED")
                print(str(exc))
                print("FALLING BACK TO TEXT-ONLY IMAGE GENERATION")
                print("=" * 60)

                response = self.client.images.generate(

                    model=self.image_model,

                    prompt=prompt,

                    size=IMAGE_SIZE,

                    quality=IMAGE_QUALITY,

                    output_format=IMAGE_FORMAT,

                    n=1

                )

            finally:

                for file_handle in opened_files:
                    file_handle.close()

        else:

            response = self.client.images.generate(

                model=self.image_model,

                prompt=prompt,

                size=IMAGE_SIZE,

                quality=IMAGE_QUALITY,

                output_format=IMAGE_FORMAT,

                n=1

            )

        if not response.data:

            raise RuntimeError(
                "OpenAI returned no image data."
            )

        image = response.data[0]

        if not image.b64_json:

            raise RuntimeError(
                "OpenAI returned no base64 image data."
            )

        image_bytes = base64.b64decode(
            image.b64_json
        )

        if not image_bytes:

            raise RuntimeError(
                "Generated image is empty."
            )

        return {

            "provider":

                "OPENAI",

            "model":

                self.image_model,

            "size":

                IMAGE_SIZE,

            "quality":

                IMAGE_QUALITY,

            "format":

                IMAGE_FORMAT,

            "bytes":

                image_bytes

        }

