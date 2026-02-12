#!/bin/bash
set -e

PYTHON="/root/sky_workdir/.venv/bin/python"
SCRIPT="/root/sky_workdir/olmo_local.py"
COMMON="--turns 20 --max-new-tokens 512"

echo "=== OLMo 3.1 32B Instruct pipeline sweep ==="
START=$(date +%s)

echo -e "\n>>> Phase 1: SFT"
$PYTHON $SCRIPT --model allenai/Olmo-3.1-32B-Instruct-SFT $COMMON

echo -e "\n>>> Phase 2: DPO"
$PYTHON $SCRIPT --model allenai/Olmo-3.1-32B-Instruct-DPO $COMMON

echo -e "\n>>> Phase 3: RLVR (final)"
$PYTHON $SCRIPT --model allenai/Olmo-3.1-32B-Instruct $COMMON

END=$(date +%s)
echo -e "\n=== Done! Total: $((END - START))s ==="
echo "Results in: results_nothink/"
