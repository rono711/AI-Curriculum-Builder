from pathlib import Path

from image_runner import ImageRunner


# ==========================================================
# Image Builder
# ==========================================================

class ImageBuilder:

    def __init__(self):

        self.runner = ImageRunner()

    # ======================================================
    # Generate
    # ======================================================

    def generate(

            self,

            build_root,

            build_name,

            lesson_package_id,

            parent_code,

            force_regenerate=False

    ):

        build_root = Path(
            build_root
        )

        if not build_name:

            raise RuntimeError(
                "build_name cannot be empty."
            )

        if not lesson_package_id:

            raise RuntimeError(
                "lesson_package_id cannot be empty."
            )


        if not parent_code:

            raise RuntimeError(
                "parent_code cannot be empty."
            )


        # ==================================================
        # Prompt
        # ==================================================

        prompt_file = (
            build_root
            /
            "Prompts"
            /
            build_name
            /
            "image.md"
        )

        if not prompt_file.exists():

            raise FileNotFoundError(
                f"IMAGE prompt not found: "
                f"{prompt_file}"
            )

        # ==================================================
        # Output
        # ==================================================

        output_folder = (
            build_root
            /
            "Images"
            /
            build_name
        )

        print("=" * 60)
        print("IMAGE BUILDER")
        print("Build Root :", build_root)
        print("Build Name :", build_name)
        print("Lesson     :", lesson_package_id)
        print("Parent Code:", parent_code)
        print("Prompt     :", prompt_file)
        print("Output     :", output_folder)
        print("=" * 60)

        return self.runner.generate(

            prompt_file=prompt_file,

            output_folder=output_folder,

            lesson_package_id=lesson_package_id,

            parent_code=parent_code,

            force_regenerate=force_regenerate

        )
