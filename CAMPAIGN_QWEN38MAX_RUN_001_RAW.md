# CAMPAIGN_QWEN38MAX_RUN_001_RA

本文件是 Dify 自托管后台数据库中该次运行的原始输出，正文一字未改。
表头之外未增删任何内容；未删除 think、未补写 Final、未纠错、未重排。

## 运行元数据（来源：本机自托管 Dify PostgreSQL 只读查询）

| 字段 | 值 |
|---|---|
| app_id | `f6b6870f-1cba-49e4-a884-8745fa13a8ba` |
| app_name | `DIYU_DEMO_CAMPAIGN_QWEN_V0_1` |
| workflow_id | `93b7e598-d871-4d6f-b6a7-347fc919faa4` |
| run_id | `54bdaeb1-fff0-4b0d-a91d-4e55b51f7954` |
| started_at | `2026-08-20T18:31:34.794795` |
| finished_at | `2026-08-20T18:38:13.996068` |
| status | `succeeded` |
| elapsed_time | `399.201273` 秒 |
| workflow_steps | `3` |
| provider | `langgenius/tongyi/tongyi` |
| exact_model_identifier | `qwen3.8-max` |
| model_plugin_version | `langgenius/tongyi:0.2.13@76feba79a09357673e1ebe24f1ec98123062d3f3198abe08551804def1fcd020` |
| temperature | NOT_AVAILABLE_FROM_BACKEND |
| top_p | `0.8` |
| max_tokens | NOT_AVAILABLE_FROM_BACKEND |
| completion_params 原值 | `{"top_p": 0.8}` |
| finish_reason | `stop` |
| total_tokens | `33115` |
| prompt_tokens | `14438` |
| reasoning_tokens | NOT_AVAILABLE_FROM_BACKEND |
| completion_tokens | `18677` |
| input_file | `CAMPAIGN_QWEN_RUN_001_INPUT.md` |
| input_sha256（后台 workflow_runs.inputs.campaign_input 原值） | `a2a53f2cf7e56104304ddfb3fb90a7ec007cc7a0897ca2499acdd905c6f89f31` |
| DSL 文件 | `DIYU_DEMO_CAMPAIGN_QWEN_V0_1.yml` |
| DSL SHA-256 | `34e22d4f04851d0bcb9c1a25d1820683b1cc0ed17880f9757e0bcc135c6552e4` |
| Campaign Skill 文件 | `Campaign_Orchestrator_v0.1.md` |
| Campaign Skill SHA-256 | `c7ef284e40e7c4cd0d4081632fca7df17bd1a80fbd3f3b5267be4aea1040a0fb` |
| System Prompt 来源 | 本次运行 graph 快照中 LLM 节点 system 消息，与 Campaign_Orchestrator_v0.1.md 逐字一致（SHA-256 相同） |
| 是否取得完整 Final | `是` |
| 是否包含 reasoning / think | `是（正文内 think 块，标签原样保留）` |
| 后台 outputs.reasoning_content 字段 | `空字符串`（后台未单独返回推理内容） |
| 原始输出 SHA-256（后台 outputs.text 原值） | `f5da10e871926de04a872328126ad9eaa880ba22ed9cf9560936bf7996462ba5` |

## 字段说明

- `started_at` / `finished_at` 为数据库存储值；Dify 面板按账号时区 `Asia/Shanghai` 显示，比此处晚 8 小时。
- `reasoning_tokens` 后台 usage 中不存在该字段。
- `model_plugin_version` 取自后台 `plugin_installations` 当前安装值，后台未按运行快照存储插件版本。
- 后台 `outputs.reasoning_content` 为空字符串，推理内容与正文合并返回在 `outputs.text` 中，按合并文本原值完整保存。
- `DSL SHA-256` 对应仓库中已归档的 DSL 文件；该文件是 qwen-max 配置的导出版本。本次运行的模型与 `completion_params` 以上表所列 graph 快照原值为准。

---

## 原始输出（后台 `outputs.text` 原值，一字未改）

<think>
We need answer in Chinese likely. User asks execute Campaign Orchestrator run, output complete but concise Campaign decision package, no method, no thinking. Need use only system and input. Need determine if enough. We have brand facts, confirmed account cards, current materials/resources, min acceptance conditions. Need output markdown format specified. Need not output scripts. Need likely READY_WITH_CONDITIONS? Let's inspect inputs.

We need produce Campaign decision package. Need ensure only facts from input. Main business task: initial autumn commute wardrobe first stage, four weeks. Goals include understand judgment, establish key product version/d搭配 cognition, form role content sources, guide appointment try-on and consult, verify multi-account division. Need choose one primary customer change. We can pick: target 30-45 urban women facing "work/see clients/family/pickup/travel etc multi-scene commute" decision blockage: don't know how to judge if Xuli Ji's autumn commute items suit current life and how to compare/use; after content form judgment about "not uniform must-buy, choose by tasks and conditions" and can decide whether to submit try-on/consult via enterprise WeChat. But primary customer change likely from "seeing similar items but unsure what to compare/exclude" to "can identify which item tasks/conditions fit her and whether to try-on". Need only one. We have accounts: Lin Xu, Zhou Ning, Su He, Chen Wan. Current resources: Lin one 30-min interview + A01; Zhou two 1h shoots + B01/B02; Su one 3h shoot + one 30 min supplement + C01/C02; Chen one 30-min fact confirmation + D01/D02. Production 3 main short videos + 2 lightweight graphic/short clips in 7 days. Platforms not locked? Brand facts: before formal Campaign content brief and A/B, Founder locks one content publishing platform per baseline; cannot test multiple formats. Input says platforms available but final platform待决. This is condition not blocking core content? System says final publishing platform unconfirmed: don't choose platform; condition. So READY_WITH_CONDITIONS likely due platform pending? Also acceptance has confirmed unified entry, owner, substitute, capacity, minimal info, confirmation states. So CTA can be enabled? Yes min acceptance conditions confirmed. But platform not confirmed may affect CTA placement but can still say only enterprise WeChat official customer service. Also need condition: specific SKU facts are registered, so ok. Need maybe no conflict. Need not stop INPUT_INSUFFICIENT because we have task, target, accounts, fact chain, min production. Need maybe output READY_WITH_CONDITIONS due platform待决 and maybe Chen Wan limited capacity not continuous; but acceptance conditions are enough. Also need not overstate. Need choose participating accounts. With 7 days max 3 main videos +2 light. Four accounts? Need minimum sufficient. All four cards confirmed but not necessarily all publish. Need decide main speaker. Which fact chain most complete and directly pushes customer change? Zhou Ning has B01 selection comparison table, can support main chain and two units. Su He has try-on records, can convert to use. Lin has one brand trade-off, good for entry but not enough for continuous. Chen has one store problem and acceptance, limited. For primary customer change maybe customer needs move from "wanting commute clothes but afraid uniform must-buy" to "can compare by wardrobe tasks and decide try-on". Main account could be Zhou Ning because selection comparison helps reduce invalid choices; but customer entry might be Lin Xu's rejection of must-buy list to establish brand judgment. Yet main speaker should from most complete fact chain: Zhou Ning. But can Lin open? Maybe yes: first content Lin A01 as brand trade-off entry: why not must-buy list. Then Zhou Ning main chain: six items tasks and comparison/exclusion. Then Su He: try-on adjustment. Then Chen Wan: acceptance / how to submit. But production capacity: 3 main short videos + 2 lightweight. Need four? Could make Lin as light quote/graphic? Need minimum runnable chain. Could have 3 main videos: Zhou (selection compare), Su (try-on use), Chen (service next step)? Lin maybe light graphic/short clip using A01? Or Lin as finite participating only if A01 can be made as opening within capacity. Need assign roles. Since main customer change includes understanding brand judgment? The task goals include let target understand brand's judgment on mature women commute dressing. Lin's A01 is direct. But only one core content. Could be main speaker? Lin's fact chain less continuous but direct for brand judgment. However main speaker should be most complete and direct. If primary change is "from seeing similar items not knowing compare/exclude to forming selection order and try-on direction", Zhou main. Lin provides brand-level reason why not uniform list. Su provides use. Chen provides action. This seems good.

Need account roles:
- Zhou Ning: main account. Uses B01, B02, IMG-P01, DOC-B01. Customer problem: similar items, what compare/exclude. New judgment: six items have different wardrobe tasks; exclude by structure/combination not slogans; limits to try-on.
- Su He: independent participating. Uses C01, C02, VID-C01, IMG-C02. Problem: how to wear/combine into real scenes. New judgment: same item can adjust formality/layers, but depends on body/scene; not fixed three-piece.
- Lin Xu: limited participating? Uses A01, AUD-A01. Problem: whether brand judgment fits me. New judgment: reject must-buy list, items have fit/non-fit, conditions. Could be first entry if capacity allows. Maybe independent? It adds brand-level judgment not replaceable. But if only 3 main videos +2 light, can include Lin as one light graphic/short clip or maybe main video? Need protect minimum chain. Let's design minimum runnable content chain maybe 3 core units: Zhou -> Su -> Chen. Lin optional triggered if capacity or as light. But goal includes brand judgment; can Zhou cite Lin's A01 and add product comparison? But if Lin not publish, brand judgment still present via Zhou citing founder? Need cross-account citation allowed if source and add judgment. But for account matrix verification maybe need Lin? The business task includes verify multiple IP accounts division. But not necessarily all publish. Could have Lin limited publish if capacity. Since production capacity max 3 main +2 light. We can include 4 accounts with 4 pieces? e.g. 3 main videos: Zhou, Su, Chen; 1 light graphic: Lin; 1 light short slice: maybe Su/Chen? Need not fill quota. Maybe minimum chain: 3 pieces: Zhou main video, Su main video, Chen light graphic? But Chen can only 30min fact confirmation, no continuous appearance; can produce light. Need CTA. If Chen not publish, CTA can be in Zhou/Su content referencing unified entry? But account responsibility says Chen接. For user action, if Chen not publish, can still have other accounts cite entry? The min acceptance says all accounts if reference only unified entry. But Chen account's role is to catch service needs. Maybe include Chen as limited: only if 30min confirmation and store problem D01 can make a light piece: "If you have this kind of question, how to submit". But capacity maybe yes: 2 light图文/short clips can include Lin + Chen. Main videos: Zhou and Su? But max 3 main, can do 2 main +2 light. Minimum chain could be 2 main +1 light? Need enough. Let's think.

