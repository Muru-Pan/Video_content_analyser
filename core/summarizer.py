from __future__ import annotations

import re
from pathlib import Path

from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM


BASE_DIR = Path(__file__).resolve().parent.parent
SUMMARY_PROMPT_PATH = BASE_DIR / "prompts" / "summary_prompt.txt"


def summarize_transcript(transcript: str) -> dict[str, str]:
    trimmed_transcript = transcript[:12000]
    prompt_template = PromptTemplate.from_template(
        SUMMARY_PROMPT_PATH.read_text(encoding="utf-8")
    )
    llm = OllamaLLM(model="mistral")
    chain = prompt_template | llm
    response = chain.invoke({"transcript": trimmed_transcript}).strip()
    parsed = _parse_summary_response(response)
    if not parsed["summary"]:
        parsed["summary"] = "Summary generation did not return a structured result."
    if not parsed["title"]:
        parsed["title"] = "Untitled Video Summary"
    if not parsed["category"]:
        parsed["category"] = "Other"
    return parsed


def _parse_summary_response(response: str) -> dict[str, str]:
    patterns = {
        "summary": r"SUMMARY:\s*(.*?)(?=\nTITLE:|\nCATEGORY:|\Z)",
        "title": r"TITLE:\s*(.*?)(?=\nSUMMARY:|\nCATEGORY:|\Z)",
        "category": r"CATEGORY:\s*(.*?)(?=\nSUMMARY:|\nTITLE:|\Z)",
    }
    parsed: dict[str, str] = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, response, flags=re.IGNORECASE | re.DOTALL)
        parsed[key] = match.group(1).strip() if match else ""
    return parsed
