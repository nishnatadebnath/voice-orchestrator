# Usage

Run commands from the repository root. The prompt store uses the relative
directory `app/prompts`.

## Install

The source uses Python 3.9+ syntax and Pydantic v2 APIs. Install the API
runtime dependencies from `requirements.txt`; install `rich` separately for
the interactive text CLI:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pip install rich
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

Set up the Gemini key in a root-level `.env` file:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
```

Both supported entry points load `.env`. Do not commit a real API key.

## Interactive CLI

Start the text chat from the repository root:

```bash
python -m app.cli
```

Type a message and press Enter. The CLI creates a session ID on startup and
displays the active bot with each response. Available slash commands:

| Command | Purpose |
| --- | --- |
| `/help` | Show available commands |
| `/history` | Show this session's conversation |
| `/status` | Show session ID, active bot, and message count |
| `/new` | Start a fresh session |
| `/clear` | Clear the screen without clearing conversation state |
| `/exit` | Exit the CLI |

`exit`, `quit`, and `/quit` also exit.

The CLI logs at INFO level to the terminal. Keep that terminal open to inspect
routing, handoff, and prompt logs. The CLI catches request exceptions, logs a
traceback, and displays a short failure message.

## FastAPI service

Start the API independently from the repository root:

```bash
uvicorn app.main:app --reload
```

By default, Uvicorn listens at `http://127.0.0.1:8000`. Keep this terminal
open to inspect application and Uvicorn logs. `--reload` restarts the
development server when source files change; in-memory sessions are reset
when the application process restarts.

### Health check

```bash
curl http://127.0.0.1:8000/health
```

Response:

```json
{"status":"ok"}
```

This endpoint confirms the API process responds; it does not check Gemini
credentials or model availability.

### Chat request and response

Send a JSON object with a non-whitespace `session_id` (1–100 characters) and
`message` (1–5000 characters):

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"demo-session","message":"How does a gold loan work?"}'
```

Response shape:

```json
{
  "session_id": "demo-session",
  "response": "A response generated for your question.",
  "active_bot": "gold_loan"
}
```

The response text and selected bot depend on the model's routing and
generation. The API returns the active bot, not the router's confidence or
reason. Invalid request data is rejected by FastAPI/Pydantic with a 422
validation response.

### Interactive API documentation

With the service running, open Swagger UI at
[`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs). The OpenAPI schema
is available at `/openapi.json`; FastAPI's ReDoc UI is at
[`http://127.0.0.1:8000/redoc`](http://127.0.0.1:8000/redoc).

## Running and inspecting interfaces separately

Run `python -m app.cli` in one terminal or `uvicorn app.main:app --reload` in
another; neither is a wrapper around the other. Each has its own in-memory
session store, so using the same session ID in the two processes does not
share conversation history. See [Logging](logging.md) for the log fields and
troubleshooting guidance.
