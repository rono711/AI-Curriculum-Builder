from pathlib import Path
import json

from shared.ai_client import AIClient


# ==========================================================
# Quiz Runner
# ==========================================================

class QuizRunner:

    def __init__(self):

        self.client = AIClient()

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
        print("QUIZ PROMPT")
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

        #
        # Quiz
        #

        result = self.client.generate(

            prompt

        )

        #
        # Description
        #

        description = self.client.generate(

            description_prompt

        )

        print("=" * 60)
        print("QUIZ GENERATED")
        print("Tokens :", result["total_tokens"])
        print("=" * 60)

        return {

            "status":

                "SUCCESS",

            "provider":

                result["provider"],

            "model":

                result["model"],
            #
            # Moodle
            #

            "title":

                "Checking Your Thinking",

            "description":

                description["content"],

            #
            # Content
            #
            "gift":

                result["content"],

             #
            # Tokens
            #

            "prompt_tokens":

                result["prompt_tokens"]

                +

                description["prompt_tokens"],

            "completion_tokens":

                result["completion_tokens"]

                +

                description["completion_tokens"],

            "total_tokens":

                result["total_tokens"]

                +

                description["total_tokens"]

        }