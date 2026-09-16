import sys
from pathlib import Path
import json

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

from quiz_runner import QuizRunner

from quiz_writer import QuizWriter


# ==========================================================
# Quiz Builder
# ==========================================================

class QuizBuilder:

    def __init__(self):

        self.runner = QuizRunner()

    # ======================================================
    # Apply Pre-Generated Batch Result
    # ======================================================

    def apply_batch_result(
            self,
            workbook_path,
            lesson_package_id,
            content,
            description,
            provider="CHATGPT_BATCH",
            model=""
    ):
        """
        Apply an already-generated Quiz result.

        This method performs no AI generation.
        """

        workbook_path = Path(
            workbook_path
        )

        paths = BuildPaths(
            str(workbook_path)
        )

        quiz_folder = paths.quiz_folder

        quiz_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        gift_content = (
            self.runner.process_batch_content(
                content,
                lesson_package_id
            )
        )

        result = {
            "status":
                "SUCCESS",
            "provider":
                provider,
            "model":
                model,
            "title":
                "Checking Your Thinking",
            "description":
                str(description or "").strip(),
            "gift":
                gift_content,
            "prompt_tokens":
                0,
            "completion_tokens":
                0,
            "total_tokens":
                0,
        }

        if not result["description"]:
            raise RuntimeError(
                "Quiz batch description is empty."
            )

        gift_file = (
            quiz_folder
            / "lesson_quiz.gift"
        )

        gift_file.write_text(
            result["gift"],
            encoding="utf-8"
        )

        json_file = (
            quiz_folder
            / "lesson_quiz.json"
        )

        json_file.write_text(
            json.dumps(
                result,
                indent=4,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

        writer = QuizWriter(
            str(workbook_path)
        )

        writer.update_quiz(
            lesson_package_id=lesson_package_id,
            quiz_filename=gift_file.name,
            generation_status="COMPLETED",
            review_status="PENDING"
        )

        writer.update_descriptions(
            lesson_package_id=lesson_package_id,
            quiz_title=result["title"],
            quiz_description=result["description"],
            generation_status="COMPLETED",
            review_status="PENDING"
        )

        writer.update_asset_register(
            lesson_package_id=lesson_package_id,
            asset_type="QUIZ",
            filename=gift_file.name,
            url=""
        )

        writer.log(
            component="Quiz Engine",
            action="Apply Batch Quiz",
            status="SUCCESS",
            details=gift_file.name
        )

        writer.save()

        return result

    # ======================================================
    # Generate
    # ======================================================

    def generate(

            self,

            build_root,

            build_name,

            lesson_package_id

    ):

        #
        # Workbook
        #

        workbook_path = (

            Path(build_root)

            / "Workbook"

            / f"{build_name}.xlsx"

        )
        #
        # Workbook Writer
        #

        writer = QuizWriter(

            str(workbook_path)

        )
        #
        # Build Paths
        #

        paths = BuildPaths(

            str(workbook_path)

        )

        #
        # Prompt Assets
        #

        prompt_file = (

            paths.prompts_folder

            / "quiz.md"

        )

        description_prompt_file = (

                paths.prompts_folder

                / "checking_your_thinking.md"

        )

        metadata_file = (

            paths.prompts_folder

            / "quiz.json"

        )

        #
        # Quiz Folder
        #

        quiz_folder = (

            paths.build_root

            / "Quiz"

            / build_name

        )

        quiz_folder.mkdir(

            parents=True,

            exist_ok=True

        )

        print("=" * 60)
        print("QUIZ PROMPT")
        print(prompt_file)
        print("=" * 60)

        #
        # Generate Quiz
        #

        result = self.runner.generate(

            prompt_file=str(prompt_file),
            description_prompt_file=str(description_prompt_file),
            metadata_file=str(metadata_file)

        )

        #
        # Save GIFT
        #

        gift_file = (

            quiz_folder

            / "lesson_quiz.gift"

        )

        gift_file.write_text(

            result["gift"],

            encoding="utf-8"

        )

        #
        # Save JSON
        #

        json_file = (

            quiz_folder

            / "lesson_quiz.json"

        )

        json_file.write_text(

            json.dumps(

                result,

                indent=4,

                ensure_ascii=False

            ),

            encoding="utf-8"

        )

        #
        # Workbook Writer
        #

        writer = QuizWriter(

            str(workbook_path)

        )
        #
        # Update Quiz Worksheet
        #
        writer.update_quiz(

            lesson_package_id=lesson_package_id,

            quiz_filename=gift_file.name,

            generation_status="COMPLETED",

            review_status="PENDING"

        )
        #
        # Update Descriptions Worksheet
        #
        print("=" * 60)
        print("CALLING update_descriptions")
        print("=" * 60)

        writer.update_descriptions(

            lesson_package_id=lesson_package_id,

            quiz_title=result["title"],

            quiz_description=result["description"],

            generation_status="COMPLETED",

            review_status="PENDING"

        )
        #
        # Asset Register
        #
        writer.update_asset_register(

            lesson_package_id=lesson_package_id,

            asset_type="QUIZ",

            filename=gift_file.name,

            url=""

        )
        #
        # Build Log
        #
        writer.log(

            component="Quiz Engine",

            action="Generate Quiz",

            status="SUCCESS",

            details=gift_file.name

        )
        #
        # Save Workbook
        #
        writer.save()
        #
        # Finished
        #
        return result