Need output "当前产能上限": seven days 3 main short video +2 light graphic/short clips. We should not force all. Need list minimum runnable content chain. Could be:
1. Lin Xu light图文/short: reject must-buy list (A01) entry. (if platform locked and material confirmed)
2. Zhou Ning main video: six items tasks, compare/exclude (B01). main judgment chain.
3. Su He main video: try-on adjustment for meeting/pickup or office temp (C01). 
4. Chen Wan light图文/short: how to submit try-on/consult via enterprise WeChat, min info, states (D01/D02 + acceptance). 
This is 2 main +2 light. But is there a main missing? Could use 3 main: Zhou, Su, maybe Lin? Lin only 30min interview and A01, could be main short video? It says 3 main max. We can set minimum runnable: Zhou main, Su main, Chen light. Lin optional if capacity. But then brand entry not in minimum? Could start with Zhou directly: "Why we don't do must-buy list? from selection comparison". Zhou can cite Lin's A01 and add product comparison. That may be enough. But the task includes brand judgment; Lin's fact can be cited. However account cards: Lin mission brand why choose/reject; if not publish, Zhou can cite but cannot replace brand-level judgment? It can cite and add commodity comparison. But if primary change includes brand fit, maybe Lin needed. Yet minimum sufficient maybe 3 accounts: Zhou main, Su independent, Chen limited. Lin optional. But confirmed account cards include four; not all must fight. Need justify non-participation? If Lin optional, maybe "有限参战" not non. If not in minimum, maybe if capacity insufficient cut Lin first. But if Lin doesn't publish, do we lose unique brand judgment? Zhou can cite A01 but only as brand judgment source; but Zhou's new judgment is commodity comparison. Could still push customer. But the brand-level "why reject must-buy" could be communicated by Zhou citing founder. But account responsibility says Lin explains brand trade-off; maybe if Lin not publish, the matrix lacks that account. But campaign can be single or few accounts. Need choose参战 with necessity. Let's evaluate each:
- Lin: unique brand trade-off A01. Does it directly push main customer change? If main change is about forming judgment of "not buy uniformly, compare by tasks", yes. But only one content. Could be entry. Resource: one 30-min interview, can make one light or main. If capacity enough, include as limited. If not, can be omitted? The main change can still be achieved by Zhou? The customer may need brand trust; but Zhou's selection comparison can demonstrate. Lin adds why brand chooses this approach. Since task includes "understand brand's judgment", Lin seems valuable. But we can include as one light within capacity. Since 2 light available. Good.
- Chen: needed for CTA and service question. But acceptance conditions confirmed, can other accounts state entry? But Chen account unique to catch. However Chen only 30 min fact confirmation; can produce one light. Include limited. If capacity insufficient, CTA can still be in content? System: if entry confirmed, all accounts can reference same entry. But if Chen not publish, user action still possible. But Chen's account role is service. Could decide Chen limited; if not enough, not publish but CTA still can be referenced by main accounts? Need be careful: account card says Chen mission when customer has service need. If no Chen publish, maybe not fulfilling matrix test. But capacity says Chen not guarantee continuous; one 30min. We can include one light. Good.

Four accounts all参战 but with different weights: Zhou main; Su independent; Lin limited; Chen limited. Content total maybe 4 pieces: 2 main videos (Zhou, Su), 2 light (Lin, Chen). Or 3 main videos +1 light? We need ensure within capacity. We can set minimum runnable content chain as 3 pieces: Zhou main, Su main, Chen light. Optional Lin light if capacity and platform locked. But if Lin optional, brand entry maybe optional. However the primary customer change may need brand judgment? We can embed Lin's A01 in Zhou's content as citation. Then minimum still has brand judgment via citation. But if we want account matrix validation, Lin optional not necessary. Yet the input task includes "形成不同组织角色各自可信的内容来源" and verify multi-account division. Minimum with three accounts still verifies some. But four account cards confirmed; maybe expected to use all four? The capacity allows 5 pieces, so can include all four without exceeding. But system says minimum sufficient, not fill quota. Need prove each necessary. If include all four, each has distinct contribution. It's okay if within capacity and not forced. But must give reduction order. Maybe include 4 pieces, optional 5th. Let's decide.

Need also platform: not confirmed. Should not choose platform. We can state publishing platform待 Founder锁定; all content produced as platform-neutral? The brand facts say before formal Campaign制作任务包 and A/B, Founder locks one content publishing platform. Cannot test multiple formats. So condition: before publishing, Founder must lock one platform; current plan does not select platform. Does this block production? Maybe not; can produce content but final format/platform need condition. We can output READY_WITH_CONDITIONS. Current important condition: platform锁定; no additional promises. Also maybe "陈晚出镜/事实确认 only 30min" condition. But acceptance is confirmed. Need "当前不能声称已经具备的条件": platform not selected; no real customer cases; no performance promises; no inventory pressure; no service promises beyond min; no second-store person named; no confirmed reply time; no actual history. Need mention.

Need content target. Need avoid abstract. Let's craft:
优先目标顾客: 30-45 urban women in multi-role commute (work, clients, family, pickup, travel/social), considering autumn clothes but worried about over-formality, repeated items, not knowing which to choose.
当前情境与决策阻塞: She sees many similar commute items and "must-buy" style messages; doesn't know what to compare, whether items fit her real scenes/body; afraid buying invalid or too formal/not enough.
唯一主要顾客变化: From "wanting autumn commute clothes but stuck in similar choices/unclear use" to "able to use wardrobe task and scene conditions to exclude, recognize which Xuli items may be worth trying, and decide whether to submit try-on/consult". Need include new understanding: items have different tasks, no unified must-buy; fit depends on try-on; can form next step.
顾客需要形成的理解、判断或信任: Xuli doesn't push uniform list; selection based on tasks/combination/limits; try-on and scene adjustment matter; store can receive specific questions.
支撑目标: establish cognition of key items (silhouette suit, wide-leg pants, shirt, knit vest, skirt, light jacket); show role division; generate valid store consultation applications. But not main? Actually main customer change includes maybe apply? The final action is apply. But content cannot guarantee conversion.
最终希望采取的行动: through企业微信官方客服 submit到店试穿/搭配咨询申请 with problem/store/date. But only if she has specific problem cannot solve via content.
不能直接归因给内容的结果: actual appointment confirmed, store visit, try-on, transaction, repeat, quota usage, service satisfaction, platform algorithm exposure etc. Need no baseline.
最低可观察信号: Not metrics? System says no fake. Could be: users can state specific problem, intended store, date when submitting; comments/private messages contain specific scene/question/comparison; not just praise. But if platform not confirmed, observation may depend. Need safe: after content, if users ask about specific SKU comparison, scene combination, try-on conditions, or submit min info. Not numbers. Need not set target numbers. Could say minimum observable signal: at least some user inquiries include specific scene/problem rather than generic "how much"; or submitted applications contain three min info. But no baseline; can state qualitative. Need not claim count. Maybe "如有反馈，有效信号是..." not count.

参战账号 table:
- 林序: limited参战 (opening/brand judgment support).依据 A01 confirmed record. Contribution: explain why refuse must-buy list, item fit/non-fit. Conditions: Lin 30min interview completed; platform locked; can be reduced to citation by Zhou if capacity insufficient.
- 周宁: main.依据 B01/B02, two shoots. Contribution: product comparison/exclusion, wardrobe tasks, limits. Conditions: product facts confirmed; two shoots; if no registered facts for SKU, stop.
- 苏禾: independent.依据 C01/C02, one 3h shoot + supplement. Contribution: real try-on/scene combination adjustments; not fixed formulas. Conditions: internal try-on personnel willing on camera? Input says can; must label internal; if cannot label or no try-on record, cancel.
- 陈晚: limited参战/service承接.依据 D01/D02 and acceptance. Contribution: translate service need to next step, min application info, states. Conditions: only 30min fact confirmation; no continuous; if entry/owner/substitute/quota changes, pause CTA.
Maybe also 门店导购团队: fact support not account. Need fact support roles: 导购团队 can provide B-roll and first-line material but no independent account; not package as account owner experience. 内部试穿人员 appear but not real customers. 第二门店当班负责人 substitute only backend, no account.

Non-participating accounts: 门店导购团队 not independent; maybe if no fixed main voice. Also if any of four not used? If Lin optional? But table includes all four. Could have no non-participating except导购团队. But "本轮不参战账号及理由": 门店导购团队 not account. Also maybe if capacity insufficient, Lin or Chen本轮不发布? But table says limited. Need maybe mention if reduction triggers, Lin/Chen can not publish; their facts can be cited. But under not参战 maybe "无其他已确认账号完全不参战；若产能进一步下降，林序/陈晚可降为不发布，仅事实引用". But format asks 本轮不参战账号及理由. Could write "门店导购团队：不独立建号/不作为发布账号；理由..." Also maybe "无其他". Good.

