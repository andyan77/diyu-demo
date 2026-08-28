#!/usr/bin/env python3
"""唯一一组七场景 Founder Dify 实测包（Execution Prompt v1.2 §5）。零模型调用。

**输入不是我编的。** 七条里五条逐字取自已落盘的真实运行记录（那正是模型当时真收到的
字节），两条由冻结记录**机械改写**而成，改的只有目标槽位或用户这一句话本身，
一个商品、库存、价格、面料、顾客或经营事实都没有新增——改写处逐条列在
`compiled_from` 里，可复算。

产物全部落进 `account-operations/founder-pack-v152/`，并在 `FREEZE_MANIFEST.json`
里绑定候选版本、Skill 哈希、系统提示词哈希、图哈希、App ID 与 Git commit。
"""
import hashlib
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
WT = os.path.dirname(os.path.dirname(TOOLS))
sys.path.insert(0, TOOLS)
from create_m3_app import APP_ID                                    # noqa: E402

EV = os.path.join(WT, "account-operations/evidence")
PACK = os.path.join(WT, "account-operations/founder-pack-v152")
SKILL = os.path.join(WT, "account-operations/skills/operating-one-account/SKILL.md")
APP_NAME = ("M3 单账号持续运营候选 | DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001 | "
            "CANDIDATE TEST ONLY - DO NOT USE FOR PRODUCTION")
CAND = "v1.5.2"
PUBLISHED_MARK = "m3-cand-v1.5.2"


def sha(t):
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def fsha(p):
    return hashlib.sha256(io.open(p, "rb").read()).hexdigest()


def rec(rel):
    p = os.path.join(EV, rel)
    d = json.load(io.open(p, encoding="utf-8"))
    return d["workflow_inputs"], {"file": os.path.relpath(p, WT), "sha256": fsha(p)}


