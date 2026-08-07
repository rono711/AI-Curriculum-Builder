import os

from openai import OpenAI

from dotenv import load_dotenv


# ==========================================================
# Environment
# ==========================================================

load_dotenv(

    "/volume1/docker/curriculum-builder/.env"

)


# ==========================================================
# Quiz Client
# ==========================================================

class QuizClient:

    def __init__(self):

        self.client = OpenAI(

            api_key=os.getenv(

                "OPENAI_API_KEY"

            )

        )

        self.model = os.getenv(

            "OPENAI_MODEL",

            "gpt-5.5"

        )

    # ======================================================
    # Generate
    # ======================================================

    def generate(

            self,

            prompt

    ):

        response = self.client.responses.create(

            model=self.model,

            input=prompt

        )

        gift = response.output_text

        usage = response.usage

        return {

            "status":

                "SUCCESS",

            "provider":

                "CHATGPT",

            "model":

                self.model,

            "gift":

                gift,

            "prompt_tokens":

                usage.input_tokens,

            "completion_tokens":

                usage.output_tokens,

            "total_tokens":

                usage.total_tokens

        }
