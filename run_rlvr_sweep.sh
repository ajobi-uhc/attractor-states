#!/bin/bash
set -e

SCRIPT="olmo_local.py"
PYTHON="python"

source .venv/bin/activate

REVISIONS="step_100 step_400 step_750"

for rev in $REVISIONS; do
    echo "========================================"
    echo "Running RLVR revision: $rev"
    echo "========================================"
    $PYTHON $SCRIPT --model allenai/Olmo-3-32B-Think --revision $rev --turns 20 --seeds 6 --max-new-tokens 256
    echo ""
done

# Final model (main branch, no revision)
echo "========================================"
echo "Running RLVR final (main)"
echo "========================================"
$PYTHON $SCRIPT --model allenai/Olmo-3-32B-Think --turns 20 --seeds 6 --max-new-tokens 256
