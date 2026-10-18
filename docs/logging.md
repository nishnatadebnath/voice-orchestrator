# Logging

The CLI and API write logs to their own terminal; the application does not
configure a log file.

## CLI logs

Run the CLI and leave its terminal visible:

```bash
python -m app.cli
```

The CLI configures INFO-level logging with Rich output. Google GenAI and
`httpx` library loggers are raised to WARNING to reduce noise. If a CLI
interaction fails, the CLI logs the exception traceback and shows a message
asking you to check the terminal.

## FastAPI logs

Run the API in a terminal:

```bash
uvicorn app.main:app --reload
```

The application configures INFO-level logging with timestamps, level, logger
name, and message. Uvicorn's startup and access logs also appear in this
terminal. Application logs use the root logging configuration.

To keep a local copy while watching the output, redirect either command's
combined output to `tee`, for example:

```bash
uvicorn app.main:app --reload 2>&1 | tee api.log
```

## Useful application log entries

The orchestrator logs at INFO level:

- **Routing decision:** session ID, active bot, target bot, confidence, and
  reason.
- **Bot handoff:** source and destination, but only when the selected bot
  changes.
- **Prompt selection:** prompt ID, XML version, and bot.

These are internal logs. The `/chat` JSON response includes `active_bot` but
does not include routing confidence or reason.

## Troubleshooting

- **`GEMINI_API_KEY is missing`:** Set `GEMINI_API_KEY` in a `.env` file at the
  repository root or in the process environment. Restart the process.
- **Import error at startup:** `requirements.txt` currently lists pytest but
  not the runtime libraries. Install the packages shown in
  [Usage: Install](usage.md#install) in the active virtual environment.
- **Prompt not found or prompt ID mismatch:** Run the command from the
  repository root and check that the matching `app/prompts/<id>.xml` exists
  and declares the same ID.
- **Invalid API request:** Check that `session_id` and `message` are
  non-whitespace strings no longer than 100 and 5000 characters respectively.
  FastAPI returns 422 for request validation errors.
- **API health succeeds but chat fails:** `/health` checks that the process is
  responding, not Gemini availability. Check the server terminal for the
  model/API error and verify the key and network access.
- **Unexpected routing:** Inspect the target, confidence, and reason in the
  `Routing decision` log. For a handoff, inspect the adjacent `Bot handoff`
  entry. These values are model-generated decisions, not deterministic rules.
