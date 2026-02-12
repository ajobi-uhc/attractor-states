#!/bin/bash
set -e

PYTHON="/root/sky_workdir/.venv/bin/python"
SCRIPT="/root/sky_workdir/olmo_local.py"
COMMON="--turns 30 --max-new-tokens 512"

echo "=== Resuming sweep (thinking stripped) ==="
START=$(date +%s)

# --- SFT step 10790 (crashed here last time) ---
echo -e "\n>>> SFT 5e-5 step 10790"
$PYTHON $SCRIPT --model allenai/Olmo-3-32B-Think-SFT --revision "5e-5-step10790" $COMMON

# --- DPO (main) ---
echo -e "\n>>> DPO (main)"
$PYTHON $SCRIPT --model allenai/Olmo-3-32B-Think-DPO $COMMON

# --- RLVR 3.1 checkpoints ---
for step in 0050 0500 1200 2300; do
    echo -e "\n>>> RLVR 3.1 step ${step}"
    $PYTHON $SCRIPT --model allenai/Olmo-3.1-32B-Think --revision "step_${step}" $COMMON
done

# --- RLVR 3.1 final (main) ---
echo -e "\n>>> RLVR 3.1 final (main)"
$PYTHON $SCRIPT --model allenai/Olmo-3.1-32B-Think $COMMON

END=$(date +%s)
echo -e "\n=== Done! Total: $((END - START))s ==="
