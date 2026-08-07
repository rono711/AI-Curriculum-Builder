import os

from openai import OpenAI

from base_provider import BaseProvider

from dotenv import load_dotenv

load_dotenv("/volume1/docker/curriculum-builder/.env")


# ==========================================================
# ChatGPT Provider
# ==========================================================

class ChatGPTProvider(BaseProvider):

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise RuntimeError(

                "OPENAI_API_KEY environment variable is not set."

            )

        self.client = OpenAI(

            api_key=api_key

        )

        #
        # Default model
        #

        self.model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")

    # ======================================================
    # Generate
    # ======================================================

    def generate(

            self,

            prompt_asset

    ):
        prompt = prompt_asset["prompt"]

        response = self.client.responses.create(

            model=self.model,

            input=prompt

        )

        markdown = response.output_text

        usage = getattr(

            response,

            "usage",

            None

        )

        return {

            "markdown":

                markdown,

            "provider":

                "CHATGPT",

            "model":

                self.model,

            "tokens":

                getattr(

                    usage,

                    "total_tokens",

                    None

                )

                if usage

                else None,

            "cost":

                None

        }
