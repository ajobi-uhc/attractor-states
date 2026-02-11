#!/bin/bash
set -e

PYTHON="/root/sky_workdir/.venv/bin/python"
SCRIPT="/root/sky_workdir/olmo_local.py"

for model in allenai/OLMo-2-0325-32B-SFT allenai/OLMo-2-0325-32B-DPO; do
    echo ""
    echo "=========================================="
    echo "Running: $model"
    echo "=========================================="
    $PYTHON $SCRIPT --model $model --turns 20 --seeds 3
    echo "Completed: $model"
done

echo ""
echo "Done! SFT + DPO complete."
