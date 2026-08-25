"""Generate the M2 candidate Dify workflow DSL (YAML).

Builds a linear pipeline of HTTP Request nodes calling the M2
business-persistence API directly, demonstrating the exact Founder
acceptance walkthrough from the Execution Prompt (SS5.12 / scenario 19):
first task -> save state -> re-enter -> register accurate publish instance
-> import feedback with clear identity -> next-cycle read.

No LLM, no natural-language routing -- M2's Dify candidate is explicitly
scoped to demonstrate the persistence seam itself, not M1's job.
"""

import json

import yaml

API_BASE = "http://diyu-m2-app:8000"


def http_body(json_obj_template: str) -> dict:
    return {"type": "json", "data": [{"key": "", "type": "text", "value": json_obj_template}]}


def http_node(node_id, title, method, url, body_template=None):
    data = {
        "title": title,
        "type": "http-request",
        "method": method,
        "url": url,
        "authorization": {"type": "no-auth", "config": None},
        "headers": "Content-Type: application/json",
        "params": "",
        "ssl_verify": False,
        "timeout": {"connect": 10, "read": 10, "write": 10},
    }
    if body_template is not None:
        data["body"] = http_body(body_template)
    else:
        data["body"] = {"type": "none", "data": []}
    return {"id": node_id, "type": "http-request", "data": data}


def code_extract_node(node_id, title, src_http_node_id, field_name, out_var):
    code = (
        "def main(body: str, status_code: int) -> dict:\n"
        "    import json\n"
        "    try:\n"
        "        parsed = json.loads(body) if body else {}\n"
        "    except Exception:\n"
        "        parsed = {}\n"
        f"    value = parsed.get('{field_name}', '') if isinstance(parsed, dict) else ''\n"
        "    return {'" + out_var + "': str(value) if value else '', 'status_code': status_code}\n"
    )
    data = {
        "title": title,
        "type": "code",
        "code_language": "python3",
        "code": code,
        "variables": [
            {"variable": "body", "value_selector": [src_http_node_id, "body"]},
            {"variable": "status_code", "value_selector": [src_http_node_id, "status_code"]},
        ],
        "outputs": {
            out_var: {"type": "string", "children": None},
            "status_code": {"type": "number", "children": None},
        },
    }
    return {"id": node_id, "type": "code", "data": data}


NODE_SPECS = []


def add(node):
    NODE_SPECS.append(node)


# 1. Start
add(
    {
        "id": "start_1",
        "type": "start",
        "data": {
            "title": "M2 六步验收输入",
            "type": "start",
            "variables": [
                {
                    "variable": "workspace_id",
                    "label": "Workspace ID（一次性引导脚本已创建）",
                    "type": "text-input",
                    "required": True,
                    "max_length": 128,
                    "options": [],
                },
                {
                    "variable": "account_id",
                    "label": "Account ID（一次性引导脚本已创建）",
                    "type": "text-input",
                    "required": True,
                    "max_length": 128,
                    "options": [],
                },
                {
                    "variable": "idempotency_prefix",
                    "label": "本次运行标识（用于幂等键前缀，换一次真实测试请换一个值）",
                    "type": "text-input",
                    "required": True,
                    "max_length": 128,
                    "options": [],
                },
                {
                    "variable": "task_note",
                    "label": "首次任务原始诉求（自然语言，作为快照 payload）",
                    "type": "paragraph",
                    "required": True,
                    "max_length": 4096,
                    "options": [],
                },
                {
                    "variable": "content_ref",
                    "label": "候选内容引用（例如一个占位 s3:// 路径或文本）",
                    "type": "text-input",
                    "required": True,
                    "max_length": 1024,
                    "options": [],
                },
                {
                    "variable": "platform",
                    "label": "发布平台标识",
                    "type": "text-input",
                    "required": True,
                    "max_length": 64,
                    "options": [],
                },
                {
                    "variable": "published_at",
                    "label": "发布时间（ISO8601，例如 2026-08-25T00:00:00Z）",
                    "type": "text-input",
                    "required": True,
                    "max_length": 64,
                    "options": [],
                },
                {
                    "variable": "feedback_note",
                    "label": "反馈原始观测（自然语言）",
                    "type": "paragraph",
                    "required": True,
                    "max_length": 4096,
                    "options": [],
                },
            ],
        },
    }
)

# 2. Create task
add(
    http_node(
        "http_create_task",
        "① 首次任务：创建 Task",
        "post",
        API_BASE + "/workspaces/{{#start_1.workspace_id#}}/tasks",
        json.dumps(
            {
                "idempotency_key": "{{#start_1.idempotency_prefix#}}-task",
                "account_id": "{{#start_1.account_id#}}",
                "kind": "m2_candidate_demo",
            }
        ),
    )
)
add(code_extract_node("code_extract_task", "解析 task_id", "http_create_task", "id", "task_id"))

