from app.memory import SessionStore
from app.orchestrator import Orchestrator
from app.prompt_store.file_store import FilePromptStore
from app.prompt_store.service import PromptService


class GoldLoanRoutingLLM:
    def __init__(self):
        self.prompts = []

    def generate(
        self,
        system_prompt,
        message,
        history,
        response_schema=None,
    ):
        self.prompts.append(system_prompt)
        if response_schema is not None:
            return (
                '{"target_bot":"gold_loan",'
                '"reason":"Gold-backed borrowing question",'
                '"confidence":1.0}'
            )
        return "Gold-loan response"


def test_gold_loan_bot_is_routed_and_uses_its_prompt():
    llm_client = GoldLoanRoutingLLM()
    session_store = SessionStore()
    orchestrator = Orchestrator(
        session_store=session_store,
        prompt_service=PromptService(FilePromptStore()),
        llm_client=llm_client,
    )

    response = orchestrator.handle_message(
        "gold-loan-test",
        "How does a loan against gold work?",
    )

    assert response == "Gold-loan response"
    assert session_store.get_active_bot("gold-loan-test") == "gold_loan"
    assert '"gold_loan"' in llm_client.prompts[0]
    assert "gold valuation" in llm_client.prompts[1]
