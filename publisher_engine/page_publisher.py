# ==========================================================
# Page Publisher
# ==========================================================

from pathlib import Path


class PagePublisher:

    def __init__(

            self,

            moodle

    ):

        self.moodle = moodle

    # ======================================================
    # Mission
    # ======================================================

    # ======================================================
    # Mission
    # ======================================================

    def publish_mission(

            self,

            course,

            section,

            lesson,

            build_root,

            build_name

    ):

        import json

        metadata = lesson["metadata"]

        descriptions = lesson["descriptions"]

        print("=" * 60)
        print("DISPLAY TITLE READ BY PUBLISHER")
        print(descriptions.get("display_title"))
        print("=" * 60)

        display_title = descriptions.get("display_title", "")

        if display_title:
            display_title = str(display_title).strip()

        if not display_title:
            display_title = metadata["lesson_title"]

        page_title = f'{metadata["curriculum_code"]} - {display_title}'

        #
        # --------------------------------------------------
        # Lesson Content
        # --------------------------------------------------
        #

        content_folder = (

                Path(build_root)

                / "Content"

                / build_name

        )

        lesson_markdown = ""

        lesson_file = (

                content_folder

                / "lesson_output.md"

        )

        if lesson_file.exists():
            lesson_markdown = lesson_file.read_text(

                encoding="utf-8"

            )

        #
        # --------------------------------------------------
        # HTML
        # --------------------------------------------------
        #

        html = f"""
        <pre>

        {lesson_markdown}

        </pre>
        """

        payload = {

            "lesson_package_id":

                metadata["lesson_package_id"],

            "activity_type":

                "MISSION",

            "courseid":

                course["courseid"],

            "section":

                section["section"],

            "title":

                page_title,

        "description":

        descriptions.get(

            "mission_description",

            ""

        ),

        "content":

        html

        }

        return self.moodle.publish_page(

            payload

        )

    def publish_did_you_know(

            self,

            course,

            section,

            lesson,

            build_root,

            build_name

    ):

        metadata = lesson["metadata"]

        descriptions = lesson["descriptions"]

        slides_folder = (

                Path(build_root)

                / "Slides"

                / build_name

        )

        iframe = ""

        import json

        urls = slides_folder / "slides_urls.json"

        if urls.exists():

            data = json.loads(

                urls.read_text(

                    encoding="utf-8"

                )

            )

            embed = data.get(

                "gamma_embed_url",

                ""

            )

            if embed:
                iframe = f"""

        <iframe
        src="{embed}"
        width="100%"
        height="720"
        allowfullscreen>
        </iframe>

        """

        return self.moodle.publish_page({

            "lesson_package_id":

                metadata["lesson_package_id"],

            "activity_type":

                "DID_YOU_KNOW",

            "courseid":

                course["courseid"],

            "section":

                section["section"],

            "title":

                "💡 Did You Know?",

            "description":

                descriptions.get(

                    "slides_description",

                    ""

                ),

            "content":

                iframe

        })

    # ======================================================
    # Activities
    # ======================================================

    # ======================================================
    # Activities
    # ======================================================

    def publish_activities(

            self,

            course,

            section,

            lesson,

            build_root,

            build_name

    ):

        metadata = lesson["metadata"]

        descriptions = lesson["descriptions"]

        activities_folder = (

                Path(build_root)

                / "Activities"

                / build_name

        )

        html = ""

        html_file = (

                activities_folder

                / "activities.html"

        )

        if html_file.exists():
            html = html_file.read_text(

                encoding="utf-8"

            )

        payload = {

            "lesson_package_id":

                metadata["lesson_package_id"],

            "activity_type":

                "ACTIVITIES",

            "courseid":

                course["courseid"],

            "section":

                section["section"],

            "title":

                "✋ Let's Do It",

            "description":

                descriptions.get(

                    "activities_description",

                    ""

                ),

            "content":

                html

        }

        return self.moodle.publish_page(

            payload

        )

    # ======================================================
    # Recap
    # ======================================================

    def publish_recap(

            self,

            course,

            section,

            lesson,

            build_root,

            build_name

    ):

        metadata = lesson["metadata"]

        descriptions = lesson["descriptions"]

        recap_folder = (

                Path(build_root)

                / "Recap"

                / build_name

        )

        html = ""

        html_file = (

                recap_folder

                / "recap.html"

        )

        if html_file.exists():
            html = html_file.read_text(

                encoding="utf-8"

            )

        payload = {

            "lesson_package_id":

                metadata["lesson_package_id"],

            "activity_type":

                "RECAP",

            "courseid":

                course["courseid"],

            "section":

                section["section"],

            "title":

                "🎯 What We Discovered",

            "description":

                descriptions.get(

                    "recap_description",

                    ""

                ),

            "content":

                html

        }

        return self.moodle.publish_page(

            payload

        )
