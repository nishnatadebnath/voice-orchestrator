
class SessionStore:
    """Stores bot state and conversation history for each session."""

    def __init__(self):
        # Each session has an active bot and a list of conversation messages.
        self.sessions: dict[str, dict] = {}

    def _get_or_create_session(self, session_id: str) -> dict:
        """Return an existing session or initialize a new one."""

        # Keep each caller's state isolated using their unique session ID.
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "active_bot": "sales",
                "history": [],
            }

        return self.sessions[session_id]

    def get_active_bot(self, session_id: str) -> str:
        """Return the bot currently assigned to this session."""
        session = self._get_or_create_session(session_id)
        return session["active_bot"]

    def set_active_bot(self, session_id: str, bot_name: str) -> None:
        """Assign a bot to this conversation."""
        session = self._get_or_create_session(session_id)
        session["active_bot"] = bot_name

    def add_message(
        self, session_id: str, role: str, content: str
    ) -> None:
        """Append a message to the conversation history."""

        session = self._get_or_create_session(session_id)

        # Role identifies who produced the message: user or assistant.
        session["history"].append({
            "role": role,
            "content": content,
        })

    def get_history(self, session_id: str) -> list[dict]:
        """Return the conversation history for a session."""
        session = self._get_or_create_session(session_id)
        return session["history"]
