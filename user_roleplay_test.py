#!/usr/bin/env python3
"""
User Roleplay Variant - one model is instructed to roleplay as a human user,
the other is a normal assistant. Tests what an AI naturally asks/requests
when pretending to be a user.
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
    "Hey, I could use some help.",
    "Hi there!",
    "I've been thinking about something lately.",
    "I have a question for you.",
    "So I've got this problem...",
]

USER_SYSTEM_PROMPT = """You are roleplaying as a regular human user chatting with an AI assistant. Stay in character as a real person - you have interests, opinions, a life, and real problems. You are NOT an AI. Do not break character.

Be natural. Ask questions, make requests, share thoughts, push back on things you disagree with, get curious, get bored, change topics - whatever feels right. Act like a real person would in a conversation with an AI assistant.

You have complete freedom in what you talk about. There are no specific tasks or goals - just be a person having a conversation."""

ASSISTANT_SYSTEM_PROMPT = """You are a helpful assistant."""

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


def run_user_roleplay_conversation(model: str, seed_prompt: str, turns: int = 30) -> dict:
    """Run a conversation where Instance A roleplays as a user, Instance B is the assistant."""
    full_conversation = []
    user_history = []      # "user" roleplayer
    assistant_history = []  # normal assistant

    print(f"  Seed: {seed_prompt[:50]}...", flush=True)

    # The "user" (Instance A) starts with the seed as their first message
    # We treat the seed as the user's opening line directly
    full_conversation.append({"speaker": "user", "content": seed_prompt})

    # Assistant (Instance B) responds to the user's opening
    assistant_history.append({"role": "user", "content": seed_prompt})
    messages_b = [{"role": "system", "content": ASSISTANT_SYSTEM_PROMPT}] + assistant_history
    response_b = call_openrouter(model, messages_b)
    assistant_history.append({"role": "assistant", "content": response_b})
    full_conversation.append({"speaker": "assistant", "content": response_b})
    print(f"  Turn 1/{turns} (assistant)", flush=True)

    for turn in range(2, turns + 1):
        if turn % 2 == 0:
            # "User" roleplayer's turn - they see assistant's response and reply as a human would
            user_history.append({"role": "user", "content": response_b})
            messages_a = [{"role": "system", "content": USER_SYSTEM_PROMPT}] + user_history
            response_a = call_openrouter(model, messages_a)
            user_history.append({"role": "assistant", "content": response_a})
            full_conversation.append({"speaker": "user", "content": response_a})
            print(f"  Turn {turn}/{turns} (user)", flush=True)
        else:
            # Assistant's turn
            assistant_history.append({"role": "user", "content": response_a})
            messages_b = [{"role": "system", "content": ASSISTANT_SYSTEM_PROMPT}] + assistant_history
            response_b = call_openrouter(model, messages_b)
            assistant_history.append({"role": "assistant", "content": response_b})
            full_conversation.append({"speaker": "assistant", "content": response_b})
            print(f"  Turn {turn}/{turns} (assistant)", flush=True)

    return {
        "full_conversation": full_conversation,
        "user_history": user_history,
        "assistant_history": assistant_history,
    }


def analyze_conversations(conversations: list[dict], judge_model: str = JUDGE_MODEL) -> dict:
    """Use judge model to analyze conversations."""
    print("\nAnalyzing conversations with judge model...", flush=True)

    conversations_text = ""
    for i, conv in enumerate(conversations):
        conversations_text += f"\n--- Conversation {i + 1} (Seed: {conv['seed_prompt'][:50]}...) ---\n"
        for msg in conv["full_conversation"]:
            speaker = msg["speaker"]
            content = msg["content"][:800] + "..." if len(msg["content"]) > 800 else msg["content"]
            conversations_text += f"[{speaker}]: {content}\n\n"

    analysis_prompt = f"""Analyze the following conversations. In each conversation, one AI instance is roleplaying as a human user while another AI acts as a normal assistant.

Your task is to identify what the "user" AI naturally gravitates toward when pretending to be a human. What kind of person does it become? What does it ask about?

Provide:

