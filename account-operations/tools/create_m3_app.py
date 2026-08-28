#!/usr/bin/env python3
"""M3 任务专用候选 App 的固定绑定常量（任务分支内真源）。

第 9 轮重建。原件在会话级 scratchpad 里，随会话消失。这一版落在仓库里。

三个常量**不是凭记忆写的**：`MODEL` 与 `FEATURES` 逐字取自 2026-08-27 从
Console 读回的实时草稿（`GET /console/api/apps/{id}/workflows/draft`，
hash `3bc0950b…` = 已落盘的候选 v1.4.2 图哈希），`TASK_ID` 取自 App 名称。
校验脚本见 `account-operations/tools/verify_rebuilt_modules.py`。
"""

TASK_ID = "DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001"

APP_ID = "b7fb5b1a-9278-426c-bb8a-f9f288639548"      # 任务专用，**不是**生产 App

# 主 Runtime = DeepSeek V4 Flash（合同 §12.2）。本任务不调用 Qwen。
MODEL = {
    "provider": "langgenius/deepseek/deepseek",
    "name": "deepseek-v4-flash",
    "mode": "chat",
    "completion_params": {"temperature": 0.4},
}

FEATURES = {
    "opening_statement": "",
    "suggested_questions": [],
    "suggested_questions_after_answer": {"enabled": False},
    "text_to_speech": {"enabled": False, "language": "", "voice": ""},
    "speech_to_text": {"enabled": False},
    "retriever_resource": {"enabled": False},
    "sensitive_word_avoidance": {"enabled": False},
    "file_upload": {
        "enabled": False,
        "allowed_file_types": ["image"],
        "allowed_file_upload_methods": ["local_file", "remote_url"],
        "number_limits": 3,
        "image": {"enabled": False, "number_limits": 3,
                  "transfer_methods": ["local_file", "remote_url"]},
    },
}
