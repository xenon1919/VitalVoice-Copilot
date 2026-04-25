from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Personal Health Voice Copilot"
    env: str = "dev"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    rag_top_k: int = 4
    memory_top_k: int = 3

    docs_dir: str = "data/docs"
    rag_index_dir: str = "storage/faiss"
    memory_index_dir: str = "storage/memory_faiss"
    memory_db_path: str = "data/memory/memory_records.json"

    whisper_model_size: str = "base"
    tts_engine: str = "gtts"
    tts_language: str = "en"
    tts_tld: str = "co.uk"
    tts_slow: bool = False
    output_audio_path: str = "storage/response.mp3"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def base_dir(self) -> Path:
        """Get the base project directory"""
        return Path(__file__).parent.parent.parent

    def ensure_dirs(self) -> None:
        Path(self.docs_dir).mkdir(parents=True, exist_ok=True)
        Path(self.rag_index_dir).mkdir(parents=True, exist_ok=True)
        Path(self.memory_index_dir).mkdir(parents=True, exist_ok=True)
        Path(self.memory_db_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.output_audio_path).parent.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_dirs()
    return settings