Angles:
林序:
- problem: Is Xuli's choice suitable for my current life? Why not must-buy?
- facts: A01 recording, meeting notes; brand facts; no promise.
- new judgment: brand rejects unified purchase answer; clothes have fit/not fit; choice conditions; leave final choice to customer.
- difference: brand-level trade-off vs Zhou product comparison vs Su use vs Chen service.
- relationship: direct pragmatic, co-judgment, no preaching.
- cite: can cite Zhou/Su/Chen facts + brand value judgment.
- stop: if cannot get Lin 30min or platform not locked? Platform not stop production? maybe if no A01 confirmation or if becomes corporate news.

周宁:
- problem: similar items, what compare/exclude first.
- facts: B01 comparisons for six SKUs, registered materials/prices/structure, photos; B02.
- new judgment: six items tasks; compare shoulder/length/combination, exclude versions not fit; not all necessary; some conclusions need try-on.
- difference: pre-purchase comparison, not try-on or service.
- relationship: screening partner, explicit limits.
- cite: Lin A01 brand trade-off, Su try-on, Chen questions; add comparison.
- stop: if no registered facts or no comparison record.

苏禾:
- problem: how to wear/combine for meeting/pickup/office temp etc.
- facts: C01 three internal try-ons, C02 display adjustment.
- new judgment: formality/layers can adjust; vest not fixed three-piece; skirt/pants change relation; depends on body/shoes/habits; no unified answer.
- difference: actual use after product selection.
- relationship: patient companion, no body judgment; label internal try-on.
- cite: Zhou product facts, Lin brand, Chen service; add use judgment.
- stop: if no real try-on/adjustment or cannot label internal.

陈晚:
- problem: I have specific try-on/consult need, what next?
- facts: D01 anonymous store question, D02 service boundary, Founder confirmed min acceptance.
- new judgment: how to submit min info; difference submitted vs confirmed; who confirms; no promises.
- difference: service landing, not product comparison or outfit plan.
- relationship: reliable现场.
- cite: Zhou/Su facts + service next step.
- stop: if entry/owner/substitute/quota unconfirmed/changed; if cannot 30min confirmation.

