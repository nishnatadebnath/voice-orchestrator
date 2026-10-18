
from enum import Enum
from pydantic import BaseModel, Field


class BotName(str, Enum):
    SALES = "sales"
    PERSONAL_LOAN = "personal_loan"
    GOLD_LOAN = "gold_loan"


class RelevantMessage(BaseModel):
    message_index: int = Field(ge=0)
    relevance_score: float = Field(ge=0.0, le=1.0)
    reason: str = Field(min_length=1)


class RoutingDecision(BaseModel):
    target_bot: BotName
    reason: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    relevant_context: list[RelevantMessage] = Field(default_factory=list)
