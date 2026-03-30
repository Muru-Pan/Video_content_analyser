from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from core.chunker import chunk_transcript
from core.downloader import download_youtube_audio
from core.embedder import build_or_load_vectorstore
from core.qa_chain import answer_question
from core.runtime import ensure_ollama_running
from core.summarizer import summarize_transcript
from core.transcriber import transcribe_audio
from core.utils import (
    ensure_directories,
    ensure_ffmpeg_installed,
    ensure_js_runtime,
    media_to_audio,
    safe_video_id,
)


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TEMP_DIR = DATA_DIR / "temp"
ensure_directories(DATA_DIR)

app = FastAPI(title="Video Content Analyzer API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _resolve_input(youtube_url: str | None, uploaded_file: UploadFile | None) -> tuple[Path, str]:
    if youtube_url and youtube_url.strip():
        ensure_ffmpeg_installed()
        ensure_js_runtime()
        return download_youtube_audio(youtube_url.strip(), DATA_DIR / "audio")

    if uploaded_file and uploaded_file.filename:
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        temp_source = TEMP_DIR / uploaded_file.filename
        with temp_source.open("wb") as file_handle:
            shutil.copyfileobj(uploaded_file.file, file_handle)

        video_id = safe_video_id(Path(uploaded_file.filename).stem)
        audio_path = media_to_audio(temp_source, DATA_DIR / "audio", video_id)
        return audio_path, video_id

    raise ValueError("Provide a YouTube URL or upload a media file.")


def _process_video(
    youtube_url: str | None,
    uploaded_file: UploadFile | None,
    whisper_model: str,
    force_reprocess: bool,
) -> dict[str, Any]:
    audio_path, video_id = _resolve_input(youtube_url, uploaded_file)
    transcript = transcribe_audio(
        audio_path=audio_path,
        output_dir=DATA_DIR / "transcripts",
        model_name=whisper_model,
        video_id=video_id,
        force=force_reprocess,
    )
    chunks = chunk_transcript(transcript["text"], transcript["segments"])
    build_or_load_vectorstore(
        chunks=chunks,
        index_root=DATA_DIR / "indexes",
        video_id=video_id,
        force=force_reprocess,
    )
    ensure_ollama_running()
    summary = summarize_transcript(transcript["text"])

    status = f"Ready. Processed video id: {video_id}"
    if not force_reprocess:
        status += " (cached transcript/index reused when available)."

    return {
        "video_id": video_id,
        "audio_path": str(audio_path),
        "transcript": transcript["text"],
        "segments": transcript["segments"],
        "summary": summary["summary"],
        "title": summary["title"],
        "category": summary["category"],
        "status": status,
    }


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/process")
async def process_video_endpoint(
    youtube_url: str | None = Form(default=None),
    whisper_model: str = Form(default="base"),
    force_reprocess: bool = Form(default=False),
    file: UploadFile | None = File(default=None),
) -> dict[str, Any]:
    try:
        return _process_video(youtube_url, file, whisper_model, force_reprocess)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        if file:
            await file.close()


@app.post("/api/ask")
def ask_question_endpoint(payload: dict[str, str]) -> dict[str, Any]:
    video_id = (payload.get("video_id") or "").strip()
    question = (payload.get("question") or "").strip()

    if not video_id:
        raise HTTPException(status_code=400, detail="Process a video first before asking questions.")
    if not question:
        raise HTTPException(status_code=400, detail="Enter a question to query the transcript.")

    try:
        ensure_ollama_running()
        result = answer_question(
            question=question,
            index_root=DATA_DIR / "indexes",
            video_id=video_id,
        )
        return result
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app:app", host="127.0.0.1", port=port, reload=False)
