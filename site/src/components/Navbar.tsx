
import { Layers, Terminal, ExternalLink } from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-sci-border/80 bg-sci-dark/90 backdrop-blur-md">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-sky-500/10 border border-sky-500/30 text-sky-400">
            <Layers className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-semibold tracking-tight text-white font-mono text-base">CUMCM Modeling Skills</span>
              <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-xs font-medium text-emerald-400 border border-emerald-500/20">v1.0.0</span>
            </div>
            <p className="text-[11px] text-slate-400">Agent-Native Mathematical Modeling Toolkit</p>
          </div>
        </div>

        <nav className="hidden md:flex items-center gap-1">
          {[
            { id: 'overview', label: '工作流总览' },
            { id: 'skills', label: '技能矩阵' },
            { id: 'architecture', label: 'DAG 与反馈环' },
            { id: 'example', label: '竞赛实战示例' },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`rounded-md px-3.5 py-1.5 text-xs font-medium transition-all ${
                activeTab === item.id
                  ? 'bg-sky-500/10 text-sky-400 border border-sky-500/30'
                  : 'text-slate-300 hover:bg-slate-800/60 hover:text-white'
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <a
            href="https://github.com/Fatespur/mathmod-pilot"
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/80 px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-700 hover:text-white transition-all shadow-sm"
          >
            <Terminal className="h-3.5 w-3.5 text-sky-400" />
            <span>GitHub</span>
            <ExternalLink className="h-3 w-3 opacity-60" />
          </a>
        </div>
      </div>
    </header>
  );
};
