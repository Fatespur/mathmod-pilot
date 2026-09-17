import { useState } from 'react';
import { WORKFLOW_STAGES, WorkflowStage } from '../data/workflowData';
import { SKILLS_DATA, SkillItem } from '../data/skillsData';
import { GitBranch, ArrowRight, CornerDownRight, CheckSquare } from 'lucide-react';

interface InteractiveWorkflowProps {
  onSelectSkill: (skill: SkillItem) => void;
}

export const InteractiveWorkflow: React.FC<InteractiveWorkflowProps> = ({ onSelectSkill }) => {
  const [selectedStage, setSelectedStage] = useState<WorkflowStage>(WORKFLOW_STAGES[1]); // Default to S1

  const activeSkills = SKILLS_DATA.filter(
    (s) => s.name === selectedStage.owner_skill || (selectedStage.associated_skills && selectedStage.associated_skills.includes(s.name))
  );

  return (
    <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <GitBranch className="h-5 w-5 text-sky-400" />
            <span>Interactive Modeling Workflow (可交互建模全生命周期)</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            点击下方阶段卡片，探索每个阶段的入口契约、放行门禁与所属 Skill。
          </p>
        </div>
      </div>

      {/* Stage Grid Buttons */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-2 mb-6">
        {WORKFLOW_STAGES.map((st) => {
          const isSelected = selectedStage.id === st.id;
          return (
            <button
              key={st.id}
              onClick={() => setSelectedStage(st)}
              className={`flex flex-col text-left p-3 rounded-xl border transition-all cursor-pointer ${
                isSelected
                  ? 'border-sky-500 bg-sky-950/40 shadow-sm shadow-sky-500/20'
                  : 'border-sci-border bg-sci-surface hover:border-slate-600 hover:bg-slate-800/40'
              }`}
            >
              <div className="flex items-center justify-between w-full mb-1">
                <span className={`font-mono text-xs font-bold px-1.5 py-0.5 rounded ${
                  isSelected ? 'bg-sky-500 text-white' : 'bg-slate-800 text-slate-300'
                }`}>
                  {st.id}
                </span>
                {st.is_conditional && (
                  <span className="text-[10px] text-amber-400 bg-amber-500/10 px-1 rounded border border-amber-500/20">条件</span>
                )}
              </div>
              <div className="text-xs font-semibold text-slate-200 line-clamp-1">{st.name.split('&')[0]}</div>
              <div className="text-[10px] text-slate-400 font-mono mt-1">
                {st.owner_skill}
              </div>
            </button>
          );
        })}
      </div>

      {/* Selected Stage Detail Panel */}
      <div className="rounded-2xl border border-sci-border bg-sci-surface p-5 sm:p-6 shadow-xl">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-sci-border pb-4 mb-5">
          <div>
            <div className="flex items-center gap-2.5">
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/40">
                {selectedStage.id}
              </span>
              <h3 className="text-lg font-bold text-white">{selectedStage.name}</h3>
            </div>
            <p className="text-xs text-slate-300 mt-1.5">{selectedStage.description}</p>
          </div>

          <div className="flex items-center gap-2 self-start md:self-auto">
            <span className="text-xs text-slate-400">前置依赖：</span>
            {selectedStage.depends_on.length > 0 ? (
              selectedStage.depends_on.map((dep) => (
                <span key={dep} className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700">
                  {dep}
                </span>
              ))
            ) : (
              <span className="text-xs text-slate-500 font-mono">无 (入口)</span>
            )}
          </div>
        </div>

        {/* Inputs vs Outputs Artifacts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/60">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-300 mb-2.5">
              <CornerDownRight className="h-4 w-4 text-sky-400" />
              <span>入口工件契约 (Entry Artifacts)</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {selectedStage.entry_artifacts.map((art) => (
                <span key={art} className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800/80 text-sky-300 border border-sky-500/20">
                  {art}
                </span>
              ))}
            </div>
          </div>

          <div className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/60">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-300 mb-2.5">
              <CheckSquare className="h-4 w-4 text-emerald-400" />
              <span>出口放行产物 (Exit Artifacts)</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {selectedStage.exit_artifacts.map((art) => (
                <span key={art} className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800/80 text-emerald-300 border border-emerald-500/20">
                  {art}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Owning Skills */}
        <div>
          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
            本阶段执行与支撑技能 (Associated Skills)
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {activeSkills.map((sk) => (
              <div
                key={sk.name}
                onClick={() => onSelectSkill(sk)}
                className="group p-3 rounded-xl border border-sci-border bg-sci-card hover:border-sky-500/60 hover:bg-slate-800/80 transition-all cursor-pointer"
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span className="font-mono text-xs font-bold text-sky-400 group-hover:text-sky-300 transition-colors">
                    {sk.name}
                  </span>
                  <ArrowRight className="h-3.5 w-3.5 text-slate-500 group-hover:text-sky-400 group-hover:translate-x-0.5 transition-all" />
                </div>
                <div className="text-xs font-medium text-slate-200 mb-1">{sk.title}</div>
                <div className="text-[11px] text-slate-400 line-clamp-2">{sk.description}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
