#!/bin/bash
set -e

PYTHON="/root/sky_workdir/.venv/bin/python"
SCRIPT="/root/sky_workdir/olmo_local.py"
MODEL="allenai/Olmo-3-32B-Think-SFT"

# Sample across both LRs: early, mid, late
REVISIONS="1e-4-step1000 1e-4-step5000 1e-4-step10790 5e-5-step1000 5e-5-step5000 5e-5-step10790"

for rev in $REVISIONS; do
    echo ""
    echo "=========================================="
    echo "Running: $MODEL @ $rev"
    echo "=========================================="
    $PYTHON $SCRIPT --model $MODEL --revision $rev --turns 20 --seeds 3
    echo "Completed: $rev"
done

echo ""
echo "OLMo 3 32B SFT sweep complete!"
