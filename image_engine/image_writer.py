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

            parent_code

    ):

        return (
            self.output_folder
            /
            f"{parent_code}_image_prompt.txt"
        )

    def image_path(

            self,

            parent_code

    ):

        return (
            self.output_folder
            /
            f"{parent_code}_content_description.png"
        )

    # ======================================================
    # Existing Image
    # ======================================================

    def image_exists(

            self,

            parent_code

    ):

        path = self.image_path(
            parent_code
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

            parent_code,

            prompt

    ):

        path = self.prompt_path(
            parent_code
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

            parent_code,

            image_bytes

    ):

        path = self.image_path(
            parent_code
        )

        path.write_bytes(
            image_bytes
        )

        return path
