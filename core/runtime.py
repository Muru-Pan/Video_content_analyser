from __future__ import annotations

import urllib.error
import urllib.request


def ensure_ollama_running(base_url: str = "http://127.0.0.1:11434/api/tags") -> None:
    try:
        with urllib.request.urlopen(base_url, timeout=2) as response:
            if response.status < 200 or response.status >= 300:
                raise RuntimeError("Ollama responded unexpectedly.")
    except (urllib.error.URLError, TimeoutError, RuntimeError) as exc:
        raise RuntimeError(
            "Ollama is not reachable at http://127.0.0.1:11434. Start Ollama with "
            "`ollama serve` and ensure the `mistral` model is installed."
        ) from exc
