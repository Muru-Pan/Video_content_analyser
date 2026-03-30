from __future__ import annotations

from typing import Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

from core.utils import seconds_to_timestamp


def chunk_transcript(
    transcript_text: str,
    segments: list[dict[str, Any]],
    chunk_size: int = 2000,
    chunk_overlap: int = 200,
) -> list[dict[str, Any]]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    texts = splitter.split_text(transcript_text)
    chunked_segments: list[dict[str, Any]] = []
    search_from = 0

    for idx, chunk_text in enumerate(texts):
        start_pos = transcript_text.find(chunk_text, search_from)
        if start_pos == -1:
            start_pos = search_from
        search_from = start_pos + max(1, len(chunk_text) - chunk_overlap)

        timestamp = _estimate_chunk_timestamp(transcript_text, segments, start_pos)
        chunked_segments.append(
            {
                "text": chunk_text,
                "chunk_index": idx,
                "timestamp": seconds_to_timestamp(timestamp),
                "start_seconds": float(timestamp),
            }
        )

    return chunked_segments


def _estimate_chunk_timestamp(
    transcript_text: str,
    segments: list[dict[str, Any]],
    character_position: int,
) -> float:
    if not segments:
        return 0.0

    running_length = 0
    for segment in segments:
        segment_text = (segment.get("text") or "").strip()
        running_length += len(segment_text) + 1
        if running_length >= character_position:
            return float(segment.get("start", 0.0))

    return float(segments[-1].get("start", 0.0))
