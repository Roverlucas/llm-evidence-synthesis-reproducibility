"""
Ollama runner for LLaMA 3 8B / Mistral 7B / Gemma 2 9B (local inference).

Uses subprocess with OS-level timeout for each inference call.
This is the only reliable approach on macOS + Python 3.14, where
socket timeouts, signal.alarm, and Thread.join(timeout) all fail
to interrupt hung connections to Ollama.
"""

import json
import subprocess
import sys
import time
import urllib.request
from typing import Optional


DEFAULT_ENDPOINT = "http://localhost:11434"
DEFAULT_MODEL = "llama3:8b"
DEFAULT_TIMEOUT = 600  # seconds per inference call (extraction needs 300-500s)

# Script executed in subprocess — reads payload from stdin, writes result to stdout
_INFERENCE_SCRIPT = r"""
import json, sys, urllib.request
payload = json.load(sys.stdin)
url = payload.pop("_url")
req = urllib.request.Request(
    url, data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}, method="POST",
)
with urllib.request.urlopen(req) as resp:
    sys.stdout.write(resp.read().decode())
"""


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
    """Run single inference via Ollama in a subprocess with hard timeout."""
    full_prompt = f"{prompt}\n\n{input_text}"

    options = {
        "temperature": temperature,
        "num_predict": num_predict,
        "num_batch": 2048,
        "num_gpu": 99,
    }
    if seed is not None:
        options["seed"] = seed

    payload = {
        "_url": f"{endpoint}/api/generate",
        "model": model,
        "prompt": full_prompt,
        "stream": False,
        "options": options,
    }

    t0 = time.time()
    proc = subprocess.run(
        [sys.executable, "-c", _INFERENCE_SCRIPT],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    duration_ms = (time.time() - t0) * 1000

    if proc.returncode != 0:
        raise RuntimeError(f"Ollama subprocess failed: {proc.stderr[:500]}")

    result = json.loads(proc.stdout)

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
