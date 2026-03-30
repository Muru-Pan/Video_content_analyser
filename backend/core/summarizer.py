from __future__ import annotations

import re
from pathlib import Path

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPT_PATH = BASE_DIR / "prompts" / "summary_prompt.txt"
ALLOWED_CATEGORIES = {"Education", "Technology", "Finance", "Health", "Entertainment", "Other"}


def summarize_transcript(transcript_text: str) -> dict[str, str]:
    import os
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))
    prompt = PromptTemplate.from_template(PROMPT_PATH.read_text(encoding="utf-8"))
    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"transcript": transcript_text[:12000]}).strip()
    parsed = _parse(response)
    return {
        "summary": parsed.get("summary") or "Summary unavailable.",
        "title": parsed.get("title") or "Untitled Video",
        "category": parsed.get("category") if parsed.get("category") in ALLOWED_CATEGORIES else "Other",
    }





def _parse(response: str) -> dict[str, str]:
    patterns = {
        "summary": r"SUMMARY:\s*(.*?)(?=\nTITLE:|\nCATEGORY:|\Z)",
        "title": r"TITLE:\s*(.*?)(?=\nSUMMARY:|\nCATEGORY:|\Z)",
        "category": r"CATEGORY:\s*(.*?)(?=\nSUMMARY:|\nTITLE:|\Z)",
    }
    parsed: dict[str, str] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
        parsed[key] = match.group(1).strip() if match else ""
    return parsed
