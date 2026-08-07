from base_provider import BaseProvider


class NotebookLMProvider(BaseProvider):

    def generate(

            self,

            prompt_asset

    ):
        raise NotImplementedError()
