from __future__ import annotations

import os


def ensure_llm_ready() -> None:
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing. Please set it in your environment file or export it.")


def llm_status() -> str:
    try:
        ensure_llm_ready()
        return "reachable"
    except RuntimeError:
        return "unreachable"
