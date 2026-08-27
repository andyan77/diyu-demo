export const meta = {
  name: 'm3-ab-blind-judging-v4',
  description: 'EP-08 v1.3 单臂盲评：36 份提示词由 args 逐字传入，判定者拿到的就是冻结那 36 份',
  phases: [{ title: 'Judge', detail: '12 个不透明单元 × 3 名互不通气的判定者，各自绝对判定' }],
}

// 与 v3 的实质差别只有一条：提示词**不在这里拼**。
// 它们由 make_judge_prompts_v4.py 在跑之前从单一模板生成、当场核验逐字同构、落盘冻结，
// 再原样从 args 传进来。这样 ADDENDUM_003 §3 的同构约束是构造性成立的，
// 不需要事后再从 harness 记录里把提示词捞出来核验一遍。
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
const results = await parallel(A.prompts.map(p => () =>
  agent(p.prompt, { label: `${p.unit}/j${p.judge}`, phase: 'Judge', schema: SCHEMA })
    .then(v => ({ unit: p.unit, judge: p.judge, verdict: v }))
    .catch(() => null)
))

const ok = results.filter(Boolean)
log(`${ok.length}/${A.prompts.length} 份判定完成`)
return { verdicts: ok, requested: A.prompts.length, returned: ok.length }
