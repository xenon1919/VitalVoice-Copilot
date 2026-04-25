from __future__ import annotations

from pathlib import Path

import faiss
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core import load_index_from_storage
from llama_index.core.readers import SimpleDirectoryReader
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore

from app.core.config import get_settings


class RAGIndexManager:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.embed_model = HuggingFaceEmbedding(model_name=self.settings.embedding_model)
        self.persist_dir = self.settings.rag_index_dir

    def build_or_load_index(self) -> VectorStoreIndex:
        persist = Path(self.persist_dir)
        if (persist / "docstore.json").exists():
            storage_context = StorageContext.from_defaults(
                vector_store=FaissVectorStore.from_persist_dir(self.persist_dir),
                persist_dir=self.persist_dir,
            )
            return load_index_from_storage(storage_context=storage_context, embed_model=self.embed_model)

        reader = SimpleDirectoryReader(self.settings.docs_dir, recursive=True)
        docs = reader.load_data()
        if not docs:
            docs = reader.load_data(required_exts=[".txt", ".md", ".pdf"])

        faiss_index = faiss.IndexFlatL2(384)
        vector_store = FaissVectorStore(faiss_index=faiss_index)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            docs,
            storage_context=storage_context,
            embed_model=self.embed_model,
        )
        index.storage_context.persist(persist_dir=self.persist_dir)
        return index
