#!/bin/bash
set -e

PYTHON="/root/sky_workdir/.venv/bin/python"
SCRIPT="/root/sky_workdir/olmo_local.py"

# Sample checkpoints across SFT training: early, early-mid, mid, mid-late, late, final
STEPS="step5000 step10000 step20000 step30000 step43000"

for step in $STEPS; do
    echo ""
    echo "=========================================="
    echo "Running checkpoint: $step"
    echo "=========================================="
    $PYTHON $SCRIPT --model allenai/Olmo-3-7B-Think-SFT --revision $step --turns 20 --seeds 3
    echo "Completed: $step"
done

echo ""
echo "All checkpoints complete!"
