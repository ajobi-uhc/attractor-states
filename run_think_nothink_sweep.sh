#!/bin/bash
set -e

PYTHON="/root/sky_workdir/.venv/bin/python"
SCRIPT="/root/sky_workdir/olmo_local.py"
COMMON="--turns 30 --max-new-tokens 512"

echo "=== OLMo 3.1 32B Think sweep (thinking stripped) ==="
START=$(date +%s)

# --- SFT checkpoints (lr=5e-5): early, mid, late ---
for step in 1000 3000 6000 10790; do
    echo -e "\n>>> SFT 5e-5 step ${step}"
    $PYTHON $SCRIPT --model allenai/Olmo-3-32B-Think-SFT --revision "5e-5-step${step}" $COMMON
done

# --- DPO (only main) ---
echo -e "\n>>> DPO (main)"
$PYTHON $SCRIPT --model allenai/Olmo-3-32B-Think-DPO $COMMON

# --- RLVR 3.1: sample across the full trajectory ---
for step in 0050 0500 1200 2300; do
    echo -e "\n>>> RLVR 3.1 step ${step}"
    $PYTHON $SCRIPT --model allenai/Olmo-3.1-32B-Think --revision "step_${step}" $COMMON
done

# --- RLVR 3.1 final (main) ---
echo -e "\n>>> RLVR 3.1 final (main)"
$PYTHON $SCRIPT --model allenai/Olmo-3.1-32B-Think $COMMON

END=$(date +%s)
echo -e "\n=== Done! Total: $((END - START))s ==="
echo "Results in: results_nothink/"
