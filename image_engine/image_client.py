import base64

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

            prompt

    ):

        print("=" * 60)
        print("IMAGE GENERATION")
        print("MODEL   :", self.image_model)
        print("SIZE    :", IMAGE_SIZE)
        print("QUALITY :", IMAGE_QUALITY)
        print("FORMAT  :", IMAGE_FORMAT)
        print("=" * 60)

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

