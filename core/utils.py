from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Iterable


WINDOWS_FFMPEG_CANDIDATES = [
    r"C:\ffmpeg\bin",
    r"C:\Program Files\ffmpeg\bin",
    r"C:\Program Files (x86)\ffmpeg\bin",
]


def ensure_directories(base_dir: Path) -> None:
    for relative in ["audio", "transcripts", "indexes", "temp"]:
        (base_dir / relative).mkdir(parents=True, exist_ok=True)


def safe_video_id(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip())
    return cleaned.strip("-") or "video"


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def seconds_to_timestamp(value: float | int | None) -> str:
    total_seconds = int(value or 0)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def format_sources(sources: Iterable[dict]) -> str:
    lines = []
    for idx, source in enumerate(sources, start=1):
        timestamp = source.get("timestamp", "00:00")
        chunk_id = source.get("chunk_index", idx - 1)
        text = source.get("text", "").strip()
        lines.append(f"### Source {idx}")
        lines.append(f"- Chunk: {chunk_id}")
        lines.append(f"- Timestamp: {timestamp}")
        lines.append("")
        lines.append(text or "_No source text available._")
        lines.append("")
    return "\n".join(lines) if lines else "_No source passages available._"


def _normalize_path(value: str) -> Path:
    return Path(value.strip().strip('"').strip("'"))


def _looks_like_placeholder(value: str) -> bool:
    normalized = value.lower().replace("/", "\\")
    return "path\\to\\ffmpeg" in normalized or normalized.endswith("to\\ffmpeg\\bin")


def _resolve_ffmpeg_from_location(location: str) -> tuple[str, str] | None:
    if not location:
        return None
    if _looks_like_placeholder(location):
        return None

    raw_path = _normalize_path(location)
    candidates: list[Path] = []

    if raw_path.is_file():
        name = raw_path.name.lower()
        if name in {"ffmpeg.exe", "ffmpeg"}:
            sibling = raw_path.with_name("ffprobe.exe" if raw_path.suffix.lower() == ".exe" else "ffprobe")
            if sibling.exists():
                return str(raw_path), str(sibling)
        if name in {"ffprobe.exe", "ffprobe"}:
            sibling = raw_path.with_name("ffmpeg.exe" if raw_path.suffix.lower() == ".exe" else "ffmpeg")
            if sibling.exists():
                return str(sibling), str(raw_path)
        return None

    candidates.append(raw_path)
    candidates.append(raw_path / "bin")

    for candidate_dir in candidates:
        ffmpeg_names = ["ffmpeg.exe", "ffmpeg"]
        ffprobe_names = ["ffprobe.exe", "ffprobe"]
        ffmpeg_path = next((candidate_dir / name for name in ffmpeg_names if (candidate_dir / name).exists()), None)
        ffprobe_path = next((candidate_dir / name for name in ffprobe_names if (candidate_dir / name).exists()), None)
        if ffmpeg_path and ffprobe_path:
            return str(ffmpeg_path), str(ffprobe_path)

    return None


def get_ffmpeg_binaries() -> tuple[str, str] | None:
    env_value = os.getenv("FFMPEG_LOCATION", "").strip()
    if env_value:
        resolved = _resolve_ffmpeg_from_location(env_value)
        if resolved:
            return resolved

    ffmpeg_on_path = shutil.which("ffmpeg")
    ffprobe_on_path = shutil.which("ffprobe")
    if ffmpeg_on_path and ffprobe_on_path:
        return ffmpeg_on_path, ffprobe_on_path

    for candidate in WINDOWS_FFMPEG_CANDIDATES:
        resolved = _resolve_ffmpeg_from_location(candidate)
        if resolved:
            return resolved

    return None


def ensure_ffmpeg_installed() -> tuple[str, str]:
    binaries = get_ffmpeg_binaries()
    env_value = os.getenv("FFMPEG_LOCATION", "").strip()
    if binaries:
        return binaries

    if env_value and _looks_like_placeholder(env_value):
        raise RuntimeError(
            "FFMPEG_LOCATION is still set to the placeholder example path. Replace it with your real ffmpeg folder "
            "or remove the variable and add ffmpeg to PATH."
        )

    if env_value:
        raise RuntimeError(
            f"FFMPEG_LOCATION is set to '{env_value}', but ffmpeg and ffprobe were not found there. "
            "Use the folder that contains both binaries, a parent folder that contains `bin`, or the direct path to ffmpeg.exe."
        )

    raise RuntimeError(
        "ffmpeg is required but was not found. Install ffmpeg and either add it to PATH or set FFMPEG_LOCATION "
        "to the folder containing ffmpeg.exe and ffprobe.exe."
    )


def get_js_runtime() -> tuple[str, str] | None:
    env_runtime = os.getenv("YTDLP_JS_RUNTIME", "").strip()
    if env_runtime:
        runtime_name, _, runtime_path = env_runtime.partition(":")
        runtime_name = runtime_name.strip()
        runtime_path = runtime_path.strip().strip('"').strip("'")
        if runtime_path and Path(runtime_path).exists():
            return runtime_name, runtime_path
        runtime_binary = shutil.which(runtime_name)
        if runtime_binary:
            return runtime_name, runtime_binary

    for runtime_name in ["node", "deno", "bun"]:
        runtime_binary = shutil.which(runtime_name)
        if runtime_binary:
            return runtime_name, runtime_binary
    return None


def ensure_js_runtime() -> tuple[str, str]:
    runtime = get_js_runtime()
    if runtime:
        return runtime
    raise RuntimeError(
        "A JavaScript runtime is required for reliable YouTube extraction with yt-dlp. "
        "Install Node.js and verify `node -v`, or install Deno/Bun, then try again."
    )


def media_to_audio(source_path: Path, audio_dir: Path, video_id: str) -> Path:
    audio_dir.mkdir(parents=True, exist_ok=True)
    output_path = audio_dir / f"{video_id}.mp3"

    if source_path.suffix.lower() == ".mp3":
        shutil.copy2(source_path, output_path)
        return output_path

    ffmpeg_binary, _ = ensure_ffmpeg_installed()
    command = [
        ffmpeg_binary,
        "-y",
        "-i",
        str(source_path),
        "-vn",
        "-acodec",
        "libmp3lame",
        str(output_path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"ffmpeg conversion failed: {completed.stderr.strip()}")
    return output_path
