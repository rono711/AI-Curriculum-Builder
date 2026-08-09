from pathlib import Path

import requests
from openpyxl import load_workbook
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

            print("=" * 60)
            print("PROCESSING", lesson_package_id)
            print("=" * 60)

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
            print("PROMPT COMPLETE")
            print(prompt_type)
            print("=" * 60)

            engine_build_root = str(build["path"].parent.parent)
            engine_build_name = build["path"].stem

            engines = [
                ("Gamma", GAMMA_ENGINE_URL),
                ("Quiz", QUIZ_ENGINE_URL),
                ("Activities", ACTIVITIES_ENGINE_URL),
                ("Recap", RECAP_ENGINE_URL),
            ]

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
