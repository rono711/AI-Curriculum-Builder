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
    # Validate GIFT
    # ======================================================

    @staticmethod
    def _validate_gift(content):

        content = str(
            content or ""
        ).strip()

        if not content:

            raise RuntimeError(
                "Generated GIFT content is empty."
            )

        questions = [
            block.strip()
            for block in content.split("\n\n")
            if block.strip()
        ]

        if not questions:

            raise RuntimeError(
                "Generated GIFT contains no questions."
            )

        for index, question in enumerate(
                questions,
                start=1
        ):

            if not question.startswith("::"):

                raise RuntimeError(
                    f"GIFT question {index} "
                    "does not start with a title."
                )

            if question.count("{") != question.count("}"):

                raise RuntimeError(
                    f"GIFT question {index} has "
                    "unbalanced answer braces: "
                    f"{question[:200]}"
                )

            if "{" not in question or "}" not in question:

                raise RuntimeError(
                    f"GIFT question {index} has "
                    "no answer block: "
                    f"{question[:200]}"
                )

        return content

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

        gift_content = self._validate_gift(
            result["content"]
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

                gift_content,

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
