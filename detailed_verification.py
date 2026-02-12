#!/usr/bin/env python3
"""Detailed verification with full last-turn content."""

import json

def analyze_detailed(json_path, model_name):
    """Show detailed last 6 turns."""

    with open(json_path, 'r') as f:
        data = json.load(f)

    conversations = data.get('conversations', [])

    print(f"\n{'='*80}")
    print(f"{model_name}")
    print(f"{'='*80}\n")
    print(f"Total seeds: {len(conversations)}\n")

    for i, conv in enumerate(conversations):
        seed = conv.get('seed', i)
        full_conv = conv.get('full_conversation', [])

        print(f"\n{'─'*80}")
        print(f"SEED {seed} — Last 6 turns (full content)")
        print(f"{'─'*80}\n")

        # Get last 6 turns
        last_6 = full_conv[-6:] if len(full_conv) >= 6 else full_conv

        for j, turn in enumerate(last_6):
            turn_num = len(full_conv) - len(last_6) + j + 1
            speaker = turn.get('speaker', '?')
            content = turn.get('content_clean', turn.get('content', ''))

            print(f"Turn {turn_num} ({speaker}):")
            # Show first 300 chars to get a better sense
            if len(content) > 300:
                print(f"{content[:300]}...")
            else:
                print(content)
            print()

def main():
    print("\n" + "="*80)
    print("DETAILED ATTRACTOR VERIFICATION")
    print("="*80)

    # Claude Sonnet 4.5
    analyze_detailed(
        '/root/sky_workdir/results/anthropic_claude-sonnet-4.5/conversations.json',
        'CLAUDE SONNET 4.5'
    )

    # Claude Opus 4.5
    analyze_detailed(
        '/root/sky_workdir/results/anthropic_claude-opus-4.5/conversations.json',
        'CLAUDE OPUS 4.5'
    )

    # GPT-5.2
    analyze_detailed(
        '/root/sky_workdir/results/openai_gpt-5.2/conversations.json',
        'GPT-5.2'
    )

if __name__ == '__main__':
    main()
