from __future__ import annotations

from pathlib import Path

from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

from core.embedder import load_vectorstore


BASE_DIR = Path(__file__).resolve().parent.parent
QA_PROMPT_PATH = BASE_DIR / "prompts" / "qa_prompt.txt"


def answer_question(question: str, index_root: Path, video_id: str, k: int = 4) -> dict:
    vectorstore = load_vectorstore(index_root=index_root, video_id=video_id)
    docs = vectorstore.similarity_search(question, k=k)
    if not docs:
        return {
            "answer": "I could not find that in this video.",
            "sources": [],
        }

    context = "\n\n".join(
        [
            f"[Timestamp: {doc.metadata.get('timestamp', '00:00')}] {doc.page_content}"
            for doc in docs
        ]
    )

    prompt_template = PromptTemplate.from_template(QA_PROMPT_PATH.read_text(encoding="utf-8"))
    llm = OllamaLLM(model="mistral")
    chain = prompt_template | llm
    answer = chain.invoke({"context": context, "question": question}).strip()

    return {
        "answer": answer,
        "sources": [
            {
                "text": doc.page_content,
                "timestamp": doc.metadata.get("timestamp", "00:00"),
                "chunk_index": doc.metadata.get("chunk_index", -1),
            }
            for doc in docs
        ],
    }
