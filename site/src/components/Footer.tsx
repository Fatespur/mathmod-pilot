
import { Terminal, Shield, FileText } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-sci-border/80 bg-sci-dark py-8 text-xs text-slate-400">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-slate-300">
          <Terminal className="h-4 w-4 text-sky-400" />
          <span className="font-semibold text-white">CUMCM Mathematical Modeling Skills Toolkit</span>
          <span>— Open-Source Agent Framework</span>
        </div>

        <div className="flex items-center gap-4 text-slate-400">
          <span className="flex items-center gap-1">
            <Shield className="h-3.5 w-3.5 text-emerald-400" /> MIT Licensed
          </span>
          <span>•</span>
          <span className="flex items-center gap-1">
            <FileText className="h-3.5 w-3.5 text-sky-400" /> CUMCM / MCM / ICM Ready
          </span>
        </div>
      </div>
    </footer>
  );
};
