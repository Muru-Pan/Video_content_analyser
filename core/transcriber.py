from __future__ import annotations

import json
from pathlib import Path

import whisper

from core.utils import save_json


def transcribe_audio(
    audio_path: Path,
    output_dir: Path,
    model_name: str = "base",
    video_id: str | None = None,
    force: bool = False,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    video_id = video_id or audio_path.stem
    transcript_path = output_dir / f"{video_id}.txt"
    segments_path = output_dir / f"{video_id}.segments.json"

    if not force and transcript_path.exists() and segments_path.exists():
        cached_payload = json.loads(segments_path.read_text(encoding="utf-8"))
        return {
            "text": cached_payload.get("text", transcript_path.read_text(encoding="utf-8")).strip(),
            "segments": cached_payload.get("segments", []),
        }

    model = whisper.load_model(model_name)

    try:
        result = model.transcribe(str(audio_path), verbose=False)
    except RuntimeError as exc:
        if "out of memory" not in str(exc).lower() or model_name == "tiny":
            raise
        fallback_model = whisper.load_model("tiny")
        result = fallback_model.transcribe(str(audio_path), verbose=False)

    transcript_text = result.get("text", "").strip()
    segments = [
        {
            "start": float(segment.get("start", 0.0)),
            "end": float(segment.get("end", 0.0)),
            "text": segment.get("text", "").strip(),
        }
        for segment in result.get("segments", [])
    ]
    transcript_payload = {"text": transcript_text, "segments": segments}

    transcript_path.write_text(transcript_text, encoding="utf-8")
    save_json(segments_path, transcript_payload)
    return transcript_payload