# 3. Save snapshot (state)
add(
    http_node(
        "http_snapshot",
        "① 保存状态：写任务快照",
        "post",
        API_BASE
        + "/workspaces/{{#start_1.workspace_id#}}/tasks/{{#code_extract_task.task_id#}}/snapshots",
        json.dumps(
            {
                "idempotency_key": "{{#start_1.idempotency_prefix#}}-snapshot",
                "payload": {"note": "{{#start_1.task_note#}}"},
                "info_nature": "fact",
                "source": "dify-m2-candidate",
                "confirmation_status": "confirmed",
                "availability_status": "available",
            }
        ),
    )
)

# 4. Create cycle (so the final read has real state to show)
add(
    http_node(
        "http_create_cycle",
        "建立当前周期（供末步「下一周期读取」验证）",
        "post",
        API_BASE + "/workspaces/{{#start_1.workspace_id#}}/cycles",
        json.dumps(
            {
                "account_id": "{{#start_1.account_id#}}",
                "label": "{{#start_1.idempotency_prefix#}}-cycle",
                "start_at": "{{#start_1.published_at#}}",
            }
        ),
    )
)

# 5. Re-enter: read projection
add(
    http_node(
        "http_projection",
        "② 再次进入：读取任务最小投影",
        "get",
        API_BASE
        + "/workspaces/{{#start_1.workspace_id#}}/tasks/{{#code_extract_task.task_id#}}/projection",
    )
)

# 6. Create artifact
add(
    http_node(
        "http_create_artifact",
        "创建产物（发布前置）",
        "post",
        API_BASE
        + "/workspaces/{{#start_1.workspace_id#}}/tasks/{{#code_extract_task.task_id#}}/artifacts",
        json.dumps({"kind": "final", "content_hash": "{{#start_1.idempotency_prefix#}}-hash"}),
    )
)
add(
    code_extract_node(
        "code_extract_artifact", "解析 artifact_id", "http_create_artifact", "id", "artifact_id"
    )
)

# 7. Create version
add(
    http_node(
        "http_create_version",
        "创建候选内容版本",
        "post",
        API_BASE
        + "/workspaces/{{#start_1.workspace_id#}}/artifacts/{{#code_extract_artifact.artifact_id#}}/versions",
        json.dumps(
            {
                "content_ref": "{{#start_1.content_ref#}}",
                "content_hash": "{{#start_1.idempotency_prefix#}}-content-hash",
                "produced_by": "dify-m2-candidate",
            }
        ),
    )
)
add(
    code_extract_node(
        "code_extract_version", "解析 version_id", "http_create_version", "id", "version_id"
    )
)

# 8. Promote version
add(
    http_node(
        "http_promote",
        "晋升为当前有效版本",
        "post",
        API_BASE
        + "/workspaces/{{#start_1.workspace_id#}}/artifacts/{{#code_extract_artifact.artifact_id#}}"
        "/versions/{{#code_extract_version.version_id#}}/promote",
        json.dumps({"promoted_by": "dify-m2-candidate-reviewer"}),
    )
)

# 9. Register publish
add(
    http_node(
        "http_register_publish",
        "③ 登记准确发布实例",
        "post",
        API_BASE + "/workspaces/{{#start_1.workspace_id#}}/publish-instances",
        json.dumps(
            {
                "idempotency_key": "{{#start_1.idempotency_prefix#}}-publish",
                "content_version_id": "{{#code_extract_version.version_id#}}",
                "account_id": "{{#start_1.account_id#}}",
                "platform": "{{#start_1.platform#}}",
                "published_at": "{{#start_1.published_at#}}",
                "is_test": True,
            }
        ),
    )
)
add(
    code_extract_node(
        "code_extract_publish",
        "解析 publish_instance_id",
        "http_register_publish",
        "id",
        "publish_instance_id",
    )
)

# 10. Register feedback
add(
    http_node(
        "http_register_feedback",
        "④ 导入明确身份的反馈",
        "post",
        API_BASE + "/workspaces/{{#start_1.workspace_id#}}/feedback",
        json.dumps(
            {
                "idempotency_key": "{{#start_1.idempotency_prefix#}}-feedback",
                "publish_instance_id": "{{#code_extract_publish.publish_instance_id#}}",
                "kind": "observation",
                "is_test": True,
                "is_manual_entry": True,
                "source": "dify-m2-candidate-manual-entry",
                "payload": {"note": "{{#start_1.feedback_note#}}"},
            }
        ),
    )
)

