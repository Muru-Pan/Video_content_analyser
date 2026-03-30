from __future__ import annotations

import importlib
import shutil
import sys

from core.runtime import ollama_status
from core.utils import ensure_ffmpeg_installed, ensure_js_runtime

REQUIRED_PACKAGES = [
    "fastapi",
    "whisper",
    "yt_dlp",
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
    print(f"[{'OK' if ok else 'FAIL'}] Python {version.major}.{version.minor}.{version.micro}")
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
        print(f"[OK] JS runtime: {runtime_name} ({runtime_binary})")
        return True
    except Exception as exc:
        print(f"[FAIL] JS runtime: {exc}")
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
    status = ollama_status()
    ok = status == "reachable"
    print(f"[{'OK' if ok else 'FAIL'}] Ollama: {status}")
    return ok


def main() -> int:
    checks = [check_python(), check_ffmpeg(), check_js_runtime(), check_packages(), check_ollama()]
    print("")
    if all(checks):
        print("Backend environment looks ready.")
        return 0
    print("Backend environment is missing one or more requirements.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
