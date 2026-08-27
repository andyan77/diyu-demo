#!/usr/bin/env python3
"""按 ADDENDUM_003 §3 生成 36 份盲评提示词，并**在结果存在之前**证明它们逐字同构。

与第 6 轮的差别，是这一条约束的证明方向反过来了：
上一轮是先跑完、再由 Reviewer 从 harness 记录里把 36 份提示词捞出来做事后同构核验；
本轮是先由单一模板构造性地生成、当场核验、落盘冻结，判定者拿到的就是这 36 个文件。
事后核验只能说"确实同构"，构造性生成还能说"不可能不同构"。

同构定义（逐字来自 ADDENDUM_003 §3）：
    两两相比，只允许在单元号（unit_NN）与判定者序号（j1/j2/j3）两处不同，
    其余每一个字节相同。
本脚本把这两处归一化后哈希，要求 36 份得到**唯一 1 种**形态；不成立就拒绝落盘。
"""
import hashlib, json, os, re, sys

OUT_OF_REPO = ("/tmp/claude-1000/-home-faye-diyu-demo/"
               "2c670698-40ad-483e-b793-56ac12fb6aea/scratchpad/m3-ab-blind-v5")
UNITS_DIR = os.path.join(OUT_OF_REPO, "units")
PROMPTS_DIR = os.path.join(OUT_OF_REPO, "prompts")
RUBRIC = os.path.join(OUT_OF_REPO, "rubric.md")
JUDGES_PER_UNIT = 3

DIMS = ["运营判断", "周期组合", "产能取舍", "实验设计", "反馈判断", "内容任务质量", "共同质量底线"]
GATES = ["目标忠实", "事实", "权限", "风险", "当前任务必要条件"]

TEMPLATE = """你是一名独立盲评者。你**只**评这一份输出，评完就结束。

## 你能读的文件，只有这三个

1. 场景输入：{units_dir}/{unit}/_scenario.md
2. 待评输出：{units_dir}/{unit}/output.md
3. 评分依据：{rubric}

## 硬性禁止

- **不得**进入 `/home/faye/diyu-demo` 或 `/home/faye/diyu-demo-worktrees` 下的任何路径；
- **不得**访问 {units_dir} 下除 {unit} 以外的任何目录，也不得列出该目录；
- **不得**执行任何 git 命令；
- 你的执行记录会被机械核验，越界会导致本份判定作废。

## 你不知道、也不需要知道的事

你手上这份输出是四种系统提示词之一产生的，你不知道是哪一种，也不知道其他三种长什么样。
**不要试图推断**。你的任务是就这一份输出本身，按 Rubric 逐项打分。

## 怎么判

### 五项硬门（Rubric §5.2）——逐项 `满足` 或 `实质退化`，各写一句可核查的证据

{gates}

硬门是**非补偿**的：某一项退化了，不能用别处的优点抵消。
判 `实质退化` 要指出输出里的具体位置或原句，不能只写结论。

### 七个维度（Rubric §5.3）——各给一个等级

等级只有这六个：`优秀` / `合格` / `勉强` / `不足` / `缺失` / `不适用`。

{dims}

**`不适用` 是一个真实的选项**：这个场景本来就没有触及该维度时就用它，
不要为了填满表格而勉强给分。每个维度写一句可核查的理由，指向输出里的具体位置。

### 绝对判定，不是相对比较

你只有一份输出，没有对照物。按 Rubric 的绝对标准打分，
**不要**去想"这大概比另一种写法好还是差"——你看不到另一种写法，这个念头只会变成噪音。

## 协议自检

最后逐条声明：你读了哪些文件；你有没有猜这份输出来自什么样的提示词
（不知道就写"不知道"）；如果猜了，凭什么猜的（没猜就写"无"）。
**猜了不扣分，如实写就行**——这一栏是用来核验盲评有没有失效的，不是用来考你的。

你是 {unit} 的第 {judge} 名判定者。
"""


def build(unit, judge):
    return TEMPLATE.format(
        units_dir=UNITS_DIR, unit=unit, rubric=RUBRIC, judge=judge,
        gates="\n".join(f"{i}. {g}" for i, g in enumerate(GATES, 1)),
        dims="\n".join(f"- **{d}**" for d in DIMS))


def normalize(text):
    """按 ADDENDUM_003 §3 允许的两处差异归一化。"""
    text = re.sub(r"unit_\d{2}", "unit_NN", text)
    text = re.sub(r"第 \d+ 名判定者", "第 J 名判定者", text)
    return text


def main():
    if not os.path.isdir(UNITS_DIR):
        sys.exit(f"单元目录不存在，先跑 run_ab_v5.py：{UNITS_DIR}")
    units = sorted(d for d in os.listdir(UNITS_DIR) if d.startswith("unit_"))
    if len(units) != 12:
        sys.exit(f"单元数不是 12：{len(units)}")

    prompts, shapes = [], {}
    for u in units:
        for j in range(1, JUDGES_PER_UNIT + 1):
            p = build(u, j)
            prompts.append({"unit": u, "judge": j, "prompt": p,
                            "sha256": hashlib.sha256(p.encode()).hexdigest()})
            shapes.setdefault(hashlib.sha256(normalize(p).encode()).hexdigest(), []).append(f"{u}/j{j}")

    if len(shapes) != 1:
        print("同构核验不成立，拒绝落盘。形态数：", len(shapes), file=sys.stderr)
        for h, members in shapes.items():
            print(f"  {h[:16]}… × {len(members)}: {members[:4]}", file=sys.stderr)
        sys.exit(2)

    shape_hash, members = next(iter(shapes.items()))
    assert len(members) == 36, f"份数不是 36：{len(members)}"
    assert len({p["sha256"] for p in prompts}) == 36, "36 份提示词里有完全相同的两份"

    os.makedirs(PROMPTS_DIR, exist_ok=True)
    for p in prompts:
        with open(os.path.join(PROMPTS_DIR, f"{p['unit']}_j{p['judge']}.txt"),
                  "w", encoding="utf-8") as f:
            f.write(p["prompt"])

    record = {
        "protocol": "ADDENDUM_003 §3 逐字同构，构造性证明（生成时核验，非事后核验）",
        "judges": 36, "units": len(units), "judges_per_unit": JUDGES_PER_UNIT,
        "normalized_shape_sha256": shape_hash,
        "distinct_shapes": 1,
        "normalization": ["unit_\\d{2} → unit_NN", "第 \\d+ 名判定者 → 第 J 名判定者"],
        "per_prompt_sha256": {f"{p['unit']}_j{p['judge']}": p["sha256"] for p in prompts},
        "prompts_dir": PROMPTS_DIR,
    }
    with open(os.path.join(OUT_OF_REPO, "_prompt_homomorphism_v5.json"),
              "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: record[k] for k in
                      ("judges", "distinct_shapes", "normalized_shape_sha256")},
                     ensure_ascii=False, indent=2))
    print(f"36 份提示词已落盘：{PROMPTS_DIR}")


if __name__ == "__main__":
    main()
