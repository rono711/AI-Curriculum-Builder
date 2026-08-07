from pathlib import Path
import json

from shared.ai_client import AIClient
from shared.markdown_converter import MarkdownConverter


# ==========================================================
# Activities Runner
# ==========================================================

class ActivitiesRunner:

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
        print("ACTIVITIES PROMPT")
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
        # Activities
        #

        activities = self.client.generate(

            prompt

        )

        #
        # Description
        #

        description = self.client.generate(

            description_prompt

        )

        #
        # HTML
        #

        html = MarkdownConverter.to_html(

            activities["content"]

        )

        print("=" * 60)
        print("ACTIVITIES GENERATED")
        print("Tokens :", activities["total_tokens"])
        print("=" * 60)

        #
        # Return
        #

        return {

            "status":

                "SUCCESS",

            "provider":

                activities["provider"],

            "model":

                activities["model"],

            #
            # Moodle
            #

            "title":

                "Let's Do It",

            "description":

                description["content"],

            #
            # Content
            #

            "markdown":

                activities["content"],

            "html":

                html,

            #
            # Tokens
            #

            "prompt_tokens":

                activities["prompt_tokens"]

                +

                description["prompt_tokens"],

            "completion_tokens":

                activities["completion_tokens"]

                +

                description["completion_tokens"],

            "total_tokens":

                activities["total_tokens"]

                +

                description["total_tokens"]

        }