Content sequencing:
产能上限: 3 main short videos +2 light图文/short clips; one shoot/edit; single fact confirmation 24h; no external budget; platform待锁定. Need minimum runnable chain. Need table with stages maybe not dates. Since platform not locked, don't specify calendar. Use stages:
Stage 1 entry: Lin Xu light (optional? maybe in minimum? Let's decide). Need minimum chain likely 4 pieces? We can define minimum runnable as 3 units: Zhou main, Su main, Chen light. But then first content Zhou. Does it solve entry? Zhou can start with customer problem "similar commute clothes?" and cite Lin's rejection of must-buy. It can be enough. But if we include Lin as optional, table maybe optional content. However task goal includes brand judgment; maybe we should include Lin in minimum as light. Since capacity allows 2 light; including Lin and Chen. Minimum chain: Lin light, Zhou main, Su main, Chen light = 4 pieces (2 main+2 light). Is that minimum? Could cut Lin if necessary. But "最低可运行内容链" should be the smallest that still achieves primary change and CTA. Maybe 3 pieces: Zhou main, Su main, Chen light. But if no Lin, brand judgment less explicit but still via Zhou citing. Need choose. Since system says minimum sufficient, not fill quota. I'd define minimum as 3: Zhou, Su, Chen. Then optional Lin. But then account table Lin limited? If not in minimum, perhaps optional. But if we list Lin as limited参战, minimum not include? Could be okay: limited参战 only if conditions. But perhaps better: minimum includes Lin because A01 is the entry and unique. Let's assess cognitive progression. Best entry: Lin's rejection of must-buy list. It creates permission to compare rather than buy all. Then Zhou gives comparison. Then Su gives use. Then Chen gives action. That's four. But if capacity insufficient, cut Lin and have Zhou cite. The "minimum runnable" could be four? It uses 2 main +2 light within capacity. But if one piece fails, still can run? Minimum should be smallest safe. Maybe 3: Zhou (includes Lin citation), Su, Chen. Need still CTA. That is robust. But then Lin's account not publishing in minimum, but still参战? Maybe not. Could classify Lin as事实支持与可选发布 rather than参战? But account card has unique mission; if not publishing, maybe fact support. But the input wants verify multi-account; perhaps include four. Let's think from orchestrator: "参战不是长期账号轮流露出，而是本轮内容和证据责任." If Lin only has one A01 and capacity limited, but it adds unique brand judgment. Could be有限参战: only if capacity and platform locked. But if not in minimum, its qualification is conditional. That's acceptable. Need "成立条件". For limited, maybe content can be canceled. Good.

Maybe table:
- 林序: 有限参战（开场品牌取舍，轻量内容；如产能不足可改为周宁引用）
- 周宁: 主讲
- 苏禾: 独立参战
- 陈晚: 有限参战（承接说明；如产能不足可由主内容统一引用入口，但账号可不发）

Minimum runnable chain: 周宁 main -> 苏禾 main -> 陈晚 light. Optional: 林序 light before Zhou if capacity. But if Lin not publish, need Zhou cite A01 to retain brand judgment. That might satisfy. But the primary customer change maybe still. Let's define minimum chain with 3 units:
1. Zhou Ning main video: "Don't compare by must-buy; first see wardrobe tasks" solves entry + comparison. Uses B01, cites A01. New judgment: why not must-buy + six tasks/exclusion. Leaves: how on body/scene? 
2. Su He main video: internal try-on adjustments for meeting/pickup/temperature. Uses C01. New judgment: how adjust; not fixed. Leaves: if still specific fit question, need try-on.
3. Chen Wan light graphic/short: "If you have a specific question, how to submit" uses D01 + acceptance. New judgment: min info, states, no promise. 
This chain is 2 main +1 light. But production capacity has 2 light; optional Lin and maybe Su/Chen slice. Need include optional content:
- Lin Xu light: A01 opening if capacity and platform locked; not necessary if Zhou already cites. Trigger:剪辑完成 and Lin 30min interview; platform locked; no conflict.
- Su He/Chen short slice? Maybe if capacity: a short slice from Su try-on focusing one scene (meeting/pickup) or Chen FAQ. But not needed. Optional content: 苏禾 short slice (from C01) if main video completed; 陈晚补充 short if store question volume. But avoid补量. Could say optional only if真实反馈 asks specific question. Need not fill.

But if we include only 3 minimum, table has four accounts; Lin optional. Need in "本轮不参战账号" maybe Lin? No, if optional有限参战. Hmm.

Maybe better to set all four in minimum but with one as light. Then no optional? But system wants minimum and optional. Four pieces within capacity. Is four minimum? If one fails, can reduce to three. But "minimum" maybe not four. We can say最低可运行内容链: 3 pieces (Zhou, Su, Chen); if capacity permits add Lin as opening. But then Lin not in minimum. The output table can still list Lin有限参战 with成立条件: if included as optional. That's fine.

Need content sequencing table maybe include stage, account, problem, facts confirmer, new judgment, narrative progression, unresolved, publish/cancel conditions.
Let's create table for minimum chain:
Stage 1 (entry/comparison) Zhou Ning. Problem: similar commute items, not know compare/exclude; also why not must-buy. Facts: B01, DOC-B01, IMG-P01; cite AUD-A01 (林序确认). Confirmer: Zhou Ning for商品; Lin Xu for A01 brand取舍. New judgment: six items tasks; exclude收腰/strong shoulder? Need careful: B01 says not choose收腰/强调造型 because current更适合叠穿 and cover meeting/mobile; not represent all. Use. Narrative: from "not must-buy" to "what tasks each item takes". Leaves: how clothes feel on body and scenes.
Publish condition: platform locked; Zhou shoot completed; registered facts confirmed; if no A01 citation remove brand quote not fabricate.
Stage 2 Su He. Problem: how to wear/combine for meeting/pickup/office temp. Facts: C01 records, VID-C01, IMG-C02; product facts from Zhou. Confirmer: Su He for try-on; Zhou for product. New judgment: formality/layers can adjust; vest not fixed; lower garment changes relation; need own try-on. Narrative: from selection to actual body/scene. Leaves: individual fit and store next step.
Condition: internal try-on label; Su shoot; no claims of real customers; if no footage, use photos + oral? maybe can downgrade? If insufficient, delay/cancel.
Stage 3 Chen Wan light. Problem: if still specific fit/service need, what next. Facts: D01 anonymous question, D02 service boundary, Founder confirmed min acceptance. Confirmer: Chen Wan; Founder confirmed entry? Input says Founder confirmed. New judgment: submit via企业微信官方客服 with problem/store/date; submitted待确认 vs预约已确认; no promises. Narrative: from content judgment to service action. Leaves: none; if quota not available remain待确认.
Condition: entry/owner/substitute/quota unchanged; Chen 30min confirmation; if changes pause CTA.

Optional content:
- Lin Xu light: A01 "why not must-buy list" as opening. Trigger: capacity available after minimum; Lin interview; platform locked; need brand-level entry. It uses A01; leaves question "then what to compare" to Zhou. If capacity insufficient, Zhou cites A01.
- Su He short slice or图文: one specific adjustment e.g. shirt sleeve/领口 relax or vest layering, triggered by user questions about layering/temp; only if footage exists and no new shooting needed.
- Chen Wan supplement? maybe if real feedback asks about store process; but Chen limited. Could optional if 30min and capacity. But not necessary. Need maybe no optional to avoid fill. We can list two optional: Lin, Su short slice. Since capacity max 5, minimum 3, optional 2. Good.

Real feedback adjustment: effective feedback includes specific scene, comparison/exclusion reason, variables, misunderstanding, brand/service question. Use to adjust next focus: if many ask vest layering, prioritize Su optional; if ask product comparison, Zhou补充; if ask store process, Chen补充; if misunderstanding of "预约成功", correct; if no effective feedback, continue confirmed chain, not stop. No metrics.

产能不足 reduction order:
1 cancel optional Lin/Su slice; 2 reduce Chen to text/graphic or let main content cite unified entry without Chen publish? But if CTA remains, need only reference entry. Could reduce陈晚发布, but CTA can be in Zhou/Su? System says if unified入口 confirmed, all accounts can reference same entry. But account responsibility? okay. 3 reduce Su main? But then primary change loses use; maybe if Su cannot, Zhou can cite Su? But no, if no try-on content, lower claims. Need protect Zhou main and Chen CTA? Minimum maybe Zhou + Chen? But primary customer change needs use? Could reduce to Zhou + Chen and remove try-on claims. But if Su absent, cannot make specific wearing方案. So reduction order: optional -> 林序 -> 苏禾? But if cut Su, change target to product comparison only and pause wearing advice. Maybe better: protect Zhou main, Su main, Chen light; cut optional first; if still insufficient, Chen can not publish but main videos end with unified entry text (if approved); if still insufficient, only Zhou main with product comparison and no CTA? Need CTA can still if entry confirmed. Hmm.
Need "优先保护事实确认、顾客判断价值和最小完整内容链". Minimum complete chain likely Zhou + Su + Chen. So cut optional. If further cut, remove陈晚发布 but retain entry citation; if further, cancel苏禾 and narrow to product comparison, pause场景搭配 claims; if further, cancel campaign. Need concise.

User action & acceptance:
- desired next step: if specific scene/wardrobe/fit question not solved by content, submit via企业微信官方客服.
- current承接状态: 已具备? Input confirms entry, owner, substitute, quota, min info, states. So yes已具备 for Demo min. But platform待决 not affect acceptance? Could say部分具备? The min conditions are具备; but overall maybe已具备 for统一入口; platform not a承接 condition. However "当前不能声称已经具备" includes final publishing platform. For acceptance: 已具备（按Founder确认的最小承接条件）. But if there are no confirmed reply time etc. Need state.
- 唯一正式入口: 序里集企业微信官方客服.
- 主承接人及替补: 陈晚; 第二门店当班负责人 (no name, no account). 
- 容量:旗舰店4组/日,第二门店2组/日; Demo only, not scarcity.
- 最小必要信息: specific problem, intended store, intended date/time.
- 申请确认履约区别: 提交待确认; only explicit reply store/date/time + "预约已确认" counts; actual履约 later. Need not treat received/transferred as success.
- 内容侧可以表达: can say if specific question, submit via entry; need min info; states; not all problems solved; not promise. Can reference only same entry.
- 不得承诺: reply time, specified staff, duration, complete plan, solve, suitable items, application confirmed, date available, cross-store quota, transaction, scarcity.

异常处理:
- 事实不足: delete no basis -> lower conclusion -> change to answerable question -> delay/no publish. No generic knowledge. Specific: if SKU facts missing, Zhou stop; if try-on missing, Su stop; if store facts missing, Chen stop.
- 产能不足: cut optional, nonessential露出, coverage, complexity; protect confirmed facts and main chain.
- 承接不足: if entry/owner/substitute/quota invalid, pause CTA; keep judgment content if independent. No fake urgency.
- 普通执行 by whom: 周宁商品, 苏禾搭配, 陈晚门店服务, 剪辑/拍摄 schedule by maker? Need assign. Negative comments: account owner + relevant fact confirmer; not Founder unless brand-level.
- Which change returns which step: table maybe text. Need include per system. Could list.
- Founder事项: change task/main customer change/core brand judgment; long-term account mission/权责; major trade-off; formal brand stance/public response; major new resources; new/changed external policy/promise; cancel campaign.
- 可以明确不发: no real record;虚构顾客; unregistered SKU claims; anxiety;重复卖点; platform not locked? Maybe no publish until platform locked. Also if capacity insufficient optional canceled.

进入内容制作前必须确认:
- Founder锁定唯一内容发布平台 (because brand facts require). Is this truly blocking制作? It may block publishing and format, but can produce? System says final platform unconfirmed not block core content? It says usually not block content judgment but condition. But "进入内容制作前" maybe need platform? The input says before formal Campaign制作任务包 and A/B, Founder按基线锁定一个内容发布平台. So yes for制作任务包 maybe must confirm. Also need confirm陈晚出镜/30min? Already can. Need confirm internal try-on personnel出镜? Input says can. Need confirm whether林序 optional included? Maybe not blocking. Need only truly blocking: 唯一发布平台待锁定; if陈晚发布, her 30min fact confirmation scheduling? But input says can. Maybe "无"? But platform is a condition for publishing, not content decision? The prompt says production platform未确认 not block content judgment but must condition. But "进入内容制作前必须确认" maybe list platform. Also maybe if using A01, Lin Xu confirms final expression? Already A01 confirmed? It says可确认、可公开、可制作. But need 24h fact confirmation per piece. Not blocking. Could say: 1 Founder锁定唯一发布平台；2 若启用陈晚承接内容，确认其30分钟事实确认时间；3 若启用林序开场，确认30分钟访谈完成. But "only truly阻塞制作或对外承诺". Since platform is required before formal制作任务包? Yes. Maybe also no other. Need not list routine confirmations.

Need ensure no external facts. Need use only registered SKU facts. We can mention SKU names but no extra. Need avoid "显瘦". Need no numbers for results. Need mention demo simulated? Maybe not necessary but can state not real? In output maybe not. But input says for demo; but Campaign decision package likely for internal. Could mention "本决策包基于SIMULATED_DEMO_FACT". But output format doesn't require. Could include in运行结论 "当前不能声称已经具备" maybe not real customers. Need maybe state all materials are demo simulated? Since only input. But not necessary for campaign. However to avoid misrepresenting, can include "所有试穿为内部Demo试穿人员，不得称现实顾客". Good.

Need be concise but complete. Must not output thinking. Need final in markdown. Need ensure no conflict. No INPUT_CONFLICT. No INPUT_INSUFFICIENT.

Need check step one: main customer change must have both judgment and relationship value. We can phrase: She feels her multi-scene constraints are understood and gains a way to judge. Good.

Need "最低可观察信号": Should not set numbers. Could be:
- 用户咨询中出现具体场景/比较/排除问题（如西装与轻外套任务、马甲叠穿体积、裤长试穿）而非只问价格; 
- 通过统一入口提交的申请包含三项最小信息; 
- 评论/私信能指出事实误解或要求确认条件. 
But "最低" maybe if no signals? Could say if no signals, cannot infer change. Need not claim count. Good.

Need "不能直接归因给内容的结果": appointment confirmed, visit, transaction, repeat, quota consumption, platform traffic, follower growth? Need mention. Good.

Need account table "成立条件" include platform? For all publish: platform locked. But can put global. For each:
林序: A01可公开; 30min interview; platform locked; if not, only citation.
周宁: registered SKU facts and B01; two shoots; platform locked.
苏禾: C01/C02; internal try-on label; shoot; platform locked.
陈晚: D01/D02 + min acceptance unchanged; 30min confirmation; platform locked.

Need "事实支持、出镜、确认与承接角色":
- 林序 confirms A01 brand取舍; appears interview if optional.
- 周宁 confirms商品比较; appears.
- 苏禾 confirms试穿/陈列; internal try-on personnel出镜; not real customers.
- 陈晚 confirms一线问题/服务边界; may appear limited;承接主.
- 第二门店当班负责人替补后台, no出镜/account.
- 门店导购团队: B-roll and first-line facts, no account, not packaged.
- 拍摄/剪辑: one each.
Need maybe mention fact confirmation within 24h.

Need "各账号表达角度" detailed but concise. Need include "不必参与或应停止的条件" for each. Good.

Need content sequencing table: Include publish/cancel conditions. Need maybe use stages not dates. Since platform not locked, no dates. Good.

Need optional content trigger:
- 林序开场轻量: trigger minimum chain confirmed and capacity after; platform locked; need brand entry; if no, don't publish.
- 苏禾短切片: trigger real feedback asks specific叠穿/温差/正式度调整; existing footage enough; no extra shoot; if no, don't.
Maybe also 陈晚补充: if feedback asks entry/process; existing D01; no extra. But capacity maybe. Could list only two. Need maybe optional content not repeat. Good.

Need "真实反馈怎样调整后续": mention effective feedback criteria and actions. Good.

Need "产能不足时的缩减顺序": list ordered.

Need "异常处理与交人": include table? Could bullet. Need include "哪项变化应返回哪一步". Could use bullets matching system.

Need final "进入内容制作前必须确认": maybe:
- Founder锁定唯一发布平台；未锁定前不进入对外发布，也不得多平台测试。
- 如本轮决定发布林序或陈晚内容，确认对应30分钟访谈/事实确认时间；若不发布则不阻塞。
Is second truly blocking? If schedule not set, yes for those pieces. But maybe not "必须" if optional. Could say "若启用...". The prompt says only truly阻塞制作或对外承诺; no otherwise. Maybe:
1. Founder锁定唯一内容发布平台（品牌事实要求，未锁定不能进入正式发布/多格式测试）。
2. 若陈晚承接内容发布，确认其30分钟事实确认完成；否则该条延期，主内容仍可引用统一入口但不得以陈晚账号发布。
Maybe that's enough. But if platform is only condition, maybe output READY_WITH_CONDITIONS. Good.

Need ensure no "提升曝光" etc. Use concrete.

Need think if main customer change includes appointment? System says main customer change is content let customer from state to state; final action separate. So don't make "预约成功" main. Good.

Need maybe choose one primary customer change: "从 '想补初秋通勤衣服但被相似商品和多场景需求困住' 到 '能按衣橱任务和真实场景条件判断哪些值得试穿，并决定是否提交试穿/搭配咨询'". Good.

Need not mention "多账号种草" as goal. But organization verification as support: verify account division. Good.

Need ensure cross-account citations: In angles, mention. In content table, Zhou cites Lin A01; Su cites Zhou product; Chen cites Su/Zhou maybe. Need add source and new judgment.

Potential issue: The input says "在正式生成 Campaign 制作任务包并运行 A/B 前，由 Founder 按《笛语项目基线》的平台待决项锁定一个内容发布平台。不能因品牌具备多渠道而同时测试多种内容格式。" So our Campaign decision package may be before formal制作任务包. We can state platform待锁定; no platform selected. Good.

Need not output "READY" if conditions. Use READY_WITH_CONDITIONS.

Need maybe state "当前最重要成立条件":
- Founder locks platform before publishing;
- 周宁/苏禾/陈晚 fact confirmations within capacity;
- acceptance conditions remain unchanged;
- all试穿 labelled internal.
Maybe "最重要" singular? Could list. The format says当前最重要成立条件. Could write a list. Good.

Need "当前不能声称已经具备的条件":
- 未锁定发布平台;
- 无现实顾客案例/成交/转化;
- 未承诺回复时效/服务结果;
- 无真实历史接待量; quota not scarcity;
- 未登记洗护/防水 etc.
Good.

Need be concise but thorough. Let's draft.

Double-check no unprovided facts: Do not say "门店约600平"? not needed. Do not say "华东新一线"? can mention target city? Not necessary. Do not mention prices? Could mention registered price if needed? Not necessary. Maybe mention SKUs by name and registered facts. Good.

Need ensure no "预约到店试穿和搭配咨询" as CTA? It's allowed because acceptance confirmed. Need say "提交申请" not "预约成功". Good.

Need "唯一主要顾客变化" not multiple. We'll phrase one.

Need "支撑目标" include: establish key item cognition, brand judgment, account division, consultation applications? Wait final action is consultation application.支撑目标 maybe "帮助顾客形成对重点商品版型/搭配认知". But main includes that. Could separate:支撑目标: 1) understand brand取舍; 2) establish six SKU task cognition; 3) verify account division. But don't make parallel main. Good.

