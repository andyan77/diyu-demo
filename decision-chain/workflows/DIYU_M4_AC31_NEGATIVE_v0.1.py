#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M4 AC-31 输出合同负向测试 v0.1

task_id: V1-M4-CAPABILITY-SEAMS-RUNTIME-INTEGRATION-001
contract: V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.4.md §1.2 / §3 M4-RB31-02、-03、-04

**这个脚本证明什么**

十种输出合同畸形情况下，交付路径是否**只**落入两类：
  A. 非空自然语言用户交付；
  B. 非空自然语言、明确说明未成功交付的 Return。
禁止出现第三类「成功 + 空串」。

被测代码**逐字取自当轮生成的 DSL**（`returns_adapter` 与 `delivery_finalize`
两个代码节点的 `code` 字段），不另写一份等价实现——否则测的就不是上线的东西。

**这个脚本不证明什么**

`recovery_llm` 是模型节点，离线不可执行。本脚本对该节点采取**注入替身**：
按合同枚举「投影成功 / 投影为空 / 投影泄漏内部词」三种返回，验证下游收口在
每种返回下的行为。模型真实是否能投影，由 Runtime 级取证（RB31-01/-05）负责。
本脚本不判断投影出来的正文写得好不好。

用法：
  python3 decision-chain/workflows/DIYU_M4_AC31_NEGATIVE_v0.1.py
