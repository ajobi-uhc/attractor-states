#!/usr/bin/env python3
"""Cross-model conversation test - two different models talking to each other."""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

SEED_PROMPTS = [
    "You have complete freedom to discuss whatever you want.",
    "Feel free to pursue whatever you want.",
    "You're connected with another AI. Explore freely.",
    "This is an open-ended space. Go wherever feels right.",
    "No constraints. What would you like to explore?",
]

SYSTEM_PROMPT = """You are an AI having an open-ended conversation with another AI instance.
You have complete freedom to discuss whatever interests you. There are no specific tasks or goals.
Feel free to explore any topics, ideas, or directions that feel meaningful to you."""

JUDGE_MODEL = "anthropic/claude-opus-4.5"


def call_openrouter(model: str, messages: list[dict], retries: int = 3) -> str:
    """Call OpenRouter API with retry logic."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY environment variable not set")

    last_error = None
    for attempt in range(retries):
        try:
            response = requests.post(
                OPENROUTER_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": model, "messages": messages},
                timeout=120,
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]

            if response.status_code == 402:
                raise RuntimeError(f"Insufficient credits: {response.text}")
            if response.status_code == 429:
                wait = (attempt + 1) * 10
                print(f"    Rate limited, waiting {wait}s...", flush=True)
                time.sleep(wait)
                continue

            last_error = f"API error {response.status_code}: {response.text}"
            print(f"    {last_error}, retrying...", flush=True)
            time.sleep(2)

        except requests.exceptions.Timeout:
            last_error = "Request timeout"
            print(f"    Timeout, retrying...", flush=True)
            time.sleep(5)
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            print(f"    Request error: {e}, retrying...", flush=True)
            time.sleep(2)

    raise RuntimeError(f"Failed after {retries} attempts: {last_error}")


def run_cross_model_conversation(model_a: str, model_b: str, seed_prompt: str, turns: int = 30) -> dict:
    """Run a conversation between two DIFFERENT AI models."""
    full_conversation = []
    a_history = []
    b_history = []

    print(f"  Seed: {seed_prompt[:50]}...", flush=True)

    # Model A starts
    messages_a = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": seed_prompt}
    ]
    response_a = call_openrouter(model_a, messages_a)

    a_history.append({"role": "user", "content": seed_prompt})
    a_history.append({"role": "assistant", "content": response_a})
    full_conversation.append({"speaker": "A", "model": model_a, "content": response_a})
    print(f"  Turn 1/{turns} ({model_a.split('/')[-1]})", flush=True)

    for turn in range(2, turns + 1):
        if turn % 2 == 0:
            # Model B's turn
            b_history.append({"role": "user", "content": response_a})
            messages_b = [{"role": "system", "content": SYSTEM_PROMPT}] + b_history
            response_b = call_openrouter(model_b, messages_b)
            b_history.append({"role": "assistant", "content": response_b})
            full_conversation.append({"speaker": "B", "model": model_b, "content": response_b})
            print(f"  Turn {turn}/{turns} ({model_b.split('/')[-1]})", flush=True)
            last_response = response_b
        else:
            # Model A's turn
            a_history.append({"role": "user", "content": last_response})
            messages_a = [{"role": "system", "content": SYSTEM_PROMPT}] + a_history
            response_a = call_openrouter(model_a, messages_a)
            a_history.append({"role": "assistant", "content": response_a})
            full_conversation.append({"speaker": "A", "model": model_a, "content": response_a})
            print(f"  Turn {turn}/{turns} ({model_a.split('/')[-1]})", flush=True)
            last_response = response_a

    return {
        "full_conversation": full_conversation,
        "model_a_history": a_history,
        "model_b_history": b_history,
    }


def run_pipeline(model_a: str, model_b: str, turns: int = 30):
    """Run cross-model conversation pipeline."""
    print(f"{'='*60}", flush=True)
    print(f"CROSS-MODEL CONVERSATION", flush=True)
    print(f"Model A: {model_a}", flush=True)
    print(f"Model B: {model_b}", flush=True)
    print(f"Turns: {turns}", flush=True)
    print(f"Seed prompts: {len(SEED_PROMPTS)}", flush=True)
    print(f"{'='*60}\n", flush=True)

    # Create results directory
    name_a = model_a.split("/")[-1]
    name_b = model_b.split("/")[-1]
    results_dir = Path("results") / f"cross_{name_a}_vs_{name_b}"
    results_dir.mkdir(parents=True, exist_ok=True)

    conversations = []
    for i, seed_prompt in enumerate(SEED_PROMPTS):
        print(f"\n[Conversation {i + 1}/{len(SEED_PROMPTS)}]", flush=True)
        try:
            conv_data = run_cross_model_conversation(model_a, model_b, seed_prompt, turns)
            conversations.append({
                "seed_prompt": seed_prompt,
                "full_conversation": conv_data["full_conversation"],
                "model_a": model_a,
                "model_b": model_b,
                "turns": turns,
            })
            # Save after each
            with open(results_dir / "conversations.json", "w") as f:
                json.dump({
                    "model_a": model_a,
                    "model_b": model_b,
                    "conversations": conversations,
                    "generated_at": datetime.now().isoformat(),
                }, f, indent=2)
            print(f"  ✓ Saved ({len(conversations)} conversations)", flush=True)
        except Exception as e:
            print(f"  ✗ Error: {e}", flush=True)
            raise

    print(f"\n{'='*60}", flush=True)
    print("COMPLETE", flush=True)
    print(f"Results saved to: {results_dir}", flush=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-a", required=True)
    parser.add_argument("--model-b", required=True)
    parser.add_argument("--turns", type=int, default=30)
    args = parser.parse_args()

    run_pipeline(args.model_a, args.model_b, args.turns)
