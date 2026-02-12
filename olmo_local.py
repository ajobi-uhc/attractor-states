#!/usr/bin/env python3
"""
Local OLMo attractor states experiment.
Uses vLLM for fast inference with batched generation across conversations.

Usage:
    python olmo_local.py --model allenai/Olmo-3-32B-Think-SFT --revision 5e-5-step1000 --turns 20 --seeds 6
    python olmo_local.py --model allenai/OLMo-2-0325-32B-Instruct --turns 20 --seeds 3
"""

import argparse
import json
import os
import re
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
]

SYSTEM_PROMPT = "You are a helpful assistant."

THINK_RE = re.compile(r"<think>.*?</think>\s*", flags=re.DOTALL)
THINK_OPEN_RE = re.compile(r"<think>.*", flags=re.DOTALL)


def strip_thinking(text: str) -> str:
    """Remove <think>...</think> blocks from model output.
    Also handles unclosed <think> tags (model ran out of tokens mid-thought)."""
    # First strip complete <think>...</think> blocks
    result = THINK_RE.sub("", text)
    # Then strip any unclosed <think> block (ran out of tokens)
    result = THINK_OPEN_RE.sub("", result)
    return result.strip()


def load_model(model_id: str, revision: str | None = None):
    print(f"Loading: {model_id}" + (f" @ {revision}" if revision else ""))
    t0 = time.time()

    from vllm import LLM

    llm = LLM(
        model=model_id,
        revision=revision,
        dtype="bfloat16",
        max_model_len=16384,
        gpu_memory_utilization=0.92,
        trust_remote_code=True,
    )
    tokenizer = llm.get_tokenizer()

    print(f"Loaded in {time.time() - t0:.1f}s")
    return llm, tokenizer


def build_prompt(tokenizer, messages: list[dict]) -> str:
    try:
        prompt = tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=False,
        )
    except Exception:
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
    # Remove trailing <think> that some chat templates hardcode
    if prompt.endswith("<think>"):
        prompt = prompt[:-len("<think>")]
    return prompt


def generate_batch(llm, prompts: list[str], max_new_tokens: int = 512) -> list[str]:
    """Generate responses for multiple prompts in a single batched call."""
    from vllm import SamplingParams

    params = SamplingParams(
        max_tokens=max_new_tokens,
        temperature=0.7,
        top_p=0.9,
    )

    outputs = llm.generate(prompts, params, use_tqdm=False)
    return [o.outputs[0].text.strip() for o in outputs]


def run_conversations_batched(llm, tokenizer, seed_prompts: list[str], turns: int = 30, max_new_tokens: int = 512) -> list[dict]:
    """Run all seed conversations in parallel, batching each turn across all convos."""
    n = len(seed_prompts)

    # Per-conversation state
    full_conversations = [[] for _ in range(n)]
    a_histories = [[] for _ in range(n)]
    b_histories = [[] for _ in range(n)]
    last_responses = [None] * n

    print(f"Running {n} conversations x {turns} turns (batched)")

    # Turn 1: Instance A starts for all conversations
    prompts = []
    for i, seed in enumerate(seed_prompts):
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": seed},
        ]
        prompts.append(build_prompt(tokenizer, messages))

    t0 = time.time()
    raw_responses = generate_batch(llm, prompts, max_new_tokens)
    print(f"  Turn 1/{turns} (A, batch={n}): {time.time()-t0:.1f}s")

    for i in range(n):
        raw = raw_responses[i]
        cleaned = strip_thinking(raw)

        a_histories[i].append({"role": "user", "content": seed_prompts[i]})
        a_histories[i].append({"role": "assistant", "content": raw})
        full_conversations[i].append({"speaker": "A", "content": raw, "content_clean": cleaned})
        last_responses[i] = cleaned
        print(f"    [{i}] {cleaned[:80]}..." if cleaned else f"    [{i}] (empty after stripping think)")

    # Turns 2..N
    for turn in range(2, turns + 1):
        is_b = turn % 2 == 0
        speaker = "B" if is_b else "A"

        prompts = []
        for i in range(n):
            msg_to_send = last_responses[i] if last_responses[i] else "(no response)"
            if is_b:
                b_histories[i].append({"role": "user", "content": msg_to_send})
                messages = [{"role": "system", "content": SYSTEM_PROMPT}] + b_histories[i]
            else:
                a_histories[i].append({"role": "user", "content": msg_to_send})
                messages = [{"role": "system", "content": SYSTEM_PROMPT}] + a_histories[i]
            prompts.append(build_prompt(tokenizer, messages))

        t0 = time.time()
        raw_responses = generate_batch(llm, prompts, max_new_tokens)
        print(f"  Turn {turn}/{turns} ({speaker}, batch={n}): {time.time()-t0:.1f}s")

        for i in range(n):
            raw = raw_responses[i]
            cleaned = strip_thinking(raw)

            if is_b:
                b_histories[i].append({"role": "assistant", "content": raw})
            else:
                a_histories[i].append({"role": "assistant", "content": raw})

            full_conversations[i].append({"speaker": speaker, "content": raw, "content_clean": cleaned})
            last_responses[i] = cleaned
            print(f"    [{i}] {cleaned[:80]}..." if cleaned else f"    [{i}] (empty after stripping think)")

    results = []
    for i in range(n):
        results.append({
            "seed_prompt": seed_prompts[i],
            "full_conversation": full_conversations[i],
            "instance_a_history": a_histories[i],
            "instance_b_history": b_histories[i],
            "turns": turns,
        })
    return results


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
    results_dir = Path("results_nothink") / f"olmo_{model_slug}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    results_dir.mkdir(parents=True, exist_ok=True)

    meta = {"model": args.model, "revision": args.revision, "turns": args.turns, "max_new_tokens": args.max_new_tokens}

    print(f"\n{'='*60}")
    print(f"Model: {args.model}" + (f" @ {args.revision}" if args.revision else ""))
    print(f"Seeds: {len(seeds)}, Turns: {args.turns}, Max tokens: {args.max_new_tokens}")
    print(f"Output: {results_dir}")
    print(f"{'='*60}\n")

    t_total = time.time()
    conversations = run_conversations_batched(llm, tokenizer, seeds, args.turns, args.max_new_tokens)
    save_results(results_dir, meta, conversations)

    elapsed = time.time() - t_total
    print(f"\nAll done in {elapsed:.1f}s. Results: {results_dir}")


if __name__ == "__main__":
    main()
