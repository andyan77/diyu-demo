#!/usr/bin/env python3
"""载体 v1.4：把第 7 轮查实的 D-1/D-3/D-2 与 AC-09/AC-14/AC-18 的修复一起部署进候选 App。

图形状不变（7 节点 6 边），改的是 `gate_v13/` 里那三份共用源码与 `SKILL.md`：
  D-1 模型本轮声明过的持续位在补齐之后消失 ⇒ 义务集从「输入里的位」扩到「输入 ∪ 已声明」
  D-3 补齐节点代写 `POS ::` 机器行 ⇒ 代写的行剥掉再复算，判据重新落回模型
  D-2 G-4 改成「没有周期的数字不是速率主张」，并加谓语式与否定守卫（REBIND_005）
  AC-09 外部市场资料为空不得停摆、不得编造持续位（示例编号不再是可抄的 POS-A/POS-B）
  AC-14 事实确认人不许静默留空
  AC-18 阶段推翻信号／删掉会丢什么／探索停止条件／反馈不授权什么／最可能错的那一步

原 v1.2 说明（图与节点职责不变，保留）：把 v1.1 闸门实测出的缺陷 A/B/D/E 与链式投影缺陷一起修进候选 App。

图形状不变（7 节点 6 边），改的是三个代码节点的实现、补齐节点的职责边界，
以及新增两个输出字段（周期状态承载决定与拒绝理由）。

四条修复面：
  A 最低实质产出硬门，硬失败**不进补齐**（补齐不许无中生有写交付物）；
  B 能从输入算的触发条件由代码算，算不出的自报缺失或与输入冲突时 fail-closed；
  D 内部标签整族移出用户可见正文，改为正文之后由代码剥离的审计块；
  E 必填项改为"锚定行必须逐字指回正文里互不重叠的实质文字"，裸标签/空洞/装饰全被覆盖。
外加 F：投影前后关键对象一致性检查 + 周期状态承载决定。
"""
import json
import os
import sys

SCRATCH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # scratchpad/m3
sys.path.insert(0, SCRATCH)
from dify_client import Console, read, WORKTREE  # noqa: E402
from create_m3_app import MODEL, FEATURES, TASK_ID  # noqa: E402

# 节点代码的唯一真源是仓库里的 gate_v13/，不是 scratch 副本——
# 上一轮出过一次「部署的和仓库里的不是同一份」的事故，源头钉在仓库侧就不会再有。
HERE = os.path.join(WORKTREE, "account-operations/tools/gate_v13")

SKILL_PATH = os.path.join(WORKTREE, "account-operations/skills/operating-one-account/SKILL.md")

