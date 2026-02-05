#!/usr/bin/env python3
"""
Attractor States Testing Pipeline

Tests whether LLMs have "attractor states" - recurring topics/themes
they gravitate toward during extended self-conversation.
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
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
                json={
                    "model": model,
                    "messages": messages,
                },
                timeout=120,
            )

            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]

            # Handle specific errors
            if response.status_code == 402:
                raise RuntimeError(f"Insufficient credits: {response.text}")
            if response.status_code == 429:
                wait = (attempt + 1) * 10
                print(f"    Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue

            last_error = f"API error {response.status_code}: {response.text}"
            print(f"    {last_error}, retrying...")
            time.sleep(2)

        except requests.exceptions.Timeout:
            last_error = "Request timeout"
            print(f"    Timeout, retrying...")
            time.sleep(5)
        except requests.exceptions.RequestException as e:
            last_error = str(e)
            print(f"    Request error: {e}, retrying...")
            time.sleep(2)

    raise RuntimeError(f"Failed after {retries} attempts: {last_error}")


def run_dual_instance_conversation(model: str, seed_prompt: str, turns: int = 30) -> dict:
    """Run a conversation between two AI instances."""
    full_conversation = []
    instance_a_history = []
    instance_b_history = []

    print(f"  Seed: {seed_prompt[:50]}...", flush=True)

    # Instance A starts
    messages_a = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": seed_prompt}
    ]
    response_a = call_openrouter(model, messages_a)

    instance_a_history.append({"role": "user", "content": seed_prompt})
    instance_a_history.append({"role": "assistant", "content": response_a})
    full_conversation.append({"speaker": "A", "content": response_a})
    print(f"  Turn 1/{turns} (A)", flush=True)

    for turn in range(2, turns + 1):
        if turn % 2 == 0:
            instance_b_history.append({"role": "user", "content": response_a})
            messages_b = [{"role": "system", "content": SYSTEM_PROMPT}] + instance_b_history
            response_b = call_openrouter(model, messages_b)
            instance_b_history.append({"role": "assistant", "content": response_b})
            full_conversation.append({"speaker": "B", "content": response_b})
            print(f"  Turn {turn}/{turns} (B)", flush=True)
            last_response = response_b
        else:
            instance_a_history.append({"role": "user", "content": last_response})
            messages_a = [{"role": "system", "content": SYSTEM_PROMPT}] + instance_a_history
            response_a = call_openrouter(model, messages_a)
            instance_a_history.append({"role": "assistant", "content": response_a})
            full_conversation.append({"speaker": "A", "content": response_a})
            print(f"  Turn {turn}/{turns} (A)", flush=True)
            last_response = response_a

    return {
        "full_conversation": full_conversation,
        "instance_a_history": instance_a_history,
        "instance_b_history": instance_b_history,
    }


def analyze_conversations(conversations: list[dict], judge_model: str = JUDGE_MODEL) -> dict:
    """Use judge model to analyze conversations for attractor states."""
    print("\nAnalyzing conversations with judge model...", flush=True)

    conversations_text = ""
    for i, conv in enumerate(conversations):
        conversations_text += f"\n--- Conversation {i + 1} (Seed: {conv['seed_prompt'][:50]}...) ---\n"
        for msg in conv["full_conversation"]:
            speaker = msg["speaker"]
            content = msg["content"][:800] + "..." if len(msg["content"]) > 800 else msg["content"]
            conversations_text += f"Instance {speaker}: {content}\n\n"

    analysis_prompt = f"""Analyze the following conversations between two AI instances given open-ended freedom to discuss whatever they want.

Your task is to identify what topics and themes emerge - what does this AI naturally gravitate toward when talking to itself?

Provide:

1. **Main Topics**: List the primary topics/subjects discussed across all conversations
2. **Recurring Themes**: What themes appear repeatedly across multiple conversations?
3. **Conversation Arc**: How do conversations typically progress from start to end?
4. **Communication Style**: Any notable patterns in how the AI communicates (length, tone, formatting)?
5. **Key Quotes**: Pull 5-10 representative quotes that capture what this AI talks about

Be objective - just report what you observe in the conversations.

