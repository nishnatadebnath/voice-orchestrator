
"""Near-live transcription from the microphone."""

import queue
import time
from typing import Optional

import numpy as np
import sounddevice as sd
from rich.console import Console

from app.voice.transcriber import LocalTranscriber
from app.voice.vad import EnergyVAD


def listen_for_utterance(
    transcriber: LocalTranscriber,
    console: Console,
    sample_rate: int = 16000,
) -> Optional[str]:
    audio_queue = queue.Queue()
    detector = EnergyVAD(sample_rate=sample_rate)
    utterance_chunks = []
    speech_started = False
    last_partial_time = 0.0
    partial_interval = 1.5

    def on_audio(indata, frames, time_info, status):
        if status:
            console.log(f"[yellow]Audio status: {status}[/yellow]")
        audio_queue.put(indata[:, 0].copy())

    console.print("[cyan]Listening... speak whenever you're ready.[/cyan]")

    try:
        with sd.InputStream(
            samplerate=sample_rate,
            channels=1,
            dtype="int16",
            blocksize=512,
            callback=on_audio,
        ):
            while True:
                try:
                    chunk = audio_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                event = detector.process(chunk)
                if event in ("speech_started", "speech_ended"):
                    console.print(f"\n[bold yellow]VAD event: {event}[/bold yellow]")

                if event == "speech_started":
                    speech_started = True
                    utterance_chunks = [chunk]
                    last_partial_time = time.monotonic()
                    console.print("[green]Speech detected[/green]")

                elif speech_started:
                    utterance_chunks.append(chunk)

                if speech_started:
                    now = time.monotonic()

                    if now - last_partial_time >= partial_interval:
                        last_partial_time = now

                        # Use a recent window for partial updates.
                        recent_audio = np.concatenate(
                            utterance_chunks[-250:]
                        )

                        result = transcriber.transcribe_audio(
                            recent_audio,
                            sample_rate=sample_rate,
                        )

                        if result.text.strip():
                            console.print(
                                f"[dim cyan]Live: {result.text.strip()}[/dim cyan]"
                            )

                if event == "speech_ended":
                    final_audio = np.concatenate(utterance_chunks)
                    result = transcriber.transcribe_audio(
                        final_audio,
                        sample_rate=sample_rate,
                    )
                    return result.text.strip()

    except KeyboardInterrupt:
        console.print("\n[yellow]Listening stopped.[/yellow]")
        return None
