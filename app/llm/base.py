
from abc import ABC, abstractmethod
from typing import Optional, Type

from pydantic import BaseModel


class LLMClient(ABC):
    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        message: str,
        history: list[dict[str, str]],
        response_schema: Optional[Type[BaseModel]] = None,
    ) -> str:
        pass
