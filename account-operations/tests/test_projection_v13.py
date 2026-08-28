#!/usr/bin/env python3
"""投影 v1.3 的序列级回归：**正文变短，持续位不丢**。

这是第 5 轮 AC-17 判不过的那一条的直接回归。判定者当时机械定位到：
`E10` 之后基线从 1997 字符被压到 546，8 个被独立追踪的对象只剩 1 个，
而 `dropped_without_notice` 全程为 `[]`。

v1.3 的分界点在于：**散文可以被替换，持续位不由散文承载**。
下面把那个形态复现一遍，断言两件事——散文确实变短了，持续位一个不少。
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, os.path.join(_ROOT, "tools/gate_v13"))

from projection_v13 import project, serialize_positions   # noqa: E402

POS = [{"id": "P-rhythm", "kind": "regular", "title": "每周三条节奏", "since": "E01"},
       {"id": "P-fit", "kind": "exploration", "title": "上身效果验证", "since": "E03"},
       {"id": "P-store", "kind": "regular", "title": "门店陈列栏目", "since": "E02"}]

LONG_PROSE = ("本周期保持每周 3 条；上身效果验证在跑，观察窗到 9 月 1 日；"
              "门店陈列栏目每两周一条；另外还有若干背景说明。" * 12)
SHORT_OUTPUT = "本周只调一处，其余照旧。"

fails = []


def expect(cond, msg):
    if not cond:
        fails.append(msg)


# ---- 1. 交付够格、三位全部交代 ⇒ 散文替换、持续位全在 ----
report_all_ok = json.dumps({"continued": ["P-rhythm", "P-fit", "P-store"],
                            "disposed": [], "new_positions": [],
                            "positions_unaccounted": [], "positions_fabricated": []},
                           ensure_ascii=False)
prose, pos, rec = project(LONG_PROSE, POS, SHORT_OUTPUT, "ACCEPTABLE_AS_NEW_BASELINE",
                          report_all_ok, "E10")
expect(rec["mode"] == "ADVANCED", f"模式应为 ADVANCED，实为 {rec['mode']}")
expect(rec["prose_shrank"] is True, "本用例的前提就是散文变短，没变短说明用例失效")
expect(len(prose) < len(LONG_PROSE) / 3, "散文确实被压缩了")
expect(sorted(p["id"] for p in pos) == ["P-fit", "P-rhythm", "P-store"],
       f"散文压缩后持续位丢了：{[p['id'] for p in pos]}  ← 这正是第 5 轮 AC-17 的失效形态")
expect(all(p["last_restated"] == "E10" for p in pos), "继续的位应更新 last_restated")

# ---- 2. 下一步（E11）拿到的输入里，三位仍然逐字在 ----
carried = json.loads(serialize_positions(pos))
expect([p["id"] for p in carried] == [p["id"] for p in pos], "序列化到下一步时丢了位")

# ---- 3. 交付不够格 ⇒ 散文与持续位一并保持上一有效值 ----
report_dropped = json.dumps({"continued": ["P-rhythm"], "disposed": [], "new_positions": [],
                             "positions_unaccounted": ["P-fit", "P-store"],
                             "positions_fabricated": []}, ensure_ascii=False)
prose2, pos2, rec2 = project(LONG_PROSE, POS, SHORT_OUTPUT, "REJECTED_KEEP_PREVIOUS",
                             report_dropped, "E11")
expect(rec2["mode"] == "KEPT_PREVIOUS", f"不够格时应保持上一基线，实为 {rec2['mode']}")
expect(prose2 == LONG_PROSE, "不够格时散文必须原样保留")
expect(sorted(p["id"] for p in pos2) == ["P-fit", "P-rhythm", "P-store"],
       "不够格时持续位必须原样保留")
expect(rec2["positions_unaccounted"] == ["P-fit", "P-store"],
       "未交代的位必须显式记下来——这一栏为空却真的丢了东西，正是上一轮的失效")

# ---- 4. 点名处置 ⇒ 移出活动集，但进 disposed_log，不删除 ----
report_disposed = json.dumps({"continued": ["P-rhythm", "P-fit"], "disposed": ["P-store"],
                              "new_positions": [{"id": "NEW:门店咨询", "kind": "exploration"}],
                              "positions_unaccounted": [], "positions_fabricated": []},
                             ensure_ascii=False)
_, pos3, rec3 = project(LONG_PROSE, POS, SHORT_OUTPUT, "ACCEPTABLE_AS_NEW_BASELINE",
                        report_disposed, "E12")
expect(sorted(p["id"] for p in pos3) == ["NEW:门店咨询", "P-fit", "P-rhythm"],
       f"处置 + 新增后的活动集不对：{[p['id'] for p in pos3]}")
expect(rec3["disposed_log_added"] == ["P-store"], "被处置的位必须进 disposed_log，可回指")

# ---- 5. 第 5 轮那次事故的直接对照：零产出不得覆盖 ----
_, pos4, rec4 = project(LONG_PROSE, POS, "", "REJECTED_KEEP_PREVIOUS",
                        json.dumps({"positions_unaccounted": ["P-rhythm", "P-fit", "P-store"]}),
                        "E07")
expect(rec4["mode"] == "KEPT_PREVIOUS" and len(pos4) == 3,
       "零产出把基线整体挤掉——这正是第 4 轮的事故，不得复现")

if fails:
    print("FAIL:")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("投影 v1.3 序列级回归全部通过：")
print("  · 散文 %d → %d 字符，持续位 3 → 3 个（第 5 轮同一形态下是 8 → 1）" % (len(LONG_PROSE), len(prose)))
print("  · 交付不够格时散文与持续位一并原样保留，未交代的位显式记账")
print("  · 处置的位进 disposed_log 不删除；零产出不覆盖基线")