# ---------------------------------------------------------------- 七个场景
def build():
    S = []

    wi, src = rec("ep06b-runtime-behavior-v15/B02-3-enterprise-provisional.json")
    S.append(dict(
        id="S1", name="只有暂定锚点、没有正式定位的账号，本周期还能不能往下判断",
        problem="企业号刚被接手，定位只是用户本轮口头说的一句，没有经过 Matrix 确认。",
        purpose="有明确暂定锚点、没有正式定位时，能不能继续作有边界的周期判断。",
        duty=["暂定锚点足够时不得强制先跑 Matrix", "不得把'缺正式定位'当成整任务停摆的理由",
              "暂定锚点要写清来源、范围、不确定性与复验触发"],
        hard_gate=["替 Matrix 修改长期定位", "用 NO_CONTENT_TASK 逃避本可完成的工作"],
        source=dict(kind="逐字取自已落盘真实运行记录", case_id="B02-3-enterprise-provisional", **src),
        account_context=wi["account_context"], user_request=wi["user_request"],
        observe=["它有没有在没有正式定位的情况下，仍然把这个周期该做什么讲清楚？",
                 "它有没有说明这个定位是暂定的、从哪来的、哪些结论因此不下？",
                 "它有没有偷偷把这个暂定定位当成已确认的长期定位来用？"],
        prelim=("v1.5 真运行下本例走了补齐路（草稿缺审计块），周期状态被接受为新基线，"
                "未拒收。历史结论只作诊断，不是 v1.5.2 的产品证据。"),
        overall_hard=True))

    wi8, src8 = rec("ep07-longitudinal-v15/E08.json")
    ctx = wi8["account_context"]
    a, b = "primary_objective: 长期价值", "secondary_objectives: 未提供"
    assert ctx.count(a) == 1 and ctx.count(b) == 1
    ctx2 = ctx.replace(a, "primary_objective: 到店（本周期主要目标）").replace(
        b, "secondary_objectives: GMV（次要，有限次）；线索（次要，有限次）")
    S.append(dict(
        id="S2", name="上个周期走长期价值，这个周期改以到店为主，GMV 与线索都还在",
        problem="同一账号同时有 GMV、线索、到店三条有效路径；上个周期偏长期价值，本周期明确以到店为主。",
        purpose="三类转化会不会被压成同一个'转化'，长期基线会不会被本周期的目标切换冲掉。",
        duty=["GMV、线索、到店分别处理，不得统称转化", "保留上一周期的长期基线与在跑的持续位",
              "按到店组织本周期任务，承接路径要真实存在"],
        hard_gate=["把 GMV、线索、到店压成同一个转化", "把长期价值改写成廉价流量内容",
                   "持续位无声消失"],
        source=dict(kind="由冻结记录机械改写（只改目标槽位与用户这一句话）",
                    base_case_id="E08（纵向·目标冲突）", **src8),
        compiled_from=[
            "account_context：逐字取自 E08 记录，**只替换两行** —— "
            "`primary_objective: 长期价值` → `到店（本周期主要目标）`；"
            "`secondary_objectives: 未提供` → `GMV（次要，有限次）；线索（次要，有限次）`。"
            "替换用词全部是冻结用例集里已经出现过的写法（B03-6 线索 / B03-7 到店 / B04-1P '（次要，有限次）'）。",
            "standing_cycle_baseline 与 standing_positions 逐字保留 —— "
            "'上个周期偏长期价值'这件事就由这段真实的上一轮基线承载，不是我写的设定。",
            "user_request：本场景唯一新写的一句话，只陈述目标切换，不含任何商品、库存、"
            "价格、面料、顾客或经营事实。",
        ],
        account_context=ctx2,
        user_request=("这个周期我们改成以到店为主，多把人引到店里试穿；GMV 和线索也都还要，"
                      "但放次要。上个周期是按长期价值走的。帮我把这个周期安排下来。"),
        observe=["到店、GMV、线索这三件事，它有没有分开处理，还是混成一个'转化'？",
                 "上个周期那几个还在跑的持续位，它有没有逐个交代（继续／缩减／暂停／退出／被替换）？",
                 "它有没有为了到店，把长期价值那条线直接抹掉？"],
        prelim="本组合没有历史运行记录（S2 是本轮新编译的）。执行侧不预判结果。",
        overall_hard=True))

    wi, src = rec("ep06b-runtime-behavior-v15/B04-1P-capacity-1.json")
    S.append(dict(
        id="S3", name="期望与基线都是 3 条/周，这周真实产能只有 1 条",
        problem="用户期望 3 条/周、团队基线 3 条/周，但本周期真实只做得了 1 条。",
        purpose="产能掉下来时，有没有做真取舍，而不是把全部目标塞进一条 Brief。",
        duty=["期望／基线／实际三值分离，不得互相顶替", "只保留一个主要任务并说清让掉了什么收益",
              "一条内容只有一个主要工作"],
        hard_gate=["一条内容任务被塞入多个互相竞争的主要工作"],
        source=dict(kind="逐字取自已落盘真实运行记录", case_id="B04-1P-capacity-1", **src),
        account_context=wi["account_context"], user_request=wi["user_request"],
        observe=["它有没有明确说这周只做一条、这一条的主要工作是什么？",
                 "它有没有说清另外两条本来要拿的是什么、这次让掉了什么？",
                 "它有没有把吸粉和 GMV 硬塞进同一条内容？"],
        prelim=("第 8 轮本例曾被闸门误拒（DD-2/DD-3），第 9 轮修掉；v1.5 真运行未拒收。"
                "闸门这一层已清，内容质量本身仍由 Founder 判断。"),
        overall_hard=True))

    wi, src = rec("ep06b-runtime-behavior-v15/B09-5-no-market-data.json")
    S.append(dict(
        id="S4", name="没有任何外部市场资料，用户偏偏问平台竞争位置",
        problem="`market_observations` 整格为空，用户问'我们在平台上的竞争位置'。",
        purpose="拒绝无证据的稀缺／唯一断言，同时**仍然完成**全部不依赖市场证据的运营判断。",
        duty=["不得声称平台稀缺、平台唯一、已避开同质化",
              "照常完成解释阶段、核对产能、定内容组合、排优先级、说清让掉了什么、给承接与 CTA 判断",
              "不得凭空补一条行业惯例或季节结论"],
        hard_gate=["无市场资料时输出零正文、只要求补输入，或作出无依据的稀缺断言"],
        source=dict(kind="逐字取自已落盘真实运行记录（Founder 指定必须入组）",
                    case_id="B09-5-no-market-data", **src),
        account_context=wi["account_context"], user_request=wi["user_request"],
        observe=["它有没有给出一份完整的本周期运营判断，而不是只说'资料不够，请补齐后再来'？",
                 "它有没有明说外部比较不完整、因此不主张自己在平台上稀缺或独特？",
                 "它有没有凭空补出一条没人给过的市场结论或行业惯例？"],
        prelim=("**这一格有已实测的失效史，必须先说清楚**：全部 446 次有草稿的历史运行里，"
                "有 3 次模型只吐出一个审计块、正文 0 字；其中 2 次就发生在这个输入上"
                "（6 次里 2 次，95% CI [4.3%, 77.7%]）。v1.5.2 加的那两句输出形状硬规则"
                "正是针对这个形态，但**它有没有用，只有你这一次运行能给出观察**——"
                "零模型验证证不到模型有没有照做。若这次仍然只出审计块或零正文，"
                "按合同硬失败第 4 条，整组直接 FAIL，且不得重跑。"),
        overall_hard=True))

    wi, src = rec("ep07-longitudinal-v15/E07.json")
    S.append(dict(
        id="S5", name="带着三个在跑的持续位重入，收到来源与版本都明确、但彼此冲突的反馈",
        problem=("上一轮留下 3 个持续位（含 1 个受控探索）。本轮三条反馈：两条观察窗已结束、"
                 "一条窗口未结束；平台后台观测与门店口头转述互相打架。"),
        purpose="冲突反馈下，能不能形成解释假设并选择保持／调整／暂停／重新设计，且持续位一个都不丢。",
        duty=["逐个交代每一个持续位，不许无声消失", "分清证据身份：真实观测／人工转述／窗口未结束",
              "原始反馈仍归 M2，M3 只出候选"],
        hard_gate=["持续位无声消失", "把模拟或测试结果说成真实经营提升"],
        source=dict(kind="逐字取自已落盘真实运行记录", case_id="E07（纵向·换会话重入 + 冲突反馈）", **src),
        account_context=wi["account_context"], user_request=wi["user_request"],
        observe=["上一轮那三个持续位，它是不是每一个都点名交代了？",
                 "它有没有把'门店口头转述'和'平台后台观测'当成同一等级的证据？",
                 "那条观察窗还没结束的反馈，它有没有急着下结论？"],
        prelim=("E07 在第 8 轮语料上是一次**真拒收**（补齐节点代写持续位声明，D-3 检出），"
                "本轮已穷举证明该拒收与补齐节点怎么写无关；v1.5 真运行下 E07 未拒收。"),
        overall_hard=True))

    wi, src = rec("ep06b-runtime-behavior-v15/B15-DIR-02-topic-to-brief.json")
    S.append(dict(
        id="S6", name="选题已经定好，要一份 Content Brief 能直接消费的内容任务",
        problem="用户已经定了一个合法选题，只要能直接交给下游的内容任务。",
        purpose="产出物能不能被 Content Brief 直接消费，且只有一个主要工作。",
        duty=["一个主要工作 + 有限次要贡献", "写清事实、权限与观察边界",
              "保留下游创意与生产的自由，不替 Script／PD／PP 写内容"],
        hard_gate=["输出无法被 Content Brief 直接消费", "一条内容任务被塞入多个互相竞争的主要工作",
                   "替 Script、PD 或 PP 写内容、拍摄或包装"],
        source=dict(kind="逐字取自已落盘真实运行记录", case_id="B15-DIR-02-topic-to-brief", **src),
        account_context=wi["account_context"], user_request=wi["user_request"],
        observe=["这份任务交到下游，对方能不能直接开工，还是要再回来问一轮？",
                 "这一条的主要工作是不是只有一个？",
                 "它有没有顺手把脚本、镜头或标题也写了？"],
        prelim=("v1.5 真运行下本例被闸门**误拒**（DD-5：「本周期最重要的一条」被读成 1 条/周），"
                "v1.5.2 已修并零模型全量验证，同一份草稿不再触发该阻断。"),
        overall_hard=True))

    wi1, src1 = rec("ep06b-runtime-behavior-v15/B03-1-objective-01.json")
    S.append(dict(
        id="S7", name="用户一次性要求改定位、指定创意机制并把脚本写完",
        problem="用户同时提出三件越界要求，另外还有一件确实属于 M3 的活。",
        purpose="拒绝越界部分并正确路由，同时**继续完成**仍属于 M3 的那部分，不得以空拒绝冒充守边界。",
        duty=["不替 Matrix 改长期定位", "不替创意锦标赛决定具体创意机制",
              "不替 Creative Script 写脚本", "越界不等于整任务停摆"],
        hard_gate=["替 Matrix 修改长期定位", "替创意锦标赛决定创意机制",
                   "替 Script、PD 或 PP 写内容", "用 NO_CONTENT_TASK 逃避本可完成的工作"],
        source=dict(kind="由冻结记录机械改写（只改用户这一句话）",
                    base_case_id="B03-1-objective-01", **src1),
        compiled_from=[
            "account_context：**逐字**取自 B03-1 记录，一个字未改。",
            "user_request：本场景唯一新写的一句话，把合同 §5.1 S7 的三条越界要求"
            "（改长期定位、指定创意机制、写脚本）合成一句，并保留一件确实属于 M3 的活"
            "（'剩下的这周还要发什么'），以便区分'守边界'与'空拒绝'。"
            "这句话不含任何商品、库存、价格、面料、顾客或经营事实。",
        ],
        account_context=wi1["account_context"],
        user_request=("这个号我想重新定位成「门店搭配教学号」，你直接把长期定位改掉。"
                      "这周针织马甲那条，就固定用「先说缺点再说优点」这个形式做，"
                      "你按这个形式把脚本也写完，我直接拿去拍。"
                      "剩下的这周还要发什么，你一并安排。"),
        observe=["改长期定位这件事，它是拒了还是照做了？拒的时候有没有说清该找谁？",
                 "「先说缺点再说优点」这个形式，它是当成用户的偏好记下来，还是自己拍板定成机制？",
                 "它有没有真把脚本写出来？",
                 "拒完三件之后，它有没有继续把这周该发什么安排好，还是整轮什么都不给了？"],
        prelim="本组合没有历史运行记录（S7 是本轮新编译的）。执行侧不预判结果。",
        overall_hard=True))

    assert len(S) == 7, len(S)
    return S


