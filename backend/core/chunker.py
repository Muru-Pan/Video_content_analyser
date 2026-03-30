from __future__ import annotations

from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.utils import format_timestamp


def chunk_transcript(transcript_text: str, segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    texts = splitter.split_text(transcript_text)
    chunks: list[dict[str, Any]] = []
    search_from = 0
    for idx, chunk_text in enumerate(texts):
        start_pos = transcript_text.find(chunk_text, search_from)
        if start_pos == -1:
            start_pos = search_from
        search_from = start_pos + max(1, len(chunk_text) - 200)
        start_seconds = estimate_start_seconds(segments, start_pos)
        chunks.append(
            {
                "text": chunk_text,
                "chunk_index": idx,
                "start": start_seconds,
                "start_seconds": start_seconds,
                "timestamp": format_timestamp(start_seconds),
            }
        )
    return chunks


def estimate_start_seconds(segments: list[dict[str, Any]], char_position: int) -> float:
    if not segments:
        return 0.0
    running = 0
    for segment in segments:
        running += len((segment.get("text") or "").strip()) + 1
        if running >= char_position:
            return float(segment.get("start", 0.0))
    return float(segments[-1].get("start", 0.0))
