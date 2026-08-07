import sys
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(

        0,

        str(PROJECT_ROOT)

    )

from dotenv import load_dotenv
from openai import OpenAI

# ==========================================================
# Environment
# ==========================================================

load_dotenv(

    PROJECT_ROOT / ".env"

)

# ==========================================================
# Shared AI Client
# ==========================================================

class AIClient:

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
    # Generate Markdown
    # ======================================================

    def generate(

            self,

            prompt

    ):

        print("=" * 60)
        print("OPENAI REQUEST")
        print("MODEL :", self.model)
        print("=" * 60)

        response = self.client.responses.create(

            model=self.model,

            input=prompt

        )

        text = response.output_text

        usage = response.usage

        print("=" * 60)
        print("OPENAI RESPONSE")
        print("Prompt Tokens     :", usage.input_tokens)
        print("Completion Tokens :", usage.output_tokens)
        print("Total Tokens      :", usage.total_tokens)
        print("=" * 60)

        return {

            "status":

                "SUCCESS",

            "provider":

                "CHATGPT",

            "model":

                self.model,

            "content":

                text,

            "prompt_tokens":

                usage.input_tokens,

            "completion_tokens":

                usage.output_tokens,

            "total_tokens":

                usage.total_tokens

        }