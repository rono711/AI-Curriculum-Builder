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

            #
            # Matching-question safety
            #
            # Moodle GIFT matching pairs use:
            #
            # =Left item -> Right item
            #
            # TeX/LaTeX markup can introduce braces and other
            # characters that interfere with Moodle's GIFT parser.
            # Mathematical matching items must therefore use
            # plain-text notation such as 1/2, 3/4 or 25%.
            #
            if "->" in question:

                lines = question.splitlines()

                matching_lines = [
                    line.strip()
                    for line in lines
                    if "->" in line
                ]

                if not matching_lines:

                    raise RuntimeError(
                        f"GIFT matching question {index} "
                        "contains no matching pairs."
                    )

                for matching_line in matching_lines:

                    if not matching_line.startswith("="):

                        raise RuntimeError(
                            f"GIFT matching question {index} "
                            "contains an invalid matching pair: "
                            f"{matching_line}"
                        )

                    if matching_line.count("->") != 1:

                        raise RuntimeError(
                            f"GIFT matching question {index} "
                            "must contain exactly one -> separator "
                            "per matching pair: "
                            f"{matching_line}"
                        )

                    left, right = matching_line[1:].split(
                        "->",
                        1
                    )

                    left = left.strip()
                    right = right.strip()

                    if not left or not right:

                        raise RuntimeError(
                            f"GIFT matching question {index} "
                            "contains an empty matching item: "
                            f"{matching_line}"
                        )

                    unsafe_math_tokens = (
                        "\\(",
                        "\\)",
                        "\\[",
                        "\\]",
                        "\\frac",
                        "\\sqrt",
                        "\\begin",
                        "\\end",
                    )

                    if any(
                        token in left or token in right
                        for token in unsafe_math_tokens
                    ):

                        raise RuntimeError(
                            f"GIFT matching question {index} "
                            "contains unsupported LaTeX/TeX "
                            "markup. Use plain-text mathematics "
                            "inside matching pairs: "
                            f"{matching_line}"
                        )

                    if (
                        "{" in left
                        or "}" in left
                        or "{" in right
                        or "}" in right
                    ):

                        raise RuntimeError(
                            f"GIFT matching question {index} "
                            "contains unsafe braces inside a "
                            "matching pair: "
                            f"{matching_line}"
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