Need "最终希望采取的行动" maybe submit application. Good.

Need "最低可观察信号" maybe not count. Good.

Need table with account roles. Use markdown. Ensure not too long but detailed. The desired oververbosity 9, but user says complete but精简. Need balance. Use concise bullets.

Potential issue: The system says "内容目标必须同时具备判断价值和关系价值：顾客不仅能听懂，还应感到自己的真实处境被理解". Need include in target. We'll mention she is understood in multi-scene constraints. Good.

Potential issue: "有效反馈应包含具体场景、问题、比较或排除理由、待验证变量、事实误解或明确的品牌与服务疑问。播放、点赞、泛化称赞、单纯商品喜好和沉默不能单独证明顾客变化". Need include in feedback section. Good.

Potential issue: "已由事实和素材成立的核心内容，不以获得评论或互动作为继续执行的前提." Mention. Good.

Potential issue: "同一事实可以跨账号出现，但不能形成部门墙，也不能把同一卖点改写成多个账号版本。单个议题默认只有一个主要判断责任账号." We can mention in angles and sequence. Good.

Potential issue: "发布账号、出镜人、素材提供者、事实确认人和服务承接人是不同身份". Mention in roles. Good.

Potential issue: "不得因为企业已经拥有评论、私信、客服、企业协作工具、小程序、门店或导购，就自动指定其为正式入口或承接人." We only use confirmed企业微信官方客服. Good.

Potential issue: "申请、确认与履约区别". Include.

Potential issue: "异常发生时返回最上游判断". Include mapping.

Need maybe "当前产能上限" include people. Good.

Let's compose final. Ensure no thought. Use Chinese.

Need decide if state READY_WITH_CONDITIONS. Yes.

Let's draft final in required format.

Detailed content:

# Campaign 决策包

## 0. 运行结论
- 状态：READY_WITH_CONDITIONS
- 适用任务：“初秋通勤衣橱”第一阶段：让目标顾客理解序里集对成熟女性通勤穿着的判断，建立重点商品版型与搭配认知，并在已确认承接条件下引导到店试穿/搭配咨询申请；同时验证账号分工。
- 适用周期：四周经营任务内的首个七天制作周期（资源快照2026-08-20）；不强制每日发布。
- 当前最重要成立条件：
  - Founder 锁定唯一内容发布平台；未锁定前不选择平台，不做多平台/多格式测试。
  - 本轮只使用已登记的六款 SKU 事实、A01/B01/C01/C02/D01 素材和 Founder 已确认的最小承接条件。
  - 苏禾内容必须标注“内部演示试穿人员”，不得包装成现实顾客案例。
  - 陈晚承接内容只在统一入口、主承接人、替补、配额和确认方式不变时发布。
- 当前不能声称已经具备的条件：
  - 未确认最终发布平台。
  - 没有现实顾客案例、成交结果、转化数据或服务效果。
  - 没有回复时效、指定人员、服务时长、完整搭配方案、到店一定解决问题等承诺。
  - Demo 每日确认配额不得解释为稀缺、限量、抢约或真实服务能力。
  - 未登记防水、防风、抗皱、保暖、显瘦、耐磨、洗护等性能。

## 1. 内容目标
- 优先目标顾客：30—45岁城市女性，需要同时应对工作、见客户、家庭聚会、接送孩子、旅行和日常社交的初秋通勤穿着。
- 顾客当前情境与决策阻塞：她想补充通勤衣橱，但面对相似商品、多场景要求和“必买式”表达，不知道先比较什么、先排除什么，也担心买回来不能进入真实生活。
- 唯一主要顾客变化：让她从“想补初秋通勤衣服，但被相似商品和多场景需求困住”进展到“能按衣橱任务、身体感受和生活场景条件判断哪些商品值得试穿，并决定是否提交到店试穿或搭配咨询申请”。
- 顾客需要形成的理解、判断或信任：
  - 序里集不提供统一必买答案，商品有适合与不适合。
  - 选择通勤衣服应先看衣橱任务、版型结构、组合关系和试穿条件。
  - 同一件商品能否进入她的场景，需要结合试穿、比例、已有鞋履和穿着习惯判断。
  - 如有无法靠内容解决的具体问题，可以通过已确认入口提交申请。
- 支撑目标：
  - 建立六款重点商品“分别承担什么衣橱任务”的认知。
  - 展示品牌、商品、搭配、门店服务四类判断的分工。
  - 让顾客感到自己的多场景限制被理解，而不是被年龄或身材焦虑推动。
- 最终希望采取的行动：在形成具体适配疑问后，通过“序里集企业微信官方客服”提交到店试穿或搭配咨询申请。
- 不能直接归因给内容的结果：预约确认、到店、试穿、成交、复购、配额使用、平台流量、粉丝增长、评论数量。
- 最低可观察信号：
  - 用户提问包含具体场景、商品比较、排除理由、试穿条件或事实误解，而不是只问价格或泛泛称赞。
  - 通过统一入口提交的申请包含“具体问题＋意向门店＋意向日期/时间范围”。
  - 没有有效反馈时，不得推断顾客变化已完成。

## 2. 参战账号与主讲关系
Table.

Need ensure table not too wide? Fine.

|账号|本轮身份|参战依据|不可替代贡献|成立条件|
|林序|有限参战/可选开场|A01...|解释拒绝统一必买清单...|30分钟访谈完成...|
|周宁|主讲|B01/B02...|...|...|
|苏禾|独立参战|C01/C02...|...|...|
|陈晚|有限参战/承接说明|D01/D02+承接|...|...|

Need "本轮不参战账号及理由":
- 门店导购团队：不独立建号/不作为发布账号；尚未提供固定可持续主要表达者，也无区别于苏禾/陈晚的独立顾客问题；可作素材来源。 
- 第二门店当班负责人：仅后台替补，不建号、不出镜、不发布。
- 若产能进一步不足，林序/陈晚可降为不发布，其已确认事实可由周宁/苏禾按引用规则使用. Is that "本轮不参战"? Could mention conditional. Good.

"事实支持、出镜、确认与承接角色":
- 林序: confirms A01; optional出镜.
- 周宁: confirms B01商品比较;出镜.
- 苏禾: confirms C01/C02; internal try-on personnel出镜; not real customer.
- 陈晚: confirms D01/D02; limited出镜;主承接.
- 第二门店当班负责人:替补确认配额, no出镜.
- 门店导购团队: B-roll/first-line facts; not packaged.
- 拍摄/剪辑: 1 each; 24h fact confirmation. Good.

## 3. 各账号表达角度
Need subsections. Keep concise.

林序:
- 主要顾客问题: 这个品牌的选择是否适合我当下生活？为什么不做必买清单？
- 一手事实: A01; brand values; no promises.
- 新增判断: brand trade-off: reject unified buy; explain conditions; leave choice.
- 区别: brand取舍 vs商品比较/试穿/服务.
- 关系姿态: direct务实, co-judgment.
- 引用: Zhou/Su/Chen facts + brand value.
- 不必/停止: if no A01 or becomes企业新闻; if capacity不足可改引用.

周宁:
...
Need include specific B01 examples? Yes maybe:
- 六款商品分别承担任务; 未选收腰/强肩西装版本; 未选更宽更亮阔腿裤; 衬衫可单穿/内搭/中间层; 马甲是温差叠穿工具非必买; 半裙轻外套是补充. Need careful not overclaim. Good.

Su: include three records. Good.
Chen: include D01 question and acceptance.

## 4. 内容排序与接力
- 当前产能上限: 3 main short videos +2 light; 1 shoot/1 edit; Lin 30min, Zhou 2x1h, Su 3h+30min, Chen 30min; fact confirm 24h; no external budget; platform待锁定.
- 最低可运行内容链:
Maybe state: 最低为3件：周宁主视频、苏禾主视频、陈晚轻量承接说明；林序为可选开场。 But in table include only minimum? Then optional later. Good.

