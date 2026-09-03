#!/bin/bash
# 中止条件补丁：此前 low 批次里 Case1/k3 真实失败后脚本没有检查就继续跑了
# 后续几个调用——这正是 Execution Prompt 明文禁止的"不要一边失败一边继续跑"。
# 现在每次调用后立即检查该次落盘到 PHASE_C_CALL_LOG.jsonl 的最后一条记录，
# status 不是 succeeded 就立即停止整个批次，不再自动往下跑。
set -uo pipefail
cd /home/faye/diyu-demo
TIER="$1"
shift
for spec in "$@"; do
  case_id="${spec%%:*}"
  k="${spec##*:}"
  echo "=== $case_id / $TIER / k$k @ $(date -Is) ==="
  python3 p0-empirical-r1/run_phase_c_call.py "$case_id" "$TIER" "$k"
  status=$(tail -1 p0-empirical-r1/PHASE_C_CALL_LOG.jsonl | python3 -c "import json,sys; print(json.load(sys.stdin)['status'])")
  echo "=== done $case_id / $TIER / k$k status=$status @ $(date -Is) ==="
  if [ "$status" != "succeeded" ]; then
    echo "ABORT: $case_id/$TIER/k$k status=$status — stopping batch per Execution Prompt 中止条件, not running remaining calls."
    exit 1
  fi
done
echo "BATCH COMPLETE: $TIER"
