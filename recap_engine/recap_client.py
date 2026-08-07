import sys
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(

        0,

        str(PROJECT_ROOT)

    )

from openai import OpenAI

from dotenv import load_dotenv

from shared.markdown_converter import MarkdownConverter

# ==========================================================
# Environment
# ==========================================================

load_dotenv(

    "/volume1/docker/curriculum-builder/.env"

)


# ==========================================================
# Recap Client
# ==========================================================

class RecapClient:

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

        markdown_text = response.output_text

        html = MarkdownConverter.to_html(

            markdown_text

        )

        usage = response.usage

        return {

            "status":

                "SUCCESS",

            "provider":

                "CHATGPT",

            "model":

                self.model,

            "markdown":

                markdown_text,

            "html":

                html,

            "prompt_tokens":

                usage.input_tokens,

            "completion_tokens":

                usage.output_tokens,

                "total_tokens":

                    usage.total_tokens

        }
