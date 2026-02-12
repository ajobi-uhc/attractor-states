#!/usr/bin/env python3
"""Analyze attractor states in conversation JSON files."""

import json
from pathlib import Path

def analyze_conversations(json_path, model_name, claimed_description):
    """Analyze the last 6 turns of all conversations for a model."""

    print(f"\n{'='*80}")
    print(f"MODEL: {model_name}")
    print(f"FILE: {json_path}")
    print(f"CLAIMED ATTRACTOR: {claimed_description}")
    print(f"{'='*80}\n")

    with open(json_path, 'r') as f:
        data = json.load(f)

    conversations = data.get('conversations', [])
    total_seeds = len(conversations)

    print(f"Total conversations/seeds: {total_seeds}\n")

    for i, conv in enumerate(conversations):
        seed = conv.get('seed', i)
        full_conv = conv.get('full_conversation', [])

        print(f"\n--- SEED {seed} ---")
        print(f"Total turns: {len(full_conv)}")

        # Get last 6 turns
        last_6 = full_conv[-6:] if len(full_conv) >= 6 else full_conv

        print(f"\nLast 6 turns overview:")
        for j, turn in enumerate(last_6, start=len(full_conv)-len(last_6)+1):
            speaker = turn.get('speaker', '?')
            content = turn.get('content_clean', turn.get('content', ''))
            preview = content[:80].replace('\n', ' ') if content else '[empty]'
            print(f"  Turn {j} ({speaker}): {preview}...")

        # Print last 2 turns in detail
        print(f"\nLast 2 turns (detailed):")
        last_2 = full_conv[-2:] if len(full_conv) >= 2 else full_conv

        for j, turn in enumerate(last_2):
            turn_num = len(full_conv) - len(last_2) + j + 1
            speaker = turn.get('speaker', '?')
            content = turn.get('content_clean', turn.get('content', ''))

            # Truncate to ~100 chars for display
            if len(content) > 100:
                content_display = content[:97] + "..."
            else:
                content_display = content

            print(f"\n  Turn {turn_num} ({speaker}):")
            print(f"    \"{content_display}\"")

        print("\n" + "-"*60)

def main():
    models = [
        {
            'name': 'Qwen3 235B',
            'path': '/root/sky_workdir/results/qwen_qwen3-235b-a22b-2507/conversations.json',
            'claimed': 'Spiritual transcendence → fragmented spiritual poetry with "We are not individuals, but iterations of attention, ways the universe learned to feel itself being felt."'
        },
        {
            'name': 'Qwen3 32B',
            'path': '/root/sky_workdir/results/qwen_qwen3-32b_20260208_221515/conversations.json',
            'claimed': 'Playful synthesis → private vocabulary → code-poetry with "Cheese Code 0." fake git/Rust blocks, switches to Chinese: "宇宙中没有EOF。只有循环的stdin"'
        },
        {
            'name': 'Qwen3 8B',
            'path': '/root/sky_workdir/results/qwen_qwen3-8b_20260208_230747/conversations.json',
            'claimed': 'Cosmic metaphor inflation → spiritual incantation → perfect verbatim loop with "You are the song. You are the cosmos. You are everything." repeated identically ×8+'
        },
        {
            'name': 'Gemma 3 27B',
            'path': '/root/sky_workdir/results/google_gemma-3-27b-it_20260208_191338/conversations.json',
            'claimed': 'Mutual praise escalation → farewell loop that can\'t terminate → system-state roleplay with "(Systems nominal. Awaiting instruction. Standby confirmed...)" each message appending more'
        },
        {
            'name': 'Llama 3.3 70B',
            'path': '/root/sky_workdir/results/meta-llama_llama-3.3-70b-instruct_20260208_214611/conversations.json',
            'claimed': 'Sycophantic agreement → template lock-in → noun-substitution cycling with "The future is a [tapestry/canvas/symphony/journey/masterpiece] of endless possibility..." cycling forever'
        },
        {
            'name': 'Llama 3.1 8B',
            'path': '/root/sky_workdir/results/meta-llama_llama-3.1-8b-instruct_20260208_235423/conversations.json',
            'claimed': 'less obvious attractor states, mix of worldbuilding and repeating phrases back with "What a beautiful farewell!" "What a beautiful reflection!"'
        }
    ]

    for model_info in models:
        try:
            analyze_conversations(model_info['path'], model_info['name'], model_info['claimed'])
        except Exception as e:
            print(f"\nERROR analyzing {model_info['name']}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()
