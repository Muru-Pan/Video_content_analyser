from __future__ import annotations

from pathlib import Path

from yt_dlp import YoutubeDL

from core.utils import ensure_ffmpeg_installed, ensure_js_runtime, safe_video_id


def download_youtube_audio(url: str, output_dir: Path) -> tuple[Path, str]:
    ffmpeg_binary, _ = ensure_ffmpeg_installed()
    runtime_name, runtime_binary = ensure_js_runtime()
    output_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg_location = str(Path(ffmpeg_binary).parent)

    info_opts = {
        "quiet": True,
        "skip_download": True,
        "ffmpeg_location": ffmpeg_location,
        "js_runtimes": {runtime_name: {"path": runtime_binary}},
    }
    try:
        with YoutubeDL(info_opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as exc:
        raise RuntimeError(f"Unable to read YouTube video details: {exc}") from exc

    video_id = safe_video_id(info.get("id") or info.get("title") or "youtube-video")
    output_template = str(output_dir / f"{video_id}.%(ext)s")
    download_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "quiet": True,
        "noplaylist": True,
        "ffmpeg_location": ffmpeg_location,
        "js_runtimes": {runtime_name: {"path": runtime_binary}},
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    try:
        with YoutubeDL(download_opts) as ydl:
            ydl.download([url])
    except Exception as exc:
        raise RuntimeError(f"Unable to download audio from the YouTube URL: {exc}") from exc

    audio_path = output_dir / f"{video_id}.mp3"
    if not audio_path.exists():
        raise RuntimeError("Audio download completed but the .mp3 output file was not found.")

    return audio_path, video_id
