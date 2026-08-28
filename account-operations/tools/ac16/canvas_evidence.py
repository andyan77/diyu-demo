#!/usr/bin/env python3
"""AC-16 缺口二：**浏览器渲染画布**实证。

Prompt §12.3 写的是「Dify 交付真相是当前草稿图、实际配置和浏览器渲染画布，不是单次
API 运行历史」。前两样第 3 轮就核过了，第三样一直挂着 `NOT_VERIFIED`，理由是
「本机无 playwright / chromium，不具备浏览器自动化能力」——这句话只有后半截是真的：
chromium 二进制一直在 playwright 缓存里，缺的是一个 WebSocket 客户端（见 cdp.py）。

这里做的事：用真实登录态打开画布 URL，等 ReactFlow 渲染完，然后
  1. 从**渲染出来的 DOM**里数节点与连线，读每个节点显示的标题；
  2. 反搜画布上有没有 http_request / tool 节点（AC-13 结构半的画布版）；
  3. 点开 LLM 节点，看它的提示词面板上真的挂着 SKILL 正文；
  4. 整页截图落盘。
读的是浏览器渲染结果，不是我刚 POST 上去的那份 JSON。
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.dirname(HERE)
sys.path.insert(0, SCRATCH)
sys.path.insert(0, HERE)
from dify_client import Console, WORKTREE          # noqa: E402
from cdp import Browser                            # noqa: E402

APP = "b7fb5b1a-9278-426c-bb8a-f9f288639548"
OUT = os.path.join(WORKTREE, "account-operations/evidence/ep24-ac16-canvas-and-prompt")
EXPECTED_TITLES = ["本轮投影输入", "单账号持续运营决策", "必填项闸门（确定性检查）",
                   "按闸门报告补齐缺失项", "确定性取稿",
                   "闸门闭合复检与周期状态承载决定", "运营判断与内容任务候选"]

READ_NODES = """
(() => {
  const ns = [...document.querySelectorAll('.react-flow__node')];
  return JSON.stringify(ns.map(n => ({
    id: n.getAttribute('data-id'),
    text: (n.innerText || '').split('\\n').filter(Boolean).slice(0,2).join(' | ')
  })));
})()
"""


def main():
    os.makedirs(OUT, exist_ok=True)
    c = Console()                       # 真实登录，拿到 console cookie
    b = Browser(width=2560, height=1600)
    rep = {"what": "AC-16 缺口二 · 浏览器渲染画布实证", "app_id": APP,
           "browser": "chromium-1234（playwright 缓存里的二进制），CDP over 自写 WebSocket"}
    try:
        b.goto("http://localhost/signin", settle=2)
        b.ws.call("Network.setCookies", {"cookies": [
            {"name": k, "value": v, "domain": "localhost", "path": "/"}
            for k, v in c.jar.items()]})
        b.goto(f"http://localhost/app/{APP}/workflow", settle=6)
        rep["url"] = b.ws.evaluate("location.href")

        n = b.wait_for("document.querySelectorAll('.react-flow__node').length", timeout=120)
        e = b.ws.evaluate("document.querySelectorAll('.react-flow__edge').length")
        nodes = json.loads(b.ws.evaluate(READ_NODES) or "[]")
        rep["rendered"] = {"nodes": n, "edges": e, "node_list": nodes}

        body = b.ws.evaluate("document.body.innerText") or ""
        rep["canvas_reverse_search"] = {
            "http_request 出现在画布上": "HTTP 请求" in body or "http_request" in body.lower(),
            "tool 节点出现在画布上": "react-flow__node-tool" in (
                b.ws.evaluate("document.body.innerHTML.slice(0,400000)") or ""),
            "画布 HTML 里出现工具节点类名": "react-flow__node-tool" in (
                b.ws.evaluate("document.body.innerHTML.slice(0,400000)") or ""),
        }
        rep["titles_all_present"] = all(
            any(t in (x["text"] or "") for x in nodes) for t in EXPECTED_TITLES)
        rep["titles_expected"] = EXPECTED_TITLES

        shot = os.path.join(OUT, "canvas_v14.png")
        rep["screenshot"] = {"file": "canvas_v14.png", "bytes": b.screenshot(shot)}
        with open(shot, "rb") as f:
            rep["screenshot"]["sha256"] = hashlib.sha256(f.read()).hexdigest()

        # 点开 LLM 节点，证明画布上那个节点真的挂着 SKILL 正文
        clicked = b.ws.evaluate("""
          (() => {
            const n = [...document.querySelectorAll('.react-flow__node')]
              .find(x => (x.innerText||'').includes('单账号持续运营决策'));
            if (!n) return false;
            n.dispatchEvent(new MouseEvent('click', {bubbles:true, cancelable:true, view:window}));
            return true;
          })()""")
        time.sleep(4)
        panel = b.ws.evaluate("document.body.innerText") or ""
        rep["llm_panel"] = {
            "clicked": clicked,
            "面板里出现 SKILL 的首行标识": "operating-one-account" in panel,
            "面板里出现判断主链小节名": "判断主链" in panel or "核对三类产能" in panel,
            "面板里出现本轮新增的判据": "删掉它会丢什么" in panel or "推翻信号" in panel,
            "panel_chars": len(panel),
        }
        shot2 = os.path.join(OUT, "canvas_v14_llm_panel.png")
        rep["screenshot_panel"] = {"file": "canvas_v14_llm_panel.png",
                                   "bytes": b.screenshot(shot2)}
        with open(shot2, "rb") as f:
            rep["screenshot_panel"]["sha256"] = hashlib.sha256(f.read()).hexdigest()
    finally:
        b.close()

    rep["verdict"] = {
        "画布渲染出 7 个节点": rep.get("rendered", {}).get("nodes") == 7,
        "画布渲染出 6 条连线": rep.get("rendered", {}).get("edges") == 6,
        "七个节点标题全部出现": rep.get("titles_all_present", False),
        "画布上无 http_request / tool 节点": not any(
            rep.get("canvas_reverse_search", {}).get(k)
            for k in ("http_request 出现在画布上", "tool 节点出现在画布上")),
        "LLM 节点面板上挂着 SKILL 正文": all(
            rep.get("llm_panel", {}).get(k) for k in
            ("面板里出现 SKILL 的首行标识", "面板里出现判断主链小节名", "面板里出现本轮新增的判据")),
    }
    rep["all_pass"] = all(rep["verdict"].values())
    with open(os.path.join(OUT, "CANVAS_EVIDENCE.json"), "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=2)
    print(json.dumps(rep, ensure_ascii=False, indent=2)[:3000])
    return 0 if rep["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
