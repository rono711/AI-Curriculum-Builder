from config import (
    PIPELINE_ENGINE_URL
)
import requests

from file_naming import workbook_filename

from template_manager import (
    new_workbook,
    save_workbook,
    close_workbook
)
from writers.descriptions_writer import write_descriptions
from metadata import write_metadata

from writers.lesson_db_writer import write_lesson_db
from writers.lesson_content_writer import write_lesson_content

from writers.prompt_writer import write_prompt_queue
from writers.ai_generation_writer import write_ai_generation

from writers.slides_writer import write_slides
from writers.quiz_writer import write_quiz
from writers.activities_writer import write_activities
from writers.recap_writer import write_recap

from writers.resources_writer import write_resources
from writers.asset_register_writer import write_asset_register
from writers.moodle_publish_writer import write_moodle_publish
from writers.build_log_writer import write_build_log

from writers.lesson_metadata_writer import write_lesson_metadata


# ==========================================================
# Lesson Package Builder
# ==========================================================

class LessonPackageBuilder:

    def __init__(self):
        pass

    # ======================================================
    # Build
    # ======================================================

    def build(

            self,

            request

    ):
        #
        # Generate Build ID
        #

        build = workbook_filename(

            request["subject"],

            request["year_level"],

            request["strand"]

        )

        request["build_id"] = build["build_id"]

        request["build_filename"] = build["filename"]

        #
        # Workbook
        #

        workbook = new_workbook(

            build["path"]

        )

        #
        # Metadata
        #

        write_metadata(

            workbook,

            request,

            build["filename"]

        )

        #
        # Lesson DB
        #

        lesson_rows = write_lesson_db(

            workbook,

            request

        )
        write_lesson_metadata(
            workbook,
            lesson_rows,
            request
        )
        #
        # Lesson placeholders
        #

        write_lesson_content(

            workbook,

            lesson_rows

        )

        #
        # Prompt Queue
        #

        write_prompt_queue(

            workbook,

            lesson_rows

        )

        #
        # AI Queue
        #

        write_ai_generation(

            workbook,

            lesson_rows

        )

        #
        # Asset placeholders
        #

        write_slides(

            workbook,

            lesson_rows

        )

        write_quiz(

            workbook,

            lesson_rows

        )

        write_activities(

            workbook,

            lesson_rows

        )
        write_descriptions(
            workbook,
            lesson_rows
        )
        write_recap(

            workbook,

            lesson_rows

        )

        #
        # Supporting Resources
        #

        write_resources(

            workbook,

            lesson_rows

        )

        write_asset_register(

            workbook,

            lesson_rows

        )

        write_moodle_publish(

            workbook,

            lesson_rows

        )

        write_build_log(

            workbook,

            request

        )

        #
        # Save Workbook
        #

        save_workbook(

            workbook,

            build["path"]

        )

        close_workbook(

            workbook

        )
        build_root = str(build["path"].parent.parent)

        build_name = build["path"].stem

        response = requests.post(

            PIPELINE_ENGINE_URL,

            json={

                "build_root": build_root,

                "build_name": build_name,

                "lesson_rows": lesson_rows

            },

            timeout=3600

        )

        response.raise_for_status()

        return response.json()


#
#     lesson_package_id = lesson_rows[0]["lesson_package_id"]
#     #
#     # ==================================================
#     # Prompt Generation Pipeline
#     # ==================================================
#     #
#
#     prompt_sequence = [
#
#         "LESSON_CONTENT",
#         "DISPLAY_TITLE",
#         "MISSION",
#         "GAMMA_SLIDES",
#         "DID_YOU_KNOW",
#         "QUIZ",
#         "CHECKING_YOUR_THINKING",
#         "ACTIVITIES",
#         "LETS_DO_IT",
#         "RECAP",
#         "WHAT_WE_DISCOVERED"
#     ]
#
#     prompt_results = []
#
#     for prompt_type in prompt_sequence:
#
#         print("CALLING PROMPT ENGINE")
#         print("PROMPT TYPE:", prompt_type)
#         print("LESSON PACKAGE:", lesson_package_id)
#         print("=" * 60)
#
#         response = requests.post(
#             PROMPT_ENGINE_URL,
#             json={
#                 "workbook_path": str(build["path"]),
#                 "lesson_package_id": lesson_package_id,
#                 "prompt_type": prompt_type
#             },
#             timeout=600
#         )
#         print("PROMPT:", prompt_type)
#         print("STATUS :", response.status_code)
#
#         if response.status_code != 200:
#             print(response.text)
#         response.raise_for_status()
#
#         result = response.json()
#
#         print("=" * 60)
#         print("PROMPT RESULT")
#         print(result)
#         print("=" * 60)
#
#         prompt_results.append(result)
#
#
#         print("=" * 60)
#         print("PROMPT COMPLETE")
#         print(prompt_type)
#         print("=" * 60)
#
# #
# # ==================================================
# # Asset Generation Pipeline
# # ==================================================
# #
#
#     build_root = str(build["path"].parent.parent)
#
#     build_name = build["path"].stem
#
#     engines = [
#
#         ("Gamma", GAMMA_ENGINE_URL),
#
#         ("Quiz", QUIZ_ENGINE_URL),
#
#         ("Activities", ACTIVITIES_ENGINE_URL),
#
#         ("Recap", RECAP_ENGINE_URL),
#
#         ("Publisher", PUBLISHER_ENGINE_URL),
#
#     ]
#
#     for engine_name, engine_url in engines:
#
#         print("=" * 60)
#         print(f"CALLING {engine_name.upper()} ENGINE")
#         print("=" * 60)
#
#         response = requests.post(
#
#             engine_url,
#
#             json={
#
#                 "build_root": build_root,
#
#                 "build_name": build_name,
#
#                 "lesson_package_id": lesson_package_id
#
#             },
#
#             timeout=1800
#
#         )
#
#         print(engine_name, response.status_code)
#
#         if response.status_code != 200:
#             print(response.text)
#
#         response.raise_for_status()
#
#     #
#     # Finished
#     #
#
#     print("=" * 60)
#     print("LESSON PACKAGE BUILD COMPLETED")
#     print("Build ID :", build["build_id"])
#     print("Lesson   :", lesson_package_id)
#     print("=" * 60)
#
#     return {
#
#         "status": "SUCCESS",
#
#         "build_id": build["build_id"],
#
#         "lesson_package_id": lesson_package_id,
#
#         "filename": build["filename"],
#
#         "workbook_path": str(build["path"]),
#
#         "prompts": prompt_results
#
#     }
