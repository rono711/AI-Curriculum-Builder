from abc import ABC, abstractmethod


# ==========================================================
# Base Provider
# ==========================================================

class BaseProvider(ABC):

    @abstractmethod
    def generate(

            self,

            prompt_asset

    ):
        """
        Every AI provider must implement this.
        """

        pass
