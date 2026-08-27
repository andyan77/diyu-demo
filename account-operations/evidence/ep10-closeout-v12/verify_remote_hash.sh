#!/usr/bin/env bash
# AC-20 远端完整哈希：一条命令重验。零参数，只读。
set -euo pipefail
BR="task/m3-account-content-operator-v1"
L=$(git rev-parse HEAD)
R=$(git ls-remote origin "refs/heads/$BR" | cut -f1)
echo "local  HEAD : $L"
echo "remote $BR : $R"
if [ "$L" = "$R" ]; then echo "EQUAL"; else echo "DIFFERENT —— 本地有未推送的提交，或远端被别处推进过"; exit 1; fi
