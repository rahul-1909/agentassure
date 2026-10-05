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
  FileText,
  LayoutDashboard
} from 'lucide-react';
import Badge from './common/Badge';

export default function Navbar({ activeTab, setActiveTab, rubricVersion = 'v1.0' }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'workbench', label: 'Review Workbench', icon: Headphones },
    { id: 'test-cases', label: 'Test Cases', icon: FlaskConical },
    { id: 'release-gate', label: 'Release Gate', icon: GitMerge },
    { id: 'simulator', label: 'Persona Simulator', icon: Users },
    { id: 'tickets', label: 'Tickets', icon: TicketCheck },
    { id: 'sampling', label: 'Risk Queue', icon: Filter },
    { id: 'governance', label: 'Governance', icon: FileText },
  ];

  return (
    <header className="bg-white border-b border-slate-200/90 sticky top-0 z-50 shadow-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div 
            className="flex items-center space-x-3 cursor-pointer shrink-0" 
            onClick={() => setActiveTab('dashboard')}
          >
            <div className="w-9 h-9 bg-[#0066FF] rounded-xl flex items-center justify-center shadow-sm">
              <ShieldCheck className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="text-lg font-bold tracking-tight text-slate-900 flex items-center gap-0.5">
                Agent<span className="text-[#0066FF]">Assure</span>
              </span>
              <span className="text-[10px] text-slate-400 block tracking-wider uppercase font-semibold">
                Enterprise AI QA
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex space-x-1 overflow-x-auto py-2 px-2 scrollbar-none">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all whitespace-nowrap ${
                    isActive
                      ? 'bg-blue-50 text-[#0066FF] font-semibold shadow-xs'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/70'
                  }`}
                >
                  <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-[#0066FF]' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Meta Info */}
          <div className="hidden lg:flex items-center space-x-3 shrink-0">
            <span className="px-2.5 py-1 text-xs font-medium bg-slate-100 rounded-full text-slate-600 border border-slate-200/80">
              Rubric: <strong className="text-[#0066FF]">{rubricVersion}</strong>
            </span>
            <div className="flex items-center space-x-2 pl-2 border-l border-slate-200">
              <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs text-slate-700 font-medium">Alice (Lead QA)</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
