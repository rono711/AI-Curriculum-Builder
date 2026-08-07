from prompt_assembler import PromptAssembler
from workbook_reader import WorkbookReader
from prompt_asset_writer import PromptAssetWriter
import sys
from pathlib import Path
import requests

from config import CONTENT_ENGINE_URL
PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ==========================================================
# Prompt Builder
# ==========================================================

class PromptBuilder:

    def __init__(self):
        pass

    # ======================================================
    # Build Prompt
    # ======================================================

    def build(

            self,

            workbook_path,

            lesson_package_id,

            prompt_type

    ):
        #
        # Read Workbook
        #

        reader = WorkbookReader(

            workbook_path

        )

        lesson = reader.lesson(

            lesson_package_id

        )

        if lesson is None:
            raise ValueError(

                f"{lesson_package_id} not found."

            )

        #
        # Assemble Prompt
        #

        assembler = PromptAssembler(

            workbook_path

        )

        prompt = assembler.assemble(

            lesson_package_id,

            prompt_type

        )
        print("=" * 60)
        print("PROMPT TYPE")
        print(prompt_type)
        print("=" * 60)

        print("=" * 60)
        print("PROMPT LENGTH")
        print(len(prompt))
        print("=" * 60)

        assembler.close()

        #
        # Output Folder
        #

        from shared.build_paths import BuildPaths

        paths = BuildPaths(

            workbook_path

        )

        prompt_folder = paths.prompts_folder


        prompt_folder.mkdir(

            parents=True,

            exist_ok=True

        )

        writer = PromptAssetWriter(

            prompt_folder

        )

        #
        # Markdown
        #

        prompt_file = writer.markdown(

            f"{prompt_type.lower()}.md",

            prompt

        )
        print("=" * 60)
        print("PROMPT FILE")
        print(prompt_file)
        print("=" * 60)
        #
        # Metadata
        #

        metadata_file = writer.metadata(

            f"{prompt_type.lower()}.json",

            lesson,

            prompt_type,

            prompt_file

        )
        print("=" * 60)
        print("METADATA FILE")
        print(metadata_file)
        print("=" * 60)
        reader.close()
        # ======================================================
        # AI Engine
        # ======================================================

        #
        # Only lesson content goes to AI Engine
        #

        ai_result = None

        if prompt_type in [

            "LESSON_CONTENT",

            "DISPLAY_TITLE",

            "MISSION",

            "DID_YOU_KNOW",

            "CHECKING_YOUR_THINKING",

            "LETS_DO_IT",

            "WHAT_WE_DISCOVERED"
        ]:
            ai_response = requests.post(

                CONTENT_ENGINE_URL,

                json={

                    "provider": "CHATGPT",

                    "workbook_path": workbook_path,

                    "lesson_package_id": lesson_package_id,

                    "prompt_type": prompt_type,

                    "prompt": prompt,

                    "prompt_file": str(prompt_file),

                    "metadata_file": str(metadata_file)

                },

                timeout=600

            )
            print("=" * 60)
            print("PROMPT TYPE")
            print(prompt_type)
            print("=" * 60)

            ai_response.raise_for_status()
            ai_result = ai_response.json()

            print("=" * 60)
            print("AI ENGINE FINISHED")
            print(ai_result)
            print("=" * 60)

            print("=" * 60)
            print("PROMPT ENGINE FINISHED")
            print("Prompt Type :", prompt_type)
            print("Prompt File :", prompt_file)
            print("=" * 60)

        return {

            "status": "SUCCESS",

            "lesson_package_id":

                lesson_package_id,

            "prompt_type":

                prompt_type,

            "prompt_file":

                str(prompt_file),

            "metadata_file":

                str(metadata_file),

            "prompt":

                prompt,

            "ai":

                ai_result

        }