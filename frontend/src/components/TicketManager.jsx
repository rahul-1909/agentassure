import React, { useState } from 'react';
import { TicketCheck, ExternalLink, RefreshCw, Send, ArrowRight, ShieldCheck, CheckCircle2 } from 'lucide-react';

export default function TicketManager({
  clusters = [],
  tickets = [],
  onMineClusters,
  onCreateTicket,
  onSimulateWebhook,
  isLoading = false,
}) {
  const [selectedClusterId, setSelectedClusterId] = useState('');
  const [targetSystem, setTargetSystem] = useState('linear');

  const handleCreate = (e) => {
    e.preventDefault();
    if (!selectedClusterId) return;
    onCreateTicket({
      cluster_id: selectedClusterId,
      system_type: targetSystem,
    });
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <TicketCheck className="w-5 h-5 text-indigo-400" />
            Closed-Loop Engineering Ticketing
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Auto-clusters verified QA failures and generates Linear/Jira issues. Post-release webhooks measure whether failure frequency actually dropped.
          </p>
        </div>

        <button
          onClick={onMineClusters}
          disabled={isLoading}
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg text-xs font-bold shadow-lg transition-all flex items-center space-x-2"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Mine & Aggregate Clusters</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Discovered Clusters */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
            Identified Failure Patterns ({clusters.length})
          </h3>

          <div className="space-y-3 max-h-[460px] overflow-y-auto pr-1">
            {clusters.length === 0 ? (
              <div className="text-center py-10 text-slate-500 text-xs">
                No clusters found. Click "Mine & Aggregate Clusters".
              </div>
            ) : (
              clusters.map((c) => (
                <div
                  key={c.id}
                  onClick={() => setSelectedClusterId(c.id)}
                  className={`p-3.5 rounded-lg border text-xs cursor-pointer transition-all ${
                    selectedClusterId === c.id
                      ? 'border-indigo-500 bg-indigo-950/40 ring-1 ring-indigo-500'
                      : 'border-slate-800 bg-slate-950/40 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-semibold text-slate-200">{c.category_l1}</span>
                    <span className="font-mono text-[10px] text-rose-400 bg-rose-950/60 border border-rose-900 px-1.5 py-0.5 rounded">
                      {c.frequency}x Occurrences
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mb-2">{c.cluster_name}</p>
                  <div className="flex items-center justify-between text-[10px] text-slate-500">
                    <span>Severity: <strong className="text-slate-300">{c.severity}</strong></span>
                    <span className="text-emerald-400 font-semibold">
                      ~{c.expected_impact_reduction_pct.toFixed(0)}% Impact
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Issue Dispatch Form */}
          {selectedClusterId && (
            <div className="pt-3 border-t border-slate-800 space-y-2">
              <label className="block text-[11px] font-semibold text-slate-300">
                Target Issue Tracker
              </label>
              <div className="grid grid-cols-2 gap-2">
                <button
                  type="button"
                  onClick={() => setTargetSystem('linear')}
                  className={`py-1.5 text-xs font-semibold rounded border ${
                    targetSystem === 'linear'
                      ? 'border-indigo-500 bg-indigo-950/60 text-indigo-300'
                      : 'border-slate-800 bg-slate-800/40 text-slate-400'
                  }`}
                >
                  Linear (GraphQL)
                </button>
                <button
                  type="button"
                  onClick={() => setTargetSystem('jira')}
                  className={`py-1.5 text-xs font-semibold rounded border ${
                    targetSystem === 'jira'
                      ? 'border-indigo-500 bg-indigo-950/60 text-indigo-300'
                      : 'border-slate-800 bg-slate-800/40 text-slate-400'
                  }`}
                >
                  Jira (Atlassian)
                </button>
              </div>

              <button
                onClick={handleCreate}
                className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-xs font-bold transition-all shadow-md flex items-center justify-center space-x-1.5 mt-2"
              >
                <Send className="w-3.5 h-3.5" />
                <span>Create Standardized Ticket</span>
              </button>
            </div>
          )}
        </div>

        {/* Created Tickets and Post-Release Validation */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
              Active Engineering Tickets & Closed-Loop Verification ({tickets.length})
            </h3>

            <div className="space-y-3 max-h-[460px] overflow-y-auto">
              {tickets.length === 0 ? (
                <div className="text-center py-16 text-slate-500 text-xs">
                  No tickets created yet. Select a cluster on the left and create an issue.
                </div>
              ) : (
                tickets.map((t) => (
                  <div
                    key={t.id}
                    className="p-4 bg-slate-950/60 rounded-xl border border-slate-800 text-xs space-y-2.5"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono font-bold text-indigo-400 bg-indigo-950/60 px-2 py-0.5 rounded border border-indigo-900">
                          {t.external_id}
                        </span>
                        <span className="font-semibold text-slate-200">{t.title}</span>
                      </div>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                          t.status === 'resolved' || t.status === 'closed'
                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                            : 'bg-amber-950 text-amber-400 border border-amber-800'
                        }`}
                      >
                        {t.status}
                      </span>
                    </div>

                    <p className="text-[11px] text-slate-400 font-mono bg-slate-900/80 p-2.5 rounded border border-slate-800/80 whitespace-pre-wrap leading-relaxed">
                      {t.body}
                    </p>

                    <div className="flex items-center justify-between pt-1">
                      <div className="flex items-center space-x-3 text-[11px]">
                        <span className="text-slate-500">
                          Verified Post-Release:
                        </span>
                        {t.post_release_verified ? (
                          <span className="text-emerald-400 font-bold flex items-center gap-1">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            {t.verified_failure_rate_before?.toFixed(0)}x &rarr;{' '}
                            {t.verified_failure_rate_after?.toFixed(1)}x Defect Drop
                          </span>
                        ) : (
                          <span className="text-slate-400 italic">Awaiting CI deploy</span>
                        )}
                      </div>

                      {!t.post_release_verified && (
                        <button
                          onClick={() => onSimulateWebhook(t.external_id)}
                          className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-indigo-300 rounded text-[11px] font-medium border border-slate-700 transition-all"
                        >
                          Simulate Webhook Callback
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
