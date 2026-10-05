import React from 'react';
import { 
  ShieldCheck, 
  Headphones, 
  Scale, 
  Filter, 
  Users, 
  FlaskConical, 
  GitMerge, 
  TicketCheck, 
  FileText 
} from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, rubricVersion = 'v1.0' }) {
  const navItems = [
    { id: 'workbench', label: 'Review Workbench', icon: Headphones },
    { id: 'disagreements', label: 'Disagreement Queue', icon: Scale },
    { id: 'sampling', label: 'Smart Sampling', icon: Filter },
    { id: 'simulator', label: 'Persona Simulator', icon: Users },
    { id: 'regression', label: 'Regression Harness', icon: FlaskConical },
    { id: 'release-gate', label: 'CI Release Gate', icon: GitMerge },
    { id: 'tickets', label: 'Closed-Loop Tickets', icon: TicketCheck },
    { id: 'governance', label: 'Quality & Governance', icon: FileText },
  ];

  return (
    <header className="bg-slate-900 border-b border-slate-800 text-white sticky top-0 z-50 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('workbench')}>
            <div className="p-2 bg-indigo-600 rounded-lg shadow-lg flex items-center justify-center">
              <ShieldCheck className="w-6 h-6 text-white" />
            </div>
            <div>
              <span className="text-xl font-bold tracking-tight text-white flex items-center gap-1.5">
                Agent<span className="text-indigo-400">Assure</span>
              </span>
              <span className="text-[10px] text-slate-400 block tracking-wider uppercase font-medium">
                HITL QA & Regression Platform
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex space-x-1 overflow-x-auto py-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-1.5 px-3 py-2 rounded-md text-xs font-semibold transition-all whitespace-nowrap ${
                    isActive
                      ? 'bg-indigo-600 text-white shadow-sm'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Meta Info */}
          <div className="hidden lg:flex items-center space-x-3">
            <span className="px-2.5 py-1 text-xs font-medium bg-slate-800 border border-slate-700 rounded-full text-slate-300">
              Rubric: <strong className="text-indigo-400">{rubricVersion}</strong>
            </span>
            <div className="flex items-center space-x-2 pl-2 border-l border-slate-800">
              <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs text-slate-300 font-medium">Alice (QA Reviewer)</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
