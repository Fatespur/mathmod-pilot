
import { Compass, Sparkles, ShieldCheck } from 'lucide-react';

interface HeroProps {
  onExplore: () => void;
  onWorkflow: () => void;
}

export const Hero: React.FC<HeroProps> = ({ onExplore, onWorkflow }) => {
  return (
    <div className="relative overflow-hidden pt-12 pb-10 border-b border-sci-border/50 bg-gradient-to-b from-sky-950/20 via-transparent to-transparent">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center relative z-10">
        <div className="inline-flex items-center gap-2 rounded-full border border-sky-500/20 bg-sky-500/10 px-3 py-1 text-xs text-sky-400 mb-5">
          <Sparkles className="h-3.5 w-3.5" />
          <span>AI × 数学建模 × 科学计算全生命周期工业级框架</span>
        </div>

        <h1 className="text-3xl font-extrabold tracking-tight text-white sm:text-5xl lg:text-6xl max-w-4xl mx-auto font-sans leading-tight">
          CUMCM Mathematical Modeling <br />
          <span className="bg-gradient-to-r from-sky-400 via-teal-300 to-emerald-400 bg-clip-text text-transparent">
            Agent Skills Toolkit
          </span>
        </h1>

        <p className="mt-5 text-sm sm:text-base text-slate-300 max-w-2xl mx-auto leading-relaxed">
          从原 CUMCM 竞赛生产工程提炼萃取的标准化 Agent 技能库。
          消除模型机械套用与假大空包装，依靠<strong className="text-sky-300">状态机控制</strong>与<strong className="text-emerald-300">强类型工件契约</strong>，
          让每一个解题步骤都具备数学机理推导与严格可检验性。
        </p>

        <div className="mt-7 flex flex-wrap items-center justify-center gap-3">
          <button
            onClick={onWorkflow}
            className="flex items-center gap-2 rounded-lg bg-sky-500 px-4 py-2 text-xs font-semibold text-white shadow-md hover:bg-sky-400 transition-all cursor-pointer"
          >
            <Compass className="h-4 w-4" />
            <span>交互式探索全生命周期</span>
          </button>
          <button
            onClick={onExplore}
            className="flex items-center gap-2 rounded-lg border border-slate-700 bg-sci-card px-4 py-2 text-xs font-semibold text-slate-200 hover:bg-slate-800 hover:border-slate-600 transition-all cursor-pointer"
          >
            <ShieldCheck className="h-4 w-4 text-emerald-400" />
            <span>查阅 15 个收录技能</span>
          </button>
        </div>

        {/* Life cycle strip */}
        <div className="mt-10 max-w-4xl mx-auto p-3 rounded-xl border border-sci-border bg-sci-surface/60 backdrop-blur-sm">
          <div className="flex flex-wrap items-center justify-between text-xs text-slate-400 font-mono gap-2 px-2">
            <span className="text-sky-400 font-medium">S1 机理分解</span>
            <span>→</span>
            <span className="text-teal-400 font-medium">S2A 数据工程</span>
            <span>→</span>
            <span className="text-emerald-400 font-medium">S2B 反套路选型</span>
            <span>→</span>
            <span className="text-indigo-400 font-medium">S3 算法求解</span>
            <span>→</span>
            <span className="text-amber-400 font-medium">S4 独立验证</span>
            <span>→</span>
            <span className="text-pink-400 font-medium">S5 专业图表</span>
            <span>→</span>
            <span className="text-purple-400 font-medium">S6 规范写作</span>
            <span>→</span>
            <span className="text-emerald-400 font-medium">S7 终审对账</span>
          </div>
        </div>
      </div>
    </div>
  );
};
