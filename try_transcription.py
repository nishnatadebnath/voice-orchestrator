
from app.voice.recorder import record_audio
from app.voice.transcriber import LocalTranscriber


audio_path = record_audio(duration=5)

transcriber = LocalTranscriber()
result = transcriber.transcribe_file(audio_path)

print("\nRecognized text:", result.text)
print("Detected language:", result.language)
print("Language confidence:", result.language_probability)