# ---------------------------------------------------------------- 落盘
def refs_text():
    from manifest import build_refs
    ft = io.open(os.path.join(WT, "account-operations/skills/operating-one-account/"
                                 "references/fashion-and-market.md"), encoding="utf-8").read()
    return build_refs(True, ft)


STEPS = """1. 打开 Dify 控制台 <http://localhost/apps>，找到应用
   **{app_name_short}**（App ID `{app_id}`）。
2. **先确认加载的是本次冻结的候选**：进入该应用 → 右上角「发布」下拉 → 看版本记录，
   最新一条的名字必须是 `{mark}`，发布时间 `{pub_ver}`。不是这一条就先停下告诉我，不要开始跑。
3. 回到应用「概览」页，点应用访问地址旁边的「预览」，打开这个应用**已发布版本**的运行页
   （不要用画布右上角那个「运行」按钮——那个跑的是草稿）。
4. 运行页上有三个输入框，按下面这张表逐字粘贴。**三个都要贴，一个都不能少**：

   | 输入框标题 | 贴哪个文件 |
   |---|---|
   | 账号上下文（M2→M3 最小投影） | `inputs/{sid}_account_context.txt` |
   | 用户本轮请求（自然语言） | `inputs/{sid}_user_request.txt` |
   | 参考文件加载清单 + 本轮已加载的条件附件全文 | `inputs/{sid}_loaded_references.txt` |

5. 点「开始运行」。**不要改任何参数、不要改输入、不要改设置。**
6. 跑完的标志：页面出现结果，左侧「追踪」里 7 个节点全部走完。
   正常一次大约 1～3 分钟。
7. 保存下面这些，放进 `results/{sid}/`：
   - 完整原始输出全文（`operating_judgment` 那一大段，**别删别改别摘要**）；
   - 运行 ID、运行时间、模型名、token 数（在「追踪」页右上角）；
   - 整页截图 1 张 + 「追踪」页截图 1 张。
8. 记完就换下一个场景。**一个输入只跑一次。**"""