Table:
|阶段|内容责任账号|要解决的顾客问题|使用真实事实及确认人|新增判断|自然叙事进展|交给下一内容的未解决问题|发布或取消条件|
Stage 1 周宁: ...
Stage 2 苏禾: ...
Stage 3 陈晚: ...

Need maybe include "使用的真实事实及确认人" with names. Good.

For Stage 1 publish condition: platform locked; B01 and SKU facts confirmed; Zhou shoot; if A01 cannot be cited, remove引用, not fabricate. Cancel if no registered facts.
Stage 2: platform locked; C01/C02; Su shoot; internal label; product facts from Zhou; cancel if no real try-on.
Stage 3: platform locked; D01/D02 and承接 conditions unchanged; Chen 30min; if承接变化 pause CTA. If Chen cannot publish, main content can only引用统一入口? But if陈晚 not publish, can still CTA? Maybe condition: if陈晚无法完成，可由周宁/苏禾在已确认入口下做最小说明，但不使用陈晚账号? But account responsibility? Could be okay but need not overcomplicate. Maybe say if陈晚不能完成，该条延期；主内容仍可保留“如需进一步确认，请通过统一入口提交申请”的最小说明，但不得新增服务承诺. However if no Chen fact confirmation, can other accounts state entry? The entry is Founder confirmed, so yes. But for陈晚 account piece, cancel. Good.

Optional content:
- 林序开场轻量图文/短切片: trigger: minimum chain confirmed, capacity remains, platform locked; uses A01; solve brand fit; leaves "how to compare" to Zhou. If capacity不足,由周宁引用A01.
- 苏禾短切片/图文: trigger real feedback asks about马甲叠穿/温差/正式度调整; existing C01 footage; no new shoot; must label internal. If no feedback or no capacity, no publish.
Maybe also陈晚补充? Could skip.

Real feedback adjustment:
- Effective feedback as system. Actions: if specific product comparison -> Zhou; try-on/scene -> Su; entry/process -> Chen; brand取舍 -> Lin optional; misunderstanding of预约 -> correct; no effective feedback -> continue, not stop. No use likes/plays. Good.

产能不足缩减顺序:
1 cancel optional林序/苏禾切片.
2 reduce陈晚 to最小图文/文字引用; if still不足,陈晚账号不发，主内容只引用统一入口.
3 if苏禾素材不足，取消苏禾场景搭配内容，周宁内容降低到商品比较，不写试穿适配.
4 if周宁商品事实不足，取消商品结论，仅保留品牌取舍引用或不发布.
Need protect fact confirmation and min chain. Good.

## 5. 用户行动与承接
- 希望下一步: if specific problem not solved, submit via企业微信.
- 当前承接状态: 已具备（按Founder确认的最小承接条件）.
- 唯一正式入口: 序里集企业微信官方客服.
- 主承接人及替补: 陈晚; 第二门店当班负责人.
- 容量: Demo旗舰店4组/日，第二门店2组/日; not scarcity.
- 最小必要信息: problem, store, date/time.
- 申请确认履约区别: submitted待确认; only explicit reply store/date/time + “预约已确认”; 履约 separate.
- 内容侧可表达: can submit entry, min info, states, no promises; all accounts same entry.
- 不得承诺: list.

## 6. 异常处理与交人
- 事实不足: delete/lower/change/delay; examples.
- 产能不足: cut optional etc.
- 承接不足: pause CTA; keep judgment content if independent; no fake urgency.
- 普通执行问题由谁处理: 周宁 product; 苏禾 try-on; 陈晚 store/service; 拍摄剪辑排期 by制作负责人? Input doesn't name. Could say由拍摄/剪辑与对应账号负责人协商; negative comments by对应负责人; not Founder.
- 哪项变化返回哪一步: list:
  - 经营任务/主顾客变化/核心品牌判断 -> 目标判断，必要时Founder.
  - 参战资格/主讲关系 -> 参战判断.
  - 账号问题/证据/新判断 -> 角度判断.
  - 顺序/数量/发布时间 -> 排序判断.
  - 入口/承接人/替补/容量/确认方式 -> 承接判断，暂停CTA.
- Founder事项: list.
- 可以明确不发: no real record; unregistered claims; anxiety;虚构顾客;重复卖点;平台未锁定前对外发布; optional if capacity不足.

## 7. 进入内容制作前必须确认
- Founder锁定唯一发布平台；未锁定不进入正式发布/多格式测试.
- 若发布林序/陈晚内容，确认对应30分钟访谈/事实确认时间；否则该条延期，不影响周宁/苏禾主链（but if陈晚 affects CTA? entry confirmed so okay). Maybe also confirm internal try-on出镜? Input says can. Not necessary.
Could write:
1. Founder锁定唯一内容发布平台。
2. 若本轮发布陈晚承接内容，确认陈晚一次30分钟事实确认可完成；否则该条延期，统一入口仍可由主内容最小引用。
Maybe if林序 optional: 3. 若发布林序开场，确认林序30分钟访谈可完成. But only truly blocking? It is blocking that piece. Include.

Need maybe no "无". Good.

Double-check: Does platform lock block "制作" or only publish? Input says before formal Campaign制作任务包 and A/B, Founder locks platform. So yes. Good.

Need ensure no mention of "A/B"? Could mention. Fine.

Need maybe "当前产能上限" says max 3 main +2 light. Our minimum 3 and optional 2 fits. Good.

Potential issue: If minimum chain has陈晚 light but platform not locked, can we produce? We condition. Good.

Need ensure no "本周" or dates. Good.

Let's produce final. Ensure no analysis. Use Chinese. Need maybe keep concise but detailed. final.
</think># Campaign 决策包

## 0. 运行结论

- 状态：READY_WITH_CONDITIONS
- 适用任务：“初秋通勤衣橱”第一阶段：让目标顾客理解序里集对成熟女性通勤穿着的判断，建立重点商品版型与搭配认知，并在已确认承接条件下引导到店试穿或搭配咨询申请；同时验证多账号是否能围绕同一经营任务形成分工。
- 适用周期：四周经营任务内的首个七天制作周期；资源快照日期为 2026-08-20。本计划不强制每日发布，也不把七天周期理解为固定发布配额。
- 当前最重要成立条件：
  - Founder 尚未锁定唯一内容发布平台；未锁定前不选择平台，不发布，不做多平台或多格式测试。
  - 本轮只使用已登记的六款 SKU 事实、A01/B01/C01/C02/D01 素材，以及 Founder 已确认的最小承接条件。
  - 苏禾内容必须标注“内部演示试穿人员”，不得包装成现实顾客案例。
  - 陈晚承接内容只在统一入口、主承接人、替补、Demo 配额和确认方式不变时发布。
- 当前不能声称已经具备的条件：
  - 未确认最终发布平台。
  - 没有现实顾客案例、成交结果、转化数据、服务效果或历史接待能力证明。
  - 没有回复时效、指定服务人员、服务时长、完整搭配方案、到店一定解决问题、到店一定有适合商品等承诺。
  - Demo 每日确认配额不得解释为稀缺、限量、抢约或真实服务能力。
  - 未登记防水、防风、抗皱、保暖、显瘦、耐磨、洗护等商品性能，不得补写。

## 1. 内容目标

- 优先目标顾客：30—45 岁城市女性，需要衣服同时应对工作、见客户、家庭聚会、接送孩子、旅行和日常社交。
- 顾客当前情境与决策阻塞：她想为初秋通勤补充衣服，但面对相似商品、多场景要求和“必买式”表达，不知道先比较什么、先排除什么，也担心买回来不能进入真实生活。
- 唯一主要顾客变化：让她从“想补初秋通勤衣服，但被相似商品和多场景需求困住”进展到“能按衣橱任务、身体感受和生活场景条件判断哪些商品值得试穿，并决定是否提交到店试穿或搭配咨询申请”。
- 顾客需要形成的理解、判断或信任：
  - 序里集不提供统一必买答案，商品存在适合与不适合。
  - 选择通勤衣服应先看衣橱任务、版型结构、组合关系和试穿条件，而不是只看表面相似或卖点堆叠。
  - 同一件商品能否进入她的真实场景，需要结合试穿、比例、已有鞋履、活动强度和个人穿着习惯判断。
  - 如有无法靠内容解决的具体问题，可以通过已确认入口提交申请，但提交不等于预约成功。
- 支撑目标：
  - 建立六款重点商品“分别承担什么衣橱任务”的认知。
  - 展示品牌取舍、商品比较、试穿搭配、门店服务四类判断的分工。
  - 让顾客感到自己的多场景限制被理解，而不是被年龄、身材或身份焦虑推动。
- 最终希望采取的行动：在形成具体适配疑问后，通过“序里集企业微信官方客服”提交到店试穿或搭配咨询申请。
- 不能直接归因给内容的结果：预约确认、到店、试穿、成交、复购、配额使用、平台流量、粉丝增长、评论数量。
- 最低可观察信号：
  - 用户提问包含具体场景、商品比较、排除理由、试穿条件、事实误解或明确服务疑问，而不是只问价格、泛泛称赞或单纯表达喜欢。
  - 通过统一入口提交的申请包含“一个具体穿着/衣橱/适配问题＋意向门店＋意向日期或时间范围”。
  - 没有有效反馈时，不得推断顾客变化已完成。

## 2. 参战账号与主讲关系

