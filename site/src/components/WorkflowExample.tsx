import { useState } from 'react';
import { Lightbulb, Code2, CheckCircle } from 'lucide-react';

export const WorkflowExample: React.FC = () => {
  const steps = [
    {
      step: 'Step 1',
      stage: 'S1 Problem Analysis',
      skill: 'problem-analyzer',
      title: '赛题形式化拆解与硬断言提取',
      content: '以冷链物流疫苗配送路径优化为例：提取医院需求向量 D、单位运费 C、车辆载重与温控保质期硬约束。生成 problem_structure.json 与 hard_assertions.json。',
      code: `{
  "entities": ["Depot", "Hospital_1", "Hospital_2", "Hospital_3"],
  "demands": [120, 80, 150],
  "capacity_max": 400,
  "hard_assertions": [
    {"rule": "capacity_exceeded", "cond": "sum(alloc) <= 400"}
  ]
}`
    },
    {
      step: 'Step 2',
      stage: 'S2B Model Selection',
      skill: 'model-selection',
      title: '执行反套路门禁，构建模型投资组合',
      content: '拒绝无脑调用大模型拟合，构建：[基线] 朴素贪婪最近邻分配 -> [主选] 混合整数线性规划 (MILP) -> [备选] 带有动态退火机制的遗传算法 (GA)。',
      code: `{
  "baseline_family": "Greedy_Heuristic",
  "primary_family": "MILP_Simplex",
  "alternative_family": "Simulated_Annealing_GA",
  "identifiability_verdict": "PROVEN"
}`
    },
    {
      step: 'Step 3',
      stage: 'S3 Solver Execution',
      skill: 'mle-solver',
      title: '算法编写与数值求解',
      content: '组装目标函数与不等式约束矩阵，调用 HiGHS / SciPy 求解器执行最优解搜索，验证所有硬断言全部通过。',
      code: `from scipy.optimize import linprog
res = linprog(c, A_ub=A_ub, b_ub=b_ub, method='highs')
print(f"Optimal Total Cost: {res.fun:.2f} CNY")`
    },
    {
      step: 'Step 4',
      stage: 'S4 Model Validation',
      skill: 'model-validation',
      title: '参数灵敏度与基线超越检验',
      content: '扰动运费参数 ±10% 与需求波动 ±15%，测试解的稳健性。主选 MILP 方案相比贪婪基线成本下降 23.4% (p < 0.001)，放行进入可视化。',
      code: `{
  "superiority_over_baseline": "+23.4%",
  "p_value": 0.0004,
  "sensitivity_envelope": "STABLE",
  "gate_verdict": "PASS"
}`
    },
    {
      step: 'Step 5',
      stage: 'S5 Visualization',
      skill: 'cumcm-academic-flowchart',
      title: '生成学术方法架构图与结论误差带',
      content: '调用学术流程图引擎输出双流路线图（draw.io/SVG/PNG），调用绘图引擎生成出版级灵敏度误差带图。',
      code: `# 生成矢量学术路线图
python cumcm_flowchart.py --input diagram_plan.json --format svg --out flowchart.svg`
    },
    {
      step: 'Step 6',
      stage: 'S6 & S7 Writing & Review',
      skill: 'mcm-paper-writing',
      title: '纯 Markdown 规范论文生成与终审',
      content: '按照国奖优秀论文密度生成包含 OMML 原生公式的正文（PAPER_FINAL.md），通过 paper-review 完成全链数值宏对账。',
      code: `## 四、模型的建立与求解
根据前文假设，冷链总成本函数表示为：
$$ \min Z = \sum_{i=1}^n c_i x_i $$
受限于容量约束：$$ \sum x_i \le Q $$`
    }
  ];

  const [activeStep, setActiveStep] = useState(0);

  return (
    <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-amber-400" />
          <span>Workflow Case Walkthrough (数模竞赛实战示例走查)</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          以冷链资源优化典型赛题为例，演示 6 个核心阶段如何在契约保护下一步步推进至高水平论文。
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Step list selector */}
        <div className="lg:col-span-4 space-y-2">
          {steps.map((s, idx) => (
            <button
              key={idx}
              onClick={() => setActiveStep(idx)}
              className={`w-full flex items-center justify-between p-3 rounded-xl border text-left transition-all cursor-pointer ${
                activeStep === idx
                  ? 'border-sky-500 bg-sky-950/30 text-white shadow-sm'
                  : 'border-sci-border bg-sci-surface text-slate-300 hover:border-slate-700'
              }`}
            >
              <div>
                <div className="text-[10px] font-mono text-sky-400 font-semibold">{s.step} • {s.stage}</div>
                <div className="text-xs font-bold mt-0.5">{s.title}</div>
              </div>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                ${s.skill.split('-')[0]}
              </span>
            </button>
          ))}
        </div>

        {/* Step display container */}
        <div className="lg:col-span-8 rounded-2xl border border-sci-border bg-sci-surface p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-3 mb-4 border-b border-sci-border">
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30">
                {steps[activeStep].stage}
              </span>
              <span className="text-xs font-mono text-slate-400">
                调用技能: <strong className="text-sky-400">${steps[activeStep].skill}</strong>
              </span>
            </div>

            <h3 className="text-base font-bold text-white mb-2">{steps[activeStep].title}</h3>
            <p className="text-xs text-slate-300 leading-relaxed mb-4">
              {steps[activeStep].content}
            </p>

            <div className="rounded-xl border border-slate-800 bg-slate-950 p-4 font-mono text-xs text-slate-200 overflow-x-auto">
              <div className="text-slate-500 mb-1 flex items-center gap-1">
                <Code2 className="h-3.5 w-3.5" /> 产物与执行代码快照:
              </div>
              <pre className="text-sky-300 leading-relaxed">{steps[activeStep].code}</pre>
            </div>
          </div>

          <div className="mt-5 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span>阶段状态：<strong className="text-emerald-400 font-mono">VERIFIED & FROZEN</strong></span>
            <span className="flex items-center gap-1 text-slate-300">
              <CheckCircle className="h-4 w-4 text-emerald-400" />
              <span>数据无泄漏，合规放行</span>
            </span>
          </div>
        </div>
      </div>
    </section>
  );
};
