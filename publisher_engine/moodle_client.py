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

        result = response.json()

        if (

            isinstance(result, dict)

            and

            "exception" in result

        ):

            raise RuntimeError(

                result["message"]

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
    # Course
    # ======================================================

    def publish_course(

            self,

            payload

    ):

        return self.call(

            "local_rono_curriculumbuilder_publish_course",

            payload

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