| 账号 | 本轮身份 | 参战依据 | 不可替代贡献 | 成立条件 |
|---|---|---|---|---|
| 林序 | 有限参战，可选开场 | A01：一次可公开的品牌经营取舍记录，可确认、可公开、可制作 | 解释序里集为什么拒绝“初秋通勤六件必买”式表达，帮助顾客理解品牌取舍与自身生活是否一致 | 林序 30 分钟访谈可完成；发布平台已锁定；如产能不足，可降为被周宁引用的事实来源 |
| 周宁 | 主讲账号 | B01：六款商品选品比较表；B02：周宁可负责的专业判断；IMG-P01 商品图 | 帮助顾客面对相似通勤商品时建立比较顺序和排除顺序，说明六款商品分别承担什么衣橱任务 | 六款 SKU 登记事实不变；周宁两次集中拍摄和发布前事实确认可完成；不得补写未登记性能或适穿结论 |
| 苏禾 | 独立参战账号 | C01：三组内部演示试穿记录；C02：门店陈列调整记录 | 把商品从“选哪件”推进到“怎样试、怎样搭、怎样进入会议/接送/办公温差等真实场景” | 苏禾一次 3 小时试穿拍摄和一次 30 分钟补录可完成；必须标注内部演示试穿人员；不得包装成现实顾客案例 |
| 陈晚 | 有限参战账号，承接说明 | D01：可匿名门店问题记录；D02：当前服务承接状态；Founder 已确认最小承接条件 | 把顾客产生的具体到店试穿或搭配咨询需求接回统一入口，并说清申请、确认与履约区别 | 陈晚一次 30 分钟事实确认可完成；统一入口、主承接人、替补、配额和确认方式不变；不得新增服务承诺 |

### 本轮不参战账号及理由

- 门店导购团队：本轮不独立建号、不作为发布账号。原因是当前夹具未提供固定且可持续的主要表达者，也未形成区别于苏禾和陈晚的独立顾客问题与持续独立判断。导购团队可作为新品到店、试穿反馈、顾客问题、搭配过程和日常服务素材的一线事实来源。
- 第二门店当班负责人：本轮仅作为后台替补承接角色，不新增姓名，不建立 IP 账号，不进入内容发布。
- 若产能进一步不足，林序或陈晚可降为不发布；其已确认事实可由周宁、苏禾按跨账号引用规则使用，但不得改写成他人亲历。

### 事实支持、出镜、确认与承接角色

- 林序：确认 A01 品牌经营取舍记录；如发布林序内容，可出镜一次 30 分钟访谈。
- 周宁：确认 B01 选品比较、商品组合和已登记商品事实；本轮主要出镜账号。
- 苏禾：确认 C01 试穿记录、C02 陈列调整记录和搭配判断；内部演示试穿人员可出镜，但必须标注为内部试穿人员，不得描述为现实顾客。
- 陈晚：确认 D01 门店问题摘要、D02 服务边界和承接说明；本轮可有限出镜或不发布，主要承担主承接人角色。
- 第二门店当班负责人：仅确认第二门店 Demo 配额和替补承接，不出镜、不发布、不建立账号。
- 门店导购团队：提供 BROLL-S01 等现场空镜和一线事实支持，不作为账号主责人亲历表达。
- 拍摄与剪辑：1 名拍摄与现场执行、1 名剪辑；七天内最多完成 3 条主要短视频＋2 条轻量图文或短切片。
- 事实确认：企业内部单条事实确认预计在 24 小时内完成；具体商品、试穿、门店事实由对应负责人确认。

## 3. 各账号表达角度

### 林序

- 主要顾客问题：序里集的选择是否适合我当下的生活？为什么这个品牌不做“必买清单”？
- 本轮一手事实与来源：A01 经营取舍记录，包括否决“初秋通勤六件必买”表达、确认“商品存在适合与不适合”、要求内容说明选择条件。
- 本账号新增判断：解释品牌为什么拒绝统一购买答案，说明这种取舍对顾客的价值；不把品牌坚持包装成万能答案，也不替顾客宣布唯一正确答案。
- 与其他账号的实质区别：林序回答品牌为什么这样选择、拒绝和坚持；周宁回答商品之间怎样比较；苏禾回答商品怎样进入真实穿着；陈晚回答服务需求怎样落地。
- 关系姿态怎样自然进入内容：以直接、务实的方式先给判断，再说明依据、条件和代价；不制造焦虑，不做表演式煽情。
- 可以引用的事实及引用后必须增加的价值：可引用周宁确认的商品事实、苏禾确认的试穿观察、陈晚确认的门店问题；引用后必须增加品牌取舍或顾客价值判断。
- 不必参与或应停止的条件：如果林序 30 分钟访谈无法完成，或内容退化为领导讲话、企业新闻、活动通知，则不发布；产能不足时，A01 可作为周宁内容的引用来源。

### 周宁

- 主要顾客问题：面对几件看起来差不多的通勤衣服，我应该先比较什么、先排除什么？
- 本轮一手事实与来源：B01 六款商品选品比较表、DOC-B01 选品比较与商品组合笔记、IMG-P01 商品图；已登记 SKU 包括 XQ-2501 暮灰廓形西装、XQ-2502 深炭垂感阔腿裤、XQ-2503 雾蓝棉混衬衫、XQ-2504 燕麦针织马甲、XQ-2505 深橄榄 A 字半裙、XQ-2506 石卡其轻外套。
- 本账号新增判断：说明六款商品分别承担什么衣橱任务；解释为什么未选择某些候选版本；指出哪些结论可依据登记事实给出，哪些必须保留到真实试穿。
- 与其他账号的实质区别：周宁处理商品进入顾客选择之前的比较与排除，不处理实际试穿后的身体适配，也不处理门店服务承接。
- 关系姿态怎样自然进入内容：作为顾客的筛选与比较伙伴，不把每件商品都说成值得购买，而是帮助顾客建立排除顺序，主动说明限制。
- 可以引用的事实及引用后必须增加的价值：可引用林序 A01 品牌取舍、苏禾试穿观察、陈晚一线问题；引用后必须增加商品比较、选择条件或排除顺序层面的判断。
- 不必参与或应停止的条件：如果具体 SKU 的材质、价格、版型结构等登记事实缺失或变更，停止对该 SKU 的具体结论；不得补写功能、质量、适穿人群或洗护性能。

### 苏禾

- 主要顾客问题：这件衣服怎样穿、怎样组合，才能进入会议、接送、办公温差、晚间聚会等真实场景？
- 本轮一手事实与来源：C01 三组内部演示试穿记录、VID-C01 原始试穿视频、IMG-C02 陈列调整前后照片；可引用周宁确认的商品事实。
- 本账号新增判断：基于内部试穿和陈列调整，说明同一组合如何通过穿法调整改变正式程度；说明马甲是否成立取决于内搭体积、袖窿空间和使用温度；说明下装变化可以改变整体关系，但不能脱离顾客已有鞋履、活动强度和穿着习惯。
- 与其他账号的实质区别：苏禾处理商品进入真实身体和生活场景后的使用判断，不替代周宁的商品比较，也不替代陈晚的现场承接。
- 关系姿态怎样自然进入内容：耐心陪伴试穿和比较，不评价顾客身体，不急于给唯一答案；允许结论是“不适合”。
- 可以引用的事实及引用后必须增加的价值：可引用周宁确认的商品事实、林序确认的品牌取舍、陈晚确认的一线问题；引用后必须增加试穿、组合、比例或场景使用层面的判断。
- 不必参与或应停止的条件：如果没有真实试穿、陈列或搭配记录，不发布具体搭配结论；不得把内部试穿人员包装成现实顾客，不得声称适合所有职场妈妈或具体气温。

### 陈晚

- 主要顾客问题：我已经有具体到店试穿、搭配咨询或服务需求，下一步应该怎么做？
- 本轮一手事实与来源：D01 可匿名门店问题记录、D02 当前服务承接状态、Founder 已确认的最小承接条件。
- 本账号新增判断：把具体问题接回统一入口，说明申请需要提供的最小信息，说清“已提交，待确认”和“预约已确认”的区别。
- 与其他账号的实质区别：陈晚负责现场服务承接和后续推进，不负责商品选品比较，也不负责形成完整穿着方案。
- 关系姿态怎样自然进入内容：亲切、可靠、有现场感；先确认顾客当前处境，再给出已确认、可执行的下一步，不用热情代替解决问题。
- 可以引用的事实及引用后必须增加的价值：可引用周宁确认的商品事实和苏禾确认的试穿搭配观察；引用后必须补充门店如何承接顾客下一步。
- 不必参与或应停止的条件：如果统一入口、主承接人、替补、Demo 配额或确认方式发生变化，暂停承接类 CTA；如果陈晚 30 分钟事实确认无法完成，该条内容延期或不发。

## 4. 内容排序与接力

- 当前产能上限：
  - 七天内最多完成 3 条主要短视频＋2 条轻量图文或短切片。
  - 1 名拍摄与现场执行、1 名剪辑。
  - 林序一次 30 分钟访谈；周宁两次各 1 小时集中拍摄；苏禾一次 3 小时试穿拍摄和一次 30 分钟补录；陈晚一次 30 分钟事实确认。
  - 单条事实确认预计 24 小时内完成。
  - 未锁定唯一发布平台前，不进入正式发布，不做多平台测试。

- 最低可运行内容链：
  - 最低链为 3 个内容单元：周宁主讲商品比较 → 苏禾主讲试穿与场景使用 → 陈晚轻量承接说明。
  - 林序开场内容为可选；如产能不足，林序不单独发布，A01 可由周宁标明来源后引用。