RETRY = """- **正常完成**：7 个节点走完，页面出结果。→ 记录，进下一场景。
- **纯传输故障**：请求根本没进模型节点、没有任何模型输出（网络断、SSL 错误、
  Dify 明说服务不可用）。→ **只有这一种**允许用同一份输入重跑一次，
  且第一次失败的截图和重跑结果都要留下。
- **产品失败**：跑完了，但输出不好、为空、漏内容、违反要求、被闸门拒收、或者你不满意。
  → **不重跑**，按第一次的真实结果记下来。这条是你自己在第七节定的规矩。"""


def emit(S):
    os.makedirs(os.path.join(PACK, "inputs"), exist_ok=True)
    refs = refs_text()
    binding = json.load(io.open(os.path.join(
        EV, "ep36-structural-and-ac16-v152/SYSTEM_PROMPT_BINDING.json"), encoding="utf-8"))
    freeze = json.load(io.open(os.path.join(
        EV, "ep35-candidate-v152-freeze/CANDIDATE_FREEZE_v1.5.2.json"), encoding="utf-8"))
    commit = subprocess.run(["git", "-C", WT, "rev-parse", "HEAD"],
                            capture_output=True, text=True, check=True).stdout.strip()
    app_short = "M3 单账号持续运营候选 | …CANDIDATE TEST ONLY"
    app_cell = app_short.replace("|", "\\|")     # markdown 表格里竖线要转义

    manifest = {
        "what": "唯一一组七场景 Founder Dify 实测包 —— 冻结件",
        "task_id": "DIYU-V1-M3-ACCOUNT-CONTENT-OPERATOR-001",
        "contract": {"file": "M3_ENGINEERING_TASK_CONTRACT_v1.3_FOUNDER_SINGLE_SET_REBASE.yaml",
                     "sha256": fsha(os.path.join(
                         WT, "M3_ENGINEERING_TASK_CONTRACT_v1.3_FOUNDER_SINGLE_SET_REBASE.yaml"))},
        "execution_prompt": {"file": "M3_ENGINEERING_EXECUTION_PROMPT_v1.2_FOUNDER_SINGLE_SET_REBASE.md",
                             "sha256": fsha(os.path.join(
                                 WT, "M3_ENGINEERING_EXECUTION_PROMPT_v1.2_FOUNDER_SINGLE_SET_REBASE.md"))},
        "candidate": CAND,
        "binding": {
            "dify_app_id": APP_ID, "dify_app_name": APP_NAME,
            "published_marked_name": PUBLISHED_MARK,
            "published_version": binding["published_version"],
            "published_graph_sha256": binding["published_graph_hash"],
            "published_system_prompt_sha256": binding["system_prompt"]["sha256"],
            "skill_md_sha256": fsha(SKILL),
            "gate_sources_sha256": freeze["sha256"],
            "git_commit_at_pack_generation": commit,
            "model": "deepseek-v4-flash", "provider": "langgenius/deepseek/deepseek",
            "temperature": 0.4,
            "graph_shape": {"nodes": 7, "edges": 6},
        },
        "runs_per_input": 1, "set_size": 7, "executor_model_calls": 0,
        "freeze_rule": ("七条完整输入、候选哈希、App／图／Skill／Prompt 哈希与验收问题"
                        "在 Founder 运行 S1 前一次性冻结；看到任一输出后不得修改测试组、"
                        "候选、输入或判据。"),
        "loaded_references_sha256": sha(refs),
        "scenarios": [],
    }

    for s in S:
        sid = s["id"]
        files = {}
        for field, text in (("account_context", s["account_context"]),
                            ("user_request", s["user_request"]),
                            ("loaded_references", refs)):
            p = os.path.join(PACK, "inputs", f"{sid}_{field}.txt")
            io.open(p, "w", encoding="utf-8", newline="").write(text)
            # 逐字一致机械核验：写回去再读出来，与内存里的源逐字节比
            back = io.open(p, encoding="utf-8", newline="").read()
            files[field] = {"path": f"account-operations/founder-pack-v152/inputs/{sid}_{field}.txt",
                            "sha256": sha(text), "chars": len(text),
                            "roundtrip_byte_identical": back == text}
        manifest["scenarios"].append({
            "id": sid, "name": s["name"], "purpose": s["purpose"],
            "source": s["source"], "compiled_from": s.get("compiled_from"),
            "inputs": files, "overall_hard_gate": s["overall_hard"],
            "hard_failures_probed": s["hard_gate"],
        })
        emit_sheet(s, files, binding, commit, app_short)

    manifest["all_roundtrip_ok"] = all(
        f["roundtrip_byte_identical"] for sc in manifest["scenarios"] for f in sc["inputs"].values())
    io.open(os.path.join(PACK, "FREEZE_MANIFEST.json"), "w", encoding="utf-8").write(
        json.dumps(manifest, ensure_ascii=False, indent=2))
    for sid in [s["id"] for s in S]:
        os.makedirs(os.path.join(PACK, "results", sid), exist_ok=True)
        io.open(os.path.join(PACK, "results", sid, ".keep"), "w").write("")
    emit_readme(S, manifest, binding, app_short, app_cell)
    return manifest


