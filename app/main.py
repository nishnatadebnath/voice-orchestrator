
from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator

from app.llm.gemini_client import GeminiClient
from app.memory import SessionStore
from app.orchestrator import Orchestrator
from app.prompt_store.file_store import FilePromptStore
from app.prompt_store.service import PromptService
from dotenv import load_dotenv
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    force=True,
)
load_dotenv()



# Create the API application.
app = FastAPI(title="Voice Bot Orchestrator")

# Share the session store and orchestrator across incoming requests.
# Each conversation remains separated by its session ID.
# Create the session store for conversation history and active-bot state.
session_store = SessionStore()

# Create the centralized prompt service backed by XML files.
prompt_store = FilePromptStore()
prompt_service = PromptService(prompt_store)

# Inject both dependencies into the orchestrator.
llm_client = GeminiClient()
orchestrator = Orchestrator(
    session_store=session_store,
    prompt_service=prompt_service,
    llm_client=llm_client,
)




class ChatRequest(BaseModel):
    """Validate and constrain incoming chat requests."""

    # Require a non-empty session ID with a reasonable maximum length.
    session_id: str = Field(min_length=1, max_length=100)

    # Limit message size to prevent unexpectedly large requests.
    message: str = Field(min_length=1, max_length=5000)

    @field_validator("session_id", "message")
    @classmethod
    def reject_whitespace_only(cls, value: str) -> str:
        """Reject values that contain only whitespace."""

        if not value.strip():
            raise ValueError("Value must not be empty or whitespace only")

        return value



class ChatResponse(BaseModel):
    """Define the structure returned to the API client."""

    session_id: str
    response: str
    active_bot: str


@app.get("/health")
def health_check():
    """Indicate that the API process is responding."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Pass a user's message to the orchestrator and return its response."""

    # The orchestrator owns routing; the API doesn't decide which bot to use.
    response = orchestrator.handle_message(
        request.session_id,
        request.message,
    )

    # Include the selected bot so clients can inspect the routing decision.
    active_bot = session_store.get_active_bot(request.session_id)

    return ChatResponse(
        session_id=request.session_id,
        response=response,
        active_bot=active_bot,
    )
