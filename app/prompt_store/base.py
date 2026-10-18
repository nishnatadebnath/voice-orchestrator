
from abc import ABC, abstractmethod



class PromptStore(ABC):
    """Contract for retrieving prompts from any storage backend."""

    @abstractmethod
    def get_prompt(self, prompt_id: str) -> dict[str, str]:
        """Return a parsed prompt using its unique ID."""
        pass
