
"""Push-to-talk microphone recording."""

from typing import List

import numpy as np
import sounddevice as sd


def record_until_enter(sample_rate: int = 16000) -> np.ndarray:
    chunks: List[np.ndarray] = []

    def on_audio(indata, frames, time_info, status):
        if status:
            print("Audio warning:", status)

        chunks.append(indata[:, 0].copy())

    input("Recording... press Enter to stop.\n")

    with sd.InputStream(
        samplerate=sample_rate,
        channels=1,
        dtype="int16",
        blocksize=1024,
        callback=on_audio,
    ):
        input()

    if not chunks:
        return np.array([], dtype=np.int16)

    return np.concatenate(chunks)
