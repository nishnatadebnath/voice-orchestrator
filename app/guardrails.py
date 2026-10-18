"""Shared validation for messages entering the orchestrator."""

MAX_SESSION_ID_LENGTH = 100
MAX_MESSAGE_LENGTH = 5000


def validate_chat_input(session_id: str, message: str) -> None:
    """Reject invalid or oversized chat inputs before processing."""
    if not isinstance(session_id, str) or not session_id.strip():
        raise ValueError("Session ID must not be empty or whitespace only")
    if len(session_id) > MAX_SESSION_ID_LENGTH:
        raise ValueError("Session ID exceeds the maximum length")
    if not isinstance(message, str) or not message.strip():
        raise ValueError("Message must not be empty or whitespace only")
    if len(message) > MAX_MESSAGE_LENGTH:
        raise ValueError("Message exceeds the maximum length")
