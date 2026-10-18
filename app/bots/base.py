
from abc import ABC, abstractmethod


class BaseBot(ABC):
    """Defines the common contract that every specialist bot must follow."""

    @abstractmethod
    def respond(
        self,
        message: str,
        formatted_prompt: str,
        history: list[dict[str, str]],
    ) -> str:
        """Generate a response using prompt instructions and conversation history."""
        pass
