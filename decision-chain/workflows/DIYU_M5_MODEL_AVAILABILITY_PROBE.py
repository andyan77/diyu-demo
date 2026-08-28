#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""模型可用性探针。只用来回答一个问题：目标 provider 现在能不能调用。

**不参与任何验收，不产生任何 PASS。** 存在的理由是模型不可用时合同判 BLOCKED，
而「现在还 BLOCKED 吗」必须靠实际调用来回答，不能靠等和猜。
单次调用 max_tokens=32，成本可忽略。
"""
import importlib.util, json, os, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
_p = os.path.join(ROOT, "account-operations", "tools", "dify_client.py")
_s = importlib.util.spec_from_file_location("dc", _p)
DC = importlib.util.module_from_spec(_s); _s.loader.exec_module(DC)
ENV = "/home/faye/diyu-demo-worktrees/m3-account-content-operator-v1/.env"

PROVIDERS = {
    "deepseek": ("langgenius/deepseek/deepseek", "deepseek-v4-flash",
                 "DIYU M5 PROBE · deepseek 可用性"),
    "qwen": ("langgenius/tongyi/tongyi", "qwen3.8-max",
             "DIYU M5 PROBE · 模型可用性探针（一次性）"),
}
FEAT = {"file_upload": {"enabled": False, "allowed_file_types": ["image"],
                        "allowed_file_extensions": [".JPG"],
                        "allowed_file_upload_methods": ["local_file"],
                        "image": {"enabled": False, "number_limits": 3,
                                  "transfer_methods": ["local_file"]}, "number_limits": 3},
        "opening_statement": "", "retriever_resource": {"enabled": False},
        "sensitive_word_avoidance": {"enabled": False}, "speech_to_text": {"enabled": False},
        "suggested_questions": [], "suggested_questions_after_answer": {"enabled": False},
        "text_to_speech": {"enabled": False, "language": "", "voice": ""}}


def _graph(provider, model):
    def n(i, pos, data):
        return {"id": i, "type": "custom", "position": pos, "width": 244, "height": 100,
                "selected": False, "data": data}
    def e(a, b, at, bt):
        return {"id": "%s-%s" % (a, b), "type": "custom", "source": a, "target": b,
                "sourceHandle": "source", "targetHandle": "target", "zIndex": 0,
                "data": {"sourceType": at, "targetType": bt, "isInIteration": False}}
    return {"nodes": [
        n("p_start", {"x": 80, "y": 100}, {"type": "start", "title": "输入", "variables": [
            {"variable": "q", "label": "q", "type": "text-input", "required": False,
             "max_length": 50, "options": []}]}),
        n("p_llm", {"x": 380, "y": 100}, {
            "type": "llm", "title": "探针",
            "model": {"mode": "chat", "name": model, "provider": provider,
                      "completion_params": {"max_tokens": 32}},
            "vision": {"enabled": False}, "context": {"enabled": False, "variable_selector": []},
            "prompt_template": [{"role": "user", "id": "u1", "text": "只回答两个字：可用"}]}),
        n("p_end", {"x": 680, "y": 100}, {"type": "end", "title": "结束", "outputs": [
            {"variable": "text", "value_selector": ["p_llm", "text"]}]})],
        "edges": [e("p_start", "p_llm", "start", "llm"), e("p_llm", "p_end", "llm", "end")],
        "viewport": {"x": 0, "y": 0, "zoom": 0.9}}


def ensure(c, which):
    provider, model, name = PROVIDERS[which]
    st, apps = c.call("GET", "/console/api/apps?page=1&limit=100")
    hit = [a for a in apps["data"] if a.get("name") == name]
    if hit:
        return hit[0]["id"]
    st, app = c.call("POST", "/console/api/apps", body={
        "name": name, "mode": "workflow", "icon_type": "emoji", "icon": "🔌",
        "icon_background": "#EEEEEE",
        "description": "只用于确认 provider 是否可调用，不参与任何验收"})
    app_id = app["id"]
    st, cur = c.call("GET", "/console/api/apps/%s/workflows/draft" % app_id)
    c.call("POST", "/console/api/apps/%s/workflows/draft" % app_id,
           body={"graph": _graph(provider, model), "features": FEAT,
                 "hash": cur.get("hash") if st == 200 else None,
                 "environment_variables": [], "conversation_variables": []}, timeout=180)
    c.call("POST", "/console/api/apps/%s/workflows/publish" % app_id,
           body={"marked_name": "probe"}, timeout=180)
    return app_id


def check(which="deepseek"):
    c = DC.Console(env=DC.load_env(ENV))
    app_id = ensure(c, which)
    r = DC.run_workflow(c.app_api_key(app_id), {"q": "x"}, user="m5-probe")
    b = r.get("body") or {}; d = b.get("data") or {}
    err = str(d.get("error") or b.get("error") or "")
    ok = d.get("status") == "succeeded"
    reason = ("OK" if ok else
              ("INSUFFICIENT_BALANCE" if "Insufficient Balance" in err else
               ("TRANSPORT" if ("SSL" in err or "Server Unavailable" in err) else "OTHER")))
    return ok, reason, err[:300]


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "deepseek"
    ok, reason, err = check(which)
    print(json.dumps({"provider": which, "available": ok, "reason": reason, "error": err},
                     ensure_ascii=False))
    sys.exit(0 if ok else 1)
