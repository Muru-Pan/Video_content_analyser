from __future__ import annotations

import os
import shutil
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.chunker import chunk_transcript
from core.downloader import DownloadError, download_youtube_audio
from core.embedder import build_or_load_vectorstore
from core.qa_chain import ask_question
from core.runtime import ensure_llm_ready, llm_status
from core.summarizer import summarize_transcript
from core.transcriber import TranscriptionError, transcribe_audio
from core.utils import cleanup_temp_file, data_dir, ensure_directories, media_to_audio, safe_video_id, transcript_to_lines

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("DATA_DIR", data_dir()))
TEMP_DIR = DATA_DIR / "temp"
ensure_directories(DATA_DIR)

app = FastAPI(title="Video Content Analyzer API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    video_id: str
    question: str


def process_pipeline(
    youtube_url: str | None,
    uploaded_file: UploadFile | None,
    whisper_model: str,
    force_reprocess: bool,
) -> dict:
    temp_path: Path | None = None
    try:
        if youtube_url:
            audio_path, video_id = download_youtube_audio(youtube_url, DATA_DIR / "audio", force=force_reprocess)
            source_url = youtube_url
        elif uploaded_file and uploaded_file.filename:
            TEMP_DIR.mkdir(parents=True, exist_ok=True)
            temp_path = TEMP_DIR / uploaded_file.filename
            with temp_path.open("wb") as handle:
                shutil.copyfileobj(uploaded_file.file, handle)
            video_id = safe_video_id(Path(uploaded_file.filename).stem)
            audio_path = media_to_audio(temp_path, DATA_DIR / "audio", video_id)
            source_url = ""
        else:
            raise HTTPException(status_code=422, detail="Provide a YouTube URL or upload a media file.")

        transcript = transcribe_audio(audio_path, DATA_DIR / "transcripts", whisper_model, video_id, force_reprocess)
        chunks = chunk_transcript(transcript["text"], transcript["segments"])
        build_or_load_vectorstore(chunks, DATA_DIR / "indexes", video_id, force_reprocess)
        ensure_llm_ready()
        summary = summarize_transcript(transcript["text"])
        transcript_lines = transcript_to_lines(transcript["segments"])
        return {
            "video_id": video_id,
            "audio_path": str(audio_path),
            "transcript": transcript_lines,
            "segments": transcript["segments"],
            "summary": summary["summary"],
            "title": summary["title"],
            "category": summary["category"],
            "status": "Done",
            "source_url": source_url,
        }
    finally:
        cleanup_temp_file(temp_path)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "llm": llm_status()}


@app.post("/api/process")
async def process_video_endpoint(
    youtube_url: str = Form(default=""),
    file: UploadFile | None = File(default=None),
    whisper_model: str = Form(default="base"),
    force_reprocess: str = Form(default="false"),
):
    force = force_reprocess.lower() == "true"
    if not youtube_url.strip() and file is None:
        raise HTTPException(status_code=422, detail="Provide a YouTube URL or upload a media file.")
    try:
        payload = process_pipeline(youtube_url.strip() or None, file, whisper_model, force)
        return payload
    except HTTPException:
        raise
    except DownloadError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except TranscriptionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        detail = str(exc)
        if "No index found" in detail:
            raise HTTPException(status_code=404, detail=detail) from exc
        raise HTTPException(status_code=400, detail=detail) from exc
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Unexpected server error.") from exc
    finally:
        if file:
            await file.close()


@app.post("/api/ask")
def ask_question_endpoint(body: AskRequest):
    if not body.question.strip():
        raise HTTPException(status_code=400, detail="Enter a question before submitting.")
    try:
        ensure_llm_ready()
        return ask_question(body.question.strip(), DATA_DIR / "indexes", body.video_id.strip())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="No index found for this video. Process it first.") from exc
    except RuntimeError as exc:
        detail = str(exc)
        if "No index found" in detail:
            raise HTTPException(status_code=404, detail="No index found for this video. Process it first.") from exc
        raise HTTPException(status_code=400, detail=detail) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unexpected server error.") from exc
