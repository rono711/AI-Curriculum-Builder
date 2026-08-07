import os
import time
import requests

from dotenv import load_dotenv

load_dotenv("/volume1/docker/curriculum-builder/.env")


# ==========================================================
# Gamma Client
# ==========================================================

class GammaClient:

    def __init__(self):

        self.api_key = os.getenv("GAMMA_API_KEY")

        if not self.api_key:

            raise RuntimeError(

                "GAMMA_API_KEY not configured."

            )

        self.base_url = "https://public-api.gamma.app/v1.0"

        self.headers = {

            "X-API-KEY": self.api_key,

            "Content-Type": "application/json"

        }
        self.logo = os.getenv("RONO_LOGO")

    # ======================================================
    # Submit Generation
    # ======================================================

    def submit(

            self,

            prompt,

            cards=12

    ):

        payload = {

            "inputText":

                prompt,

            "textMode":

                "generate",

            "format":

                "presentation",

            "numCards":

                cards,

            "exportAs":

                "pptx"

        }

        response = requests.post(

            f"{self.base_url}/generations",

            headers=self.headers,

            json=payload,

            timeout=120

        )

        response.raise_for_status()

        return response.json()

    # ======================================================
    # Poll
    # ======================================================

    def poll(

            self,

            generation_id,

            interval=5,

            timeout=600

    ):

        start = time.time()

        while True:

            response = requests.get(

                f"{self.base_url}/generations/{generation_id}",

                headers=self.headers,

                timeout=60

            )

            response.raise_for_status()

            result = response.json()

            status = result.get(

                "status",

                ""

            ).lower()

            print(

                "Gamma:",

                status

            )

            if status == "completed":

                return result

            if status == "failed":

                raise RuntimeError(

                    "Gamma generation failed."

                )

            if (

                time.time() - start

            ) > timeout:

                raise TimeoutError(

                    "Gamma timed out."

                )

            time.sleep(

                interval

            )
