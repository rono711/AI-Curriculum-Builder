from pathlib import Path
import json
import re

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
    def _numeric_shortanswer_variants(answer):
        """
        Return equivalent display variants for an integer numeral.

        Examples:
            415 602 -> 415 602, 415,602, 415602
            1,234   -> 1,234, 1 234, 1234

        This deliberately handles integer numerals only.
        Decimal, textual and mixed alphanumeric answers are
        left untouched.
        """

        answer = str(answer or "").strip()

        if not answer:
            return [answer]

        # Optional sign followed by digits grouped either with
        # spaces/commas or with no grouping.
        if not re.fullmatch(
            r"[+-]?(?:\d+|\d{1,3}(?:[ ,]\d{3})+)",
            answer
        ):
            return [answer]

        sign = ""

        if answer[0] in "+-":
            sign = answer[0]
            body = answer[1:]
        else:
            body = answer

        digits = re.sub(
            r"[ ,]",
            "",
            body
        )

        # Guard against accidental non-numeric normalization.
        if not digits.isdigit():
            return [answer]

        plain = sign + digits

        # Group from the right in thousands.
        groups = []

        remaining = digits

        while remaining:
            groups.insert(
                0,
                remaining[-3:]
            )

            remaining = remaining[:-3]

        spaced = sign + " ".join(groups)
        comma = sign + ",".join(groups)

        variants = [
            answer,
            plain,
            spaced,
            comma,
        ]

        return list(
            dict.fromkeys(variants)
        )


    @classmethod
    def _expand_numeric_shortanswer_variants(
            cls,
            content
    ):
        """
        Expand single-answer numeric GIFT short answers.

        Only questions whose answer block contains one positive
        '=answer' entry and whose entire answer is an integer
        numeral are changed.

        Multiple-choice, matching, true/false, decimal, textual
        and mixed answers are left untouched.
        """

        content = str(content or "")

        questions = re.split(
            r"(\n\s*\n)",
            content
        )

        for index in range(
                0,
                len(questions),
                2
        ):
            question = questions[index]

            if not question.strip():
                continue

            # Normalize numeric answers only for the designated
            # short-answer question family.
            #
            # Before traceability:
            #     ::SA1::
            #
            # After traceability:
            #     ::CB_000248_001_SA001::
            #
            # This prevents numeric multiple-choice or matching
            # answers from being modified accidentally.
            title_match = re.match(
                r"^\s*::([^:]+)::",
                question
            )

            if not title_match:
                continue

            title = title_match.group(1).strip()

            is_shortanswer = bool(
                re.fullmatch(
                    r"SA\d+",
                    title,
                    flags=re.IGNORECASE
                )
                or re.fullmatch(
                    r"CB_\d+_\d+_SA\d+",
                    title,
                    flags=re.IGNORECASE
                )
            )

            if not is_shortanswer:
                continue

            match = re.search(
                r"\{\s*=\s*([^~=\n{}]+?)\s*\}",
                question,
                flags=re.DOTALL
            )

            if not match:
                continue

            answer = match.group(1).strip()

            variants = (
                cls._numeric_shortanswer_variants(
                    answer
                )
            )

            if len(variants) <= 1:
                continue

            answer_block = "{\n" + "\n".join(
                "=" + variant
                for variant in variants
            ) + "\n}"

            question = (
                question[:match.start()]
                + answer_block
                + question[match.end():]
            )

            questions[index] = question

        return "".join(questions)


    @staticmethod
    def _validate_gift(content):

        content = str(
            content or ""
        ).strip()

        #
        # Escape mathematical equality signs inside GIFT text.
        #
        # GIFT uses an unescaped equals sign as an answer marker.
        # Convert mathematical equality such as:
        #
        #     4 x 3 = 12
        #
        # to:
        #
        #     4 x 3 \= 12
        #
        # Existing escaped equality signs are preserved.
        #
        content = re.sub(
            r"(?<!\\)(?<=\s)=(?=\s)",
            lambda match: r"\=",
            content
        )

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

                    #
                    # Reject remaining unescaped equals signs.
                    #
                    if (
                        re.search(r"(?<!\\)=", left)
                        or re.search(r"(?<!\\)=", right)
                    ):

                        raise RuntimeError(
                            f"GIFT matching question {index} "
                            "contains an unescaped equals sign. "
                            "Use \\= for mathematical equality: "
                            f"{matching_line}"
                        )

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
    # Question Traceability
    # ======================================================

    @staticmethod
    def _add_question_traceability(content, lesson_package_id):
        """
        Replace generated GIFT question names such as Q1, T1, M1 and SA1
        with stable Curriculum Builder question keys.

        Example:
            LP_000238_001 + Q1
            -> CB_000238_001_Q001

        Only the GIFT question name is changed. Question text, answers
        and GIFT answer syntax are left untouched.
        """
        import re

        package_match = re.fullmatch(
            r"LP_(\d+)_(\d+)",
            str(lesson_package_id).strip()
        )

        if not package_match:
            raise ValueError(
                "Invalid lesson_package_id for question traceability: "
                f"{lesson_package_id}"
            )

        build_number = package_match.group(1)
        lesson_number = package_match.group(2)

        prefix = (
            f"CB_{build_number}_{lesson_number}"
        )

        pattern = re.compile(
            r"::(SA|Q|T|M)(\d+)::"
        )

        seen_keys = set()

        def replace(match):
            question_type = match.group(1)
            sequence = int(match.group(2))

            question_key = (
                f"{prefix}_{question_type}{sequence:03d}"
            )

            if question_key in seen_keys:
                raise ValueError(
                    f"Duplicate generated question key: {question_key}"
                )

            seen_keys.add(question_key)

            return f"::{question_key}::"

        traced_content, count = pattern.subn(
            replace,
            content
        )

        if count == 0:
            raise ValueError(
                "No supported GIFT question names were found "
                "for traceability."
            )

        print("=" * 60)
        print("QUESTION TRACEABILITY")
        print("Lesson Package:", lesson_package_id)
        print("Questions Tagged:", count)
        print("=" * 60)

        return traced_content

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

        gift_content = (
            self._expand_numeric_shortanswer_variants(
                result["content"]
            )
        )

        gift_content = self._validate_gift(
            gift_content
        )

        gift_content = self._add_question_traceability(
            gift_content,
            metadata["lesson_package_id"]
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
