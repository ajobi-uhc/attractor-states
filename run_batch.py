#!/usr/bin/env python3
"""
Batch runner for attractor states testing.
Runs models SEQUENTIALLY (one at a time) to avoid rate limits.
Saves results after each model completes.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

MODELS = [
    "anthropic/claude-sonnet-4.5",
    "deepseek/deepseek-v3.2",
    "moonshotai/kimi-k2.5",
    "google/gemini-2.5-flash",
    "x-ai/grok-4.1-fast",
    "arcee-ai/trinity-large-preview:free",
    "openai/gpt-5.2",
]


def run_model(model: str, turns: int = 30) -> dict:
    """Run attractor test for a single model."""
    print(f"\n{'#'*60}")
    print(f"# STARTING: {model}")
    print(f"{'#'*60}\n", flush=True)

    result = subprocess.run(
        [sys.executable, "attractor_test.py", "--model", model, "--turns", str(turns)],
        timeout=3600,  # 1 hour timeout per model
    )

    status = "success" if result.returncode == 0 else "failed"
    print(f"\n{'#'*60}")
    print(f"# {status.upper()}: {model}")
    print(f"{'#'*60}\n", flush=True)

    return {
        "model": model,
        "status": status,
        "returncode": result.returncode,
        "completed_at": datetime.now().isoformat(),
    }


def save_batch_summary(results: list):
    """Save batch summary after each model."""
    summary = {
        "run_at": datetime.now().isoformat(),
        "models_completed": len([r for r in results if r["status"] == "success"]),
        "models_failed": len([r for r in results if r["status"] == "failed"]),
        "results": results,
    }
    with open("results/batch_summary.json", "w") as f:
        json.dump(summary, f, indent=2)


def main():
    print(f"{'='*60}")
    print(f"BATCH ATTRACTOR STATES TEST")
    print(f"Models to test: {len(MODELS)}")
    print(f"Running SEQUENTIALLY (one at a time)")
    print(f"{'='*60}\n", flush=True)

    Path("results").mkdir(exist_ok=True)

    results = []
    for i, model in enumerate(MODELS):
        print(f"\n[{i+1}/{len(MODELS)}] {model}", flush=True)

        try:
            result = run_model(model)
            results.append(result)
        except subprocess.TimeoutExpired:
            print(f"TIMEOUT: {model}", flush=True)
            results.append({
                "model": model,
                "status": "timeout",
                "completed_at": datetime.now().isoformat(),
            })
        except Exception as e:
            print(f"ERROR: {model} - {e}", flush=True)
            results.append({
                "model": model,
                "status": "error",
                "error": str(e),
                "completed_at": datetime.now().isoformat(),
            })

        # Save summary after each model
        save_batch_summary(results)
        print(f"Batch summary updated ({len(results)}/{len(MODELS)} models done)", flush=True)

    print(f"\n{'='*60}")
    print("BATCH COMPLETE")
    print(f"{'='*60}")
    for r in results:
        icon = "✓" if r["status"] == "success" else "✗"
        print(f"  {icon} {r['model']}: {r['status']}")

    print(f"\nResults in: results/<model_name>/")
    print(f"Summary in: results/batch_summary.json")


if __name__ == "__main__":
    main()
