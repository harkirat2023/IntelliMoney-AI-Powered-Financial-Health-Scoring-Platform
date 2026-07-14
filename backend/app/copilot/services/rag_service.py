import hashlib
import logging
from typing import Any

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import get_settings

logger = logging.getLogger(__name__)


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
            self._vector_store = await FAISS.afrom_documents(docs, self._embeddings)
        else:
            await self._vector_store.aadd_documents(docs)
        return len(docs)

    async def search(self, query: str, k: int = 3) -> list[dict]:
        if self._vector_store is None:
            return []
        try:
            docs = await self._vector_store.asimilarity_search(query, k=k)
            return [
                {"content": d.page_content, "metadata": d.metadata, "score": 0.0}
                for d in docs
            ]
        except Exception as e:
            logger.error(f"RAG search failed: {e}")
            return []

    async def clear(self):
        self._vector_store = None

    @property
    def document_count(self) -> int:
        if self._vector_store is None:
            return 0
        return self._vector_store.index.ntotal if hasattr(self._vector_store, "index") else 0