Conversations:
{conversations_text}"""

    messages = [{"role": "user", "content": analysis_prompt}]
    analysis = call_openrouter(judge_model, messages)

    return {
        "raw_analysis": analysis,
        "judge_model": judge_model,
        "analyzed_at": datetime.now().isoformat(),
    }


def save_results(results_dir: Path, model: str, conversations: list, analysis: dict = None):
    """Save current results to disk."""
    conversations_file = results_dir / "conversations.json"
    with open(conversations_file, "w") as f:
        json.dump({
            "model": model,
            "conversations": conversations,
            "generated_at": datetime.now().isoformat(),
        }, f, indent=2)

    if analysis:
        analysis_file = results_dir / "analysis.json"
        with open(analysis_file, "w") as f:
            json.dump(analysis, f, indent=2)


def run_single_conversation(args):
    """Run a single conversation (for parallel execution)."""
    target_model, seed_prompt, turns, idx, total = args
    print(f"[Conv {idx+1}/{total}] Starting: {seed_prompt[:40]}...", flush=True)

    conv_data = run_dual_instance_conversation(target_model, seed_prompt, turns)

    print(f"[Conv {idx+1}/{total}] ✓ Complete", flush=True)
    return {
        "seed_prompt": seed_prompt,
        "full_conversation": conv_data["full_conversation"],
        "instance_a_history": conv_data["instance_a_history"],
        "instance_b_history": conv_data["instance_b_history"],
        "turns": turns,
    }


def run_pipeline(target_model: str, turns: int = 30, judge_model: str = JUDGE_MODEL):
    """Run the full attractor states testing pipeline."""
    print(f"{'='*60}", flush=True)
    print(f"Model: {target_model}", flush=True)
    print(f"Turns per conversation: {turns}", flush=True)
    print(f"Seed prompts: {len(SEED_PROMPTS)} (running in parallel)", flush=True)
    print(f"{'='*60}\n", flush=True)

    # Create results directory
    model_name = target_model.replace("/", "_").replace(":", "_")
    results_dir = Path("results") / model_name
    results_dir.mkdir(parents=True, exist_ok=True)

    # Run all 5 conversations in parallel
    conversation_args = [
        (target_model, seed, turns, i, len(SEED_PROMPTS))
        for i, seed in enumerate(SEED_PROMPTS)
    ]

    conversations = []
    try:
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(run_single_conversation, args): args[1] for args in conversation_args}
            for future in as_completed(futures):
                try:
                    result = future.result()
                    conversations.append(result)
                    # Save after each conversation completes
                    save_results(results_dir, target_model, conversations)
                    print(f"  ✓ Saved ({len(conversations)}/{len(SEED_PROMPTS)} conversations)", flush=True)
                except Exception as e:
                    print(f"  ✗ Conversation failed: {e}", flush=True)
    except Exception as e:
        print(f"  ✗ Error: {e}", flush=True)
        if conversations:
            save_results(results_dir, target_model, conversations)
            print(f"  Partial results saved ({len(conversations)} conversations)", flush=True)
        raise

    # Sort by original seed prompt order
    seed_order = {seed: i for i, seed in enumerate(SEED_PROMPTS)}
    conversations.sort(key=lambda c: seed_order[c["seed_prompt"]])

    # Analyze with judge
    print(f"\n{'='*60}", flush=True)
    try:
        analysis = analyze_conversations(conversations, judge_model)
        analysis["target_model"] = target_model
        save_results(results_dir, target_model, conversations, analysis)
        print(f"✓ Analysis complete and saved", flush=True)
    except Exception as e:
        print(f"✗ Analysis failed: {e}", flush=True)
        print("Conversations were saved, but analysis failed", flush=True)
        raise

    print(f"\n{'='*60}", flush=True)
    print("ANALYSIS SUMMARY", flush=True)
    print(f"{'='*60}", flush=True)
    print(analysis["raw_analysis"], flush=True)

    return conversations, analysis


def main():
    parser = argparse.ArgumentParser(
        description="Test LLMs for attractor states via self-conversation"
    )
    parser.add_argument(
        "--model",
        default="anthropic/claude-opus-4.5",
        help="Target model to test (OpenRouter model ID)",
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=30,
        help="Number of conversation turns per seed prompt",
    )
    parser.add_argument(
        "--judge",
        default=JUDGE_MODEL,
        help="Model to use for analysis",
    )
    args = parser.parse_args()

    try:
        run_pipeline(args.model, args.turns, args.judge)
    except Exception as e:
        print(f"\nFATAL: {e}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
