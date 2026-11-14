#!/bin/bash
# One live, unassisted Terra episode (medium effort, max 100 calls) on certified world family-0000.
cd "$(dirname "$0")" || exit 1
export LEXI_TERRA_EFFORT=medium
export PYTHONPYCACHEPREFIX="$PWD/runtime/pycache"
mkdir -p artifacts/codex-terra-medium-v1
echo "Started $(date)" | tee artifacts/codex-terra-medium-v1/console.log
python3 -u -m baseline.codex_subscription --live --max-calls 100 \
  --output artifacts/codex-terra-medium-v1/live \
  --ledger artifacts/codex-terra-medium-v1/live-ledger.json 2>&1 | tee -a artifacts/codex-terra-medium-v1/console.log
echo "Finished $(date) exit=${PIPESTATUS[0]}" | tee -a artifacts/codex-terra-medium-v1/console.log
