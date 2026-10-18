# Design decisions

This page separates behavior present in the repository from work that is not
implemented. No separate roadmap or planned work is currently documented in
the source.

## Implemented decisions

| Decision | Implementation | Rationale and trade-off |
| --- | --- | --- |
| Shared orchestrator | CLI and API both call `Orchestrator.handle_message`. | Keeps validation, routing, prompt selection, and response flow consistent. Each interface constructs its own instance; they do not share process state. |
| Separate CLI and API interfaces | `python -m app.cli` runs an interactive text interface; `uvicorn app.main:app --reload` serves FastAPI. | They can be run and observed independently. Sessions are isolated by process. |
| Centralized XML prompts | Specialist prompts live in `app/prompts/` and are loaded and formatted through `app/prompt_store/`. XML IDs and versions are validated and prompt ID/version are logged. | Prompt wording is separate from bot classes. Disk loading keeps the implementation simple; it is not a database-backed or distributed prompt service. |
| Session handling | `SessionStore` keys in-memory active bot, complete history, and selected context by session ID. Selected context is merged and capped at 20 messages. | Simple session isolation without a storage service. State is lost at process exit and is not shared across workers or interfaces. |
| LLM abstraction | The `LLMClient` interface is injected into the router and specialist bots; `GeminiClient` is the current implementation. | Separates orchestration from provider-specific calls. The interface permits another implementation, but no alternate adapter is included. |
| Guardrails | Input validation rejects blank values, session IDs longer than 100 characters, and messages longer than 5000 characters. Pydantic enforces the same API limits. Specialist prompt text also directs responses not to invent certain product details or guarantees. | Basic request bounds and prompt guidance are implemented. There is no separate output moderation system or comprehensive policy engine. |
| Cloud Gemini model | `GeminiClient` uses Gemini (`gemini-3.5-flash-lite` by default) and reads `GEMINI_API_KEY` from the environment. | Uses a hosted model without local inference setup, but requires a key, network access, and an external API. |

## Not implemented (not a stated plan)

The following capabilities should not be assumed from the abstractions or
current behavior. They are not listed here as planned commitments:

- Durable session storage, cross-process session sharing, or database-backed
  history.
- Local/offline model inference or a second provider adapter.
- Authentication, authorization, or rate limiting for the API.
- API response fields for routing confidence and reason; these are currently
  available in terminal logs only.
- A separate output validation/moderation layer beyond the current input
  checks and prompt instructions.

## Local and cloud model trade-offs

The implemented client is cloud-based. It avoids local model installation and
serving, but chat and routing generation depend on Gemini credentials,
connectivity, and provider availability. A local model could reduce external
service dependency, but would require model/runtime setup and an adapter
implementing `LLMClient`; no such adapter or supported configuration exists
in this repository today.

## Runtime dependency note

`requirements.txt` currently contains pytest only. The runtime packages
imported by the CLI and API must be installed separately; see
[Usage: Install](usage.md#install). This documentation records the repository
as it exists and does not imply that these missing dependency declarations
have been added.
