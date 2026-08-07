import re


# ==========================================================
# Placeholder Replacer
# ==========================================================

class PlaceholderReplacer:

    def __init__(

            self,

            values

    ):

        self.values = values

    # ======================================================
    # One Placeholder
    # ======================================================

    def replace(

            self,

            text

    ):

        if not text:
            return ""

        result = str(text)

        for key, value in self.values.items():
            placeholder = "{{" + key + "}}"

            result = result.replace(

                placeholder,

                str(value)

                if value is not None

                else ""

            )

        #
        # Remove unresolved placeholders
        #

        result = re.sub(

            r"\{\{.*?\}\}",

            "",

            result

        )

        return result

    # ======================================================
    # Multiple Templates
    # ======================================================

    def replace_many(

            self,

            templates

    ):

        output = []

        for template in templates:
            output.append(

                self.replace(

                    template

                )

            )

        return output

    # ======================================================
    # Join Templates
    # ======================================================

    def assemble(

            self,

            templates

    ):

        return "\n\n".join(

            self.replace_many(

                templates

            )

        )
