from __future__ import annotations

from pathlib import Path

from faster_whisper import WhisperModel

from app.core.config import get_settings


class WhisperSTTService:
    def __init__(self) -> None:
        settings = get_settings()
        self.model = WhisperModel(settings.whisper_model_size, device="cpu", compute_type="int8")

    def transcribe(self, audio_path: str) -> str:
        file_path = Path(audio_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        segments, _ = self.model.transcribe(str(file_path))
        text = " ".join(segment.text.strip() for segment in segments if segment.text)
        return text.strip()
