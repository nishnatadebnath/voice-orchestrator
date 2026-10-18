
from dataclasses import dataclass
from typing import Optional

import numpy as np
from faster_whisper import WhisperModel


@dataclass
class TranscriptionResult:
    text: str
    language: Optional[str]
    language_probability: Optional[float]


class LocalTranscriber:
    def __init__(self, model_size: str = "small") -> None:
        self.model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",
        )

    def transcribe_file(self, audio_path: str) -> TranscriptionResult:
        segments, info = self.model.transcribe(
            audio_path,
            beam_size=5,
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
            if segment.text.strip()
        )

        return TranscriptionResult(
            text=text,
            language=info.language,
            language_probability=info.language_probability,
        )

    def transcribe_audio(
        self,
        audio: np.ndarray,
        sample_rate: int = 16000,
    ) -> TranscriptionResult:
        """Transcribe an in-memory mono audio buffer."""
        if audio.size == 0:
            return TranscriptionResult(
                text="",
                language=None,
                language_probability=None,
            )

        # Whisper expects normalized floating-point audio.
        audio_float = audio.astype(np.float32) / 32768.0

        segments, info = self.model.transcribe(
            audio_float,
            beam_size=1,
            language=None,
            vad_filter=False,
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
            if segment.text.strip()
        )

        return TranscriptionResult(
            text=text,
            language=info.language,
            language_probability=info.language_probability,
        )
