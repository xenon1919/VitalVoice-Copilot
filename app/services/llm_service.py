from __future__ import annotations

import json
from typing import Any, Iterable

import google.generativeai as genai

from app.core.config import get_settings


class GeminiService:
    def __init__(self) -> None:
        settings = get_settings()
        self.model_name = settings.gemini_model
        self.enabled = bool(settings.gemini_api_key)
        if self.enabled:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None

    def generate_text(self, prompt: str) -> str:
        if not self.enabled or self.model is None:
            return (
                "I can share general health guidance based on your symptoms. "
                "Please monitor symptoms, hydrate, rest, and seek medical care if they worsen."
            )
        response = self.model.generate_content(prompt)
        return response.text or "I could not generate a response."

    def generate_json(self, prompt: str, fallback: dict[str, Any]) -> dict[str, Any]:
        raw = self.generate_text(prompt)
        try:
            start = raw.find("{")
            end = raw.rfind("}")
            if start == -1 or end == -1:
                return fallback
            return json.loads(raw[start : end + 1])
        except json.JSONDecodeError:
            return fallback

    def generate_text_stream(self, prompt: str) -> Iterable[str]:
        if not self.enabled or self.model is None:
            yield (
                "I can share general health guidance based on your symptoms. "
                "Please monitor symptoms, hydrate, rest, and seek medical care if they worsen."
            )
            return

        response_stream = self.model.generate_content(prompt, stream=True)
        for chunk in response_stream:
            text = getattr(chunk, "text", None)
            if text:
                yield text