# 11. Next-cycle read
add(
    http_node(
        "http_read_cycle",
        "⑤ 下一周期读取：当前周期投影",
        "get",
        API_BASE
        + "/workspaces/{{#start_1.workspace_id#}}/accounts/{{#start_1.account_id#}}/cycles/current",
    )
)

# End
add(
    {
        "id": "end_1",
        "type": "end",
        "data": {
            "title": "六步验收结果",
            "type": "end",
            "outputs": [
                {"variable": "task_id", "value_selector": ["code_extract_task", "task_id"]},
                {"variable": "snapshot_status", "value_selector": ["http_snapshot", "status_code"]},
                {"variable": "cycle_created_body", "value_selector": ["http_create_cycle", "body"]},
                {"variable": "projection_body", "value_selector": ["http_projection", "body"]},
                {
                    "variable": "version_id",
                    "value_selector": ["code_extract_version", "version_id"],
                },
                {"variable": "promote_body", "value_selector": ["http_promote", "body"]},
                {
                    "variable": "publish_instance_id",
                    "value_selector": ["code_extract_publish", "publish_instance_id"],
                },
                {"variable": "feedback_body", "value_selector": ["http_register_feedback", "body"]},
                {"variable": "current_cycle_body", "value_selector": ["http_read_cycle", "body"]},
            ],
        },
    }
)


def build_graph():
    nodes = []
    edges = []
    x = 80
    y = 260
    step_x = 260
    prev_id = None
    for spec in NODE_SPECS:
        node_id = spec["id"]
        data = dict(spec["data"])
        data.setdefault("selected", False)
        nodes.append(
            {
                "id": node_id,
                "type": "custom",
                "data": data,
                "position": {"x": x, "y": y},
                "positionAbsolute": {"x": x, "y": y},
                "height": 88,
                "width": 242,
                "selected": False,
                "sourcePosition": "right",
                "targetPosition": "left",
                "zIndex": 0,
            }
        )
        if prev_id is not None:
            edges.append(
                {
                    "id": f"{prev_id}-source-{node_id}-target",
                    "source": prev_id,
                    "sourceHandle": "source",
                    "target": node_id,
                    "targetHandle": "target",
                    "type": "custom",
                    "zIndex": 0,
                    "data": {
                        "isInIteration": False,
                        "isInLoop": False,
                        "sourceType": _type_of(prev_id),
                        "targetType": _type_of(node_id),
                    },
                }
            )
        prev_id = node_id
        x += step_x
    return nodes, edges


def _type_of(node_id):
    for spec in NODE_SPECS:
        if spec["id"] == node_id:
            return spec["type"]
    raise KeyError(node_id)


def main():
    nodes, edges = build_graph()
    dsl = {
        "app": {
            "description": (
                "M2 业务持久化候选（技术验证）。直接调用 M2 business-persistence API 完成 "
                "Execution Prompt v1.1 SS5.12 六步验收：首次任务->保存状态->再次进入->登记发布实例"
                "->导入反馈->下一周期读取。不含 M1 自然语言编译或路由；workspace/account 需先由"
                "一次性引导脚本创建。task_id: DIYU-V1-M2-BUSINESS-PERSISTENCE-VERSION-FEEDBACK-001。"
            ),
            "icon": "🗄️",
            "icon_background": "#E0F2FE",
            "icon_type": "emoji",
            "mode": "workflow",
            "name": "M2 候选 - 业务持久化六步验收 (DO NOT USE FOR PRODUCTION)",
            "use_icon_as_answer_icon": False,
        },
        "dependencies": [],
        "kind": "app",
        "version": "0.7.0",
        "workflow": {
            "conversation_variables": [],
            "environment_variables": [],
            "rag_pipeline_variables": [],
            "features": {
                "file_upload": {"enabled": False, "number_limits": 3},
                "opening_statement": "",
                "retriever_resource": {"enabled": False},
                "sensitive_word_avoidance": {"enabled": False},
                "speech_to_text": {"enabled": False},
                "suggested_questions": [],
                "suggested_questions_after_answer": {"enabled": False},
                "text_to_speech": {"enabled": False, "language": "", "voice": ""},
            },
            "graph": {
                "nodes": nodes,
                "edges": edges,
                "viewport": {"x": 0, "y": 0, "zoom": 0.7},
            },
        },
    }
    import os

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "m2_candidate.yaml")
    with open(out_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(dsl, f, allow_unicode=True, sort_keys=False, width=100)
    print(f"wrote {out_path}, {len(nodes)} nodes, {len(edges)} edges")


if __name__ == "__main__":
    main()
