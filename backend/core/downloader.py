from __future__ import annotations

from pathlib import Path

from yt_dlp import YoutubeDL

from core.utils import ensure_ffmpeg_installed, ensure_js_runtime, safe_video_id, strip_ansi


class DownloadError(RuntimeError):
    pass


def download_youtube_audio(youtube_url: str, output_dir: Path, force: bool = False) -> tuple[Path, str]:
    ffmpeg_binary, _ = ensure_ffmpeg_installed()
    runtime_name, runtime_binary = ensure_js_runtime()
    output_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg_location = str(Path(ffmpeg_binary).parent)

    info_opts = {
        "quiet": True,
        "skip_download": True,
        "ffmpeg_location": ffmpeg_location,
        "js_runtimes": {runtime_name: {"path": runtime_binary}},
        "noplaylist": True,
    }
    try:
        with YoutubeDL(info_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
    except Exception as exc:
        raise DownloadError("Unable to download audio. Check the URL and try again.") from exc

    video_id = safe_video_id(info.get("id") or info.get("title") or "youtube-video")
    audio_path = output_dir / f"{video_id}.mp3"
    if audio_path.exists() and not force:
        return audio_path, video_id

    download_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(output_dir / f"{video_id}.%(ext)s"),
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
            ydl.download([youtube_url])
    except Exception as exc:
        detail = strip_ansi(str(exc))
        if "private" in detail.lower() or "restricted" in detail.lower() or "unavailable" in detail.lower():
            raise DownloadError("This video is unavailable or restricted.") from exc
        raise DownloadError("Unable to download audio. Check the URL and try again.") from exc

    if not audio_path.exists():
        raise DownloadError("Unable to download audio. Check the URL and try again.")
    return audio_path, video_id
