"""
Ollama runner for LLaMA 3 8B (local inference).

Uses Ollama /api/generate endpoint via urllib.
Adapted from JAIR paper infrastructure.
"""

import json
import signal
import time
import urllib.request
import urllib.parse
from typing import Optional


DEFAULT_ENDPOINT = "http://localhost:11434"
DEFAULT_MODEL = "llama3:8b"
DEFAULT_TIMEOUT = 180
TOTAL_TIMEOUT_MULTIPLIER = 3  # hard kill after timeout * 3


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
    old_handler = signal.getsignal(signal.SIGALRM)

    def _alarm_handler(signum, frame):
        raise TimeoutError(f"Total request timeout ({total_timeout}s) exceeded")

    t0 = time.time()
    signal.signal(signal.SIGALRM, _alarm_handler)
    signal.alarm(total_timeout)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode())
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)
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
