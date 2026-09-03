#!/bin/bash
set -uo pipefail
cd /home/faye/diyu-demo
TIER="$1"
shift
for spec in "$@"; do
  case_id="${spec%%:*}"
  k="${spec##*:}"
  echo "=== $case_id / $TIER / k$k @ $(date -Is) ==="
  python3 p0-empirical-r1/run_phase_c_call.py "$case_id" "$TIER" "$k"
  echo "=== done $case_id / $TIER / k$k @ $(date -Is) ==="
done
echo "BATCH COMPLETE: $TIER"
