import markdown


# ==========================================================
# Markdown Converter
# ==========================================================

class MarkdownConverter:

    @staticmethod
    def to_html(

            markdown_text

    ):

        return markdown.markdown(

            markdown_text,

            extensions=[

                "tables",

                "fenced_code",

                "sane_lists"

            ]

        )