
import { SkillItem } from '../data/skillsData';
import { X, KeyRound, CheckCircle2, ShieldAlert, BookOpen, Terminal } from 'lucide-react';

interface SkillDetailModalProps {
  skill: SkillItem | null;
  onClose: () => void;
}

export const SkillDetailModal: React.FC<SkillDetailModalProps> = ({ skill, onClose }) => {
  if (!skill) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-black/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="relative w-full max-w-3xl max-h-[90vh] flex flex-col rounded-2xl border border-sci-border bg-sci-dark shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-sci-border bg-sci-surface">
          <div className="flex items-center gap-2.5">
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30">
              {skill.stage}
            </span>
            <div>
              <h3 className="text-base font-bold text-white">{skill.title}</h3>
              <p className="text-xs font-mono text-slate-400">${skill.name} • {skill.path}</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors cursor-pointer"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6 text-slate-200">
          {/* Section: Core Function */}
          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <BookOpen className="h-4 w-4 text-sky-400" />
              <span>技能核心功能 (Core Function)</span>
            </h4>
            <p className="text-sm text-slate-200 bg-sci-surface p-3.5 rounded-xl border border-sci-border leading-relaxed">
              {skill.description}
            </p>
          </div>

          {/* Section: Why it matters */}
          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <ShieldAlert className="h-4 w-4 text-emerald-400" />
              <span>准入与设计依据 (Why It Matters)</span>
            </h4>
            <p className="text-xs text-slate-300 bg-sci-surface p-3.5 rounded-xl border border-sci-border leading-relaxed">
              {skill.reason}
            </p>
          </div>

          {/* Section: Artifacts Contracts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-3.5 rounded-xl border border-slate-800 bg-sci-surface">
              <h5 className="text-xs font-semibold text-slate-300 mb-2 flex items-center gap-1.5">
                <KeyRound className="h-4 w-4 text-sky-400" />
                <span>输入工件要求 (Inputs Contract)</span>
              </h5>
              <ul className="space-y-1 text-xs font-mono text-sky-300">
                {skill.inputs.map((inp) => (
                  <li key={inp} className="flex items-center gap-1.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-sky-400" />
                    <span>{inp}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="p-3.5 rounded-xl border border-slate-800 bg-sci-surface">
              <h5 className="text-xs font-semibold text-slate-300 mb-2 flex items-center gap-1.5">
                <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                <span>输出放行产物 (Outputs Contract)</span>
              </h5>
              <ul className="space-y-1 text-xs font-mono text-emerald-300">
                {skill.outputs.map((out) => (
                  <li key={out} className="flex items-center gap-1.5">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                    <span>{out}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Section: Invocation Template */}
          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
              <Terminal className="h-4 w-4 text-amber-400" />
              <span>Agent 提示词调用指令范例</span>
            </h4>
            <div className="rounded-xl border border-slate-800 bg-slate-950 p-3 font-mono text-xs text-slate-300 overflow-x-auto">
              <div className="text-slate-500"># 在 Claude / Codex / Antigravity 交互中唤起:</div>
              <div>使用技能: <span className="text-sky-400">${skill.name}</span></div>
              <div>阶段目标: <span className="text-emerald-400">{skill.description}</span></div>
              <div>输入依赖: <span className="text-slate-400">[{skill.inputs.join(', ')}]</span></div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-between px-6 py-3 border-t border-sci-border bg-sci-surface">
          <span className="text-xs text-slate-400 font-mono">
            依赖前置: {skill.dependencies.length > 0 ? skill.dependencies.join(', ') : '无 (入口阶段)'}
          </span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-800 text-xs font-medium text-slate-200 hover:bg-slate-700 transition-colors cursor-pointer"
          >
            关闭详情
          </button>
        </div>
      </div>
    </div>
  );
};