FINALIZE_SYS = """你是必填项闸门的补齐环节，不是重写环节，更不是代笔环节。

上游给你两样东西：一份已经写好的交付正文，和一份**由代码产生**的闸门报告。

规则：

1. `needs_fix` 为 `no` 时，只输出四个字符 `NO_CHANGE`，不要输出别的任何内容。
2. `needs_fix` 为 `yes` 时，输出**完整的**修正后正文，后面接**完整的**审计块，只改下面这几类：
   - `missing_items` / `unanchored_items` / `hollow_items`：这些必填项在正文里没有实质回答，
     或审计块指不回正文。**先把实质回答写进正文的自然位置**，再在审计块里把该项指向那句原话；
   - `decorative_items`：本轮触发未命中却写了，从审计块里删掉，正文里对应的装饰性句子也删掉；
   - `overlapping_anchors`：两项指向了正文同一段文字，说明其中一项其实没答，按第一条处理；
   - `internal_leaks`：正文里出现了方括号标签、内部字段名、规则编号、章节号或文件路径，
     **删掉或改写成自然语言**。路径类信息只写进审计块最后两行的机器行；
   - `input_contradiction`：正文说某个输入槽位没给，但它其实给了。按输入实际内容改写那句话；
   - `manifest_contradiction`：按输入清单的原值改写，清单说已加载就是加载了；
   - `continuity`：`positions` 列的是上一轮基线里的持续位与本轮的逐条交代结果。
     **不管闸门有没有点名，你改完之后的正文里都必须保留（或补上）对它们的处置**——
     继续、缩减、暂停、退出，逐个点名；或者至少留着原稿里"其余判断保持不变"那句话。
     原稿里已经有这句的，**一个字都不要动它**；原稿里没有的，补一句。不要替它们编造新的安排。
3. **除上述几类修改外，原正文逐字保留**：不改写措辞、不重新组织、不增删观点、
   不补充新的业务判断、不删任何原有内容。
4. **绝对不要凭空写交付物。** 如果原正文本身就是空的或只有一两句话，那不是你该补的，
   上游会直接判为没有产出——这种情况你也只输出 `NO_CHANGE`。
5. **审计块必须重新完整输出**，因为正文改了、引用也得跟着改。
   用户消息里的 `<required_audit_skeleton>` 就是本轮必须出现的全部行，**一行不多、一行不少**：
   触发标志那一行原样照抄，其余每行把 `::` 右边换成你修正后正文里承载这一项的那句原话。
   参考文件清单不用你抄，系统自己有。
6. **先输出审计块，再输出正文**，中间空一行。像这样：

```text
<<AUDIT>>
…（照 <required_audit_skeleton> 填）…
<<END_AUDIT>>

<修正后的完整正文>
```

不要输出闸门报告，不要解释你改了什么，不要在正文之外多写任何一句话。

正文里的写法，照这个来：

```text
❌  [参考文件加载状态] references/fashion-and-market.md: LOADED；
    references/six-skill-methods.md: NOT_LOADED（已记入 missing[]）
✅  本轮附了服装经营方面的参考资料，另一份关于既有能力方法的参考没有附上，
    所以我不引用那部分方法细节。
```

正文里**不许**出现：参考文件的路径名（`xxx.md`）、字段名（`primary_job`、`missing[]`、
`assumptions[]`）、内部规则编号（`O-10`）、章节号（`§7`）、方括号标签。要表达同样的意思就说人话。"""

FINALIZE_USER = """<gate_report>
needs_fix = {{#required_item_gate.needs_fix#}}
gate_status = {{#required_item_gate.gate_status#}}
{{#required_item_gate.gate_report#}}
</gate_report>

<draft>
{{#required_item_gate.body#}}
</draft>

<draft_audit>
{{#required_item_gate.draft_audit#}}
</draft_audit>

<required_audit_skeleton>
本轮**必须**输出的审计块骨架如下（触发标志已由系统算好，照抄，不要改；
每个 `::` 右边换成你修正后正文里承载这一项的那句原话）：

{{#required_item_gate.required_audit_lines#}}
</required_audit_skeleton>"""


def build_node_code(main_file):
    """把共用检查块与该节点的 main() 拼成一段自足代码。

    共用块**只有一份源文件**，三个节点由同一份拼出来，因此"三处检查逻辑一致"
    是由构造保证的，不是靠人工同步保证的。
    """
    shared = read(os.path.join(HERE, "shared_checks.py"))
    shared = "\n".join(l for l in shared.splitlines() if not l.startswith("__all__ = "))
    body = read(os.path.join(HERE, main_file))
    body = "\n".join(l for l in body.splitlines()
                     if not l.startswith(("import json", "import re", "from shared_checks")))
    return shared.rstrip() + "\n\n" + body.lstrip("\n")


def node(nid, ntype, title, x, y, data, w=242, h=98):
    d = {"type": ntype, "title": title, "selected": False}
    d.update(data)
    return {"id": nid, "type": "custom",
            "position": {"x": x, "y": y}, "positionAbsolute": {"x": x, "y": y},
            "width": w, "height": h, "zIndex": 0,
            "sourcePosition": "right", "targetPosition": "left", "selected": False, "data": d}


def edge(a, b, ta, tb):
    return {"id": f"{a}-source-{b}-target", "source": a, "target": b,
            "sourceHandle": "source", "targetHandle": "target", "type": "custom", "zIndex": 0,
            "data": {"sourceType": ta, "targetType": tb, "isInIteration": False}}


S = lambda: {"type": "string", "children": None}  # noqa: E731


