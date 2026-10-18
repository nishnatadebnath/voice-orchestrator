
"""Real Gemini implementation of the shared LLM interface."""

import os

from google import genai
from google.genai import types

from app.llm.base import LLMClient
from typing import Optional, Type

from pydantic import BaseModel


class GeminiClient(LLMClient):
    """Generate conversational responses using the Gemini API."""

    def __init__(self, model: str = "gemini-3.5-flash-lite"):
        # Read the API key from the environment, never from source code.
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing. Check your .env configuration."
            )

        self.client = genai.Client(api_key=api_key)
        self.model = model

    def generate(
        self,
        system_prompt: str,
        message: str,
        history: list[dict[str, str]],
        response_schema: Optional[Type[BaseModel]] = None,
    ) -> str:
        """Send the prompt, previous messages, and current message to Gemini."""

        contents = []

        # Gemini uses "model" for assistant responses in conversation history.
        for item in history:
            role = item["role"]

            if role == "assistant":
                role = "model"

            if role not in ("user", "model"):
                continue

            contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=item["content"])],
                )
            )

        # Add the current message after the previous conversation history.
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=message)],
            )
        )

        
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
        )

        if response_schema is not None:
            config.response_mime_type = "application/json"
            config.response_schema = response_schema

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config=config,
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text
