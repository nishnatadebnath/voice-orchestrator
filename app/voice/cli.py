
"""Rich voice interface for the existing orchestrator."""

import logging
import uuid

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

from app.llm.gemini_client import GeminiClient
from app.memory import SessionStore
from app.orchestrator import Orchestrator
from app.prompt_store.file_store import FilePromptStore
from app.prompt_store.service import PromptService
from app.voice.recorder import record_until_enter
from app.voice.transcriber import LocalTranscriber

load_dotenv()

console = Console()


def main() -> None:
    logging.basicConfig(level=logging.ERROR)

    # Initialize the existing orchestrator dependencies.
    session_store = SessionStore()
    prompt_store = FilePromptStore()
    prompt_service = PromptService(prompt_store)
    llm_client = GeminiClient()

    orchestrator = Orchestrator(
        session_store=session_store,
        prompt_service=prompt_service,
        llm_client=llm_client,
    )

    session_id = f"voice-{uuid.uuid4().hex[:8]}"

    # Use the smaller Whisper model for faster transcription.
    transcriber = LocalTranscriber(model_size="base")

    console.clear()
    console.print(
        Panel(
            "[bold cyan]VOICE ASSISTANT[/bold cyan]\n"
            "[dim]Local speech recognition · Multi-bot orchestration[/dim]\n\n"
            "[green]●[/green] Ready\n"
            "[dim]Press Enter to start recording.[/dim]\n"
            "[dim]Press Enter again to stop recording.[/dim]\n"
            "[dim]Press Ctrl+C to exit.[/dim]",
            title="[bold]Voice Orchestrator[/bold]",
            border_style="cyan",
            padding=(1, 3),
        )
    )

    turn = 0

    while True:
        try:
            console.print()
            input("[cyan]Press Enter to speak...[/cyan]")

            # Record until the user presses Enter again.
            audio = record_until_enter(sample_rate=16000)

            if audio.size == 0:
                console.print(
                    "[yellow]No audio recorded. Please try again.[/yellow]"
                )
                continue

            # Run Whisper once on the complete recording.
            with console.status(
                "[cyan]Transcribing audio...[/cyan]",
                spinner="dots",
            ):
                result = transcriber.transcribe_audio(
                    audio,
                    sample_rate=16000,
                )

            message = result.text.strip()

            if not message:
                console.print(
                    "[yellow]No speech recognized. Please try again.[/yellow]"
                )
                continue

            turn += 1
            language = result.language or "unknown"

            console.print()
            console.print(
                Panel(
                    message,
                    title=f"[bold green]You · {language}[/bold green]",
                    border_style="green",
                    padding=(1, 2),
                )
            )

            # Send the transcription through the existing orchestrator.
            with console.status(
                "[magenta]Thinking...[/magenta]",
                spinner="dots",
            ):
                response = orchestrator.handle_message(
                    session_id,
                    message,
                )

            active_bot = session_store.get_active_bot(session_id)
            bot_label = str(active_bot) if active_bot else "Assistant"

            console.print(
                Panel(
                    response,
                    title=f"[bold magenta]{bot_label}[/bold magenta]",
                    border_style="magenta",
                    padding=(1, 2),
                )
            )

            console.print(
                Text(f"Turn {turn} complete", style="dim"),
                justify="right",
            )
            console.print(Rule(style="dim"))

        except (KeyboardInterrupt, EOFError):
            console.print()
            console.print(
                Panel(
                    "[bold]Voice session ended.[/bold]\n"
                    "[dim]Thanks for using the voice assistant.[/dim]",
                    border_style="cyan",
                )
            )
            break

        except Exception as exc:
            logging.getLogger(__name__).exception(
                "Failed to process voice interaction"
            )
            console.print(
                f"[bold red]Something went wrong:[/bold red] {exc}"
            )
            console.print(
                "[dim]Check the terminal logs for details.[/dim]"
            )

        
if __name__ == "__main__":
    main()