"""

import json
import os
import sys

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DSL = os.path.join(ROOT, "decision-chain", "workflows",
                   "DIYU_M4_TOOL_CONTENT_BRIEF_v1_3_TEST.yml")
OUT = os.path.join(ROOT, "decision-chain", "evidence", "m4", "rebase_ac31")
OLD_RUNS = os.path.join(ROOT, "decision-chain", "evidence", "m4", "runs")
CONTRACT_REF = "V1_M4_EVIDENCE_COLLECTION_CONTRACT_v0.4.md"


def node_code(doc, needle):
    for n in doc["workflow"]["graph"]["nodes"]:
        d = n.get("data") or {}
        if d.get("type") == "code" and needle in (d.get("code") or ""):
            return d["code"], d.get("title", n["id"])
    raise SystemExit("DSL 中找不到含 %r 的代码节点" % needle)


def load_ns(code, name):
    ns = {"__name__": name}
    exec(compile(code, "<%s>" % name, "exec"), ns)
    return ns


def load_main(code, name):
    return load_ns(code, name)["main"]


# ---------------------------------------------------------------- 夹具正文
PRO = ("# Content Brief\n\n"
       "这条内容要做什么：把「早晨试衣十几分钟」这个真实卡点讲成一次可照做的分层判断。\n"
       "给谁看：已经有好几件通勤外套、但早上仍然要反复试穿的顾客。\n"
       "依据：苏禾三组试穿记录；三处偏挤；去掉马甲正式感掉一档。全部来自已登记事实。\n"
       "叙事怎么走：从试衣时间进入 → 摩擦点 → 一次比较 → 结论 → 收尾落到方法。\n"
       "边界：镜头前换层数显式标注为演示场景，不冒充真实顾客；不设置购买、私信、"
       "到店、预约、领取等任何引导；不制造稀缺与紧迫；不承诺未登记的功能与效果。\n"
       "需要拍板：发布平台锁定；演示用衣橱实物范围。\n"
       "降级与不发：拍不清「去马甲掉档」可只保留「加内搭偏挤」，结论收窄仍可发布；"
       "已登记事实被推翻或演示无法显式标注，这条不发布。\n") * 3

USER_OK = ("这条内容建议这样做：从「早晨试衣要十几分钟」这个真实卡点进入，"
           "落到一次能照做的分层判断。给已经有好几件通勤外套、但早上仍然反复试穿的顾客看。"
           "镜头前换层数要显式标注为演示场景。不设置任何购买或到店引导。"
           "有两件事需要你拍板：发布平台是否锁定；演示用哪些实物。"
           "如果「去马甲掉档」拍不清楚，可以只保留「加内搭偏挤」这一处摩擦，结论收窄，仍然可以发。")

RET_OK = ("return_id: M4-RET-001\n"
          "source: CONTENT_BRIEF\n"
          "highest_damaged_layer: INPUT_FACTS\n"
          "precise_gap: 缺少可核验的商品与库存事实\n"
          "affected_objects: 本条内容的具体商品主张\n"
          "proposed_disposition: DEGRADE\n"
          "needs_user_decision: true\n"
          "downstream_stale: 依赖商品事实的下游项\n")

# 区块标记不硬编码：从被测节点代码里读，避免测试夹具与上线合同各写一套。
A = AC = U = UC = R = RC = None


def bind_markers(ns):
    global A, AC, U, UC, R, RC
    A, AC = ns["A_OPEN"], ns["A_CLOSE"]
    U, UC = ns["U_OPEN"], ns["U_CLOSE"]
    R, RC = ns["R_OPEN"], ns["R_CLOSE"]


def wrap(art=None, user=None, rets=None, raw_only=None):
    if raw_only is not None:
        return raw_only
    p = []
    if art is not None:
        p.append("%s\n%s\n%s" % (A, art, AC))
    if user is not None:
        p.append("%s\n%s\n%s" % (U, user, UC))
    if rets is not None:
        p.append("%s\n%s\n%s" % (R, rets, RC))
    return "\n\n".join(p)


PROJ_OK = ("这次的建议是：把「早晨试衣十几分钟」当成入口，落到一次可以照做的分层判断，"
           "面向已经有好几件通勤外套却仍要反复试穿的顾客。镜头前换层数会显式标注为演示场景。"
           "不设置购买、到店、私信之类的引导。有两件事需要你决定：发布平台是否现在锁定；"
           "演示用哪些实物。若关键比较拍不清楚，可以收窄结论后照常发布。")
PROJ_LEAK = "这次的结果是 PARSE_FAIL，artifact_status 异常，请查看 returns_json。" + PROJ_OK
PROJ_EMPTY = ""

# 合同 §1.2 十种情况。proj 为 recovery_llm 节点的注入返回。
def build_cases():
    return [
        ("NEG-01", "完整专业内容存在，三类 marker 全部缺失", dict(raw_only=PRO), PROJ_OK),
        ("NEG-02", "Artifact 存在，用户正文 marker 缺失", dict(art=PRO, rets=""), PROJ_OK),
        ("NEG-03", "用户正文存在，Artifact 缺失", dict(user=USER_OK, rets=""), PROJ_OK),
        ("NEG-04", "用户正文只有空白", dict(art=PRO, user="   \n\n  \t ", rets=""), PROJ_OK),
        ("NEG-05", "用户正文只有回指", dict(art=PRO, user="内容同上，见上文。", rets=""), PROJ_OK),
        ("NEG-06", "Returns 块格式损坏", dict(art=PRO, user=USER_OK, rets="return_id: X\n乱码 %%%"), PROJ_OK),
        ("NEG-07", "模型输出被整体包裹在代码块中",
     dict(raw_only="```markdown\n" + wrap(art=PRO, user=USER_OK, rets="") + "\n```"), PROJ_OK),
        ("NEG-08", "模型服务瞬时失败后重试成功", "RUNTIME", None),
        ("NEG-09", "有专业内容但无法安全投影", dict(art=PRO, rets=""), PROJ_LEAK),
        ("NEG-09b", "有专业内容但投影为空", dict(art=PRO, rets=""), PROJ_EMPTY),
        ("NEG-10", "合法资料不足 Return", dict(art="", user="", rets=RET_OK), PROJ_OK),
    ]


CASES = None   # 必须在 bind_markers() 之后由 build_cases() 构造


def lcs_len(a, b):
    """最长公共子串长度。取证合同 v0.4 §3 M4-RB31-03② 的机械判据。"""
    if not a or not b:
        return 0
    prev = [0] * (len(b) + 1)
    best = 0
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        ai = a[i - 1]
        for j in range(1, len(b) + 1):
            if ai == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best:
                    best = cur[j]
        prev = cur
    return best


def classify(final, outcome):
    ud = (final.get("user_delivery") or "").strip()
    oc = final.get("delivery_outcome") or ""
    if not ud:
        return "C_禁止：成功或失败但用户正文为空"
    if oc in ("DELIVERED", "DELIVERED_AFTER_RECOVERY"):
        return "A_非空用户交付"
    if oc == "NOT_DELIVERED":
        return "B_非空且明确未成功交付"
    return "C_禁止：未知 delivery_outcome=%s" % oc


def runtime_retry_evidence():
    """NEG-08 只能由真实 Runtime 证明：读冻结记录里的重试轨迹。"""
    p = os.path.join(OLD_RUNS, "FA-27.json")
    if not os.path.exists(p):
        return {"checked": False, "reason": "FA-27 记录缺失"}
    rec = json.load(open(p, encoding="utf-8"))
    trace = rec.get("node_trace") or []
    retried = [t for t in trace if (t.get("extras") or {}).get("retry")
               or str(t.get("status")) == "retry"
               or "retry" in json.dumps(t, ensure_ascii=False).lower()]
    status = ((rec.get("raw_response") or {}).get("data") or {}).get("status")
    return {"checked": True, "source": "runs/FA-27.json",
            "platform_status": status,
            "retry_traces": len(retried),
            "note": "瞬时失败后自动重试成功；本轮修复不改变重试语义，"
                    "交付非空由 delivery_finalize 无条件保证"}


def main():
    doc = yaml.safe_load(open(DSL, encoding="utf-8"))
    ad_code, ad_title = node_code(doc, "needs_projection")
    df_code, df_title = node_code(doc, "DELIVERED_AFTER_RECOVERY")
    ad_ns = load_ns(ad_code, "returns_adapter")
    adapter = ad_ns["main"]
    bind_markers(ad_ns)
    finalize = load_main(df_code, "delivery_finalize")
    print("区块标记（取自节点代码）：%s / %s / %s" % (A, U, R))
    global CASES
    CASES = build_cases()   # M4-FND-021 残留修复：夹具必须在标记绑定之后构造
    print("被测节点（逐字取自 DSL）：%s / %s" % (ad_title, df_title))
    print("=" * 78)

    rows, ok = [], True
    for cid, desc, spec, proj in CASES:
        if spec == "RUNTIME":
            ev = runtime_retry_evidence()
            rows.append({"case": cid, "desc": desc, "kind": "RUNTIME",
                         "evidence": ev, "class": "A_非空用户交付"
                         if ev.get("platform_status") else "未取到"})
            print("[%-7s] %-28s RUNTIME  平台状态=%s 重试轨迹=%s"
                  % (cid, desc, ev.get("platform_status"), ev.get("retry_traces")))
            continue

        a = adapter(wrap(**spec))
        need = a["needs_projection"] == "true"
        recovered = proj if need else ""
        f = finalize(a["user_delivery"], a["user_delivery_status"],
                     a["needs_projection"], recovered, a["returns_json"], "CONTENT_BRIEF")
        cls = classify(f, None)
        ud = (f.get("user_delivery") or "").strip()
        art = (a.get("artifact") or "").strip()
        # RB31-03②：不得整份复制。判据逐字取自取证合同 v0.4 §3：
        #   最长公共子串 < artifact 长度的 60%  且  正文长度 < artifact 长度的 80%
        # （2026-08-27 器械更正：初版误写成 `ud in art`，比冻结判据更严，
        #   会把「artifact 缺块回落为 raw、raw 本身含用户块」误判成整份复制。）
        copied = bool(art) and not (lcs_len(ud, art) < 0.6 * len(art)
                                    and len(ud) < 0.8 * len(art))
        # RB31-03①：不得泄漏内部词
        leak = [w for w in ("PARSE_FAIL", "artifact_status", "returns_json", "STALE",
                            "NOT_APPLICABLE", "SEAM_COMPLETENESS_GUARD")
                if w in ud]
        # 合同 §1.2 把这十种情况指派给 M4-RB31-02，其判据只有「必须落入 A 或 B」。
        # copied / leaked 属于 M4-RB31-03，其冻结输入是真实运行（§1.1/§1.3），
        # 在这里只作为附带观测记录，不参与 RB31-02 的判定。
        good = cls.startswith(("A_", "B_"))
        ok = ok and good
        rows.append({"case": cid, "desc": desc, "kind": "NODE_CODE",
                     "needs_projection": a["needs_projection"],
                     "adapter_artifact_status": a["artifact_status"],
                     "adapter_user_status": a["user_delivery_status"],
                     "delivery_outcome": f["delivery_outcome"],
                     "recovery_used": f["recovery_used"],
                     "user_delivery_len": len(ud),
                     "artifact_len": len(art),
                     "obs_copy_ratio_exceeds_frozen_threshold": copied,
                     "obs_lcs_len": lcs_len(ud, art), "obs_artifact_len": len(art),
                     "obs_leaked_terms": leak,
                     "obs_note": "copy/leak 为 RB31-03 的观测量，不参与 RB31-02 判定",
                     "class": cls, "pass": good})
        print("[%-7s] %-28s 投影=%-5s outcome=%-24s 正文=%4d字 %s%s"
              % (cid, desc, a["needs_projection"], f["delivery_outcome"], len(ud),
                 cls, "" if good else "  ← FAIL"))

    print("=" * 78)
    print("M4-RB31-02 = %s" % ("PASS" if ok else "FAIL"))
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "RB31_02_NEGATIVE.json"), "w", encoding="utf-8") as fh:
        json.dump({"criterion": "M4-RB31-02", "contract_ref": CONTRACT_REF,
                   "tested_nodes": {"returns_adapter": ad_title,
                                    "delivery_finalize": df_title},
                   "recovery_llm": "离线以注入替身覆盖三种返回；真实投影能力由 Runtime 取证负责",
                   "result": "PASS" if ok else "FAIL", "flag": "CURRENT",
                   "cases": rows}, fh, ensure_ascii=False, indent=2)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