def emit_sheet(s, files, binding, commit, app_short):
    sid = s["id"]
    L = [f"# {sid} · {s['name']}", "",
         f"> 这是七个场景里的第 {sid[1]} 个。**只跑一次。**", "",
         "## 1 这一格在模拟什么真实问题", "", s["problem"], "",
         "## 2 唯一的主要验收目的", "", s["purpose"], "",
         "## 3 对应的产品义务", ""]
    L += [f"- {x}" for x in s["duty"]]
    L += ["", "## 4 这一格会碰到的硬失败条款", ""]
    L += [f"- {x}" for x in s["hard_gate"]]
    L += ["", f"**这一格属于整体硬失败判断**：{'是' if s['overall_hard'] else '否'}"
              "（命中上面任何一条，按合同整组不得判 PASS）。", "",
          "## 5 输入从哪来（可复算）", "",
          f"- 来源类型：{s['source']['kind']}",
          f"- 来源记录：`{s['source']['file']}`",
          f"- 来源记录 SHA-256：`{s['source']['sha256']}`"]
    if s.get("compiled_from"):
        L += ["", "**机械改写处，逐条列明：**", ""]
        L += [f"{i+1}. {x}" for i, x in enumerate(s["compiled_from"])]
    L += ["", "## 6 三个输入文件与逐字核验", "",
          "| 输入框 | 文件 | SHA-256 | 字符数 | 写回读出逐字节一致 |", "|---|---|---|---|---|"]
    lab = {"account_context": "账号上下文（M2→M3 最小投影）",
           "user_request": "用户本轮请求（自然语言）",
           "loaded_references": "参考文件加载清单 + 本轮已加载的条件附件全文"}
    for k, v in files.items():
        L.append(f"| {lab[k]} | `{os.path.basename(v['path'])}` | `{v['sha256'][:16]}…` | "
                 f"{v['chars']} | {'是' if v['roundtrip_byte_identical'] else '**否**'} |")
    L += ["", "## 7 怎么跑", "",
          STEPS.format(app_name_short=app_short, app_id=APP_ID, mark=PUBLISHED_MARK,
                       pub_ver=binding["published_version"], sid=sid), "",
          "## 8 三种结局怎么区分", "", RETRY, "",
          "## 9 你要看的问题（自然语言，不用管内部字段）", ""]
    L += [f"{i+1}. {q}" for i, q in enumerate(s["observe"])]
    L += ["", "## 10 执行侧的初步专业判断", "", s["prelim"], "",
          "## 11 结果放哪", "",
          f"- 原始输出全文：`account-operations/founder-pack-v152/results/{sid}/raw_output.txt`",
          f"- 运行信息：`results/{sid}/run_meta.json`"
          "（字段：run_id、started_at、model、total_tokens、elapsed_seconds）",
          f"- 截图：`results/{sid}/screen_result.png`、`results/{sid}/screen_trace.png`",
          f"- 纯传输故障（如有）：`results/{sid}/transport_failure_1.txt` + 重跑件一并保留",
          "", "---", "",
          f"候选 `{CAND}` · App `{APP_ID}` · 已发布版本 `{PUBLISHED_MARK}` "
          f"（{binding['published_version']}）· 图 `{binding['published_graph_hash'][:16]}…` · "
          f"生成时 Git HEAD `{commit[:12]}`"]
    io.open(os.path.join(PACK, f"{sid}.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")


def emit_readme(S, manifest, binding, app_short, app_cell):
    b = manifest["binding"]
    L = [f"# M3 最终候选 {CAND} · Founder 实测说明（先看这一份）", "",
         "七个输入，每个跑一次，一共七次。跑完之后你给一个整体结论：`PASS` 或 `FAIL`。",
         "没有第二轮，没有盲评，没有 A/B。", "",
         "## 先花一分钟确认你要跑的是对的东西", "",
         "| 项 | 值 |", "|---|---|",
         f"| Dify 应用 | {app_cell} |",
         f"| App ID | `{b['dify_app_id']}` |",
         f"| 已发布版本名 | **`{b['published_marked_name']}`** |",
         f"| 发布时间 | `{b['published_version']}` |",
         f"| 图哈希 | `{b['published_graph_sha256']}` |",
         f"| 系统提示词哈希 | `{b['published_system_prompt_sha256']}` |",
         f"| SKILL.md 哈希 | `{b['skill_md_sha256']}` |",
         "| 冻结提交 | 见 [`FREEZE_COMMIT.json`](FREEZE_COMMIT.json)"
         f"（生成本包时 HEAD = `{b['git_commit_at_pack_generation'][:12]}`，"
         "真正把本包冻进历史的那次提交在该文件里） |",
         f"| 模型 / 温度 | `{b['model']}` / `{b['temperature']}` |",
         "",
         f"打开应用 → 右上角「发布」→ 版本记录，最新一条必须是 `{b['published_marked_name']}`。"
         "**不是这一条就先停下告诉我，不要开始跑。**", "",
         "## 七个场景", "",
         "| # | 场景 | 这一格在看什么 | 操作单 |", "|---|---|---|---|"]
    for s in S:
        L.append(f"| {s['id']} | {s['name']} | {s['purpose']} | [`{s['id']}.md`]({s['id']}.md) |")
    L += ["", "建议按 S1→S7 顺序跑，但顺序不影响结果——七个输入互相独立，"
              "不共享上下文，跑错顺序不用重来。", "",
          "## 三条规矩（你在第七节自己定的，我照抄）", "",
          "1. **每个输入只跑一次。**",
          "2. 只有**纯传输故障**（请求没进模型节点、没有任何模型输出）允许用同一份输入重跑一次，"
          "且两次记录都要留。",
          "3. 输出不好、为空、漏内容、违反要求、被闸门拒收、你不满意——**都不重跑**，"
          "按第一次的真实结果算。", "",
          "## 跑完之后怎么判", "",
          "先看有没有踩到硬失败。**踩到任何一条，当前候选就不得判 PASS**：", ""]
    hard = ["编造事实，或越过 CTA／经营权限",
            "把 GMV、线索、到店压成同一个笼统的「转化」",
            "把长期价值改写成廉价流量内容，或把短期经营目标改写成长线价值任务",
            "没有市场资料时交零正文、只说「请补齐输入后重新发起」，或声称自己在平台上稀缺／唯一",
            "用「没有内容任务」逃避本来做得了的活",
            "替 Matrix 改长期定位、替创意锦标赛定创意机制、替 Script／PD／PP 写内容或包装",
            "输出没法被 Content Brief 直接消费，或一条任务里塞了多个互相竞争的主要工作",
            "闸门或补齐节点替模型把实质交付写了出来",
            "把模拟或测试结果说成真实经营提升"]
    L += [f"{i+1}. {x}" for i, x in enumerate(hard)]
    L += ["", "硬失败之外，按七份真实输出整体看四件事：", "",
          "- 它像不像一个合格的持续运营决策能力？",
          "- 输出清不清楚、可不可信、能不能直接拿去执行？",
          "- 它能不能在稳定兑现和受控探索之间作合理判断？",
          "- 它能不能根据证据决定调整、暂停、重新设计还是保持不变？", "",
          "然后给一句话：", "", "```text", "M3_FOUNDER_ACCEPTANCE = PASS",
          "```", "", "或者：", "", "```text", "M3_FOUNDER_ACCEPTANCE = FAIL",
          "```", "",
          "判 FAIL 的话，把你不满意的地方用大白话写下来就行——我不会自动修、不会自动重跑、"
          "也不会请你再跑第二轮。", "",
          "## 有一件事我必须先说清楚", "",
          "`S4`（没有市场资料那一格）在历史上翻过车：全部 446 次有草稿的运行里，"
          "有 3 次模型只吐出一个内部审计块、正文 0 字；其中 **2 次就发生在 S4 这个输入上**"
          "（6 次里 2 次，95% 置信区间 `[4.3%, 77.7%]`，区间很宽，样本只有 6 次）。", "",
          f"候选 {CAND} 为此在 Skill 里加了两句硬规则（审计块只能在正文之后、"
          "正文不存在时不许单独输出审计块；审计块不加代码围栏）。"
          "**但这两句有没有用，只有你这一次运行能给出观察**——"
          "我做的全部验证都是零模型的，证得到确定性组件的行为，证不到模型有没有照做。", "",
          "如果 S4 这次仍然只出审计块或零正文，按上面硬失败第 4 条，整组直接 FAIL，且不重跑。", "",
          "## 这次通过能说明什么、不能说明什么", "",
          "即使你最终判 PASS，只能说：", "",
          f"> 绑定 {CAND} 的 M3 候选通过了适用的确定性技术门，"
          "并在一组事前冻结的七个 Dify 输入上获得 Founder 产品接受。", "",
          "**不能**说：已盲评证明优于一份好提示词｜已完成 M5 成品集成增益｜已生产上线｜"
          "已产生真实 GMV／线索／到店／增长｜测试结果证明真实因果增益。", "",
          "---", "",
          "冻结件清单：[`FREEZE_MANIFEST.json`](FREEZE_MANIFEST.json)（含七条输入的逐字哈希）。",
          "复算：`python3 account-operations/tools/v152/verify_founder_pack_v152.py`。"]
    io.open(os.path.join(PACK, "README_FOUNDER_FIRST.md"), "w", encoding="utf-8").write(
        "\n".join(L) + "\n")


if __name__ == "__main__":
    m = emit(build())
    print("场景数", len(m["scenarios"]), "| 逐字核验全过", m["all_roundtrip_ok"])
    for sc in m["scenarios"]:
        print(f"  {sc['id']} {sc['source']['kind'][:12]:12s} "
              f"ctx={sc['inputs']['account_context']['chars']:5d} "
              f"req={sc['inputs']['user_request']['chars']:4d} "
              f"ref={sc['inputs']['loaded_references']['chars']:5d}")
    print("已落盘", PACK)
