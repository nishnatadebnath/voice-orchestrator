
from enum import Enum
from pydantic import BaseModel, Field


class BotName(str, Enum):
    SALES = "sales"
    PERSONAL_LOAN = "personal_loan"


class RoutingDecision(BaseModel):
    target_bot: BotName
    reason: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
