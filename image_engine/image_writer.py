from pathlib import Path


# ==========================================================
# Image Writer
# ==========================================================

class ImageWriter:

    def __init__(

            self,

            output_folder

    ):

        self.output_folder = Path(
            output_folder
        )

        self.output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

    # ======================================================
    # Paths
    # ======================================================

    def prompt_path(

            self,

            curriculum_code

    ):

        return (
            self.output_folder
            /
            f"{curriculum_code}_elaboration_image_prompt.txt"
        )

    def image_path(

            self,

            curriculum_code

    ):

        return (
            self.output_folder
            /
            f"{curriculum_code}_elaboration.png"
        )

    # ======================================================
    # Existing Image
    # ======================================================

    def image_exists(

            self,

            curriculum_code

    ):

        path = self.image_path(
            curriculum_code
        )

        return (
            path.exists()
            and
            path.is_file()
            and
            path.stat().st_size > 0
        )

    # ======================================================
    # Write Prompt
    # ======================================================

    def write_prompt(

            self,

            curriculum_code,

            prompt

    ):

        path = self.prompt_path(
            curriculum_code
        )

        path.write_text(
            prompt,
            encoding="utf-8"
        )

        return path

    # ======================================================
    # Write Image
    # ======================================================

        # ======================================================
    # Write Image
    # ======================================================

    def write_image(

            self,

            curriculum_code,

            image_bytes

    ):

        path = self.image_path(
            curriculum_code
        )

        path.write_bytes(
            image_bytes
        )

        return path
