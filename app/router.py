
"""Model-based intent routing for specialist bots."""

import json
import re

from app.llm.base import LLMClient
from app.models import RoutingDecision


class IntentRouter:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def route(
        self,
        message: str,
        active_bot: str,
        history: list[dict[str, str]],
    ) -> RoutingDecision:

        routing_prompt = """
You are the intent router for a multi-bot assistant.

Available bots:
- sales: product discovery and general sales enquiries.
- personal_loan: personal loans, eligibility, applications,
  interest rates, and repayments.
- gold_loan: gold-backed loans, eligibility, valuation,
  loan amounts, interest rates, and repayments.

Your responsibilities:

1. Select exactly one destination bot based on the user's latest message
   and the conversation context.
2. If the intent is ambiguous or unrelated, prefer the active bot.
3. Never answer the user. Only produce the routing decision.
4. Assess how relevant each previous message is to the selected bot.
5. Score relevance from 0.0 to 1.0:
   - 0.0: irrelevant to the destination bot.
   - 0.5: potentially useful context.
   - 1.0: directly useful context.
6. Include only messages with a relevance score greater than 0.0
   in relevant_context.
7. Use the original zero-based message indices provided in the history.
8. Consider both user and assistant messages, but prioritize useful
   user-provided facts and context.
9. Relevance is specific to the selected destination bot.
   Do not include messages merely because they are recent.
10. Do not infer that a message is relevant solely because it mentions
    a product. Consider whether it helps answer the current request.

Return the structured RoutingDecision.
"""
        history_with_indices = [
            {"index": index, **item}
            for index, item in enumerate(history)
        ]

        raw_decision = self.llm_client.generate(
            system_prompt=routing_prompt,
            message=(
                f"Active bot: {active_bot}\n"
                f"Conversation history:\n"
                f"{json.dumps(history_with_indices, ensure_ascii=False)}\n\n"
                f"Latest user message: {message}\n\n"
                "Choose the destination bot and score the relevance of "
                "the previous messages for that bot."
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
            return RoutingDecision(**decision_data)

        except (json.JSONDecodeError, KeyError, ValueError, TypeError) as exc:
            raise ValueError(
                f"Gemini returned an invalid routing decision: {raw_decision}"
            ) from exc
