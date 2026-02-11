#!/bin/bash
set -e

PYTHON="/root/sky_workdir/.venv/bin/python"
SCRIPT="/root/sky_workdir/olmo_local.py"
MODEL="allenai/Olmo-3-32B-Think-SFT"

REVISIONS="5e-5-step1000 5e-5-step3000 5e-5-step6000 5e-5-step9000 5e-5-step10790"

for rev in $REVISIONS; do
    echo ""
    echo "=========================================="
    echo "Running extra seeds: $MODEL @ $rev"
    echo "=========================================="
    $PYTHON $SCRIPT --model $MODEL --revision $rev --turns 20 --seeds 6 --max-new-tokens 256
    echo "Completed: $rev"
done

echo ""
echo "Done!"
