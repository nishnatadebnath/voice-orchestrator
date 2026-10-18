
"""Provide centralized access to prompts and their formatted text."""

from app.prompt_store.base import PromptStore
from app.prompt_store.formatter import format_prompt as format_prompt_text


class PromptService:
    """Central entry point for retrieving and formatting prompts."""

    def __init__(self, store: PromptStore):
        self.store = store

    def get_prompt(self, prompt_id: str) -> dict[str, str]:
        """Return the parsed prompt, including its metadata."""
        return self.store.get_prompt(prompt_id)

    def format_prompt(self, prompt_id: str) -> str:
        """Retrieve and format a prompt by its ID."""
        prompt = self.get_prompt(prompt_id)
        return format_prompt_text(prompt)

    def format_loaded_prompt(self, prompt: dict[str, str]) -> str:
        """Format a prompt that has already been retrieved."""
        return format_prompt_text(prompt)
