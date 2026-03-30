from __future__ import annotations

import json
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )


def build_or_load_vectorstore(chunks: list[dict], index_root: Path, video_id: str, force: bool = False) -> FAISS:
    index_path = index_root / video_id
    if index_path.exists() and not force and (index_path / "index.faiss").exists() and (index_path / "index.pkl").exists():
        return FAISS.load_local(str(index_path), get_embeddings(), allow_dangerous_deserialization=True)

    index_path.mkdir(parents=True, exist_ok=True)
    documents = [
        Document(
            page_content=chunk["text"],
            metadata={
                "chunk_index": chunk["chunk_index"],
                "timestamp": chunk["timestamp"],
                "start_seconds": chunk["start_seconds"],
            },
        )
        for chunk in chunks
    ]
    vectorstore = FAISS.from_documents(documents, get_embeddings())
    vectorstore.save_local(str(index_path))
    (index_path / "chunks.json").write_text(json.dumps(chunks, indent=2, ensure_ascii=True), encoding="utf-8")
    return vectorstore


def load_vectorstore(index_root: Path, video_id: str) -> FAISS:
    index_path = index_root / video_id
    if not index_path.exists() or not (index_path / "index.faiss").exists() or not (index_path / "index.pkl").exists():
        raise FileNotFoundError("No index found for this video. Process it first.")
    return FAISS.load_local(str(index_path), get_embeddings(), allow_dangerous_deserialization=True)
