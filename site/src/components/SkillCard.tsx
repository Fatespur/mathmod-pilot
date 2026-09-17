
import { SkillItem } from '../data/skillsData';
import { ArrowRight, KeyRound, CheckCircle } from 'lucide-react';

interface SkillCardProps {
  skill: SkillItem;
  onViewDetails: (skill: SkillItem) => void;
}

export const SkillCard: React.FC<SkillCardProps> = ({ skill, onViewDetails }) => {
  const stageColorMap: Record<string, string> = {
    'S0': 'border-purple-500/30 text-purple-400 bg-purple-500/10',
    'S1': 'border-sky-500/30 text-sky-400 bg-sky-500/10',
    'S2A': 'border-teal-500/30 text-teal-400 bg-teal-500/10',
    'S2B': 'border-emerald-500/30 text-emerald-400 bg-emerald-500/10',
    'S3': 'border-blue-500/30 text-blue-400 bg-blue-500/10',
    'S3-dbg': 'border-rose-500/30 text-rose-400 bg-rose-500/10',
    'S4': 'border-amber-500/30 text-amber-400 bg-amber-500/10',
    'S5A': 'border-pink-500/30 text-pink-400 bg-pink-500/10',
    'S5B': 'border-fuchsia-500/30 text-fuchsia-400 bg-fuchsia-500/10',
    'S6': 'border-cyan-500/30 text-cyan-400 bg-cyan-500/10',
    'Support-PH2': 'border-indigo-500/30 text-indigo-400 bg-indigo-500/10',
    'S7': 'border-emerald-500/30 text-emerald-400 bg-emerald-500/10',
    'Benchmark': 'border-amber-500/30 text-amber-400 bg-amber-500/10',
  };

  const badgeColor = stageColorMap[skill.stage] || 'border-slate-600 text-slate-300 bg-slate-800';

  return (
    <div className="flex flex-col justify-between rounded-2xl border border-sci-border bg-sci-surface p-5 hover:border-slate-600 hover:shadow-lg transition-all group">
      <div>
        <div className="flex items-center justify-between gap-2 mb-3">
          <span className={`text-[11px] font-mono font-semibold px-2 py-0.5 rounded-md border ${badgeColor}`}>
            {skill.stage}
          </span>
          <span className="text-[10px] text-slate-400 font-mono bg-slate-800/80 px-2 py-0.5 rounded">
            {skill.category}
          </span>
        </div>

        <h3 className="text-base font-bold text-white group-hover:text-sky-300 transition-colors">
          {skill.title}
        </h3>
        <p className="text-xs font-mono text-slate-400 mt-0.5">
          ${skill.name}
        </p>

        <p className="mt-2.5 text-xs text-slate-300 line-clamp-3 leading-relaxed">
          {skill.description}
        </p>

        <div className="mt-4 pt-3 border-t border-slate-800 flex flex-col gap-1.5 text-[11px] text-slate-400">
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1"><KeyRound className="h-3 w-3 text-sky-400" /> 输入工件</span>
            <span className="font-mono text-slate-300">{skill.inputs.length} 项</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-1"><CheckCircle className="h-3 w-3 text-emerald-400" /> 输出产物</span>
            <span className="font-mono text-slate-300">{skill.outputs.length} 项</span>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-3">
        <button
          onClick={() => onViewDetails(skill)}
          className="w-full flex items-center justify-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/60 py-2 text-xs font-medium text-slate-200 hover:bg-sky-500 hover:text-white hover:border-sky-500 transition-all cursor-pointer"
        >
          <span>查看技能详情</span>
          <ArrowRight className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
};
