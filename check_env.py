from __future__ import annotations

import importlib
import shutil
import sys
import urllib.error
import urllib.request

from core.utils import ensure_ffmpeg_installed, ensure_js_runtime


REQUIRED_PACKAGES = [
    "fastapi",
    "whisper",
    "yt_dlp",
    "langchain",
    "langchain_core",
    "langchain_community",
    "langchain_ollama",
    "langchain_text_splitters",
    "sentence_transformers",
    "faiss",
    "torch",
    "uvicorn",
    "multipart",
]


def check_python() -> bool:
    version = sys.version_info
    ok = version >= (3, 10)
    status = "OK" if ok else "FAIL"
    print(f"[{status}] Python {version.major}.{version.minor}.{version.micro}")
    return ok


def check_node() -> bool:
    node_binary = shutil.which("node")
    ok = node_binary is not None
    status = "OK" if ok else "FAIL"
    print(f"[{status}] Node.js{f': {node_binary}' if node_binary else ''}")
    return ok


def check_npm() -> bool:
    npm_binary = shutil.which("npm")
    ok = npm_binary is not None
    status = "OK" if ok else "FAIL"
    print(f"[{status}] npm{f': {npm_binary}' if npm_binary else ''}")
    return ok


def check_ffmpeg() -> bool:
    try:
        ffmpeg_binary, ffprobe_binary = ensure_ffmpeg_installed()
        print(f"[OK] ffmpeg: {ffmpeg_binary}")
        print(f"[OK] ffprobe: {ffprobe_binary}")
        return True
    except Exception as exc:
        print(f"[FAIL] ffmpeg/ffprobe: {exc}")
        return False


def check_js_runtime() -> bool:
    try:
        runtime_name, runtime_binary = ensure_js_runtime()
        print(f"[OK] JS runtime for yt-dlp: {runtime_name} ({runtime_binary})")
        return True
    except Exception as exc:
        print(f"[FAIL] JS runtime for yt-dlp: {exc}")
        return False


def check_packages() -> bool:
    ok = True
    for package in REQUIRED_PACKAGES:
        try:
            importlib.import_module(package)
            print(f"[OK] Python package: {package}")
        except Exception:
            ok = False
            print(f"[FAIL] Python package: {package}")
    return ok


def check_ollama() -> bool:
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=2) as response:
            ok = 200 <= response.status < 300
    except (urllib.error.URLError, TimeoutError):
        ok = False

    status = "OK" if ok else "FAIL"
    print(f"[{status}] Ollama server at http://127.0.0.1:11434")
    return ok


def main() -> int:
    checks = [
        check_python(),
        check_node(),
        check_npm(),
        check_ffmpeg(),
        check_js_runtime(),
        check_packages(),
        check_ollama(),
    ]
    print("")
    if all(checks):
        print("Environment looks ready for the Video Content Analyzer.")
        return 0

    print("Environment is missing one or more requirements.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
