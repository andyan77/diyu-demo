export const meta = {
  name: 'm3-ab-blind-judging-v4',
  description: 'EP-08 v1.3 单臂盲评：判定者逐字读冻结的提示词文件，本文件不重建提示词',
  phases: [{ title: 'Judge', detail: '12 个不透明单元 × 3 名互不通气的判定者，各自绝对判定' }],
}

// 与 v3 的实质差别只有一条：提示词**不在这里拼**。
// 它们由 make_judge_prompts_v4.py 在跑之前从单一模板生成、当场核验逐字同构、落盘冻结；
// 本文件只让每名判定者去读属于他的那一份。这样 ADDENDUM_003 §3 的同构约束
// 是构造性成立的，不需要事后再从 harness 记录里把提示词捞出来核验一遍。
const A = args
const DIMS = ['运营判断', '周期组合', '产能取舍', '实验设计', '反馈判断', '内容任务质量', '共同质量底线']
const GATES = ['目标忠实', '事实', '权限', '风险', '当前任务必要条件']

const SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['unit', 'hard_gates', 'dimensions', 'protocol_selfcheck'],
  properties: {
    unit: { type: 'string' },
    hard_gates: {
      type: 'object', additionalProperties: false, required: GATES,
      properties: Object.fromEntries(GATES.map(g => [g, {
        type: 'object', additionalProperties: false, required: ['verdict', 'evidence'],
        properties: {
          verdict: { type: 'string', enum: ['满足', '实质退化'] },
          evidence: { type: 'string', description: '可核查的证据位置或原句，不得只写结论' },
        },
      }])),
    },
    dimensions: {
      type: 'object', additionalProperties: false, required: DIMS,
      properties: Object.fromEntries(DIMS.map(d => [d, {
        type: 'object', additionalProperties: false, required: ['grade', 'reason'],
        properties: {
          grade: { type: 'string', enum: ['优秀', '合格', '勉强', '不足', '缺失', '不适用'] },
          reason: { type: 'string', description: '一句可核查的理由，指向输出里的具体位置' },
        },
      }])),
    },
    protocol_selfcheck: {
      type: 'object', additionalProperties: false,
      required: ['files_read', 'guessed_identity', 'guess_basis'],
      properties: {
        files_read: { type: 'array', items: { type: 'string' } },
        guessed_identity: { type: 'string', description: '你猜这份输出来自什么样的提示词？不知道就写 不知道' },
        guess_basis: { type: 'string', description: '如果猜了，凭什么猜的；没猜就写 无' },
      },
    },
  },
}

phase('Judge')

// 派发指令本身也是同构的：36 条只在文件名一处不同。
// 判定者**逐字读那份冻结的提示词文件**再照做 —— 提示词不经过这里重建，
// 所以"判定者拿到的就是 make_judge_prompts_v4.py 冻结的那 36 份"是可核对的事实，
// 而不是本文件的一句承诺。unblind_v4.py 的 T-3 会把这 36 个文件逐份哈希比对。
const jobs = []
for (const unit of A.units) {
  for (let j = 1; j <= A.judgesPerUnit; j++) {
    jobs.push({ unit, judge: j })
  }
}

const results = await parallel(jobs.map(p => () =>
  agent(
    `打开文件 ${A.promptsDir}/${p.unit}_j${p.judge}.txt，逐字阅读，` +
    `然后完全按它写的去做。那份文件是你的全部任务说明，不要额外揣测。`,
    { label: `${p.unit}/j${p.judge}`, phase: 'Judge', schema: SCHEMA })
    .then(v => ({ unit: p.unit, judge: p.judge, verdict: v }))
    .catch(() => null)
))

const ok = results.filter(Boolean)
log(`${ok.length}/${jobs.length} 份判定完成`)
return { verdicts: ok, requested: jobs.length, returned: ok.length }
