import os
import requests

from dotenv import load_dotenv

# ==========================================================
# Environment
# ==========================================================

load_dotenv(

    "/volume1/docker/curriculum-builder/.env"

)


# ==========================================================
# Moodle Client
# ==========================================================

class MoodleClient:

    def __init__(self):

        self.base_url = os.getenv(

            "MOODLE_URL"

        ).rstrip("/")

        self.token = os.getenv(

            "MOODLE_TOKEN"

        )

    # ======================================================
    # REST Call
    # ======================================================

    def call(

            self,

            function,

            payload

    ):

        url = (

            self.base_url

            + "/webservice/rest/server.php"

        )

        data = {

            "wstoken":

                self.token,

            "moodlewsrestformat":

                "json",

            "wsfunction":

                function

        }

        data.update(

            payload

        )

        response = requests.post(

            url,

            data=data,

            timeout=300

        )

        response.raise_for_status()

        try:

            result = response.json()

        except ValueError as exc:

            raise RuntimeError(
                "Moodle returned a non-JSON response: "
                + response.text[:1000]
            ) from exc

        if (
            isinstance(result, dict)
            and
            "exception" in result
        ):

            print("=" * 60)
            print("MOODLE RAW ERROR RESPONSE")
            print(result)
            print("=" * 60)

            exception_name = result.get(
                "exception",
                "Unknown Moodle exception"
            )

            error_code = result.get(
                "errorcode",
                ""
            )

            message = result.get(
                "message",
                ""
            )

            debug_info = result.get(
                "debuginfo",
                ""
            )

            error_parts = [
                f"Moodle exception: {exception_name}",
                f"Error code: {error_code}",
                f"Message: {message}"
            ]

            if debug_info:

                error_parts.append(
                    f"Debug info: {debug_info}"
                )

            raise RuntimeError(
                "\n".join(
                    error_parts
                )
            )

        return result
       

    # ======================================================
    # Health
    # ======================================================

    def health(self):

        return self.call(

            "local_rono_curriculumbuilder_health",

            {}

        )

    # ======================================================
    # Rono Publisher - Ensure Course
    # ======================================================

    def ensure_course(
            self,
            school_level,
            subject,
            year_level
    ):

        return self.call(
            "local_rono_publisher_ensure_course",
            {
                "school_level":
                    school_level,

                "subject":
                    subject,

                "year_level":
                    year_level,
            }
        )

    # ======================================================
    # Section
    # ======================================================

    def publish_section(

            self,

            payload

    ):

        return self.call(

            "local_rono_curriculumbuilder_publish_section",

            payload

        )

    # ======================================================
    # Mission / Activities / Recap
    # ======================================================

    def publish_page(

            self,

            payload

    ):

        return self.call(

            "local_rono_curriculumbuilder_publish_page",

            payload

        )

    # ======================================================
    # Quiz
    # ======================================================

    def publish_quiz(

            self,

            payload

    ):

        return self.call(

            "local_rono_curriculumbuilder_publish_quiz",

            payload

        )
    # ======================================================
    # Rono Publisher - Complete Lesson
    # ======================================================

    def publish_lesson(

            self,

            payload

    ):

        """
        Publish one complete curriculum lesson using the
        Moodle 5.2 Rono Publisher plugin.

        Moodle function:

            local_rono_publisher_publish_lesson

        The endpoint creates:

            Strand section
            Sub-strand subsection
            Content Description
            Lesson Content
            Did You Know
            Checking Your Thinking Quiz
            Question Bank category
            Questions
            Quiz slots
            Activities
            Recap
        """

        return self.call(

            "local_rono_publisher_publish_lesson",

            payload

        )
    # ======================================================
    # Rono Publisher - Update Existing Component
    # ======================================================

    def update_component(

            self,

            payload

    ):

        """
        Update one existing published lesson component
        using its exact Moodle course-module ID.

        Moodle function:

            local_rono_publisher_update_component

        Initial supported component:

            recap
        """

        return self.call(

            "local_rono_publisher_update_component",

            payload

        )
    # ======================================================
    # Rono Publisher - Update Elaboration Banner
    # ======================================================

    def update_elaboration_banner(
            self,
            payload
    ):

        """
        Update the exact existing Moodle Text & Media
        elaboration banner by CMID.

        Moodle function:
            local_rono_publisher_update_elaboration_banner
        """

        return self.call(
            "local_rono_publisher_update_elaboration_banner",
            payload
        )

    # ======================================================
    # Synchronise
    # ======================================================

    def sync(

            self,

            payload

    ):

        return self.call(

            "local_rono_curriculumbuilder_sync_lesson",

            payload

        )
