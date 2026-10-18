
"""Interactive terminal UI for the voice bot orchestrator."""

import logging
import uuid

from dotenv import load_dotenv
from rich import box
from rich.align import Align
from rich.console import Console
from rich.logging import RichHandler
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

load_dotenv()

from app.llm.gemini_client import GeminiClient
from app.memory import SessionStore
from app.orchestrator import Orchestrator
from app.prompt_store.file_store import FilePromptStore
from app.prompt_store.service import PromptService

console = Console()


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=console,
                rich_tracebacks=True,
                show_path=False,
            )
        ],
        force=True,
    )

    # Keep third-party request logs from overwhelming the chat UI.
    logging.getLogger("google_genai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def new_session_id() -> str:
    return f"cli-{uuid.uuid4().hex[:8]}"


def show_header() -> None:
    console.clear()

    title = Text()
    title.append("VOICE", style="bold cyan")
    title.append(" BOT", style="bold white")
    title.append("  /  ", style="dim")
    title.append("ORCHESTRATOR", style="bold magenta")

    subtitle = Text(
        "Multi-bot AI assistant  •  Interactive developer console",
        style="dim",
        justify="center",
    )

    content = Table.grid(padding=(0, 1))
    content.add_column(justify="center")
    content.add_row(title)
    content.add_row(subtitle)

    console.print(
        Panel(
            Align.center(content),
            border_style="bright_blue",
            box=box.DOUBLE,
            padding=(1, 2),
        )
    )
    console.print()


def show_help() -> None:
    table = Table(
        title="Available commands",
        box=box.ROUNDED,
        border_style="bright_blue",
        show_lines=True,
    )
    table.add_column("Command", style="bold cyan", no_wrap=True)
    table.add_column("Description", style="white")

    commands = [
        ("/help", "Show available commands"),
        ("/history", "View this session's conversation"),
        ("/status", "Show session and active bot"),
        ("/new", "Start a fresh conversation"),
        ("/clear", "Clear the terminal screen"),
        ("/exit", "Exit the CLI"),
    ]

    for command, description in commands:
        table.add_row(command, description)

    console.print(table)


def show_status(
    session_id: str,
    session_store: SessionStore,
) -> None:
    history = session_store.get_history(session_id)
    active_bot = session_store.get_active_bot(session_id)

    table = Table(box=box.SIMPLE, show_header=False)
    table.add_column("Property", style="dim")
    table.add_column("Value", style="bold")

    table.add_row("Session", session_id)
    table.add_row("Active bot", active_bot)
    table.add_row(
        "Messages",
        str(len(history)),
    )

    console.print(
        Panel(
            table,
            title="[bold cyan]Session status[/bold cyan]",
            border_style="cyan",
        )
    )


def show_history(
    session_id: str,
    session_store: SessionStore,
) -> None:
    history = session_store.get_history(session_id)

    if not history:
        console.print("[dim]No messages in this session yet.[/dim]")
        return

    console.print(
        Panel(
            f"[bold]{len(history)}[/bold] messages in this session",
            title="[bold cyan]Conversation history[/bold cyan]",
            border_style="cyan",
        )
    )

    for item in history:
        role = item.get("role", "unknown")
        message = item.get("content", "")

        if role == "user":
            console.print(
                Panel(
                    str(message),
                    title="[bold cyan]You[/bold cyan]",
                    border_style="cyan",
                    box=box.ROUNDED,
                )
            )
        else:
            console.print(
                Panel(
                    Markdown(str(message)),
                    title="[bold green]Assistant[/bold green]",
                    border_style="green",
                    box=box.ROUNDED,
                )
            )


def main() -> None:
    configure_logging()

    session_store = SessionStore()
    prompt_store = FilePromptStore()
    prompt_service = PromptService(prompt_store)
    llm_client = GeminiClient()

    orchestrator = Orchestrator(
        session_store=session_store,
        prompt_service=prompt_service,
        llm_client=llm_client,
    )

    session_id = new_session_id()

    show_header()
    console.print(
        "[green]●[/green] Connected to your local orchestrator",
    )
    console.print(
        "[dim]Type a message to chat, /help for commands, or /exit to quit.[/dim]\n"
    )

    while True:
        try:
            message = Prompt.ask(
                "[bold bright_cyan]You[/bold bright_cyan]"
            ).strip()

            if not message:
                continue

            command = message.lower()

            if command in {"/exit", "exit", "quit", "/quit"}:
                console.print(
                    Panel(
                        "[bold green]Session ended. See you next time![/bold green]",
                        box=box.ROUNDED,
                        border_style="green",
                    )
                )
                break

            if command == "/help":
                show_help()
                continue

            if command == "/status":
                show_status(session_id, session_store)
                continue

            if command == "/history":
                show_history(session_id, session_store)
                continue

            if command == "/clear":
                show_header()
                console.print(
                    "[dim]Screen cleared. Your conversation is unchanged.[/dim]\n"
                )
                continue

            if command == "/new":
                session_id = new_session_id()
                console.print(
                    Panel(
                        f"Started a fresh conversation.\n"
                        f"[dim]Session: {session_id}[/dim]",
                        title="[bold green]New session[/bold green]",
                        border_style="green",
                    )
                )
                continue

            with console.status(
                "[bold yellow]Thinking...[/bold yellow]",
                spinner="dots",
                spinner_style="cyan",
            ):
                response = orchestrator.handle_message(
                    session_id,
                    message,
                )

            active_bot = session_store.get_active_bot(session_id)

            console.print(
                Panel(
                    Markdown(response),
                    title=(
                        f"[bold green]Assistant[/bold green] "
                        f"[dim]· {active_bot}[/dim]"
                    ),
                    border_style="green",
                    box=box.ROUNDED,
                    padding=(1, 2),
                )
            )
            console.print()

        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Goodbye![/dim]")
            break
        except Exception:
            logging.getLogger(__name__).exception(
                "Failed to process the CLI interaction"
            )
            console.print(
                Panel(
                    "Something went wrong while processing that message. "
                    "Check the terminal logs for details.",
                    title="[bold red]Request failed[/bold red]",
                    border_style="red",
                )
            )


if __name__ == "__main__":
    main()
