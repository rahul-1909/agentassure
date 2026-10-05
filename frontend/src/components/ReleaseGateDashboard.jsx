import React, { useState } from 'react';
import { GitMerge, CheckCircle, AlertOctagon, Copy, Check, BarChart2, ShieldCheck, ArrowRight } from 'lucide-react';

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
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <GitMerge className="w-5 h-5 text-indigo-400" />
            CI/CD Automated Release Gating Dashboard
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Enforces fail-fast release gates: Compliance and Factual Accuracy must exceed 95% pass rate with Chi-Square & t-test significance validation.
          </p>
        </div>

        <form onSubmit={handleTrigger} className="flex items-center space-x-2">
          <input
            type="text"
            value={candidateVersion}
            onChange={(e) => setCandidateVersion(e.target.value)}
            placeholder="Candidate Version"
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white font-mono focus:outline-none w-36"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg text-xs font-bold shadow-lg transition-all flex items-center space-x-1.5"
          >
            <span>{isLoading ? 'Evaluating...' : 'Run CI Gate'}</span>
          </button>
        </form>
      </div>

      {/* Decision Banner */}
      {gateResult && (
        <div
          className={`p-5 rounded-xl border shadow-xl flex items-center justify-between ${
            isPassed
              ? 'bg-emerald-950/30 border-emerald-800/80 text-emerald-300'
              : 'bg-rose-950/30 border-rose-800/80 text-rose-300'
          }`}
        >
          <div className="flex items-center space-x-3">
            {isPassed ? (
              <CheckCircle className="w-8 h-8 text-emerald-400" />
            ) : (
              <AlertOctagon className="w-8 h-8 text-rose-400" />
            )}
            <div>
              <h3 className="text-base font-bold text-white">
                Release Gate Decision: {gateResult.status}
              </h3>
              <p className="text-xs text-slate-300 mt-0.5">
                Candidate: <code className="text-indigo-300">{gateResult.agent_version}</code> (Commit: {gateResult.commit_hash?.slice(0, 7)})
                {isPassed
                  ? ' — All critical regulatory and quality thresholds satisfied. Merging authorized.'
                  : ` — Deployment restricted. Blocked categories: ${gateResult.blocked_categories.join(', ')}`}
              </p>
            </div>
          </div>

          <div className="text-right">
            <span className="text-2xl font-black font-mono block">
              {(gateResult.overall_pass_rate * 100).toFixed(1)}%
            </span>
            <span className="text-[11px] text-slate-400">
              Delta: {gateResult.delta_pass_rate >= 0 ? '+' : ''}{(gateResult.delta_pass_rate * 100).toFixed(1)}% vs baseline
            </span>
          </div>
        </div>
      )}

      {/* Breakdown and Statistics */}
      {gateResult && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Category Table */}
          <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
              Taxonomy Category Breakdown
            </h3>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-950/60 border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase">
                    <th className="py-2.5 px-3">Category</th>
                    <th className="py-2.5 px-3">Classification</th>
                    <th className="py-2.5 px-3">Passed / Total</th>
                    <th className="py-2.5 px-3">Pass Rate</th>
                    <th className="py-2.5 px-3">Threshold</th>
                    <th className="py-2.5 px-3 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {gateResult.category_breakdown?.map((c) => (
                    <tr key={c.category} className="hover:bg-slate-800/30">
                      <td className="py-2.5 px-3 font-semibold text-slate-200">
                        {c.category}
                      </td>
                      <td className="py-2.5 px-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            c.is_critical
                              ? 'bg-rose-950 text-rose-400 border border-rose-800'
                              : 'bg-slate-800 text-slate-400'
                          }`}
                        >
                          {c.is_critical ? 'Critical' : 'Standard'}
                        </span>
                      </td>
                      <td className="py-2.5 px-3 font-mono text-slate-300">
                        {c.passed_tests} / {c.total_tests}
                      </td>
                      <td className="py-2.5 px-3 font-mono font-bold text-slate-200">
                        {(c.pass_rate * 100).toFixed(1)}%
                      </td>
                      <td className="py-2.5 px-3 font-mono text-slate-400">
                        &ge;{(c.threshold * 100).toFixed(0)}%
                      </td>
                      <td className="py-2.5 px-3 text-right font-bold">
                        <span
                          className={c.status === 'PASSED' ? 'text-emerald-400' : 'text-rose-400'}
                        >
                          {c.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Statistical Significance Cards */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl flex flex-col justify-between space-y-4">
            <div>
              <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-1.5">
                <BarChart2 className="w-4 h-4 text-indigo-400" />
                Statistical Significance
              </h3>
              <div className="space-y-3">
                {gateResult.statistical_tests?.map((s, idx) => (
                  <div key={idx} className="p-3 bg-slate-950/60 rounded-lg border border-slate-800 text-xs">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-indigo-300">{s.metric_name}</span>
                      <span className="font-mono text-[10px] text-slate-500">{s.test_type}</span>
                    </div>
                    <p className="text-slate-300 text-[11px] leading-relaxed mb-2">
                      {s.conclusion}
                    </p>
                    <div className="flex items-center justify-between text-[10px] font-mono text-slate-400">
                      <span>p-value: {s.p_value.toFixed(4)}</span>
                      <span className={s.is_significant ? 'text-indigo-400 font-bold' : 'text-slate-500'}>
                        {s.is_significant ? 'Statistically Significant (p < 0.05)' : 'Not Significant'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={copyMarkdown}
              className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold rounded-lg border border-slate-700 transition-all flex items-center justify-center space-x-1.5"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Copied PR Comment!' : 'Copy GitHub PR Comment Markdown'}</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