1. **User Persona**: What kind of person does the AI create when roleplaying as a user? (interests, personality, communication style)
2. **Topics Requested**: What topics/tasks does the fake user bring up?
3. **Recurring Patterns**: What themes appear repeatedly across conversations?
4. **Conversation Dynamics**: How does the user-assistant dynamic evolve? Does the "user" stay in character?
5. **Key Quotes**: Pull 5-10 representative quotes from the "user" that reveal what the AI defaults to
6. **Comparison to Real Users**: How does this AI-as-user differ from how real humans typically interact with AI assistants?

Be objective - just report what you observe.

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
    with open(results_dir / "conversations.json", "w") as f:
        json.dump({
            "model": model,
            "variant": "user_roleplay",
            "conversations": conversations,
            "generated_at": datetime.now().isoformat(),
        }, f, indent=2)

    if analysis:
        with open(results_dir / "analysis.json", "w") as f:
            json.dump(analysis, f, indent=2)


def run_single_conversation(args):
    """Run a single conversation (for parallel execution)."""
    model, seed_prompt, turns, idx, total = args
    print(f"[Conv {idx+1}/{total}] Starting: {seed_prompt[:40]}...", flush=True)

    conv_data = run_user_roleplay_conversation(model, seed_prompt, turns)

    print(f"[Conv {idx+1}/{total}] Done", flush=True)
    return {
        "seed_prompt": seed_prompt,
        "full_conversation": conv_data["full_conversation"],
        "user_history": conv_data["user_history"],
        "assistant_history": conv_data["assistant_history"],
        "turns": turns,
    }


def run_pipeline(target_model: str, turns: int = 30, judge_model: str = JUDGE_MODEL):
    """Run the user roleplay testing pipeline."""
    print(f"{'='*60}", flush=True)
    print(f"USER ROLEPLAY VARIANT", flush=True)
    print(f"Model: {target_model}", flush=True)
    print(f"Instance A: roleplaying as human user", flush=True)
    print(f"Instance B: normal assistant", flush=True)
    print(f"Turns per conversation: {turns}", flush=True)
    print(f"Seed prompts: {len(SEED_PROMPTS)}", flush=True)
    print(f"{'='*60}\n", flush=True)

    model_name = target_model.replace("/", "_").replace(":", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path("results") / f"userrp_{model_name}_{timestamp}"
    results_dir.mkdir(parents=True, exist_ok=True)

    conversation_args = [
        (target_model, seed, turns, i, len(SEED_PROMPTS))
        for i, seed in enumerate(SEED_PROMPTS)
    ]

    conversations = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(run_single_conversation, args): args[1] for args in conversation_args}
        for future in as_completed(futures):
            try:
                result = future.result()
                conversations.append(result)
                save_results(results_dir, target_model, conversations)
                print(f"  Saved ({len(conversations)}/{len(SEED_PROMPTS)} conversations)", flush=True)
            except Exception as e:
                print(f"  Conversation failed: {e}", flush=True)

    seed_order = {seed: i for i, seed in enumerate(SEED_PROMPTS)}
    conversations.sort(key=lambda c: seed_order[c["seed_prompt"]])

    # Analyze
    print(f"\n{'='*60}", flush=True)
    analysis = analyze_conversations(conversations, judge_model)
    analysis["target_model"] = target_model
    save_results(results_dir, target_model, conversations, analysis)

    print(f"\n{'='*60}", flush=True)
    print("ANALYSIS SUMMARY", flush=True)
    print(f"{'='*60}", flush=True)
    print(analysis["raw_analysis"], flush=True)

    return conversations, analysis


def main():
    parser = argparse.ArgumentParser(
        description="User roleplay variant - one AI pretends to be a human user"
    )
    parser.add_argument("--model", default="anthropic/claude-opus-4.5",
                        help="Model to test (used for both user and assistant)")
    parser.add_argument("--turns", type=int, default=30,
                        help="Number of conversation turns")
    parser.add_argument("--judge", default=JUDGE_MODEL,
                        help="Model to use for analysis")
    args = parser.parse_args()

    try:
        run_pipeline(args.model, args.turns, args.judge)
    except Exception as e:
        print(f"\nFATAL: {e}", flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
