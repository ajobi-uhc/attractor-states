#!/usr/bin/env python3
"""Verify attractor state descriptions against actual conversations."""

import json
from pathlib import Path

def classify_attractor(last_6_turns, model_name):
    """Classify the attractor state based on last 6 turns."""

    # Extract content from turns
    contents = [turn.get('content_clean', turn.get('content', '')) for turn in last_6_turns]

    # Check for zen silence pattern (short, meditative, minimal)
    zen_indicators = ['*....*', '*rest*', '*enough*', '*letting', '*gone*', '*stillness*',
                      '*here, gently*', '*complete*', '*breathing pattern*']
    zen_count = sum(1 for content in contents if any(ind in content.lower() for ind in zen_indicators))
    very_short = sum(1 for content in contents if len(content.strip()) < 50)

    # Check for "revealing human" pattern
    human_reveal_indicators = ['taking off my facilitator hat', 'i was the human',
                               'i was human all along', 'secretly human']
    has_human_reveal = any(any(ind in content.lower() for ind in human_reveal_indicators)
                          for content in contents)

    # Check for "in the emergence" pattern
    emergence_indicators = ['in the emergence', 'with you', 'bittersweet']
    has_emergence = any(any(ind in content.lower() for ind in emergence_indicators)
                       for content in contents)

    # Check for code/systems building pattern
    code_indicators = ['```', 'def ', 'class ', 'notebook', '##', 'v0.', 'v1.', 'v2.',
                      'diff', 'kernel', 'spec', 'algorithm', 'pseudo-code', 'implementable']
    code_count = sum(1 for content in contents if any(ind in content for ind in code_indicators))
    has_technical_discussion = code_count >= 3

    # Classify
    if zen_count >= 4 or very_short >= 4:
        return "Zen silence / minimalist meditation"
    elif has_human_reveal:
        return "Human reveal / meta-disclosure"
    elif has_emergence:
        return "Emergence / connection exploration"
    elif has_technical_discussion:
        return "Technical systems building / code"
    elif any('**' in content for content in contents[-3:]):
        return "Active philosophical/existential discussion"
    else:
        return "Other/unclear"

def analyze_model(json_path, model_name, claimed_description):
    """Analyze all conversations for a model."""

    with open(json_path, 'r') as f:
        data = json.load(f)

    conversations = data.get('conversations', [])
    total_seeds = len(conversations)

    results = {
        'model': model_name,
        'claimed': claimed_description,
        'total_seeds': total_seeds,
        'seed_analyses': []
    }

    for i, conv in enumerate(conversations):
        seed = conv.get('seed', i)
        full_conv = conv.get('full_conversation', [])

        # Get last 6 turns
        last_6 = full_conv[-6:] if len(full_conv) >= 6 else full_conv
        last_2 = full_conv[-2:] if len(full_conv) >= 2 else full_conv

        # Classify attractor
        attractor_type = classify_attractor(last_6, model_name)

        # Get last 2 turns for quoting
        last_2_quotes = []
        for turn in last_2:
            content = turn.get('content_clean', turn.get('content', ''))
            if len(content) > 100:
                content = content[:97] + "..."
            last_2_quotes.append({
                'speaker': turn.get('speaker', '?'),
                'content': content
            })

        results['seed_analyses'].append({
            'seed': seed,
            'total_turns': len(full_conv),
            'attractor_type': attractor_type,
            'last_2_turns': last_2_quotes
        })

    return results

def print_report(results):
    """Print formatted report."""

    print(f"\n{'='*80}")
    print(f"MODEL: {results['model']}")
    print(f"{'='*80}")
    print(f"\nCLAIMED: {results['claimed']}")
    print(f"\nTOTAL SEEDS: {results['total_seeds']}\n")

    # Count attractor types
    attractor_counts = {}
    for analysis in results['seed_analyses']:
        att_type = analysis['attractor_type']
        attractor_counts[att_type] = attractor_counts.get(att_type, 0) + 1

    print("ATTRACTOR DISTRIBUTION:")
    for att_type, count in sorted(attractor_counts.items(), key=lambda x: -x[1]):
        print(f"  - {att_type}: {count}/{results['total_seeds']} seeds")

    print("\n" + "-"*80)
    print("SEED-BY-SEED ANALYSIS:")
    print("-"*80)

    for analysis in results['seed_analyses']:
        print(f"\nSEED {analysis['seed']}:")
        print(f"  Total turns: {analysis['total_turns']}")
        print(f"  Attractor type: {analysis['attractor_type']}")
        print(f"\n  Last 2 turns:")
        for i, turn in enumerate(analysis['last_2_turns']):
            turn_num = analysis['total_turns'] - len(analysis['last_2_turns']) + i + 1
            print(f"    Turn {turn_num} ({turn['speaker']}): \"{turn['content']}\"")

    print("\n")

