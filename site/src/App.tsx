import { useState } from 'react';
import { Navbar } from './components/Navbar';
import { Hero } from './components/Hero';
import { StatsBar } from './components/StatsBar';
import { InteractiveWorkflow } from './components/InteractiveWorkflow';
import { SkillExplorer } from './components/SkillExplorer';
import { ArchitectureGraph } from './components/ArchitectureGraph';
import { WorkflowExample } from './components/WorkflowExample';
import { SkillDetailModal } from './components/SkillDetailModal';
import { Footer } from './components/Footer';
import { SkillItem } from './data/skillsData';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [selectedSkill, setSelectedSkill] = useState<SkillItem | null>(null);

  return (
    <div className="min-h-screen bg-sci-dark text-slate-100 flex flex-col justify-between selection:bg-sky-500/30 selection:text-sky-200">
      <div>
        <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />
        <Hero
          onExplore={() => {
            setActiveTab('skills');
            const el = document.getElementById('skills-section');
            el?.scrollIntoView({ behavior: 'smooth' });
          }}
          onWorkflow={() => {
            setActiveTab('overview');
            const el = document.getElementById('workflow-section');
            el?.scrollIntoView({ behavior: 'smooth' });
          }}
        />
        <StatsBar />

        <main className="pb-16 space-y-8">
          {activeTab === 'overview' && (
            <div id="workflow-section">
              <InteractiveWorkflow onSelectSkill={setSelectedSkill} />
              <div id="skills-section">
                <SkillExplorer onSelectSkill={setSelectedSkill} />
              </div>
              <ArchitectureGraph />
              <WorkflowExample />
            </div>
          )}

          {activeTab === 'skills' && (
            <div id="skills-section">
              <SkillExplorer onSelectSkill={setSelectedSkill} />
            </div>
          )}

          {activeTab === 'architecture' && (
            <div>
              <ArchitectureGraph />
            </div>
          )}

          {activeTab === 'example' && (
            <div>
              <WorkflowExample />
            </div>
          )}
        </main>
      </div>

      <Footer />

      {/* Detail Modal */}
      <SkillDetailModal skill={selectedSkill} onClose={() => setSelectedSkill(null)} />
    </div>
  );
}

export default App;
