from chatgpt_provider import ChatGPTProvider
from gemini_provider import GeminiProvider
from gamma_provider import GammaProvider
from notebooklm_provider import NotebookLMProvider


# ==========================================================
# Provider Router
# ==========================================================

class ProviderRouter:

    def __init__(self):
        self.providers = {

            "CHATGPT":

                ChatGPTProvider(),

            "GEMINI":

                GeminiProvider(),

            "GAMMA":

                GammaProvider(),

            "NOTEBOOKLM":

                NotebookLMProvider()

        }

    # ======================================================
    # Provider
    # ======================================================

    def provider(

            self,

            name

    ):
        name = name.upper()

        if name not in self.providers:
            raise ValueError(

                f"Unknown Content Provider: {name}"

            )

        return self.providers[name]

    # ======================================================
    # Execute
    # ======================================================

    def generate(

            self,

            provider,

            prompt_asset

    ):
        engine = self.provider(

            provider

        )

        return engine.generate(

            prompt_asset

        )
