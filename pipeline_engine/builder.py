from pathlib import Path
import sys

import requests
from openpyxl import load_workbook



# ==========================================================
# Shared Project Modules
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from build_registry import (
    start_build,
    mark_published,
    mark_update_ready
)
from config import (
    PROMPT_ENGINE_URL,
    GAMMA_ENGINE_URL,
    QUIZ_ENGINE_URL,
    ACTIVITIES_ENGINE_URL,
    RECAP_ENGINE_URL,
    PUBLISHER_ENGINE_URL,
    PROMPT_TIMEOUT,
    ENGINE_TIMEOUT
)


# ==========================================================
# Pipeline Builder
# ==========================================================

class PipelineBuilder:

    def __init__(self):
        print("=" * 60)
        print("PIPELINE BUILDER INITIALIZED")
        print("=" * 60)
    # ======================================================
    # Moodle Publication Status
    # ======================================================

    @staticmethod
    def _get_publication_status(
            workbook_path,
            lesson_package_id
    ):

        workbook = load_workbook(
            workbook_path,
            read_only=True,
            data_only=True
        )

        try:

            if "Moodle_Publish" not in workbook.sheetnames:
                return ""

            sheet = workbook[
                "Moodle_Publish"
            ]

            headers = {}

            for cell in sheet[1]:

                if not cell.value:
                    continue

                key = (
                    str(cell.value)
                    .strip()
                    .lower()
                    .replace(" ", "_")
                    .replace("-", "_")
                )

                headers[key] = cell.column

            if "lesson_package_id" not in headers:
                return ""

            if "publication_status" not in headers:
                return ""

            for row in range(
                    2,
                    sheet.max_row + 1
            ):

                value = sheet.cell(
                    row=row,
                    column=headers[
                        "lesson_package_id"
                    ]
                ).value

                if str(value) == str(
                        lesson_package_id
                ):

                    status = sheet.cell(
                        row=row,
                        column=headers[
                            "publication_status"
                        ]
                    ).value

                    if status is None:
                        return ""

                    return str(
                        status
                    ).strip().upper()

            return ""

        finally:

            workbook.close()

    # ======================================================
    # Run Pipeline
    # ======================================================

    def run(

            self,

            build_root,

            build_name,

            lesson_rows

    ):
        #
        # ==================================================
        # Prompt Generation Pipeline
        # ==================================================
        #
        build = {
            "path": Path(build_root) / "Workbook" / f"{build_name}.xlsx",
            "build_id": build_name,
            "filename": f"{build_name}.xlsx"
        }

        results = []

        for lesson in lesson_rows:

            lesson_package_id = lesson["lesson_package_id"]

            elaboration_key = lesson["elaboration_key"]

            print("=" * 60)
            print("PROCESSING", lesson_package_id)
            print("ELABORATION KEY:", elaboration_key)
            print("=" * 60)

            registry_record_id = start_build(

                elaboration_key=elaboration_key,

                learning_area=lesson["learning_area"],

                subject=lesson["subject"],

                year_level=lesson["year_level"],

                strand=lesson["strand"],

                sub_strand=lesson["sub_strand"],

                parent_code=lesson["parent_code"],

                topic_id=lesson["topic_id"],

                curriculum_code=lesson["curriculum_code"],

                content_description=lesson["content_description"],

                elaboration=lesson["elaboration"],

                build_id=lesson["build_id"],

                lesson_package_id=lesson_package_id,

                build_mode=lesson.get(
                    "build_mode",
                    "NEW"
                ),

                update_components=lesson.get(
                    "update_components",
                    []
                )

            )

            print(
                "REGISTRY RECORD:",
                registry_record_id,
                "STATUS: BUILDING"
            )

            # ==================================================
            # Build Mode / Selective UPDATE
            # ==================================================

            build_mode = str(
                lesson.get(
                    "build_mode",
                    "NEW"
                )
            ).strip().upper()

            update_components = (
                lesson.get(
                    "update_components",
                    []
                )
                or []
            )

            print("=" * 60)
            print("PIPELINE EXECUTION MODE")
            print("Build Mode:", build_mode)
            print(
                "Update Components:",
                update_components
                or "ALL - NEW BUILD"
            )
            print("=" * 60)

            # ==================================================
            # Prompt Selection
            # ==================================================

            if build_mode == "NEW":

                prompt_sequence = [

                    "LESSON_CONTENT",
                    "DISPLAY_TITLE",
                    "MISSION",

                    "GAMMA_SLIDES",
                    "DID_YOU_KNOW",

                    "QUIZ",
                    "CHECKING_YOUR_THINKING",

                    "ACTIVITIES",
                    "LETS_DO_IT",

                    "RECAP",
                    "WHAT_WE_DISCOVERED"

                ]

            else:

                prompt_map = {

                    "lesson_content": [
                        "LESSON_CONTENT",
                        "DISPLAY_TITLE",
                        "MISSION"
                    ],

                    "slides": [
                        "GAMMA_SLIDES",
                        "DID_YOU_KNOW"
                    ],

                    "quiz": [
                        "QUIZ",
                        "CHECKING_YOUR_THINKING"
                    ],

                    "activities": [
                        "ACTIVITIES",
                        "LETS_DO_IT"
                    ],

                    "recap": [
                        "RECAP",
                        "WHAT_WE_DISCOVERED"
                    ]

                }

                prompt_sequence = []

                for component in update_components:

                    prompt_sequence.extend(
                        prompt_map.get(
                            component,
                            []
                        )
                    )

                prompt_sequence = list(
                    dict.fromkeys(
                        prompt_sequence
                    )
                )

            print(
                "Prompt Sequence:",
                prompt_sequence
            )

            prompt_results = []

            for prompt_type in prompt_sequence:

                print("CALLING PROMPT ENGINE")
                print("PROMPT TYPE:", prompt_type)
                print("LESSON PACKAGE:", lesson_package_id)
                print("=" * 60)

                response = requests.post(
                    PROMPT_ENGINE_URL,
                    json={
                        "workbook_path": str(build["path"]),
                        "lesson_package_id": lesson_package_id,
                        "prompt_type": prompt_type
                    },
                    timeout=PROMPT_TIMEOUT)
                print("PROMPT:", prompt_type)
                print("STATUS :", response.status_code)

                if response.status_code != 200:
                    print(response.text)
                response.raise_for_status()

                result = response.json()

                print("=" * 60)
                print("PROMPT RESULT")
                print(result)
                print("=" * 60)

                prompt_results.append(result)

            print("=" * 60)
            print("PROMPT GENERATION COMPLETE")
            print(
                "Prompts Executed:",
                prompt_sequence
            )
            print("=" * 60)
            engine_build_root = str(build["path"].parent.parent)
            engine_build_name = build["path"].stem

            if build_mode == "NEW":

                engines = [

                    (
                        "Gamma",
                        GAMMA_ENGINE_URL
                    ),

                    (
                        "Quiz",
                        QUIZ_ENGINE_URL
                    ),

                    (
                        "Activities",
                        ACTIVITIES_ENGINE_URL
                    ),

                    (
                        "Recap",
                        RECAP_ENGINE_URL
                    )

                ]

            else:

                engine_map = {

                    "slides": (
                        "Gamma",
                        GAMMA_ENGINE_URL
                    ),

                    "quiz": (
                        "Quiz",
                        QUIZ_ENGINE_URL
                    ),

                    "activities": (
                        "Activities",
                        ACTIVITIES_ENGINE_URL
                    ),

                    "recap": (
                        "Recap",
                        RECAP_ENGINE_URL
                    )

                }

                engines = []

                for component in update_components:

                    engine = engine_map.get(
                        component
                    )

                    if engine:

                        engines.append(
                            engine
                        )

            print(
                "Engines Selected:",
                [
                    name
                    for name, url in engines
                ]
            )
            for engine_name, engine_url in engines:

                print("=" * 60)
                print(f"CALLING {engine_name.upper()} ENGINE")
                print("=" * 60)

                response = requests.post(
                    engine_url,
                    json={
                        "build_root": engine_build_root,
                        "build_name": engine_build_name,
                        "lesson_package_id": lesson_package_id
                    },
                    timeout=ENGINE_TIMEOUT
                )

                print(engine_name, response.status_code)

                if response.status_code != 200:
                    print(response.text)

                response.raise_for_status()


            # ==================================================
            # UPDATE Moodle Safety Barrier
            # ==================================================
            #
            # Selective UPDATE generation is now supported,
            # but Moodle in-place UPDATE publishing has not
            # yet been implemented.
            #
            # NEVER allow UPDATE to fall through into the
            # existing NEW publisher because that publisher
            if build_mode == "UPDATE":

                mark_update_ready(
                    registry_record_id,
                    update_components=",".join(
                        update_components
                    )
                )

                print("=" * 60)
                print("UPDATE GENERATION COMPLETE")
                print(
                    "Components:",
                    update_components
                )
                print(
                    "REGISTRY RECORD:",
                    registry_record_id,
                    "STATUS: UPDATE_READY"
                )
                print(
                    "MOODLE UPDATE PUBLISHING BLOCKED"
                )
                print("=" * 60)

                results.append({
                    "lesson_package_id":
                        lesson_package_id,

                    "status":
                        "UPDATE_READY",

                    "build_mode":
                        "UPDATE",

                    "update_components":
                        update_components,

                    "prompts":
                        prompt_results,

                    "publisher": {
                        "status": "BLOCKED",
                        "reason":
                            "MOODLE_UPDATE_NOT_ENABLED"
                    }
                })

                continue
            # ==================================================
            # Moodle Publication
            # ==================================================

            publication_status = self._get_publication_status(
                build["path"],
                lesson_package_id
            )

            print("=" * 60)
            print("MOODLE PUBLICATION STATUS")
            print("Lesson :", lesson_package_id)
            print("Status :", publication_status or "NOT PUBLISHED")
            print("=" * 60)

            publisher_result = None

            if publication_status == "PUBLISHED":

                print("=" * 60)
                print("PUBLISHER SKIPPED")
                print(
                    lesson_package_id,
                    "is already PUBLISHED."
                )
                print("=" * 60)

                publisher_result = {
                    "status": "SKIPPED",
                    "reason": "ALREADY_PUBLISHED"
                }
                #
                # Workbook confirms this lesson package
                # was already successfully published.
                # Synchronize the persistent registry.
                #

                mark_published(
                    registry_record_id
                )

                print(
                    "REGISTRY RECORD:",
                    registry_record_id,
                    "STATUS: PUBLISHED"
                )

            else:

                print("=" * 60)
                print("CALLING PUBLISHER ENGINE")
                print("=" * 60)

                response = requests.post(
                    PUBLISHER_ENGINE_URL,
                    json={
                        "build_root":
                            engine_build_root,

                        "build_name":
                            engine_build_name,

                        "lesson_package_id":
                            lesson_package_id
                    },
                    timeout=ENGINE_TIMEOUT
                )

                print(
                    "Publisher",
                    response.status_code
                )

                if response.status_code != 200:
                    print(response.text)

                response.raise_for_status()

                publisher_result = response.json()

                if (
                    publisher_result.get("status")
                    != "SUCCESS"
                ):

                    raise RuntimeError(
                        "Publisher Engine did not "
                        "return SUCCESS for "
                        f"{lesson_package_id}: "
                        f"{publisher_result}"
                    )
                mark_published(

                    record_id=
                        registry_record_id,

                    moodle_course_id=
                        publisher_result.get(
                            "courseid"
                        ),

                    moodle_section_id=
                        publisher_result.get(
                            "strandsectionid"
                        ),

                    moodle_subsection_cmid=
                        publisher_result.get(
                            "subsectioncmid"
                        ),

                    moodle_subsection_section_id=
                        publisher_result.get(
                            "subsectionsectionid"
                        ),

                    moodle_content_description_cmid=
                        publisher_result.get(
                            "contentdescriptioncmid"
                        ),

                    moodle_lesson_content_cmid=
                        publisher_result.get(
                            "lessoncontentcmid"
                        ),

                    moodle_did_you_know_cmid=
                        publisher_result.get(
                            "didyouknowcmid"
                        ),

                    moodle_quiz_id=
                        publisher_result.get(
                            "quizid"
                        ),

                    moodle_quiz_cmid=
                        publisher_result.get(
                            "quizcmid"
                        ),

                    moodle_activities_cmid=
                        publisher_result.get(
                            "activitiescmid"
                        ),

                    moodle_recap_cmid=
                        publisher_result.get(
                            "recapcmid"
                        )

                )

                print(
                    "REGISTRY RECORD:",
                    registry_record_id,
                    "STATUS: PUBLISHED"
                )
            #
            # Finished
            #

            print("=" * 60)
            print("LESSON PACKAGE BUILD COMPLETED")
            print("Build ID :", build["build_id"])
            print("Lesson   :", lesson_package_id)
            print("=" * 60)

            results.append({
                "lesson_package_id":
                    lesson_package_id,

                "status":
                    "SUCCESS",

                "prompts":
                    prompt_results,

                "publisher":
                    publisher_result
            })

        return {

            "status": "SUCCESS",

            "build_id": build["build_id"],

            "filename": build["filename"],

            "workbook_path": str(build["path"]),

            "lessons": results

        }
