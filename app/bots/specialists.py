
from app.bots.base import BaseBot
from app.llm.base import LLMClient


class SalesBot(BaseBot):
    """Handles sales-related conversations using an LLM."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def respond(
        self,
        message: str,
        formatted_prompt: str,
        history: list[dict[str, str]],
    ) -> str:
        """Generate a sales response using the configured LLM."""
        return self.llm_client.generate(
            system_prompt=formatted_prompt,
            message=message,
            history=history,
        )


class PersonalLoanBot(BaseBot):
    """Handles personal-loan conversations using an LLM."""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def respond(
        self,
        message: str,
        formatted_prompt: str,
        history: list[dict[str, str]],
    ) -> str:
        """Generate a personal-loan response using the configured LLM."""
        return self.llm_client.generate(
            system_prompt=formatted_prompt,
            message=message,
            history=history,
        )
