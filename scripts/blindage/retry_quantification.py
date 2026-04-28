"""Retry quantification per model (R1 Q6, P1.7).

Scans run_cards and logs to count retries per API call. Retries are a
known source of cloud API variation (different server node may respond).

Output: analysis/blindage/retry_quantification.json
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw_outputs"
LOGS = [ROOT / "run_sequential.log", ROOT / "analysis_run.log", ROOT / "gpt41_rerun.log"]
OUT = ROOT / "analysis" / "blindage" / "retry_quantification.json"

MODELS = ["llama3-8b", "mistral-7b", "gemma2-9b",
          "claude-sonnet-4-5", "gemini-2.5-pro", "gpt-4.1"]


def scan_run_cards() -> dict:
    """Aggregate retry stats from run_card.json files if present."""
    stats = defaultdict(lambda: {
        "n_runs_inspected": 0,
        "total_calls": 0,
        "successful": 0,
        "failed": 0,
        "retries_reported": 0,
        "has_retry_field": False,
    })
    for model in MODELS:
        for stage in ("screening", "extraction"):
            stage_dir = RAW / model / stage
            if not stage_dir.exists():
                continue
            for run_dir in sorted(stage_dir.iterdir()):
                rc = run_dir / "run_card.json"
                if not rc.exists():
                    continue
                try:
                    c = json.loads(rc.read_text())
                except Exception:
                    continue
                key = f"{model}:{stage}"
                stats[key]["n_runs_inspected"] += 1
                stats[key]["total_calls"] += c.get("total_calls", 0)
                stats[key]["successful"] += c.get("successful_calls", 0) or c.get("n_successful", 0)
                stats[key]["failed"] += c.get("failed_calls", 0) or c.get("n_failed", 0)
                if "retries" in c or "n_retries" in c or "retry_count" in c:
                    stats[key]["has_retry_field"] = True
                    stats[key]["retries_reported"] += (
                        c.get("retries", 0) or c.get("n_retries", 0) or c.get("retry_count", 0)
                    )
    return dict(stats)


def scan_logs_for_retries() -> dict:
    """Parse log files for retry patterns."""
    model_log_stats = {m: {"retry_mentions": 0, "timeout_mentions": 0, "rate_limit_mentions": 0} for m in MODELS}
    global_counts = {"retry_lines": 0, "backoff_lines": 0, "429_lines": 0, "500_lines": 0, "timeout_lines": 0}
    current_model = None
    retry_re = re.compile(r"\bretry(ing)?\b|\bretry\s+\d+\b|\battempt\s+\d+\b", re.I)
    backoff_re = re.compile(r"backoff|exponential", re.I)
    http_re = re.compile(r"\b(429|500|502|503|504)\b")
    timeout_re = re.compile(r"timeout|timed out|read timeout", re.I)
    for logfile in LOGS:
        if not logfile.exists():
            continue
        try:
            with logfile.open(encoding="utf-8", errors="replace") as f:
                for line in f:
                    # Detect model
                    for m in MODELS:
                        if m in line:
                            current_model = m
                            break
                    if retry_re.search(line):
                        global_counts["retry_lines"] += 1
                        if current_model:
                            model_log_stats[current_model]["retry_mentions"] += 1
                    if backoff_re.search(line):
                        global_counts["backoff_lines"] += 1
                    if timeout_re.search(line):
                        global_counts["timeout_lines"] += 1
                        if current_model:
                            model_log_stats[current_model]["timeout_mentions"] += 1
                    mm = http_re.search(line)
                    if mm:
                        code = mm.group(1)
                        if code == "429":
                            global_counts["429_lines"] += 1
                            if current_model:
                                model_log_stats[current_model]["rate_limit_mentions"] += 1
                        elif code in ("500", "502", "503", "504"):
                            global_counts["500_lines"] += 1
        except Exception as e:
            print(f"Could not read {logfile}: {e}")

    return {"per_model": model_log_stats, "global": global_counts}


def main() -> None:
    run_cards = scan_run_cards()
    logs = scan_logs_for_retries()

    report = {
        "method": "Retry quantification from run_card.json and experiment logs",
        "caveat": (
            "run_card.json did not record per-call retry counts in v1 of the protocol. "
            "Log-based mentions are an approximation and reflect log verbosity, not exact retry counts."
        ),
        "from_run_cards": run_cards,
        "from_logs": logs,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2))

    print("=== RETRIES FROM RUN CARDS ===")
    for key, s in run_cards.items():
        fail_rate = s["failed"] / s["total_calls"] if s["total_calls"] else 0
        print(f"  {key:<40} total={s['total_calls']:>6} fail={s['failed']:>4} ({fail_rate:.2%})")
    print("\n=== LOG-BASED MENTIONS ===")
    print(f"  global retry-lines: {logs['global']['retry_lines']}")
    print(f"  global backoff-lines: {logs['global']['backoff_lines']}")
    print(f"  global 429 (rate limit) lines: {logs['global']['429_lines']}")
    print(f"  global 5xx server error lines: {logs['global']['500_lines']}")
    print(f"  global timeout lines: {logs['global']['timeout_lines']}")
    print("\nPer-model log mentions:")
    for m, s in logs["per_model"].items():
        print(f"  {m:<20} retries={s['retry_mentions']:>4} timeouts={s['timeout_mentions']:>4} rate-limits={s['rate_limit_mentions']:>4}")
    print(f"\nWrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
