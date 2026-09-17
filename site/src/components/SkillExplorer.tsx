import { useState, useMemo } from 'react';
import { SKILLS_DATA, SkillItem } from '../data/skillsData';
import { SkillCard } from './SkillCard';
import { Search, Filter, Cpu } from 'lucide-react';

interface SkillExplorerProps {
  onSelectSkill: (skill: SkillItem) => void;
}

export const SkillExplorer: React.FC<SkillExplorerProps> = ({ onSelectSkill }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('ALL');

  const categories = useMemo(() => {
    const cats = Array.from(new Set(SKILLS_DATA.map((s) => s.category)));
    return ['ALL', ...cats];
  }, []);

  const filteredSkills = useMemo(() => {
    return SKILLS_DATA.filter((s) => {
      const matchSearch =
        s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        s.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchCategory = selectedCategory === 'ALL' || s.category === selectedCategory;
      return matchSearch && matchCategory;
    });
  }, [searchTerm, selectedCategory]);

  return (
    <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <Cpu className="h-5 w-5 text-sky-400" />
            <span>Skill Catalog & Explorer (技能全景检索)</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            共收录 {SKILLS_DATA.length} 个标准化竞赛技能，支持按名称、阶段或方法论搜索。
          </p>
        </div>

        {/* Search Bar */}
        <div className="relative w-full md:w-72">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="搜索技能名称、阶段、算法..."
            className="w-full rounded-xl border border-sci-border bg-sci-surface pl-9 pr-4 py-2 text-xs text-slate-100 placeholder-slate-500 focus:border-sky-500 focus:outline-none transition-colors"
          />
        </div>
      </div>

      {/* Category Pills */}
      <div className="flex flex-wrap items-center gap-1.5 mb-6">
        <span className="text-xs text-slate-400 flex items-center gap-1 mr-1">
          <Filter className="h-3.5 w-3.5" /> 分类筛选：
        </span>
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1 rounded-lg text-xs font-mono transition-all cursor-pointer ${
              selectedCategory === cat
                ? 'bg-sky-500 text-white font-semibold shadow-sm'
                : 'bg-sci-surface border border-sci-border text-slate-300 hover:border-slate-600'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Cards Grid */}
      {filteredSkills.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredSkills.map((sk) => (
            <SkillCard key={sk.name} skill={sk} onViewDetails={onSelectSkill} />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 border border-dashed border-slate-800 rounded-2xl bg-sci-surface/40">
          <p className="text-sm text-slate-400">未找到匹配的技能，请更换检索词或分类条件。</p>
        </div>
      )}
    </section>
  );
};
