from __future__ import annotations

import os
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

from core.embedder import load_vectorstore

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "qa_prompt.txt"


def ask_question(question: str, index_root: Path, video_id: str) -> dict:
    vectorstore = load_vectorstore(index_root, video_id)
    docs = vectorstore.similarity_search(question, k=4)
    if not docs:
        return {"answer": "I could not find that in this video.", "sources": []}

    context = "\n\n".join(
        f"[Timestamp: {doc.metadata.get('timestamp', '00:00')}] {doc.page_content}" for doc in docs
    )
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
    prompt = PromptTemplate.from_template(PROMPT_PATH.read_text(encoding="utf-8"))
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question}).strip()
    return {
        "answer": answer,
        "sources": [
            {
                "text": doc.page_content,
                "timestamp": doc.metadata.get("timestamp", "00:00"),
                "start_seconds": float(doc.metadata.get("start_seconds", 0.0)),
                "chunk_index": int(doc.metadata.get("chunk_index", -1)),
            }
            for doc in docs
        ],
    }
