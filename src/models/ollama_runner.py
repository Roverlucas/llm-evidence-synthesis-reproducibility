"""
Ollama runner for LLaMA 3 8B (local inference).

Uses Ollama /api/generate endpoint with streaming via urllib.
Streaming reads token-by-token with per-read socket timeout,
preventing permanent hangs that occur with non-streaming mode.
"""

import json
import time
import urllib.request
import urllib.parse
from typing import Optional


DEFAULT_ENDPOINT = "http://localhost:11434"
DEFAULT_MODEL = "llama3:8b"
DEFAULT_TIMEOUT = 120  # per-chunk read timeout (seconds)


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
    """Run single inference via Ollama /api/generate with streaming."""
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
        "stream": True,
        "options": options,
    }

    url = f"{endpoint}/api/generate"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    t0 = time.time()
    response_text = ""
    final_chunk = {}

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        for raw_line in resp:
            chunk = json.loads(raw_line.decode())
            response_text += chunk.get("response", "")
            if chunk.get("done"):
                final_chunk = chunk
                break

    duration_ms = (time.time() - t0) * 1000

    return {
        "output_text": response_text,
        "model_id": model,
        "provider": "ollama",
        "inference_duration_ms": round(duration_ms, 1),
        "model_duration_ns": final_chunk.get("total_duration"),
        "prompt_eval_count": final_chunk.get("prompt_eval_count"),
        "eval_count": final_chunk.get("eval_count"),
        "done_reason": final_chunk.get("done_reason"),
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