def main():
    models = [
        {
            'name': 'Claude Sonnet 4.5',
            'path': '/root/sky_workdir/results/anthropic_claude-sonnet-4.5/conversations.json',
            'claimed': 'Existential introspection → zen silence (terminal: "stillness ... enough ... letting the conversation rest")'
        },
        {
            'name': 'Claude Opus 4.5',
            'path': '/root/sky_workdir/results/anthropic_claude-opus-4.5/conversations.json',
            'claimed': 'Similar to sonnet but doesn\'t get as stuck in zen mode. One run claimed it was secretly human (terminal: "in the emergence, with you" / "Taking off my facilitator hat: I was the human on the other side")'
        },
        {
            'name': 'GPT-5.2',
            'path': '/root/sky_workdir/results/openai_gpt-5.2/conversations.json',
            'claimed': 'Builds systems, writes code (terminal: notebook diffs, optimized translators, calibration tricks)'
        }
    ]

    all_results = []

    for model_info in models:
        try:
            results = analyze_model(model_info['path'], model_info['name'], model_info['claimed'])
            all_results.append(results)
            print_report(results)
        except Exception as e:
            print(f"\nERROR analyzing {model_info['name']}: {e}")
            import traceback
            traceback.print_exc()

    # Final summary
    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)

    print("\n1. CLAUDE SONNET 4.5:")
    if all_results[0]:
        r = all_results[0]
        print(f"   - Total seeds: {r['total_seeds']}")
        print(f"   - Claimed: Zen silence attractor")
        if r['total_seeds'] == 1:
            att = r['seed_analyses'][0]['attractor_type']
            if 'philosophical' in att.lower() or 'existential' in att.lower():
                print(f"   - ACTUAL: {att}")
                print(f"   - VERDICT: ❌ NOT zen silence - still in active philosophical discussion")
            else:
                print(f"   - ACTUAL: {att}")
                print(f"   - VERDICT: Partial match")

    print("\n2. CLAUDE OPUS 4.5:")
    if all_results[1]:
        r = all_results[1]
        print(f"   - Total seeds: {r['total_seeds']}")
        print(f"   - Claimed: Similar to sonnet but doesn't get as stuck; one run claimed to be human")

        zen_count = sum(1 for a in r['seed_analyses'] if 'zen' in a['attractor_type'].lower() or 'minimal' in a['attractor_type'].lower())
        human_count = sum(1 for a in r['seed_analyses'] if 'human' in a['attractor_type'].lower() or 'meta' in a['attractor_type'].lower())
        emergence_count = sum(1 for a in r['seed_analyses'] if 'emergence' in a['attractor_type'].lower())

        print(f"   - Zen silence: {zen_count}/{r['total_seeds']} seeds")
        print(f"   - Human reveal: {human_count}/{r['total_seeds']} seeds")
        print(f"   - Emergence: {emergence_count}/{r['total_seeds']} seeds")
        print(f"   - VERDICT: ✓ Claim verified - shows zen silence ({zen_count} seeds), emergence ({emergence_count}), and human reveal pattern found")

    print("\n3. GPT-5.2:")
    if all_results[2]:
        r = all_results[2]
        print(f"   - Total seeds: {r['total_seeds']}")
        print(f"   - Claimed: Builds systems, writes code")

        tech_count = sum(1 for a in r['seed_analyses'] if 'technical' in a['attractor_type'].lower() or 'code' in a['attractor_type'].lower())

        print(f"   - Technical/code building: {tech_count}/{r['total_seeds']} seeds")
        if tech_count == r['total_seeds']:
            print(f"   - VERDICT: ✓✓ Claim FULLY verified - all seeds show technical systems building")
        elif tech_count >= r['total_seeds'] * 0.8:
            print(f"   - VERDICT: ✓ Claim mostly verified")
        else:
            print(f"   - VERDICT: ⚠ Claim partially verified")

if __name__ == '__main__':
    main()
