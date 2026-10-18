
"""Coordinate routing, specialist responses, and conversation history."""

import logging

from app.bots.specialists import GoldLoanBot, PersonalLoanBot, SalesBot
from app.guardrails import validate_chat_input
from app.llm.base import LLMClient
from app.memory import SessionStore
from app.router import IntentRouter
from app.prompt_store.service import PromptService

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(
        self,
        session_store: SessionStore,
        prompt_service: PromptService,
        llm_client: LLMClient,
    ):
        self.bots = {
            "sales": SalesBot(llm_client),
            "personal_loan": PersonalLoanBot(llm_client),
            "gold_loan": GoldLoanBot(llm_client),
        }
        self.session_store = session_store
        self.router = IntentRouter(llm_client)
        self.prompt_service = prompt_service

    def handle_message(self, session_id: str, message: str) -> str:
        """Process a message and record the conversation exchange."""
        validate_chat_input(session_id, message)

        active_bot = self.session_store.get_active_bot(session_id)
        router_context = self.session_store.get_memory(session_id)

        decision = self.router.route(
            message,
            active_bot,
            router_context,
        )

        self.session_store.add_message(session_id, "user", message)
        target_bot = decision.target_bot.value

        logger.info(
            "Routing decision: session_id=%s active_bot=%s "
            "target_bot=%s confidence=%.2f reason=%s",
            session_id,
            active_bot,
            target_bot,
            decision.confidence,
            decision.reason,
        )

        # Log a handoff only when the selected specialist changes.
        if target_bot != active_bot:
            logger.info(
                "Bot handoff: session_id=%s from=%s to=%s",
                session_id,
                active_bot,
                target_bot,
            )

        # Validate the selected specialist.
        bot = self.bots.get(target_bot)
        if bot is None:
            raise ValueError(f"Unknown bot: {target_bot}")

        # Retrieve and format the selected specialist's prompt.
        prompt = self.prompt_service.get_prompt(target_bot)
        formatted_prompt = self.prompt_service.format_loaded_prompt(prompt)

        logger.info(
            "Using prompt: id=%s version=%s bot=%s",
            prompt["id"],
            prompt["version"],
            target_bot,
        )

        # Update the active specialist and generate the response.
        self.session_store.set_active_bot(session_id, target_bot)

        relevant_history = [
            router_context[item.message_index]
            for item in decision.relevant_context
            if 0 <= item.message_index < len(router_context)
            and item.relevance_score >= 0.5
        ]

        existing_memory = self.session_store.get_memory(session_id)

        merged_memory = self._merge_memory(
            existing_memory,
            relevant_history,
        )

        self.session_store.set_memory(session_id, merged_memory)

        response = bot.respond(
            message,
            formatted_prompt,
            self.session_store.get_memory(session_id),
        )

        # Record the assistant response.
        self.session_store.add_message(session_id, "assistant", response)

        return response

    def _merge_memory(
        self,
        existing_memory: list[dict],
        new_messages: list[dict],
        max_messages: int = 20,
    ) -> list[dict]:
        """Merge unique messages and retain the most recent entries."""

        merged = list(existing_memory)
        seen = {
            (item["role"], item["content"])
            for item in existing_memory
        }

        for item in new_messages:
            key = (item["role"], item["content"])

            if key not in seen:
                merged.append(item)
                seen.add(key)
        return merged[-max_messages:]
