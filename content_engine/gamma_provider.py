from base_provider import BaseProvider

import requests

from shared.services import GENERATE_PRESENTATION


class GammaProvider(BaseProvider):

    def __init__(self):
        self.url = GENERATE_PRESENTATION

    def generate(

            self,

            prompt_asset

    ):
        response = requests.post(

            self.url,

            json=prompt_asset,

            timeout=300

        )

        response.raise_for_status()

        return response.json()
