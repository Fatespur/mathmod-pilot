
import { Network, RefreshCw, ArrowRight } from 'lucide-react';
import { REVISION_DAG } from '../data/workflowData';

export const ArchitectureGraph: React.FC = () => {
  return (
    <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          <Network className="h-5 w-5 text-sky-400" />
          <span>Architecture & Revision DAG (架构拓扑与自愈反馈环)</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          数学建模竞赛绝非线性流水线，本框架内置了严格的质量闭环与回退反馈有向图。
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Interactive SVG DAG */}
        <div className="lg:col-span-2 rounded-2xl border border-sci-border bg-sci-surface p-6">
          <h3 className="text-sm font-semibold text-slate-200 mb-4 flex items-center justify-between">
            <span>端到端阶段工件流转拓扑</span>
            <span className="text-xs font-mono text-sky-400 bg-sky-500/10 px-2 py-0.5 rounded border border-sky-500/20">
              Deterministic DAG
            </span>
          </h3>

          <div className="w-full overflow-x-auto py-2">
            <svg viewBox="0 0 760 380" className="w-full h-auto min-w-[650px] font-mono text-xs">
              <defs>
                <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                  <path d="M 0 1 L 10 5 L 0 9 z" fill="#38bdf8" />
                </marker>
                <marker id="arrow-rev" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                  <path d="M 0 1 L 10 5 L 0 9 z" fill="#f43f5e" />
                </marker>
              </defs>

              {/* S0 Orchestration node */}
              <rect x="20" y="40" width="100" height="45" rx="8" fill="#182234" stroke="#818cf8" strokeWidth="1.5" />
              <text x="70" y="62" fill="#fff" textAnchor="middle" fontWeight="bold" fontSize="11">S0 编排</text>
              <text x="70" y="75" fill="#a5b4fc" textAnchor="middle" fontSize="9">orchestrator</text>

              {/* Line S0 -> S1 */}
              <line x1="120" y1="62" x2="160" y2="62" stroke="#38bdf8" strokeWidth="1.5" markerEnd="url(#arrow)" />

              {/* S1 Problem */}
              <rect x="160" y="40" width="110" height="45" rx="8" fill="#182234" stroke="#38bdf8" strokeWidth="1.5" />
              <text x="215" y="62" fill="#fff" textAnchor="middle" fontWeight="bold" fontSize="11">S1 赛题拆解</text>
              <text x="215" y="75" fill="#7dd3fc" textAnchor="middle" fontSize="9">problem-analyzer</text>

              {/* Line S1 -> S2A */}
              <line x1="270" y1="62" x2="310" y2="62" stroke="#38bdf8" strokeWidth="1.5" markerEnd="url(#arrow)" />

              {/* S2A Data */}
              <rect x="310" y="40" width="110" height="45" rx="8" fill="#182234" stroke="#2dd4bf" strokeWidth="1.5" />
              <text x="365" y="62" fill="#fff" textAnchor="middle" fontWeight="bold" fontSize="11">S2A 数据处理</text>
              <text x="365" y="75" fill="#5eead4" textAnchor="middle" fontSize="9">data-processing</text>

              {/* Line S2A -> S2B */}
              <line x1="420" y1="62" x2="460" y2="62" stroke="#38bdf8" strokeWidth="1.5" markerEnd="url(#arrow)" />

              {/* S2B Model Selection */}
              <rect x="460" y="40" width="120" height="45" rx="8" fill="#182234" stroke="#34d399" strokeWidth="1.5" />
              <text x="520" y="62" fill="#fff" textAnchor="middle" fontWeight="bold" fontSize="11">S2B 反套路遴选</text>
              <text x="520" y="75" fill="#6ee7b7" textAnchor="middle" fontSize="9">model-selection</text>

              {/* Line S2B -> S3 */}
              <line x1="580" y1="62" x2="620" y2="62" stroke="#38bdf8" strokeWidth="1.5" markerEnd="url(#arrow)" />

              {/* S3 Solver */}
              <rect x="620" y="40" width="110" height="45" rx="8" fill="#182234" stroke="#60a5fa" strokeWidth="1.5" />
              <text x="675" y="62" fill="#fff" textAnchor="middle" fontWeight="bold" fontSize="11">S3 算法求解</text>
              <text x="675" y="75" fill="#93c5fd" textAnchor="middle" fontSize="9">mle-solver</text>

              {/* Line S3 -> S3-dbg loop */}
              <path d="M 675 85 L 675 140" stroke="#f43f5e" strokeWidth="1.5" strokeDasharray="3,3" markerEnd="url(#arrow-rev)" />
              <rect x="620" y="140" width="110" height="45" rx="8" fill="#2a1215" stroke="#f43f5e" strokeWidth="1.5" />
              <text x="675" y="162" fill="#fda4af" textAnchor="middle" fontWeight="bold" fontSize="11">S3-dbg 故障自愈</text>
              <text x="675" y="175" fill="#f43f5e" textAnchor="middle" fontSize="9">systematic-debugging</text>
              <path d="M 620 162 L 590 162 L 590 85 L 620 85" stroke="#34d399" strokeWidth="1" strokeDasharray="3,3" fill="none" />

              {/* Line S3 -> S4 */}
              <path d="M 675 40 L 675 20 L 520 20 L 520 -5" stroke="none" />
              <path d="M 675 85 L 675 220 L 580 220" stroke="#38bdf8" strokeWidth="1.5" markerEnd="url(#arrow)" />

              {/* S4 Validation */}
              <rect x="460" y="200" width="120" height="45" rx="8" fill="#182234" stroke="#fbbf24" strokeWidth="1.5" />
              <text x="520" y="222" fill="#fff" textAnchor="middle" fontWeight="bold" fontSize="11">S4 独立验证门禁</text>
              <text x="520" y="235" fill="#fcd34d" textAnchor="middle" fontSize="9">model-validation</text>

              {/* Revision S4 -> S2B */}
              <path d="M 520 200 L 520 85" stroke="#f43f5e" strokeWidth="1.5" strokeDasharray="4,3" markerEnd="url(#arrow-rev)" />
              <text x="528" y="145" fill="#f43f5e" fontSize="9">验证失败回退</text>

              {/* Line S4 -> S5 */}
              <line x1="460" y1="222" x2="420" y2="222" stroke="#38bdf8" strokeWidth="1.5" markerEnd="url(#arrow)" />

              {/* S5 Visualization */}
              <rect x="300" y="200" width="120" height="45" rx="8" fill="#182234" stroke="#f472b6" strokeWidth="1.5" />
              <text x="360" y="222" fill="#fff" textAnchor="middle" fontWeight="bold" fontSize="11">S5 图表与架构图</text>
              <text x="360" y="235" fill="#f9a8d4" textAnchor="middle" fontSize="9">scipilot / flowchart</text>

              {/* Line S5 -> S6 */}
              <line x1="300" y1="222" x2="260" y2="222" stroke="#38bdf8" strokeWidth="1.5" markerEnd="url(#arrow)" />

              {/* S6 Writing */}
              <rect x="140" y="200" width="120" height="45" rx="8" fill="#182234" stroke="#22d3ee" strokeWidth="1.5" />
              <text x="200" y="222" fill="#fff" textAnchor="middle" fontWeight="bold" fontSize="11">S6 规范论文写作</text>
              <text x="200" y="235" fill="#67e8f9" textAnchor="middle" fontSize="9">mcm-paper-writing</text>

              {/* Line S6 -> S7 */}
              <path d="M 200 245 L 200 300 L 260 300" stroke="#38bdf8" strokeWidth="1.5" markerEnd="url(#arrow)" />

              {/* S7 Review */}
              <rect x="260" y="280" width="130" height="45" rx="8" fill="#182234" stroke="#34d399" strokeWidth="1.5" />
              <text x="325" y="302" fill="#fff" textAnchor="middle" fontWeight="bold" fontSize="11">S7 终审与对账门禁</text>
              <text x="325" y="315" fill="#6ee7b7" textAnchor="middle" fontSize="9">paper-review</text>

              {/* Revision S7 -> S4 */}
              <path d="M 390 302 L 490 302 L 490 245" stroke="#f43f5e" strokeWidth="1.5" strokeDasharray="4,3" markerEnd="url(#arrow-rev)" />
              <text x="440" y="295" fill="#f43f5e" fontSize="9">数值宏错漏校准</text>

              {/* Final Release */}
              <rect x="440" y="280" width="120" height="45" rx="8" fill="#064e3b" stroke="#10b981" strokeWidth="1.5" />
              <text x="500" y="302" fill="#ecfdf5" textAnchor="middle" fontWeight="bold" fontSize="11">最终竞赛交付包</text>
              <text x="500" y="315" fill="#a7f3d0" textAnchor="middle" fontSize="9">Release Package</text>
              <line x1="390" y1="302" x2="440" y2="302" stroke="#10b981" strokeWidth="1.5" markerEnd="url(#arrow)" />
            </svg>
          </div>
        </div>

        {/* Right: Revision DAG details */}
        <div className="rounded-2xl border border-sci-border bg-sci-surface p-5 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
              <RefreshCw className="h-4 w-4 text-rose-400" />
              <span>核心修订反馈回路 (Revision DAG)</span>
            </h3>
            <div className="space-y-2.5">
              {REVISION_DAG.map((rev, idx) => (
                <div key={idx} className="p-2.5 rounded-xl border border-slate-800 bg-sci-card text-xs">
                  <div className="flex items-center justify-between font-mono mb-1">
                    <span className="text-rose-400 font-semibold">{rev.trigger}</span>
                    <span className="text-[10px] text-slate-400 flex items-center gap-1">
                      {rev.source} <ArrowRight className="h-2.5 w-2.5" /> {rev.target}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-300">{rev.action}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400">
            <span className="text-amber-400 font-semibold">自愈保障</span>：上游修改时，系统自动级联失效所有派生图表与正文，杜绝历史脏数据滞留。
          </div>
        </div>
      </div>
    </section>
  );
};
