import sys
from pathlib import Path
import json
import requests

# ==========================================================
# Project Root
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(

        0,

        str(PROJECT_ROOT)

    )
from shared.build_paths import BuildPaths

# ==========================================================
# Providers
# ==========================================================

from provider_router import ProviderRouter

# ==========================================================
# Shared Services
# ==========================================================

from shared.services import (

    GENERATE_PROMPT,

    UPDATE_MARKDOWN,

    UPDATE_WORKBOOK

)

# ==========================================================
# CONTENT Builder
# ==========================================================

class CONTENTBuilder:

    def __init__(self):

        self.router = ProviderRouter()

        print("=" * 60)
        print("CONTENT Builder INITIALIZED")
        print("=" * 60)

    # ======================================================
    # Generate
    # ======================================================

    print("=" * 60)
    print("CONTENT BUILDER FILE")
    print(__file__)
    print("=" * 60)
    def generate(

        self,

        request

    ):

        print("=" * 60)
        print("GENERATE STARTED")
        print("=" * 60)


        # ==================================================
        # Build Folder
        # ==================================================

        #
        # Build Paths
        #

        paths = BuildPaths(

            request.workbook_path

        )

        #
        # Content Folder
        #

        content_folder = paths.content_folder

        content_folder.mkdir(

            parents=True,

            exist_ok=True

        )

        print("=" * 60)
        print("CONTENT FOLDER")
        print(content_folder)
        print("EXISTS:", content_folder.exists())
        print("=" * 60)

        #
        # Output Filename
        #

        OUTPUT_FILES = {

            "LESSON_CONTENT": "lesson_output",

            "DISPLAY_TITLE": "display_title",

            "MISSION": "mission",

            "DID_YOU_KNOW": "did_you_know",

            "CHECKING_YOUR_THINKING": "checking_your_thinking",

            "LETS_DO_IT": "lets_do_it",

            "WHAT_WE_DISCOVERED": "what_we_discovered"

        }

        base_name = OUTPUT_FILES.get(

            request.prompt_type,

            request.prompt_type.lower()

        )
        #
        # Description Prompt File
        #

        description_prompt_file = (

                paths.prompts_folder

                / f"{base_name}.md"

        )

        #
        # Prompt Asset
        #

        prompt_asset = {

            "prompt":

                request.prompt,

            "prompt_file":

                request.prompt_file,

            "description_prompt_file":

                str(description_prompt_file),

            "metadata_file":

                request.metadata_file,

            "workbook_path":

                request.workbook_path,

            "lesson_package_id":

                request.lesson_package_id,

            "prompt_type":

                request.prompt_type

        }
        # ==================================================
        # CONTENT Result
        # ==================================================

        result = self.router.generate(

            request.provider,

            prompt_asset

        )
        print("=" * 60)
        print("CONTENT RESULT")
        print(result)
        print("=" * 60)

        # ==================================================
        # Save Markdown
        # ==================================================

        response_md = (

                content_folder

                / f"{base_name}.md"

        )

        response_md.write_text(

            result["markdown"],

            encoding="utf-8"

        )

        # ==================================================
        # Save JSON
        # ==================================================

        response_json = (

                content_folder

                / f"{base_name}.json"

        )

        with open(

            response_json,

            "w",

            encoding="utf-8"

        ) as f:

            json.dump(

                result,

                f,

                indent=4,

                ensure_ascii=False

            )

        print("=" * 60)
        print("CONTENT OUTPUT SAVED")
        print(response_md)
        print(response_json)
        print("=" * 60)

        # ==================================================
        # Workbook Service
        # ==================================================

        WORKBOOK_MAP = {

            "LESSON_CONTENT": (

                "Lesson_Content",

                "lesson_markdown"

            ),

            "DISPLAY_TITLE": (

                "Descriptions",

                "display_title"

            ),

            "MISSION": (

                "Descriptions",

                "mission_description"

            ),

            "DID_YOU_KNOW": (

                "Descriptions",

                "slides_description"

            ),

            "CHECKING_YOUR_THINKING": (

                "Descriptions",

                "quiz_description"

            ),

            "LETS_DO_IT": (

                "Descriptions",

                "activities_description"

            ),

            "WHAT_WE_DISCOVERED": (

                "Descriptions",

                "recap_description"

            )

        }

        if request.prompt_type in WORKBOOK_MAP:
            worksheet, field = WORKBOOK_MAP[

                request.prompt_type

            ]

            print("=" * 60)
            print("UPDATING WORKBOOK")
            print("Worksheet :", worksheet)
            print("Field     :", field)
            print("=" * 60)

            # ==================================================
            # Display Title
            # ==================================================
            print("=" * 60)
            print("DISPLAY TITLE")
            print(response_md.read_text(encoding="utf-8"))
            print("=" * 60)

            if request.prompt_type == "DISPLAY_TITLE":
                print("=" * 60)
                print("CONTENT ENGINE WORKBOOK")
                print(request.workbook_path)
                print("=" * 60)
                
                import_response = requests.post(

                    UPDATE_WORKBOOK,

                    json={

                        "workbook_path":

                            request.workbook_path,

                        "worksheet":

                            "Descriptions",

                        "lesson_package_id":

                            request.lesson_package_id,

                        "values": {

                            "display_title":

                                response_md.read_text(
                                    encoding="utf-8"
                                ).strip()

                        }

                    },

                    timeout=900

                )
                print("=" * 60)
                print("UPDATE WORKBOOK STATUS")
                print(import_response.status_code)
                print(import_response.text)
                print("=" * 60)
                import_response.raise_for_status()


            else:
                 import_response = requests.post(

                     UPDATE_MARKDOWN,

                        json={

                          "workbook_path":

                           request.workbook_path,

                           "worksheet":

                             worksheet,

                           "lesson_package_id":

                             request.lesson_package_id,

                           "markdown_file":

                             str(response_md),

                           "field":

                             field

                       },

                timeout=900

            )

            import_response.raise_for_status()

            print("=" * 60)
            print("WORKBOOK UPDATED")
            print(request.prompt_type)
            print("=" * 60)

        # ==================================================
        # Finished
        # ==================================================
        
        return {

            "status":

                "SUCCESS",

            "provider":

                request.provider,

            "lesson_package_id":

                request.lesson_package_id,

            "prompt_type":

                request.prompt_type,

            "prompt_file":

                request.prompt_file,

            "metadata_file":

                request.metadata_file,

            "markdown_file":

                str(response_md),

            "json_file":

                str(response_json),

            "workbook_path":

                request.workbook_path

        }