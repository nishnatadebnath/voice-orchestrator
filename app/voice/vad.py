
from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass
class VADConfig:
    energy_threshold: float = 500.0
    silence_threshold: float = 800.0
    silence_duration: float = 0.8
    min_speech_duration: float = 0.25


class EnergyVAD:
    def __init__(
        self,
        sample_rate: int = 16000,
        config: Optional[VADConfig] = None,
    ) -> None:
        self.sample_rate = sample_rate
        self.config = config or VADConfig()

        self.speech_active = False
        self.speech_samples = 0
        self.silence_samples = 0

    def process(self, audio_chunk: np.ndarray) -> str:
        """Return 'speech_started', 'speech', 'speech_ended', or 'silence'."""
        samples = audio_chunk.astype(np.float32)

        rms = (
            float(np.sqrt(np.mean(samples ** 2)))
            if samples.size
            else 0.0
        )

        # Use a different threshold depending on whether
        # speech is already in progress.
        threshold = (
            self.config.silence_threshold
            if self.speech_active
            else self.config.energy_threshold
        )

        if rms >= threshold:
            self.silence_samples = 0
            self.speech_samples += samples.size

            if not self.speech_active:
                self.speech_active = True
                return "speech_started"

            return "speech"

        # No speech has started yet.
        if not self.speech_active:
            return "silence"

        # Speech is active, but the audio is now quiet.
        self.silence_samples += samples.size

        required_silence_samples = int(
            self.config.silence_duration * self.sample_rate
        )

        if self.silence_samples >= required_silence_samples:
            speech_duration = (
                self.speech_samples / self.sample_rate
            )

            # Reset state before returning the event.
            self.speech_active = False
            self.speech_samples = 0
            self.silence_samples = 0

            if speech_duration >= self.config.min_speech_duration:
                return "speech_ended"

            return "silence"

        return "silence"
