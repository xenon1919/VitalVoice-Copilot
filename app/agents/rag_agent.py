from __future__ import annotations

from app.core.config import get_settings
from app.rag.index_manager import RAGIndexManager


class RAGAgent:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.manager = RAGIndexManager()
        self.index = self.manager.build_or_load_index()

    def retrieve(self, query: str) -> list[str]:
        retriever = self.index.as_retriever(similarity_top_k=self.settings.rag_top_k)
        nodes = retriever.retrieve(query)
        return [n.node.get_content().strip() for n in nodes]
