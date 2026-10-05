import React from 'react';
import { Filter, Play, RefreshCw, AlertCircle, ArrowUpRight, Flame } from 'lucide-react';

export default function RiskQueueView({
  queueItems = [],
  onSelectConversation,
  onTriggerSampling,
  isLoading = false,
}) {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Filter className="w-5 h-5 text-indigo-400" />
            Smart Sampling Prioritized Queue
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            PostgreSQL-backed risk queue prioritizing high-risk conversations: low judge score (35%) + ASR error (25%) + loops (20%) + drop-offs (10%) + negative sentiment (10%).
          </p>
        </div>

        <button
          onClick={() => onTriggerSampling(30)}
          disabled={isLoading}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg text-xs font-bold shadow-lg transition-all flex items-center space-x-2 self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Draw Stratified Batch (65/20/15)</span>
        </button>
      </div>

      {/* Sampling Strata Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-xs mb-1">
            <span className="font-semibold text-slate-300">Risk-Ranked Stratum</span>
            <span className="font-mono text-indigo-400 font-bold">65% Target</span>
          </div>
          <p className="text-[11px] text-slate-500">
            Top conversations ranked by composite multi-factor defect telemetry.
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-xs mb-1">
            <span className="font-semibold text-slate-300">New Agent Version</span>
            <span className="font-mono text-emerald-400 font-bold">20% Target</span>
          </div>
          <p className="text-[11px] text-slate-500">
            Rapid regression validation across the latest deployment candidates.
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-xs mb-1">
            <span className="font-semibold text-slate-300">Vernacular & Edge Cases</span>
            <span className="font-mono text-amber-400 font-bold">15% Target</span>
          </div>
          <p className="text-[11px] text-slate-500">
            Hinglish code-switching, barge-in interruptions, and multi-turn loops.
          </p>
        </div>
      </div>

      {/* Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-950/80 border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                <th className="py-3 px-4">Risk Rank</th>
                <th className="py-3 px-4">Customer ID</th>
                <th className="py-3 px-4">Version</th>
                <th className="py-3 px-4">Language</th>
                <th className="py-3 px-4">Judge Score</th>
                <th className="py-3 px-4">ASR Error</th>
                <th className="py-3 px-4">Loops</th>
                <th className="py-3 px-4">Stratum</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs">
              {queueItems.length === 0 ? (
                <tr>
                  <td colSpan={10} className="py-8 text-center text-slate-500">
                    No pending conversations in queue. Click "Draw Stratified Batch" above.
                  </td>
                </tr>
              ) : (
                queueItems.map((item, idx) => {
                  const riskLevel =
                    item.risk_score >= 0.6
                      ? 'text-rose-400 font-bold'
                      : item.risk_score >= 0.35
                      ? 'text-amber-400 font-semibold'
                      : 'text-emerald-400';

                  return (
                    <tr
                      key={item.id}
                      className="hover:bg-slate-800/40 transition-colors cursor-pointer"
                      onClick={() => onSelectConversation(item.id)}
                    >
                      <td className="py-3 px-4 font-mono">
                        <div className="flex items-center gap-1.5">
                          {item.risk_score >= 0.6 && <Flame className="w-3.5 h-3.5 text-rose-500" />}
                          <span className={riskLevel}>{(item.risk_score * 100).toFixed(1)}%</span>
                        </div>
                      </td>
                      <td className="py-3 px-4 font-mono text-slate-300">
                        {item.customer_id}
                      </td>
                      <td className="py-3 px-4 text-slate-300 font-mono text-[11px]">
                        {item.agent_version}
                      </td>
                      <td className="py-3 px-4 text-slate-300 uppercase font-mono text-[11px]">
                        {item.language}
                      </td>
                      <td className="py-3 px-4 font-mono text-slate-300">
                        {item.judge_score.toFixed(2)}
                      </td>
                      <td className="py-3 px-4 font-mono text-slate-300">
                        {(item.asr_error_rate * 100).toFixed(0)}%
                      </td>
                      <td className="py-3 px-4 font-mono text-slate-300">
                        {item.loop_count}
                      </td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-indigo-300 border border-slate-700">
                          {item.sample_stratum}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            item.review_status === 'pending'
                              ? 'bg-amber-950 text-amber-400 border border-amber-800'
                              : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                          }`}
                        >
                          {item.review_status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectConversation(item.id);
                          }}
                          className="px-2.5 py-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-[11px] font-semibold inline-flex items-center gap-1 transition-all"
                        >
                          <span>Review</span>
                          <ArrowUpRight className="w-3 h-3" />
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