| 阶段或时间 | 内容责任账号 | 要解决的顾客问题 | 使用的真实事实及确认人 | 新增判断 | 自然叙事进展 | 交给下一内容的未解决问题 | 发布或取消条件 |
|---|---|---|---|---|---|---|---|
| 第一阶段：从“必买焦虑”进入商品比较 | 周宁，主讲 | 顾客面对相似通勤商品，不知道比较什么、先排除什么 | B01 选品比较表、DOC-B01、IMG-P01；可引用 A01。商品事实由周宁确认，A01 由林序确认 | 说明六款商品分别承担不同衣橱任务；解释为什么某些候选版本未被选择；指出哪些结论必须保留到试穿 | 从“为什么不是六件必买”推进到“先按衣橱任务和结构条件比较” | 这些商品穿到真实身体和场景里会怎样？ | 发布平台已锁定；周宁拍摄和事实确认完成；六款 SKU 登记事实不变；如 A01 不能引用，则删除引用，不得虚构 |
| 第二阶段：从商品比较进入真实试穿与场景 | 苏禾，独立参战 | 顾客认可或考虑某件商品，但不知道怎样穿、怎样搭、是否适合会议/接送/温差等场景 | C01 三组内部演示试穿记录、VID-C01、IMG-C02；引用周宁确认的商品事实。试穿与搭配判断由苏禾确认，商品事实由周宁确认 | 说明同一组合可通过穿法调整正式程度；说明马甲不是固定三件套；说明裤装与半裙会改变整体关系，但仍需结合本人试穿、鞋履和习惯 | 从“选哪件”推进到“怎样进入真实身体和生活场景” | 如果仍有个人适配或到店试穿疑问，下一步找谁、怎样提交？ | 发布平台已锁定；苏禾拍摄和补录完成；必须标注内部演示试穿人员；如缺少真实试穿记录，延期或取消 |
| 第三阶段：从内容判断进入服务申请 | 陈晚，有限参战 | 顾客已有具体试穿、搭配咨询或服务需求，但不知道下一步怎么做 | D01 匿名门店问题记录、D02 服务边界、Founder 已确认最小承接条件。门店事实由陈晚确认，承接条件以 Founder 确认文本为准 | 说明可通过企业微信官方客服提交申请；说明最小申请信息；说明“已提交，待确认”不等于“预约已确认” | 从内容判断推进到明确、可承接的下一步 | 无；后续由企业微信承接流程处理 | 发布平台已锁定；陈晚 30 分钟事实确认完成；统一入口、主承接人、替补、配额和确认方式不变；如承接条件变化，暂停该条 CTA |

### 可选内容及触发条件

- 可选内容一：林序开场轻量图文或短切片。
  - 触发条件：最低内容链已确认，发布平台已锁定，林序 30 分钟访谈可完成，且产能仍有空余。
  - 内容责任：林序。
  - 使用事实：A01 经营取舍记录。
  - 作用：在顾客进入商品比较前，先解释序里集为什么拒绝统一必买清单。
  - 取消条件：产能不足时不发布；周宁内容可改为标明来源后引用 A01。

- 可选内容二：苏禾短切片或轻量图文。
  - 触发条件：真实反馈中出现具体的叠穿、温差、正式度、马甲体积感或裤装/半裙切换问题；现有 C01 素材足够；不需要新增拍摄。
  - 内容责任：苏禾。
  - 使用事实：C01 中已有片段或照片。
  - 作用：补充一个更细的场景问题，例如衬衫、马甲、轻外套三层叠穿时的拥挤感如何调整。
  - 取消条件：没有真实反馈触发、产能不足、或需要额外拍摄时不发布。

### 真实反馈怎样调整后续

- 有效反馈包括：具体场景、具体问题、比较或排除理由、待验证变量、事实误解、明确的品牌或服务疑问。
- 播放、点赞、泛化称赞、单纯商品喜好和沉默不能单独证明顾客变化，也不能自动决定账号接力。
- 如果反馈集中在商品比较、版型差异或选品取舍，由周宁调整下一条商品比较重点。
- 如果反馈集中在试穿、比例、叠穿、场景切换，由苏禾基于已有素材补充短切片或图文。
- 如果反馈集中在预约入口、申请信息、确认状态或门店服务，由陈晚在已确认承接条件内补充说明。
- 如果反馈涉及品牌为什么这样选择，可由林序可选内容回应，或由周宁引用 A01 后增加商品层面判断。
- 已由事实和素材成立的核心内容，不以获得评论或互动作为继续执行的前提。

### 产能不足时的缩减顺序

1. 取消林序可选开场内容，将 A01 改为周宁内容中的引用来源。
2. 取消苏禾可选短切片，只保留苏禾一条主要试穿内容。
3. 将陈晚承接内容缩减为轻量图文或最小说明；如仍不足，陈晚账号可不发布，但主内容只能引用已确认统一入口，不得新增服务承诺。
4. 如苏禾素材或确认无法完成，取消苏禾内容；周宁内容只保留商品比较，不表达具体试穿适配结论。
5. 如周宁商品事实或拍摄无法完成，取消具体商品结论；必要时仅保留品牌取舍引用，或整体延期。
6. 任何时候都优先保护事实确认、顾客判断价值和最小完整内容链，不为补齐数量发布重复内容。

## 5. 用户行动与承接

- 希望用户采取的下一步：在识别出一个无法仅凭内容解决的具体穿着、衣橱或适配问题后，通过序里集企业微信官方客服提交到店试穿或搭配咨询申请。
- 当前承接状态：已具备。依据是 Founder 已确认统一正式入口、主承接人、替补、Demo 每日确认配额、最小申请信息、确认状态和流程。
- 唯一正式入口：序里集企业微信官方客服。
- 主承接人及替补：主承接人为陈晚；替补为第二门店当班负责人。第二门店当班负责人仅作为后台运营角色，不新增姓名，不建立 IP 账号，不进入内容发布。
- 容量或受理边界：
  - 旗舰店 Demo 每日最多确认 4 组。
  - 第二门店 Demo 每日最多确认 2 组。
  - 该数字仅为 Demo 确认上限，不得解释为稀缺、限量、抢约、真实服务能力或某日一定还有名额。
- 最小必要信息：
  1. 一个具体穿着、衣橱或适配问题；
  2. 意向门店；
  3. 意向日期或时间范围。
- 申请、确认与履约的区别：
  - 用户通过企业微信官方客服提交最小申请信息后，状态为“已提交，待确认”。
  - 只有企业微信官方客服明确回复已确认门店、已确认日期或时段，并写明“预约已确认”，预约才成立。
  - “已收到”“稍后联系”“已转门店”“正在查询”“已登记意向”“请等待回复”均不等于预约成功。
  - 预约确认后，实际到店服务与履约仍是后续阶段，不得与申请或确认混同。
- 内容侧可以表达什么：
  - 可以说明如有具体问题，可通过唯一正式入口提交申请。
  - 可以说明需要提供哪些最小信息。
  - 可以说明“已提交，待确认”和“预约已确认”的区别。
  - 所有账号只能引用同一入口，不得分别留下不同联系人、二维码、口令或接单方式。
- 当前不得承诺什么：
  - 固定回复时效。
  - 指定服务人员。
  - 固定服务时长。
  - 完整搭配方案。
  - 到店一定解决问题。
  - 到店一定有适合商品。
  - 申请一定得到确认。
  - 某个日期或时段一定可约。
  - 两店配额可以自动互换。
  - 预约会带来成交或其他经营结果。

## 6. 异常处理与交人

- 事实不足：
  - 先删除无依据内容。
  - 其次降低结论强度。
  - 再改到现有事实能够完整回答的问题。
  - 仍不成立则延期或不发。
  - 不得把事实缺口改成通用知识、空泛价值观或“建议咨询”来维持排期。

- 产能不足：
  - 优先取消可选内容。
  - 减少非必要账号露出。
  - 减少覆盖面和重复切片。
  - 降低制作复杂度。
  - 优先保护事实确认、顾客判断价值和最小完整内容链。

- 承接不足：
  - 如统一入口、主承接人、替补、配额或确认方式失效，暂停相关 CTA。
  - 仍有独立判断价值的内容可以继续发布，但不得扩大服务需求。
  - 不得制造名额、排队、库存或“已经约满”等虚假紧迫感。

- 普通执行问题由谁处理：
  - 商品事实、选品比较和 SKU 表达问题，由周宁负责删除、降级、改题或延期。
  - 试穿、搭配、陈列和场景表达问题，由苏禾负责处理。
  - 门店服务、申请说明和承接表达问题，由陈晚负责处理。
  - 拍摄、剪辑、排期等制作问题，由拍摄/剪辑与对应账号负责人协商调整。
  - 普通负面评论和事实误解不交 Founder。

- 哪项变化应返回哪一步：
  - 经营任务、目标顾客变化、唯一主目标或核心品牌判断失效：返回目标判断；必要时交 Founder。
  - 参战资格、主讲关系或独立判断链结构失效：返回参战判断。
  - 账号具体顾客问题、证据使用或新增判断失效：返回角度判断。
  - 顺序、数量、发布时间或普通接力变化：返回排序判断。
  - 入口、承接人、替补、容量或确认方式变化：返回承接判断，并暂停相关 CTA。

- 必须交 Founder 的事项：
  - 改变经营任务、主要顾客变化或核心品牌判断。
  - 长期账号使命或组织权责变化。
  - 重大经营取舍。
  - 正式品牌立场或品牌级公开回应。
  - 重大新增资源投入。
  - 新增或改变对外政策与承诺。
  - 取消整个 Campaign。

- 可以明确不发的情况：
  - 没有真实记录或已确认事实支持。
  - 需要补写未登记商品性能、价格、库存、功能或适穿结论。
  - 把虚构顾客故事包装成真实案例或口碑。
  - 制造年龄、身材或身份焦虑。
  - 多个账号重复表达同一个商品卖点。
  - 发布平台未锁定前进行对外发布或多格式测试。
  - 产能不足时，可选内容、非必要露出和重复切片可直接取消。

## 7. 进入内容制作前必须确认

- Founder 锁定唯一内容发布平台；未锁定前不进入正式发布，也不得多平台或多格式测试。
- 若本轮发布林序开场内容，确认林序 30 分钟访谈可完成；否则该内容延期，A01 可改为周宁内容中的引用来源。
- 若本轮发布陈晚承接内容，确认陈晚 30 分钟事实确认可完成；否则该条延期，主内容仍可在不新增服务承诺的前提下引用已确认统一入口。
