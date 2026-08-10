from config import (
    PIPELINE_ENGINE_URL
)

import requests
import shutil
from pathlib import Path
import sys


# ==========================================================
# Shared Project Modules
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from build_registry import get_published_build


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
    # Carry Forward Previous Lesson Content
    # ======================================================

    def _carry_forward_lesson_content(
            self,
            *,
            current_workbook_path,
            previous_build_id
    ):

        previous_build_id = str(
            previous_build_id
        ).strip()

        if not previous_build_id:

            raise ValueError(
                "UPDATE requires previous_build_id."
            )

        current_workbook_path = Path(
            current_workbook_path
        )

        build_root = (
            current_workbook_path
            .parent
            .parent
        )

        workbook_folder = (
            build_root
            / "Workbook"
        )

        padded_build_id = (
            previous_build_id.zfill(6)
        )

        matches = list(
            workbook_folder.glob(
                f"BLD_*_{padded_build_id}_*.xlsx"
            )
        )

        if len(matches) != 1:

            raise RuntimeError(
                "Unable to uniquely locate previous "
                f"Build {previous_build_id}. "
                f"Matches found: {len(matches)}"
            )

        previous_workbook_path = (
            matches[0]
        )

        previous_build_name = (
            previous_workbook_path.stem
        )

        current_build_name = (
            current_workbook_path.stem
        )

        previous_content_folder = (
            build_root
            / "Content"
            / previous_build_name
        )

        current_content_folder = (
            build_root
            / "Content"
            / current_build_name
        )

        source = (
            previous_content_folder
            / "lesson_output.md"
        )

        if not source.exists():

            raise RuntimeError(
                "Previous published lesson content "
                "was not found: "
                + str(source)
            )

        current_content_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        destination = (
            current_content_folder
            / "lesson_output.md"
        )

        shutil.copy2(
            source,
            destination
        )

        print("=" * 60)
        print("UPDATE CONTENT CARRIED FORWARD")
        print(
            "Previous Build:",
            previous_build_id
        )
        print(
            "Source:",
            source
        )
        print(
            "Destination:",
            destination
        )
        print("=" * 60)

        return destination
    
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
        # ==================================================
        # Elaboration Build Protection
        # ==================================================

        build_mode = str(
            request.get(
                "build_mode",
                "NEW"
            )
        ).strip().upper()

        update_components = request.get(
            "update_components",
            []
        ) or []

        update_components = [
            str(component).strip().lower()
            for component in update_components
            if str(component).strip()
        ]

        #
        # Remove accidental duplicates while
        # preserving component order.
        #

        update_components = list(
            dict.fromkeys(
                update_components
            )
        )

        if build_mode not in (
            "NEW",
            "UPDATE"
        ):

            close_workbook(
                workbook
            )

            raise ValueError(
                "Invalid build_mode. "
                "Allowed values are NEW or UPDATE."
            )

        # ==================================================
        # Selective UPDATE Component Rules
        # ==================================================

        supported_components = {
            "lesson_content",
            "slides",
            "activities",
            "recap"
        }

        known_components = {
            "lesson_content",
            "slides",
            "quiz",
            "activities",
            "recap"
        }

        unknown_components = (
            set(update_components)
            - known_components
        )

        if unknown_components:

            close_workbook(
                workbook
            )

            raise ValueError(
                "Unknown update component(s): "
                + ", ".join(
                    sorted(
                        unknown_components
                    )
                )
            )

        #
        # NEW builds must never carry UPDATE selections.
        #

        if (
            build_mode == "NEW"
            and update_components
        ):

            close_workbook(
                workbook
            )

            raise ValueError(
                "NEW builds cannot contain "
                "update_components."
            )

        #
        # UPDATE requires at least one component.
        #

        if (
            build_mode == "UPDATE"
            and not update_components
        ):

            close_workbook(
                workbook
            )

            raise ValueError(
                "UPDATE requires at least one "
                "update component."
            )

        #
        # Quiz UPDATE is deliberately disabled
        # until safe Question Bank / Quiz slot
        # replacement is implemented.
        #

        if (
            build_mode == "UPDATE"
            and "quiz" in update_components
        ):

            close_workbook(
                workbook
            )

            raise ValueError(
                "Quiz UPDATE is not enabled yet."
            )

        unsupported_components = (
            set(update_components)
            - supported_components
        )

        if (
            build_mode == "UPDATE"
            and unsupported_components
        ):

            close_workbook(
                workbook
            )

            raise ValueError(
                "Unsupported UPDATE component(s): "
                + ", ".join(
                    sorted(
                        unsupported_components
                    )
                )
            )

        print("=" * 60)
        print("ELABORATION BUILD VALIDATION")
        print("Build Mode:", build_mode)
        print(
            "Update Components:",
            update_components
            or "NONE"
        )
        print("=" * 60)

        # ==================================================
        # Validate Every Selected Elaboration
        # ==================================================

        for lesson in lesson_rows:

            elaboration_key = lesson[
                "elaboration_key"
            ]

            published_build = get_published_build(
                elaboration_key
            )

            already_published = (
                published_build is not None
            )

            print(
                "Elaboration:",
                lesson["elaboration"]
            )

            print(
                "Already Published:",
                already_published
            )

            # ==============================================
            # NEW
            # ==============================================

            if build_mode == "NEW":

                if already_published:

                    close_workbook(
                        workbook
                    )

                    raise ValueError(
                        "This elaboration has already "
                        "been published. "
                        "Use UPDATE mode to modify it. "
                        f"Previous Build: "
                        f"{published_build.get('build_id')}"
                    )

            # ==============================================
            # UPDATE
            # ==============================================

            elif build_mode == "UPDATE":

                if not already_published:

                    close_workbook(
                        workbook
                    )

                    raise ValueError(
                        "This elaboration has not "
                        "previously been published. "
                        "UPDATE mode cannot be used. "
                        "Use NEW mode instead."
                    )

                # ==========================================
                # Moodle Identity Safety Checks
                # ==========================================

                required_moodle_ids = {

                    "lesson_content":
                        "moodle_lesson_content_cmid",

                    "slides":
                        "moodle_did_you_know_cmid",

                    "activities":
                        "moodle_activities_cmid",

                    "recap":
                        "moodle_recap_cmid"

                }

                for component in update_components:

                    registry_field = (
                        required_moodle_ids[
                            component
                        ]
                    )

                    moodle_id = (
                        published_build.get(
                            registry_field
                        )
                    )

                    if not moodle_id:

                        close_workbook(
                            workbook
                        )

                        raise ValueError(
                            "UPDATE blocked because "
                            f"{component} has no stored "
                            "Moodle CMID. "
                            "The system will not guess "
                            "which Moodle activity to update."
                        )

            # ==============================================
            # Carry Validated Data Downstream
            # ==============================================

            lesson["build_mode"] = (
                build_mode
            )

            lesson["update_components"] = (
                list(update_components)
            )

            if published_build:

                lesson[
                    "previous_build_id"
                ] = published_build.get(
                    "build_id"
                )

                lesson[
                    "previous_lesson_package_id"
                ] = published_build.get(
                    "lesson_package_id"
                )

                lesson[
                    "moodle_course_id"
                ] = published_build.get(
                    "moodle_course_id"
                )

                lesson[
                    "moodle_section_id"
                ] = published_build.get(
                    "moodle_section_id"
                )

                lesson[
                    "moodle_subsection_cmid"
                ] = published_build.get(
                    "moodle_subsection_cmid"
                )

                lesson[
                    "moodle_subsection_section_id"
                ] = published_build.get(
                    "moodle_subsection_section_id"
                )

                lesson[
                    "moodle_content_description_cmid"
                ] = published_build.get(
                    "moodle_content_description_cmid"
                )

                lesson[
                    "moodle_lesson_content_cmid"
                ] = published_build.get(
                    "moodle_lesson_content_cmid"
                )

                lesson[
                    "moodle_did_you_know_cmid"
                ] = published_build.get(
                    "moodle_did_you_know_cmid"
                )

                lesson[
                    "moodle_quiz_id"
                ] = published_build.get(
                    "moodle_quiz_id"
                )

                lesson[
                    "moodle_quiz_cmid"
                ] = published_build.get(
                    "moodle_quiz_cmid"
                )

                lesson[
                    "moodle_activities_cmid"
                ] = published_build.get(
                    "moodle_activities_cmid"
                )

                lesson[
                    "moodle_recap_cmid"
                ] = published_build.get(
                    "moodle_recap_cmid"
                )

            else:

                lesson[
                    "previous_build_id"
                ] = None

                lesson[
                    "previous_lesson_package_id"
                ] = None

                lesson[
                    "moodle_course_id"
                ] = None

                lesson[
                    "moodle_section_id"
                ] = None

                lesson[
                    "moodle_subsection_cmid"
                ] = None

                lesson[
                    "moodle_subsection_section_id"
                ] = None

                lesson[
                    "moodle_content_description_cmid"
                ] = None

                lesson[
                    "moodle_lesson_content_cmid"
                ] = None

                lesson[
                    "moodle_did_you_know_cmid"
                ] = None

                lesson[
                    "moodle_quiz_id"
                ] = None

                lesson[
                    "moodle_quiz_cmid"
                ] = None

                lesson[
                    "moodle_activities_cmid"
                ] = None

                lesson[
                    "moodle_recap_cmid"
                ] = None

        print("=" * 60)
        print("ELABORATION BUILD VALIDATION PASSED")
        print("=" * 60)

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

        # ==================================================
        # UPDATE - Carry Forward Published Lesson Context
        # ==================================================

        if build_mode == "UPDATE":

            for lesson in lesson_rows:

                self._carry_forward_lesson_content(
                    current_workbook_path=
                        build["path"],

                    previous_build_id=
                        lesson[
                            "previous_build_id"
                        ]
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
