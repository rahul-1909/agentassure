import React from 'react';
import { 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  Ticket, 
  TrendingUp, 
  ArrowRight, 
  Cpu, 
  FileText,
  Sparkles
} from 'lucide-react';
import Card from './common/Card';
import Badge from './common/Badge';
import Button from './common/Button';

export default function DashboardView({
  qualityReport,
  tickets = [],
  testCases = [],
  onNavigate,
  onReviewConversation,
}) {
  const slaPct = qualityReport?.review_sla_compliance_pct ?? 100.0;
  const kappaScore = qualityReport?.inter_rater_kappa ?? 0.88;
  const reviewedCount = qualityReport?.total_reviewed ?? 142;
  const pendingCount = qualityReport?.pending_review ?? 8;
  const testsPassingPct = 94.2;

  const failureCategories = [
    { name: 'Hallucination & KB Mismatch', count: 45, pct: 45, color: '#EF4444' },
    { name: 'Context Loss & State Drift', count: 30, pct: 30, color: '#F59E0B' },
    { name: 'Intent Misread & Loop', count: 15, pct: 15, color: '#8B5CF6' },
    { name: 'ASR Acoustic Jitter', count: 10, pct: 10, color: '#EC4899' },
  ];

  const recommendedActions = [
    {
      id: 'rec-1',
      title: 'Review "Agent quotes unauthorized interest rate"',
      description: '47 detected failures in loan quote turns. Absence of KB APR rate cap validation.',
      impact: '-15% Hallucination Regression',
      actionText: 'Review Now',
      targetTab: 'workbench',
    },
    {
      id: 'rec-2',
      title: 'Update Knowledge Base with RBI Master Directions 2026',
      description: '23 customer conversations flagged with missing regulatory compounding disclosures.',
      impact: '-8% Compliance Breaches',
      actionText: 'View Failures',
      targetTab: 'test-cases',
    },
    {
      id: 'rec-3',
      title: 'Stress-test with Hinglish Bargain Hunter persona',
      description: 'Candidate agent v2.5.0-candidate showed potential drop-off on code-switching hagglers.',
      impact: '+12% Objection Handling Stability',
      actionText: 'Launch Simulation',
      targetTab: 'simulator',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-gradient-to-r from-blue-50/80 via-white to-slate-50 p-6 rounded-2xl border border-blue-100/80">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-[#0066FF] bg-blue-100/80 px-2 py-0.5 rounded-full">
              System Overview
            </span>
            <span className="text-xs text-slate-500 font-medium">Production v2.4.0 • Gated Release Pipeline</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900 mt-1 tracking-tight">Quality Assurance Intelligence</h1>
          <p className="text-sm text-slate-600 mt-1">
            Real-time conversational AI regression monitoring, human-in-the-loop review velocity, and release safety.
          </p>
        </div>
        <div className="flex items-center gap-2.5">
          <Button variant="outline" size="md" onClick={() => onNavigate('test-cases')}>
            Browse 847 Tests
          </Button>
          <Button variant="primary" size="md" icon={ShieldCheck} onClick={() => onNavigate('release-gate')}>
            Evaluate Gate
          </Button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Quality Score</span>
            <div className="w-8 h-8 rounded-lg bg-blue-50 text-[#0066FF] flex items-center justify-center">
              <TrendingUp className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-3xl font-bold text-slate-900 tracking-tight">3.8 <span className="text-sm font-normal text-slate-500">/ 5.0</span></div>
            <div className="flex items-center gap-1.5 mt-1 text-xs text-emerald-600 font-medium">
              <span>+0.3 vs last month</span>
              <span className="text-slate-400">•</span>
              <span className="text-slate-500">Target ≥ 3.5</span>
            </div>
          </div>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Regression Tests Passing</span>
            <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-3xl font-bold text-slate-900 tracking-tight">{testsPassingPct}%</div>
            <div className="flex items-center gap-1.5 mt-1 text-xs text-slate-500 font-medium">
              <span className="text-emerald-600 font-semibold">{testCases.length || 72} active tests</span>
              <span>•</span>
              <span>Gate: ≥95%</span>
            </div>
          </div>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Reviewer Turnaround SLA</span>
            <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
              <Clock className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-3xl font-bold text-slate-900 tracking-tight">{slaPct.toFixed(1)}%</div>
            <div className="flex items-center gap-1.5 mt-1 text-xs text-slate-500 font-medium">
              <span>Inter-Rater κ = {kappaScore.toFixed(2)}</span>
              <span>•</span>
              <span className="text-emerald-600">High Agreement</span>
            </div>
          </div>
        </Card>

        <Card className="hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-500">Active Defect Tickets</span>
            <div className="w-8 h-8 rounded-lg bg-rose-50 text-rose-600 flex items-center justify-center">
              <Ticket className="w-4 h-4" />
            </div>
          </div>
          <div className="mt-3">
            <div className="text-3xl font-bold text-slate-900 tracking-tight">{tickets.length || 23}</div>
            <div className="flex items-center gap-1.5 mt-1 text-xs text-slate-500 font-medium">
              <span className="text-rose-600 font-semibold">4 Critical (S1)</span>
              <span>•</span>
              <span>Linear / Jira sync</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Main Two-Column Row */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Failure Distribution */}
        <div className="lg:col-span-6">
          <Card 
            title="Failure Distribution" 
            subtitle="Categorical breakdown across human QA confirmed failures"
            action={<Badge variant="neutral">Last 30 Days</Badge>}
          >
            <div className="space-y-4">
              {failureCategories.map((cat) => (
                <div key={cat.name} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-medium">
                    <span className="text-slate-700">{cat.name}</span>
                    <span className="text-slate-900 font-semibold">{cat.pct}% ({cat.count})</span>
                  </div>
                  <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{ width: `${cat.pct}%`, backgroundColor: cat.color }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 pt-4 border-t border-slate-100 grid grid-cols-2 gap-3 text-xs text-slate-500">
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                <span>Hallucinations: 45%</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                <span>Context Loss: 30%</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full bg-purple-500" />
                <span>Intent Loops: 15%</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2.5 h-2.5 rounded-full bg-pink-500" />
                <span>ASR Jitter: 10%</span>
              </div>
            </div>
          </Card>
        </div>

        {/* Recent Tickets */}
        <div className="lg:col-span-6">
          <Card 
            title="Recent Failure Tickets" 
            subtitle="Automated Linear & Jira issues linked to failure clusters"
            action={
              <Button variant="ghost" size="sm" onClick={() => onNavigate('tickets')}>
                View All <ArrowRight className="w-3.5 h-3.5 ml-1" />
              </Button>
            }
          >
            <div className="space-y-3">
              {(tickets.length > 0 ? tickets.slice(0, 4) : [
                {
                  id: 'TICK-1024',
                  external_id: 'LIN-1024',
                  title: 'Agent quotes interest rate absent from KB',
                  category_l1: 'Factual Accuracy',
                  severity: 'S1',
                  status: 'open',
                  frequency: 47,
                },
                {
                  id: 'TICK-1025',
                  external_id: 'LIN-1025',
                  title: 'Loss of loan amount state during code-switch',
                  category_l1: 'Context Retention',
                  severity: 'S2',
                  status: 'in_progress',
                  frequency: 31,
                },
                {
                  id: 'TICK-1026',
                  external_id: 'LIN-1026',
                  title: 'Missing mandatory RBI annual percentage rate disclosure',
                  category_l1: 'Regulatory Compliance',
                  severity: 'S1',
                  status: 'open',
                  frequency: 23,
                },
                {
                  id: 'TICK-1027',
                  external_id: 'LIN-1027',
                  title: 'Repetitive apology loop on customer barge-in',
                  category_l1: 'Dialogue Flow',
                  severity: 'S3',
                  status: 'open',
                  frequency: 18,
                }
              ]).map((ticket) => (
                <div
                  key={ticket.id}
                  className="flex items-start justify-between p-3 rounded-lg border border-slate-100 hover:border-slate-200 bg-slate-50/50 hover:bg-slate-50 transition-all"
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-slate-500 font-semibold">{ticket.external_id || ticket.id}</span>
                      <Badge variant={ticket.severity === 'S1' ? 'error' : ticket.severity === 'S2' ? 'warning' : 'neutral'}>
                        {ticket.severity}
                      </Badge>
                      <span className="text-xs text-slate-400">• {ticket.category_l1}</span>
                    </div>
                    <p className="text-xs font-medium text-slate-800 line-clamp-1">{ticket.title}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-semibold text-slate-700">{ticket.frequency || 12}x</span>
                    <p className="text-[10px] text-slate-400">occurrences</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>

      {/* Recommended Engineering Actions */}
      <Card
        title="Recommended Engineering Actions"
        subtitle="Prioritized quality improvements ranked by potential failure rate reduction"
      >
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {recommendedActions.map((action, idx) => (
            <div
              key={action.id}
              className="p-4 rounded-xl border border-slate-200/80 bg-gradient-to-b from-white to-slate-50/60 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="w-5 h-5 rounded-full bg-blue-100 text-[#0066FF] text-xs font-bold flex items-center justify-center">
                    {idx + 1}
                  </span>
                  <span className="text-xs font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200/60">
                    {action.impact}
                  </span>
                </div>
                <h4 className="text-sm font-semibold text-slate-900 leading-snug">{action.title}</h4>
                <p className="text-xs text-slate-500 mt-1.5 leading-relaxed">{action.description}</p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-100 flex justify-end">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onNavigate(action.targetTab)}
                >
                  {action.actionText} <ArrowRight className="w-3 h-3 ml-1" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
}
