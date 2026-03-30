from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Iterable

ANSI_PATTERN = re.compile(r"\x1b\[[0-9;]*m")
WINDOWS_FFMPEG_CANDIDATES = [
    r"C:\\ffmpeg\\bin",
    r"C:\\Program Files\\ffmpeg\\bin",
    r"C:\\Program Files (x86)\\ffmpeg\\bin",
]


def ensure_directories(base_dir: Path) -> None:
    for relative in ["audio", "transcripts", "indexes", "temp"]:
        (base_dir / relative).mkdir(parents=True, exist_ok=True)


def data_dir() -> Path:
    base = Path(os.getenv("DATA_DIR", Path(__file__).resolve().parent.parent / "data"))
    ensure_directories(base)
    return base


def safe_video_id(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip())
    return cleaned.strip("-") or "video"


def strip_ansi(text: str) -> str:
    return ANSI_PATTERN.sub("", text)


def save_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def format_timestamp(seconds: float | int | None) -> str:
    total_seconds = int(seconds or 0)
    minutes, secs = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def transcript_to_lines(segments: Iterable[dict]) -> str:
    lines: list[str] = []
    for segment in segments:
        timestamp = format_timestamp(segment.get("start", 0.0))
        text = (segment.get("text") or "").strip()
        if text:
            lines.append(f"[{timestamp}] {text}")
    return "\n".join(lines)


def _normalize_path(value: str) -> Path:
    return Path(value.strip().strip('"').strip("'"))


def _looks_like_placeholder(value: str) -> bool:
    normalized = value.lower().replace("/", "\\")
    return "path\\to\\ffmpeg" in normalized or normalized.endswith("to\\ffmpeg\\bin")


def _resolve_ffmpeg_from_location(location: str) -> tuple[str, str] | None:
    if not location or _looks_like_placeholder(location):
        return None

    raw_path = _normalize_path(location)
    candidate_dirs: list[Path] = []

    if raw_path.is_file():
        name = raw_path.name.lower()
        if name in {"ffmpeg.exe", "ffmpeg"}:
            sibling = raw_path.with_name("ffprobe.exe" if raw_path.suffix.lower() == ".exe" else "ffprobe")
            if sibling.exists():
                return str(raw_path), str(sibling)
        return None

    candidate_dirs.append(raw_path)
    candidate_dirs.append(raw_path / "bin")

    for directory in candidate_dirs:
        ffmpeg_path = next((directory / n for n in ["ffmpeg.exe", "ffmpeg"] if (directory / n).exists()), None)
        ffprobe_path = next((directory / n for n in ["ffprobe.exe", "ffprobe"] if (directory / n).exists()), None)
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
        raise RuntimeError("ffmpeg is not installed. See setup instructions.")
    if env_value:
        raise RuntimeError("ffmpeg is not installed. See setup instructions.")
    raise RuntimeError("ffmpeg is not installed. See setup instructions.")


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
    raise RuntimeError("Unable to download audio. Check the URL and try again.")


def media_to_audio(source_path: Path, out_dir: Path, video_id: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / f"{video_id}.mp3"
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
        raise RuntimeError(strip_ansi(completed.stderr.strip()) or "Unable to process uploaded media.")
    return output_path


def cleanup_temp_file(path: Path | None) -> None:
    if path and path.exists():
        path.unlink(missing_ok=True)