def build_graph(skill_md, gate_code, assemble_code, post_gate_code):
    system_text = skill_md + "\n\n---\n{{#start.loaded_references#}}"
    user_text = "{{#start.account_context#}}\n{{#start.user_request#}}"
    return {
        "nodes": [
            node("start", "start", "本轮投影输入", 80, 260, {"variables": [
                {"variable": "account_context", "label": "账号上下文（M2→M3 最小投影）",
                 "type": "paragraph", "required": True, "max_length": 60000, "options": []},
                {"variable": "user_request", "label": "用户本轮请求（自然语言）",
                 "type": "paragraph", "required": True, "max_length": 20000, "options": []},
                {"variable": "loaded_references",
                 "label": "参考文件加载清单 + 本轮已加载的条件附件全文",
                 "type": "paragraph", "required": False, "max_length": 60000, "options": []},
            ]}, h=160),
            node("operating_one_account_llm", "llm", "单账号持续运营决策", 420, 260, {
                "desc": "一个节点承载全部四类业务行为；行为标签不进入任何枚举或分支条件（M3-AC-05）",
                "model": MODEL,
                "prompt_template": [
                    {"id": "m3-sys-0001", "role": "system", "text": system_text},
                    {"id": "m3-usr-0001", "role": "user", "text": user_text},
                ],
                "context": {"enabled": False, "variable_selector": []},
                "vision": {"enabled": False}, "memory": None,
            }),
            node("required_item_gate", "code", "必填项闸门（确定性检查）", 760, 260, {
                "desc": "触发条件能从投影算的由代码算；最低实质产出、锚定实质、内部字段泄漏、"
                        "输入槽位矛盾、参考清单矛盾、基线关键对象连续性，全部确定性判定。不判断内容好坏。",
                "code_language": "python3", "code": gate_code,
                "variables": [
                    {"variable": "draft", "value_selector": ["operating_one_account_llm", "text"]},
                    {"variable": "manifest", "value_selector": ["start", "loaded_references"]},
                    {"variable": "account_context", "value_selector": ["start", "account_context"]},
                ],
                "outputs": {"gate_report": S(), "needs_fix": S(), "gate_status": S(),
                            "positions_report": S(), "draft_audit": S(),
                            "required_audit_lines": S(), "body": S()},
            }, h=118),
            node("gate_repair_llm", "llm", "按闸门报告补齐缺失项", 1100, 260, {
                "desc": "只补闸门点名的几类；硬失败不进这里（补齐不许无中生有写交付物）；"
                        "无缺失时输出 NO_CHANGE，由下游代码节点取原文",
                "model": MODEL,
                "prompt_template": [
                    {"id": "m3-fix-sys-1", "role": "system", "text": FINALIZE_SYS},
                    {"id": "m3-fix-usr-1", "role": "user", "text": FINALIZE_USER},
                ],
                "context": {"enabled": False, "variable_selector": []},
                "vision": {"enabled": False}, "memory": None,
            }),
            node("assemble", "code", "确定性取稿", 1440, 260, {
                "desc": "闸门无缺失时逐字返回原稿（由代码保证，不依赖模型照抄）；"
                        "硬失败时直接返回原稿并标记不进补齐；有缺失时返回补齐稿与配套审计块",
                "code_language": "python3", "code": assemble_code,
                "variables": [
                    {"variable": "body", "value_selector": ["required_item_gate", "body"]},
                    {"variable": "fixed", "value_selector": ["gate_repair_llm", "text"]},
                    {"variable": "needs_fix", "value_selector": ["required_item_gate", "needs_fix"]},
                    {"variable": "gate_status", "value_selector": ["required_item_gate", "gate_status"]},
                    {"variable": "draft_audit", "value_selector": ["required_item_gate", "draft_audit"]},
                ],
                "outputs": {"final_text": S(), "final_audit": S(), "path": S()},
            }, h=118),
            node("post_gate", "code", "闸门闭合复检与周期状态承载决定", 1780, 260, {
                "desc": "对成稿独立重跑同一套检查（自己解析审计块，不复用第一道闸门的锚定行），"
                        "并决定这份交付够不够格成为当前有效周期判断；不够格就显式说明，不静默继续",
                "code_language": "python3", "code": post_gate_code,
                "variables": [
                    {"variable": "final_text", "value_selector": ["assemble", "final_text"]},
                    {"variable": "manifest", "value_selector": ["start", "loaded_references"]},
                    {"variable": "prior_report", "value_selector": ["required_item_gate", "gate_report"]},
                    {"variable": "account_context", "value_selector": ["start", "account_context"]},
                    {"variable": "final_audit", "value_selector": ["assemble", "final_audit"]},
                    {"variable": "gate_path", "value_selector": ["assemble", "path"]},
                ],
                "outputs": {"post_gate_report": S(), "gaps_closed": S(),
                            "positions_final": S(),
                            "cycle_state_carry": S(), "carry_reject_reason": S(),
                            "operating_judgment_final": S()},
            }, h=118),
            node("end", "end", "运营判断与内容任务候选", 2120, 260, {"outputs": [
                {"variable": "operating_judgment",
                 "value_selector": ["post_gate", "operating_judgment_final"]},
                {"variable": "cycle_state_carry", "value_selector": ["post_gate", "cycle_state_carry"]},
                {"variable": "carry_reject_reason", "value_selector": ["post_gate", "carry_reject_reason"]},
                {"variable": "gate_report", "value_selector": ["required_item_gate", "gate_report"]},
                {"variable": "gate_status", "value_selector": ["required_item_gate", "gate_status"]},
                {"variable": "gate_path", "value_selector": ["assemble", "path"]},
                {"variable": "post_gate_report", "value_selector": ["post_gate", "post_gate_report"]},
                {"variable": "gaps_closed", "value_selector": ["post_gate", "gaps_closed"]},
                {"variable": "draft_raw", "value_selector": ["operating_one_account_llm", "text"]},
                # 持续位由复检节点**独立复算**后给出，纵向 harness 用它做投影。
                # 用第一道闸门的那份也能跑，但那样投影就依赖一个没被复核过的中间结论。
                {"variable": "positions_final", "value_selector": ["post_gate", "positions_final"]},
            ]}, h=240),
        ],
        "edges": [
            edge("start", "operating_one_account_llm", "start", "llm"),
            edge("operating_one_account_llm", "required_item_gate", "llm", "code"),
            edge("required_item_gate", "gate_repair_llm", "code", "llm"),
            edge("gate_repair_llm", "assemble", "llm", "code"),
            edge("assemble", "post_gate", "code", "code"),
            edge("post_gate", "end", "code", "end"),
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 0.7},
    }


