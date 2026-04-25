from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import get_settings


class MemoryAgent:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.model = SentenceTransformer(self.settings.embedding_model)
        self.db_path = Path(self.settings.memory_db_path)
        self.index_path = Path(self.settings.memory_index_dir) / "memory.index"
        self.records = self._load_records()
        self.index = self._load_or_create_index()
        if self.records and self.index.ntotal == 0:
            vectors = np.array([r["embedding"] for r in self.records], dtype=np.float32)
            self.index.add(vectors)

    def _load_records(self) -> list[dict[str, Any]]:
        if self.db_path.exists():
            with self.db_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def _save_records(self) -> None:
        with self.db_path.open("w", encoding="utf-8") as f:
            json.dump(self.records, f, ensure_ascii=True, indent=2)

    def _load_or_create_index(self) -> faiss.IndexFlatIP:
        if self.index_path.exists():
            return faiss.read_index(str(self.index_path))
        return faiss.IndexFlatIP(384)

    def _save_index(self) -> None:
        faiss.write_index(self.index, str(self.index_path))

    def add_interaction(self, user_id: str, query: str, response: str) -> None:
        text = f"User: {query}\nAssistant: {response}"
        embedding = self.model.encode(text, normalize_embeddings=True).astype(np.float32)
        self.index.add(np.array([embedding], dtype=np.float32))
        self.records.append(
            {
                "user_id": user_id,
                "query": query,
                "response": response,
                "text": text,
                "embedding": embedding.tolist(),
            }
        )
        self._save_records()
        self._save_index()

    def get_recent_for_user(self, user_id: str, limit: int = 5) -> list[str]:
        items = [r["text"] for r in self.records if r["user_id"] == user_id]
        return items[-limit:]

    def recall(self, query: str, top_k: int | None = None) -> list[str]:
        if self.index.ntotal == 0:
            return []
        k = top_k or self.settings.memory_top_k
        qvec = self.model.encode(query, normalize_embeddings=True).astype(np.float32)
        _, idx = self.index.search(np.array([qvec], dtype=np.float32), min(k, self.index.ntotal))
        hits = []
        for row in idx[0]:
            if row >= 0:
                hits.append(self.records[row]["text"])
        return hits
