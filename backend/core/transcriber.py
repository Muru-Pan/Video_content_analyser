from __future__ import annotations

import json
from pathlib import Path

import whisper

from core.utils import save_json


class TranscriptionError(RuntimeError):
    pass


def transcribe_audio(
    audio_path: Path,
    output_dir: Path,
    model_name: str,
    video_id: str,
    force: bool = False,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    transcript_path = output_dir / f"{video_id}.json"

    if transcript_path.exists() and not force:
        return json.loads(transcript_path.read_text(encoding="utf-8"))

    try:
        model = whisper.load_model(model_name)
        result = model.transcribe(str(audio_path), verbose=False)
    except RuntimeError as exc:
        if "out of memory" in str(exc).lower() and model_name not in {"tiny", "base"}:
            raise TranscriptionError("Transcription failed. Try the tiny or base model.") from exc
        raise TranscriptionError("Transcription failed. Try the tiny or base model.") from exc
    except Exception as exc:
        raise TranscriptionError("Transcription failed. Try the tiny or base model.") from exc

    payload = {
        "text": (result.get("text") or "").strip(),
        "segments": [
            {
                "start": float(segment.get("start", 0.0)),
                "end": float(segment.get("end", 0.0)),
                "text": (segment.get("text") or "").strip(),
            }
            for segment in result.get("segments", [])
        ],
    }
    save_json(transcript_path, payload)
    return payload
