# Voice Bot Orchestrator

A Python conversational assistant that routes messages to sales, personal-loan,
or gold-loan specialists. Both an interactive terminal CLI and a FastAPI
service use the same orchestration flow and XML-backed specialist prompts.

## Features

- Routes each message to a sales, personal-loan, or gold-loan specialist.
- Uses session IDs to retain in-memory conversation history, active specialist,
  and selected context.
- Uses versioned XML files for specialist instructions.
- Calls Gemini through a replaceable LLM client interface.
- Offers independent text CLI and HTTP API interfaces.

## Quick start

Use Python 3.9 or later. From the repository root, create and activate a
virtual environment, then install the runtime packages and the test dependency:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install fastapi "uvicorn[standard]" "pydantic>=2" python-dotenv google-genai rich
python -m pip install -r requirements.txt
```

`requirements.txt` currently installs pytest only; the runtime packages above
are imported by the application but are not yet listed in that file.

Create a `.env` file in the repository root and add your Gemini API key:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
```

Run either interface independently from the repository root:

```bash
python -m app.cli
```

Or, in a separate terminal:

```bash
uvicorn app.main:app --reload
```

Both interfaces write logs to their terminal. They run as separate processes
and do not share session state. See [CLI and API usage](docs/usage.md) for
commands, examples, setup details, and logging tips.

## Documentation

- [Architecture](docs/architecture.md) — components, request flow, and design
  rationale.
- [Usage](docs/usage.md) — installation, environment setup, CLI, and API.
- [Logging](docs/logging.md) — terminal logs, routing diagnostics, and
  troubleshooting.
- [Design decisions](docs/decisions.md) — implemented choices, trade-offs,
  and work not currently implemented.

## Repository layout

```text
app/
  bots/                 Specialist bot implementations
  llm/                  LLM interface and Gemini client
  prompt_store/         XML prompt loading, parsing, and formatting
  prompts/              Versioned specialist XML prompts
  voice/                Voice-related components
  cli.py                Interactive text CLI
  main.py               FastAPI application
  orchestrator.py       Shared routing and response flow
  router.py             Intent and context routing
  memory.py             In-process session state
docs/
  architecture.md
  decisions.md
  logging.md
  usage.md
tests/
```
