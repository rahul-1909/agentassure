import React, { useState } from 'react';
import { 
  GitMerge, 
  CheckCircle2, 
  AlertOctagon, 
  Copy, 
  Check, 
  BarChart2, 
  ShieldCheck, 
  ArrowRight,
  TrendingUp,
  AlertTriangle
} from 'lucide-react';
import Card from './common/Card';
import Badge from './common/Badge';
import Button from './common/Button';

export default function ReleaseGateDashboard({
  onEvaluateGate,
  gateResult,
  isLoading = false,
}) {
  const [candidateVersion, setCandidateVersion] = useState('v2.5.0-candidate');
  const [baselineVersion, setBaselineVersion] = useState('v2.4.0');
  const [commitHash, setCommitHash] = useState('7fa9b12');
  const [copied, setCopied] = useState(false);

  const handleTrigger = (e) => {
    e.preventDefault();
    onEvaluateGate({
      agent_version: candidateVersion,
      baseline_version: baselineVersion,
      commit_hash: commitHash,
    });
  };

  const copyMarkdown = () => {
    if (gateResult?.markdown_summary) {
      navigator.clipboard.writeText(gateResult.markdown_summary);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const isPassed = gateResult?.status === 'PASSED';

  return (
    <div className="space-y-6">
      {/* Title & Trigger Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2 tracking-tight">
            <GitMerge className="w-5 h-5 text-[#0066FF]" />
            CI/CD Automated Release Gating Dashboard
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Enforces fail-fast release gates: Compliance and Factual Accuracy must exceed 95% pass rate with Chi-Square & t-test significance validation.
          </p>
        </div>

        <form onSubmit={handleTrigger} className="flex items-center space-x-2">
          <input
            type="text"
            value={candidateVersion}
            onChange={(e) => setCandidateVersion(e.target.value)}
            placeholder="Candidate Version"
            className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 text-xs text-slate-800 font-mono focus:bg-white focus:ring-2 focus:ring-[#0066FF]/30 focus:outline-none w-40"
          />
          <Button
            type="submit"
            variant="primary"
            disabled={isLoading}
          >
            {isLoading ? 'Evaluating...' : 'Run CI Gate'}
          </Button>
        </form>
      </div>

      {/* Decision Banner */}
      {gateResult && (
        <div
          className={`p-5 rounded-xl border shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4 ${
            isPassed
              ? 'bg-emerald-50/60 border-emerald-200 text-emerald-950'
              : 'bg-rose-50/60 border-rose-200 text-rose-950'
          }`}
        >
          <div className="flex items-start space-x-3.5">
            {isPassed ? (
              <CheckCircle2 className="w-7 h-7 text-emerald-600 shrink-0 mt-0.5" />
            ) : (
              <AlertOctagon className="w-7 h-7 text-rose-600 shrink-0 mt-0.5" />
            )}
            <div>
              <div className="flex items-center gap-2">
                <span className={`text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                  isPassed ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'
                }`}>
                  Decision: {gateResult.status}
                </span>
                <span className="text-xs text-slate-500 font-medium">Candidate: <code className="font-semibold text-slate-800">{gateResult.agent_version}</code></span>
              </div>
              <p className="text-xs text-slate-600 mt-1.5 leading-relaxed">
                {isPassed
                  ? 'All critical regulatory and quality thresholds satisfied (>95%). Production merge authorized.'
                  : `Deployment restricted. Blocked categories breached quality gates: ${gateResult.blocked_categories.join(', ')}`}
              </p>
            </div>
          </div>

          <div className="text-right shrink-0">
            <span className="text-2xl font-bold font-mono text-slate-900 block">
              {(gateResult.overall_pass_rate * 100).toFixed(1)}%
            </span>
            <span className="text-xs text-slate-500">
              Delta: {gateResult.delta_pass_rate >= 0 ? '+' : ''}{(gateResult.delta_pass_rate * 100).toFixed(1)}% vs baseline
            </span>
          </div>
        </div>
      )}

      {/* Breakdown and Statistics */}
      {gateResult && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Category Table */}
          <div className="lg:col-span-8">
            <Card
              title="Category Quality Breakdown"
              subtitle="Fail-fast criteria evaluated across all saved test assertions"
            >
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold uppercase text-[11px]">
                      <th className="py-2.5 px-3">Category</th>
                      <th className="py-2.5 px-3">Type</th>
                      <th className="py-2.5 px-3">Passed / Total</th>
                      <th className="py-2.5 px-3">Pass Rate</th>
                      <th className="py-2.5 px-3">Gate</th>
                      <th className="py-2.5 px-3 text-right">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {gateResult.category_breakdown?.map((c) => (
                      <tr key={c.category} className="hover:bg-slate-50/60 transition-colors">
                        <td className="py-2.5 px-3 font-semibold text-slate-800">
                          {c.category}
                        </td>
                        <td className="py-2.5 px-3">
                          <Badge variant={c.is_critical ? 'error' : 'neutral'}>
                            {c.is_critical ? 'Critical' : 'Standard'}
                          </Badge>
                        </td>
                        <td className="py-2.5 px-3 font-mono text-slate-600">
                          {c.passed_tests} / {c.total_tests}
                        </td>
                        <td className="py-2.5 px-3 font-mono font-bold text-slate-900">
                          {(c.pass_rate * 100).toFixed(1)}%
                        </td>
                        <td className="py-2.5 px-3 font-mono text-slate-500">
                          &ge;{(c.threshold * 100).toFixed(0)}%
                        </td>
                        <td className="py-2.5 px-3 text-right font-bold">
                          <span
                            className={c.status === 'PASSED' ? 'text-emerald-600' : 'text-rose-600'}
                          >
                            {c.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          </div>

          {/* Statistical Significance Cards */}
          <div className="lg:col-span-4 space-y-4">
            <Card
              title="Statistical Significance"
              subtitle="Hypothesis testing vs baseline"
            >
              <div className="space-y-3.5">
                {gateResult.statistical_tests?.map((s) => (
                  <div key={s.metric_name} className="p-3 bg-slate-50 border border-slate-200/80 rounded-lg">
                    <div className="flex items-center justify-between text-xs mb-1">
                      <span className="font-semibold text-slate-800">{s.metric_name}</span>
                      <span className="font-mono text-[10px] text-slate-500 bg-white px-1.5 py-0.5 rounded border border-slate-200">
                        {s.test_type}
                      </span>
                    </div>
                    <div className="text-xs font-mono text-slate-600 mb-1">
                      p-value: <span className="font-bold text-slate-900">{s.p_value.toFixed(4)}</span>
                    </div>
                    <p className="text-xs text-slate-600 leading-snug">{s.conclusion}</p>
                  </div>
                ))}
              </div>

              {gateResult.markdown_summary && (
                <div className="mt-4 pt-3 border-t border-slate-100">
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full"
                    icon={copied ? Check : Copy}
                    onClick={copyMarkdown}
                  >
                    {copied ? 'Copied to Clipboard!' : 'Copy PR Comment'}
                  </Button>
                </div>
              )}
            </Card>
          </div>
        </div>
      )}
    </div>
  );
}