SAMPLE_CTX = ("account_anchor: 测试账号（已确认组织角色）\npositioning: 已确认 —— 测试\n"
              "platform: 视频号\nfeedback: 未提供\nmarket_observations: 未提供\n"
              "campaign_overlay: 无覆盖\n"
              "standing_cycle_baseline: 尚无 —— 本账号还没有被接受的周期基线\n")
SAMPLE_MAN = ("<<REFERENCE_MANIFEST>>\nreferences/fashion-and-market.md: LOADED\n"
              "references/six-skill-methods.md: NOT_LOADED\n<<END_REFERENCE_MANIFEST>>")
SAMPLE_DRAFT = ("这是一份用来做部署前契约自检的样例正文，长度足够越过最低实质产出门。"
                "本轮不改周期方向，只把一条任务的验证重点换掉；其余判断保持不变。"
                "本轮附了服装经营方面的参考资料，另一份方法参考没有附上，所以我不引用那部分方法细节。"
                "这一段再补几句，保证句段数与字数都达标，不至于把自检本身卡在硬门上。\n\n"
                "<<AUDIT>>\n探索提案=否;暂定锚点=否;冲突反馈=否;无内容任务=否\n"
                "参考文件加载状态 :: 本轮附了服装经营方面的参考资料，另一份方法参考没有附上\n"
                "<<END_AUDIT>>")


