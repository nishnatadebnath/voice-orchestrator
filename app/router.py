
"""Model-based intent routing for specialist bots."""

import json
import re

from app.llm.base import LLMClient
from app.models import BotName, RoutingDecision


class IntentRouter:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def route(self, message: str, active_bot: str) -> RoutingDecision:
        routing_prompt = """
You are an intent classifier for a multi-bot assistant.

Available bots:
- sales: questions about products, product discovery, and general sales enquiries.
- personal_loan: questions about personal loans, borrowing money, loan eligibility,
  loan application, interest rates, and repayment.

Choose exactly one bot based on the user's intent.
If the message is ambiguous or unrelated, prefer the active bot.
Never answer the user. Only classify the intent.

Return a JSON object with:
- target_bot: "sales" or "personal_loan"
- reason: a short explanation
- confidence: a number between 0.0 and 1.0 indicating confidence
"""

        raw_decision = self.llm_client.generate(
            system_prompt=routing_prompt,
            message=(
                f"Current active bot: {active_bot}\n"
                f"User message: {message}\n"
                'Return JSON with "target_bot", "reason", and "confidence".'
            ),
            history=[],
            response_schema=RoutingDecision,
        )

        try:
            cleaned_response = re.sub(
                r"^```(?:json)?\s*|\s*```$",
                "",
                raw_decision.strip(),
                flags=re.IGNORECASE,
            )

            decision_data = json.loads(cleaned_response)

            return RoutingDecision(
                target_bot=BotName(decision_data["target_bot"]),
                reason=decision_data["reason"],
                confidence=decision_data["confidence"],
            )

        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as exc:
            raise ValueError(
                f"Gemini returned an invalid routing decision: {raw_decision}"
            ) from exc
