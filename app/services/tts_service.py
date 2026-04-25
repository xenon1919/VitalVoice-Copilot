from __future__ import annotations

from pathlib import Path

from gtts import gTTS

from app.core.config import get_settings


class TTSService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def synthesize(self, text: str, output_path: str | None = None) -> str:
        out = Path(output_path or self.settings.output_audio_path)
        out.parent.mkdir(parents=True, exist_ok=True)

        if self.settings.tts_engine.lower() == "coqui":
            from TTS.api import TTS

            tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False)
            tts.tts_to_file(text=text, file_path=str(out))
            return str(out)

        tts = gTTS(
            text=text,
            lang=self.settings.tts_language,
            tld=self.settings.tts_tld,
            slow=self.settings.tts_slow,
        )
        tts.save(str(out))
        return str(out)
