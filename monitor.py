#!/usr/bin/env python3
"""Monitor experiment progress — checks every 10 min, logs to monitor.log"""
import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path("data/raw_outputs")
LOG = Path("monitor.log")
CHECK_INTERVAL = 600  # 10 minutes

MODELS = {
    "mistral-7b": {"screening": 10, "extraction": 10},
    "gemma2-9b": {"screening": 10, "extraction": 10},
}


def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def count_done(model, stage):
    d = OUTPUT_DIR / model / stage
    if not d.exists():
        return 0, []
    runs = []
    for rd in sorted(d.iterdir()):
        card = rd / "run_card.json"
        if card.exists():
            try:
                with open(card) as f:
                    c = json.load(f)
                ok = c["execution"]["successful_calls"]
                total = c["execution"]["total_calls"]
                pct = ok / total * 100 if total > 0 else 0
                runs.append((rd.name, ok, total, pct))
            except Exception:
                runs.append((rd.name, -1, -1, 0))
    return len(runs), runs


def check_process(parent_pid):
    """Check if parent process is alive and has active child."""
    try:
        os.kill(parent_pid, 0)
    except ProcessLookupError:
        return "DEAD", None
    # Check child
    out = subprocess.run(["ps", "-eo", "pid,ppid,etime"],
                         capture_output=True, text=True)
    for line in out.stdout.strip().split("\n"):
        parts = line.split()
        if len(parts) >= 3 and parts[1] == str(parent_pid):
            return "RUNNING", parts[0]
    return "NO_CHILD", None


def main():
    log("=== MONITOR STARTED ===")
    last_counts = {}
    stale_checks = 0

    while True:
        log("--- CHECK ---")
        # Find experiment process
        out = subprocess.run(
            ["bash", "-c", "ps aux | grep 'run_experiment' | grep -v grep"],
            capture_output=True, text=True,
        )
        procs = [l for l in out.stdout.strip().split("\n") if l.strip()]

        if not procs:
            log("WARNING: No run_experiment process found!")
            # Check if sequential runner is alive
            out2 = subprocess.run(
                ["bash", "-c", "ps aux | grep 'run_sequential' | grep -v grep"],
                capture_output=True, text=True,
            )
            if out2.stdout.strip():
                log("  run_sequential.sh still alive — may be transitioning between models")
            else:
                log("ALERT: Both run_experiment and run_sequential are DEAD!")
                log("=== ALL PROCESSES ENDED — MONITOR STOPPING ===")
                break
        else:
            for p in procs:
                parts = p.split()
                pid = int(parts[1])
                status, child = check_process(pid)
                model = "mistral" if "mistral" in p else "gemma" if "gemma" in p else "?"
                log(f"  {model} PID {pid}: {status} (child={child})")

        # Count completed runs
        all_done = True
        for model, targets in MODELS.items():
            for stage, target in targets.items():
                done, runs = count_done(model, stage)
                key = f"{model}/{stage}"
                prev = last_counts.get(key, 0)
                status = f"{done}/{target}"
                if done > prev:
                    latest = runs[-1]
                    log(f"  NEW: {key} = {status} (latest: {latest[0]} {latest[1]}/{latest[2]} = {latest[3]:.0f}%)")
                    stale_checks = 0
                else:
                    log(f"  {key} = {status}")
                last_counts[key] = done
                if done < target:
                    all_done = False

        if all_done:
            log("=== ALL EXPERIMENTS COMPLETE! ===")
            break

        stale_checks += 1
        if stale_checks >= 12:  # 2 hours with no new run
            log("WARNING: No new run completed in 2 hours — possible hang!")
            stale_checks = 0  # reset to avoid spam

        time.sleep(CHECK_INTERVAL)

    log("=== MONITOR STOPPED ===")


if __name__ == "__main__":
    main()
