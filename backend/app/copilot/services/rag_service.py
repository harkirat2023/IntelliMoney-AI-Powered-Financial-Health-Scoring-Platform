import asyncio
import hashlib
import logging
import os
import pickle
from pathlib import Path
from typing import Any

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import get_settings

logger = logging.getLogger(__name__)

RAG_INDEX_DIR = Path(__file__).resolve().parent / ".." / "data" / "rag_index"
RAG_INDEX_PATH = RAG_INDEX_DIR / "faiss_index.pkl"


class RAGService:
    def __init__(self):
        cfg = get_settings()
        self._embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " ", ""],
        )
        self._vector_store: FAISS | None = None
        self._load_index()

    def _index_path(self) -> Path:
        RAG_INDEX_DIR.mkdir(parents=True, exist_ok=True)
        return RAG_INDEX_PATH

    def _load_index(self) -> None:
        path = self._index_path()
        if path.exists():
            try:
                with open(path, "rb") as f:
                    self._vector_store = pickle.load(f)
                logger.info("Loaded FAISS index from %s", path)
            except Exception as e:
                logger.error("Failed to load FAISS index: %s", e)
                self._vector_store = None

    def _save_index(self) -> None:
        path = self._index_path()
        try:
            with open(path, "wb") as f:
                pickle.dump(self._vector_store, f)
            logger.info("Saved FAISS index to %s", path)
        except Exception as e:
            logger.error("Failed to save FAISS index: %s", e)

    async def index_document(self, content: str, metadata: dict[str, Any] | None = None) -> int:
        chunks = self._splitter.split_text(content)
        docs = [
            Document(page_content=chunk, metadata={
                **(metadata or {}),
                "chunk_id": hashlib.md5(chunk.encode()).hexdigest()[:8],
            })
            for chunk in chunks
        ]
        if not docs:
            return 0

        if self._vector_store is None:
            self._vector_store = await asyncio.to_thread(
                FAISS.from_documents, docs, self._embeddings
            )
        else:
            await asyncio.to_thread(self._vector_store.add_documents, docs)
        self._save_index()
        return len(docs)

    async def search(self, query: str, k: int = 3) -> list[dict]:
        if self._vector_store is None:
            return []
        try:
            docs = await asyncio.to_thread(
                self._vector_store.similarity_search, query, k=k
            )
            return [
                {"content": d.page_content, "metadata": d.metadata, "score": 0.0}
                for d in docs
            ]
        except Exception as e:
            logger.error(f"RAG search failed: {e}")
            return []

    async def clear(self):
        self._vector_store = None
        path = self._index_path()
        if path.exists():
            path.unlink()
            logger.info("Deleted FAISS index at %s", path)

    @property
    def document_count(self) -> int:
        if self._vector_store is None:
            return 0
        return self._vector_store.index.ntotal if hasattr(self._vector_store, "index") else 0
