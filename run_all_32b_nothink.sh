#!/bin/bash
set -e

PYTHON="/root/sky_workdir/.venv/bin/python"
SCRIPT="/root/sky_workdir/olmo_local.py"
COMMON="--turns 20 --seeds 6 --max-new-tokens 512"

echo "============================================"
echo "OLMo3 32B full sweep — thinking stripped"
echo "============================================"
START=$(date +%s)

# --- Base model (main branch) ---
echo -e "\n>>> Base: Olmo-3-32B-Think (main)"
$PYTHON $SCRIPT --model allenai/Olmo-3-32B-Think $COMMON

# --- DPO ---
echo -e "\n>>> DPO: Olmo-3-32B-Think-DPO"
$PYTHON $SCRIPT --model allenai/Olmo-3-32B-Think-DPO $COMMON

# --- SFT checkpoints (lr 5e-5) ---
for step in 1000 3000 6000 9000 10790; do
    echo -e "\n>>> SFT: 5e-5-step${step}"
    $PYTHON $SCRIPT --model allenai/Olmo-3-32B-Think-SFT --revision "5e-5-step${step}" $COMMON
done

# --- RLVR checkpoints ---
for step in 100 400 750; do
    echo -e "\n>>> RLVR: step_${step}"
    $PYTHON $SCRIPT --model allenai/Olmo-3-32B-Think --revision "step_${step}" $COMMON
done

END=$(date +%s)
echo ""
echo "============================================"
echo "All done! Total time: $((END - START))s"
echo "Results in: results_nothink/"
echo "============================================"
