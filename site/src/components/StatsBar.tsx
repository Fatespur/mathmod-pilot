
import { Cpu, GitFork, FileCode2, CheckCircle2 } from 'lucide-react';
import { SKILLS_DATA } from '../data/skillsData';
import { WORKFLOW_STAGES } from '../data/workflowData';

export const StatsBar: React.FC = () => {
  const stats = [
    { label: '收录核心 Skill', value: `${SKILLS_DATA.length} 个`, desc: '杜绝模板化，只收录实战能力', icon: Cpu, color: 'text-sky-400' },
    { label: '建模生命周期阶段', value: `${WORKFLOW_STAGES.length} 阶`, desc: '覆盖 S0 至 S7 全闭环', icon: GitFork, color: 'text-teal-400' },
    { label: '独立 CLI 与核心脚本', value: '70+ 个', desc: '去耦本地路径，开箱即用', icon: FileCode2, color: 'text-emerald-400' },
    { label: '跨阶段工件传递门禁', value: '14 处', desc: 'SHA-256 哈希签名，数据不穿越', icon: CheckCircle2, color: 'text-amber-400' },
  ];

  return (
    <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {stats.map((s, idx) => {
          const Icon = s.icon;
          return (
            <div
              key={idx}
              className="flex items-center gap-3.5 rounded-xl border border-sci-border bg-sci-surface/80 p-3.5 transition-all hover:border-slate-600"
            >
              <div className={`p-2 rounded-lg bg-slate-800/80 border border-slate-700/60 ${s.color}`}>
                <Icon className="h-5 w-5" />
              </div>
              <div>
                <div className="text-xl font-bold font-mono text-white tracking-tight">{s.value}</div>
                <div className="text-xs font-medium text-slate-300">{s.label}</div>
                <div className="text-[10px] text-slate-400">{s.desc}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
