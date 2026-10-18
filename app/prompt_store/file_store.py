
from pathlib import Path

from app.prompt_store.base import PromptStore
from app.prompt_store.xml_parser import parse_prompt


class FilePromptStore(PromptStore):
    """Retrieves and parses XML prompts stored on disk."""

    def __init__(self, prompts_dir: str = "app/prompts"):
        # Store the directory used to locate prompt files.
        self.prompts_dir = Path(prompts_dir)
         # Stores parsed prompts so repeated requests avoid disk reads and XML parsing.
        self._cache: dict[str, dict[str, str]] = {}

    def get_prompt(self, prompt_id: str) -> dict[str, str]:
        """Load a prompt and verify its XML identity matches the requested ID."""
        if not prompt_id or not all(
            char.isalnum() or char in "_-" for char in prompt_id
        ):
            raise ValueError("Invalid prompt ID")

        prompt_path = self.prompts_dir / f"{prompt_id}.xml"

        if not prompt_path.is_file():
            raise FileNotFoundError(f"Prompt not found: {prompt_id}")

        xml_content = prompt_path.read_text(encoding="utf-8")
        prompt = parse_prompt(xml_content)

        # Ensure the XML declares the same ID as the requested prompt.
        if prompt["id"] != prompt_id:
            raise ValueError(
                f"Prompt ID mismatch: requested '{prompt_id}', "
                f"but XML declares '{prompt['id']}'"
            )

        return prompt
