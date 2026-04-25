from __future__ import annotations

from app.rag.index_manager import RAGIndexManager


def main() -> None:
    manager = RAGIndexManager()
    manager.build_or_load_index()
    print("RAG index ready.")


if __name__ == "__main__":
    main()