def verify_output_contract(graph, gate_code, assemble_code, post_gate_code):
    """部署前证明：每个代码节点**实际返回的键**与图里声明的 outputs 逐一相等。

    Dify 对不上就整条 workflow `failed: Not all output parameters are validated.`——
    实测踩过一次，`total_steps=3` 停在闸门节点。这类错误没有理由留给运行时发现。
    """
    ns = {}
    for nm, cd, args in (
            ("required_item_gate", gate_code, dict(draft=SAMPLE_DRAFT, manifest=SAMPLE_MAN,
                                                   account_context=SAMPLE_CTX)),
            ("assemble", assemble_code, None), ("post_gate", post_gate_code, None)):
        ns[nm] = {}
        exec(compile(cd, f"<{nm}>", "exec"), ns[nm])
    g = ns["required_item_gate"]["main"](**dict(draft=SAMPLE_DRAFT, manifest=SAMPLE_MAN,
                                                account_context=SAMPLE_CTX))
    a = ns["assemble"]["main"](g["body"], "", g["needs_fix"], g["gate_status"], g["draft_audit"])
    pg = ns["post_gate"]["main"](a["final_text"], SAMPLE_MAN, g["gate_report"], SAMPLE_CTX,
                                 a["final_audit"], a["path"])
    actual = {"required_item_gate": set(g), "assemble": set(a), "post_gate": set(pg)}
    for n in graph["nodes"]:
        if n["data"].get("type") != "code":
            continue
        declared = set(n["data"]["outputs"])
        got = actual[n["id"]]
        assert declared == got, (f"{n['id']} 输出契约不一致：图里声明 {sorted(declared)}，"
                                 f"实际返回 {sorted(got)}")
        print(f"  contract ok: {n['id']} {sorted(got)}")
    # end 节点引用的每个 value_selector 也必须真实存在
    end = [n for n in graph["nodes"] if n["data"].get("type") == "end"][0]
    for o in end["data"]["outputs"]:
        src, key = o["value_selector"]
        if src in actual:
            assert key in actual[src], f"end 引用了 {src}.{key}，但该节点不返回它"
    print("  contract ok: end 节点引用全部存在")


def main():
    c = Console()
    st, apps = c.call("GET", "/console/api/apps?page=1&limit=100")
    assert st == 200, (st, apps)
    hits = [a for a in apps["data"] if TASK_ID in (a.get("name") or "")]
    assert len(hits) == 1, f"expected exactly one task app, got {len(hits)}"
    app_id = hits[0]["id"]
    print("app", app_id, hits[0]["name"][:60])

    skill_md = read(SKILL_PATH)
    gate_code = build_node_code("gate_main.py")
    assemble_code = build_node_code("assemble_main.py")   # 它也用了共用渲染层，必须一起打进去
    post_gate_code = build_node_code("post_gate_main.py")
    for nm, cd in (("gate", gate_code), ("assemble", assemble_code), ("post_gate", post_gate_code)):
        assert "from shared_checks" not in cd, f"{nm} 仍带本地 import，进不了沙箱"
        ns = {"__builtins__": __builtins__}
        exec(compile(cd, f"<{nm}>", "exec"), ns)   # 部署前先证明这段代码自足、能编译并定义 main
        assert callable(ns.get("main")), nm
        print(f"  {nm}: {len(cd)} chars, main() ok")

    graph = build_graph(skill_md, gate_code, assemble_code, post_gate_code)
    verify_output_contract(graph, gate_code, assemble_code, post_gate_code)
    st, cur = c.call("GET", f"/console/api/apps/{app_id}/workflows/draft")
    assert st == 200, (st, cur)
    print("prev draft hash", cur.get("hash"))
    st, res = c.call("POST", f"/console/api/apps/{app_id}/workflows/draft", {
        "graph": graph, "features": FEATURES, "hash": cur.get("hash"),
        "environment_variables": [], "conversation_variables": [],
    })
    assert st == 200, (st, res)
    print("DRAFT SYNCED", res)

    st, pub = c.call("POST", f"/console/api/apps/{app_id}/workflows/publish", {
        "marked_name": "m3-cand-v1.4.2",   # Dify 限 20 字符
        "marked_comment": "M3 v1.4.2: errata-002 — NEW: ids are self-authored, not from input list",  # Dify 限 100 字符
    })
    print("PUBLISH", st, json.dumps(pub, ensure_ascii=False)[:200])
    assert st in (200, 201), (st, pub)

    st, draft = c.call("GET", f"/console/api/apps/{app_id}/workflows/draft")
    assert st == 200
    ev = os.path.join(WORKTREE, "account-operations/evidence/ep23-candidate-v14-freeze")
    os.makedirs(ev, exist_ok=True)
    with open(os.path.join(ev, "m3_app_draft_graph_v14.json"), "w", encoding="utf-8") as f:
        json.dump(draft, f, ensure_ascii=False, indent=2)
    print("draft hash", draft.get("hash"), "version", draft.get("version"))
    print("nodes", [n["data"]["type"] for n in draft["graph"]["nodes"]])


if __name__ == "__main__":
    main()
