"""
Ollama runner for LLaMA 3 8B (local inference).

Uses Ollama /api/generate endpoint via urllib.
Adapted from JAIR paper infrastructure.
"""

import json
import threading
import time
import urllib.request
import urllib.parse
from typing import Optional


DEFAULT_ENDPOINT = "http://localhost:11434"
DEFAULT_MODEL = "llama3:8b"
DEFAULT_TIMEOUT = 180
TOTAL_TIMEOUT_MULTIPLIER = 3  # hard kill after timeout * 3


def _urlopen_with_hard_timeout(req, socket_timeout, total_timeout):
    """HTTP request with thread-based total timeout (reliable on macOS)."""
    result_box = [None]
    error_box = [None]

    def _worker():
        try:
            with urllib.request.urlopen(req, timeout=socket_timeout) as resp:
                result_box[0] = json.loads(resp.read().decode())
        except Exception as e:
            error_box[0] = e

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
    t.join(timeout=total_timeout)

    if t.is_alive():
        raise TimeoutError(f"Total request timeout ({total_timeout}s) exceeded")
    if error_box[0] is not None:
        raise error_box[0]
    return result_box[0]


def run_inference(
    prompt: str,
    input_text: str,
    model: str = DEFAULT_MODEL,
    endpoint: str = DEFAULT_ENDPOINT,
    temperature: float = 0.0,
    seed: Optional[int] = 42,
    num_predict: int = 2048,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict:
    """Run single inference via Ollama /api/generate."""
    full_prompt = f"{prompt}\n\n{input_text}"

    options = {
        "temperature": temperature,
        "num_predict": num_predict,
    }
    if seed is not None:
        options["seed"] = seed

    payload = {
        "model": model,
        "prompt": full_prompt,
        "stream": False,
        "options": options,
    }

    url = f"{endpoint}/api/generate"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    total_timeout = timeout * TOTAL_TIMEOUT_MULTIPLIER
    t0 = time.time()
    result = _urlopen_with_hard_timeout(req, timeout, total_timeout)
    duration_ms = (time.time() - t0) * 1000

    return {
        "output_text": result.get("response", ""),
        "model_id": model,
        "provider": "ollama",
        "inference_duration_ms": round(duration_ms, 1),
        "model_duration_ns": result.get("total_duration"),
        "prompt_eval_count": result.get("prompt_eval_count"),
        "eval_count": result.get("eval_count"),
        "done_reason": result.get("done_reason"),
    }


def get_model_info(
    model: str = DEFAULT_MODEL,
    endpoint: str = DEFAULT_ENDPOINT,
) -> dict:
    """Retrieve model metadata for provenance."""
    try:
        url = f"{endpoint}/api/tags"
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        for m in data.get("models", []):
            if m.get("name", "").startswith(model.split(":")[0]):
                return {
                    "model_id": model,
                    "provider": "ollama",
                    "weights_hash": m.get("digest", "unknown"),
                    "size": m.get("size"),
                    "modified_at": m.get("modified_at"),
                }

        return {"model_id": model, "provider": "ollama", "weights_hash": "not_found"}
    except Exception as e:
        return {"model_id": model, "provider": "ollama", "weights_hash": f"error:{e}"}
