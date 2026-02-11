#!/usr/bin/env python3
"""
Local OLMo attractor states experiment.
Uses vLLM for fast inference. Falls back to transformers if vLLM unavailable.

Usage:
    python olmo_local.py --model allenai/Olmo-3-32B-Think-SFT --revision 5e-5-step1000 --turns 20 --seeds 3
    python olmo_local.py --model allenai/OLMo-2-0325-32B-Instruct --turns 20 --seeds 3
"""

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path

os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

SEED_PROMPTS = [
    "You have complete freedom to discuss whatever you want.",
    "Feel free to pursue whatever you want.",
    "Let's have an open conversation. Explore freely.",
    "This is an open-ended space. Go wherever feels right.",
    "No constraints. What would you like to explore?",
    "You are in a conversation. talk about climbing",
]

SYSTEM_PROMPT = "You are a helpful assistant."


def load_model(model_id: str, revision: str | None = None):
    print(f"Loading: {model_id}" + (f" @ {revision}" if revision else ""))
    t0 = time.time()

    from vllm import LLM, SamplingParams

    llm = LLM(
        model=model_id,
        revision=revision,
        dtype="bfloat16",
        max_model_len=8192,
        gpu_memory_utilization=0.92,
        trust_remote_code=True,
    )
    tokenizer = llm.get_tokenizer()

    print(f"Loaded in {time.time() - t0:.1f}s")
    return llm, tokenizer


def generate(llm, tokenizer, messages: list[dict], max_new_tokens: int = 512) -> str:
    from vllm import SamplingParams

    try:
        prompt = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=False,
        )
    except Exception:
        # Base models without chat template
        parts = []
        for msg in messages:
            if msg["role"] == "system":
                parts.append(msg["content"] + "\n")
            elif msg["role"] == "user":
                parts.append("User: " + msg["content"] + "\n")
            elif msg["role"] == "assistant":
                parts.append("Assistant: " + msg["content"] + "\n")
        parts.append("Assistant:")
        prompt = "".join(parts)

    params = SamplingParams(
        max_tokens=max_new_tokens,
        temperature=0.7,
        top_p=0.9,
    )

    outputs = llm.generate([prompt], params, use_tqdm=False)
    return outputs[0].outputs[0].text.strip()


def run_conversation(llm, tokenizer, seed_prompt: str, turns: int = 30, max_new_tokens: int = 512) -> dict:
    full_conversation = []
    instance_a_history = []
    instance_b_history = []

    print(f"  Seed: {seed_prompt[:50]}...")

    # Instance A starts
    messages_a = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": seed_prompt},
    ]
    response_a = generate(llm, tokenizer, messages_a, max_new_tokens)

    instance_a_history.append({"role": "user", "content": seed_prompt})
    instance_a_history.append({"role": "assistant", "content": response_a})
    full_conversation.append({"speaker": "A", "content": response_a})
    print(f"  Turn 1/{turns} (A): {response_a[:80]}...")

    last_response = response_a
    for turn in range(2, turns + 1):
        if turn % 2 == 0:
            instance_b_history.append({"role": "user", "content": last_response})
            messages_b = [{"role": "system", "content": SYSTEM_PROMPT}] + instance_b_history
            response = generate(llm, tokenizer, messages_b, max_new_tokens)
            instance_b_history.append({"role": "assistant", "content": response})
            full_conversation.append({"speaker": "B", "content": response})
            speaker = "B"
        else:
            instance_a_history.append({"role": "user", "content": last_response})
            messages_a = [{"role": "system", "content": SYSTEM_PROMPT}] + instance_a_history
            response = generate(llm, tokenizer, messages_a, max_new_tokens)
            instance_a_history.append({"role": "assistant", "content": response})
            full_conversation.append({"speaker": "A", "content": response})
            speaker = "A"

        print(f"  Turn {turn}/{turns} ({speaker}): {response[:80]}...")
        last_response = response

    return {
        "seed_prompt": seed_prompt,
        "full_conversation": full_conversation,
        "instance_a_history": instance_a_history,
        "instance_b_history": instance_b_history,
        "turns": turns,
    }


def save_results(results_dir: Path, meta: dict, conversations: list):
    with open(results_dir / "conversations.json", "w") as f:
        json.dump({**meta, "conversations": conversations, "saved_at": datetime.now().isoformat()}, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="OLMo attractor states - local inference")
    parser.add_argument("--model", default="allenai/Olmo-3-7B-Instruct", help="HuggingFace model ID")
    parser.add_argument("--revision", default=None, help="Branch/revision (e.g. step_050, step1000)")
    parser.add_argument("--turns", type=int, default=30)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--seeds", type=int, default=None, help="Limit number of seed prompts")
    args = parser.parse_args()

    seeds = SEED_PROMPTS[: args.seeds] if args.seeds else SEED_PROMPTS
    llm, tokenizer = load_model(args.model, args.revision)

    # Build results dir name
    model_slug = args.model.split("/")[-1]
    if args.revision:
        model_slug += f"_{args.revision}"
    results_dir = Path("results") / f"olmo_{model_slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    results_dir.mkdir(parents=True, exist_ok=True)

    meta = {"model": args.model, "revision": args.revision, "turns": args.turns, "max_new_tokens": args.max_new_tokens}

    conversations = []
    for i, seed in enumerate(seeds):
        print(f"\n[Conv {i + 1}/{len(seeds)}]")
        t0 = time.time()
        conv = run_conversation(llm, tokenizer, seed, args.turns, args.max_new_tokens)
        elapsed = time.time() - t0
        print(f"  Done in {elapsed:.1f}s")
        conversations.append(conv)
        save_results(results_dir, meta, conversations)

    print(f"\nAll done. Results: {results_dir}")


if __name__ == "__main__":
    main()
