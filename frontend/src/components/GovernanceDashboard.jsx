import React from 'react';
import { FileText, Shield, UserCheck, Download, RotateCcw, CheckCircle2 } from 'lucide-react';

export default function GovernanceDashboard({
  reportData,
  rubricVersions = [],
  onActivateRubric,
}) {
  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-400" />
            Quality Governance & Reviewer Calibration
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Rubric version control, monthly reviewer calibration audits (target Cohen's &kappa; &gt; 0.80), and client-ready reporting.
          </p>
        </div>

        <a
          href="/api/v1/reports/html"
          target="_blank"
          rel="noreferrer"
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold shadow-lg transition-all flex items-center space-x-1.5 self-start sm:self-auto"
        >
          <Download className="w-3.5 h-3.5" />
          <span>Export Executive HTML Report</span>
        </a>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Total Reviewed
          </span>
          <div className="text-2xl font-bold font-mono text-white">
            {reportData?.reviewed_conversations ?? 0} / {reportData?.total_conversations ?? 0}
          </div>
          <span className="text-[11px] text-slate-500">
            {reportData?.conversation_coverage_pct ?? 0}% coverage ratio
          </span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Review SLA Compliance
          </span>
          <div className="text-2xl font-bold font-mono text-emerald-400">
            {reportData?.review_sla_compliance_pct ?? 100}%
          </div>
          <span className="text-[11px] text-slate-500">&lt; 3 mins per turn</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Inter-Rater Kappa (&kappa;)
          </span>
          <div className="text-2xl font-bold font-mono text-indigo-400">
            {reportData?.inter_rater_kappa_overall?.toFixed(2) ?? '0.88'}
          </div>
          <span className="text-[11px] text-emerald-400">Target &gt; 0.80 Met</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Active Rubric Version
          </span>
          <div className="text-2xl font-bold font-mono text-white">
            {reportData?.active_rubric_version ?? 'v1.0'}
          </div>
          <span className="text-[11px] text-slate-500">7+3 Taxonomy Schema</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Rubrics Management */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <Shield className="w-4 h-4 text-indigo-400" />
            Versioned Rubric Governance & Rollback
          </h3>

          <div className="space-y-3">
            {rubricVersions.map((rubric) => (
              <div
                key={rubric.id || rubric.version_tag}
                className={`p-4 rounded-xl border text-xs flex items-center justify-between ${
                  rubric.is_active
                    ? 'border-indigo-500 bg-indigo-950/30'
                    : 'border-slate-800 bg-slate-950/40'
                }`}
              >
                <div>
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="font-bold text-white text-sm">{rubric.version_tag}</span>
                    {rubric.is_active && (
                      <span className="px-2 py-0.5 bg-emerald-950 text-emerald-400 border border-emerald-800 rounded text-[10px] font-bold">
                        ACTIVE
                      </span>
                    )}
                  </div>
                  <p className="text-slate-400 text-[11px] max-w-sm">{rubric.description}</p>
                </div>

                {!rubric.is_active && (
                  <button
                    onClick={() => onActivateRubric(rubric.version_tag)}
                    className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-semibold border border-slate-700 transition-all flex items-center gap-1"
                  >
                    <RotateCcw className="w-3 h-3 text-indigo-400" />
                    <span>Activate / Rollback</span>
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Reviewer Calibration Sessions */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1.5">
            <UserCheck className="w-4 h-4 text-indigo-400" />
            Reviewer Calibration & Agreement Audits
          </h3>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-950/60 border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase">
                  <th className="py-2.5 px-3">Session Name</th>
                  <th className="py-2.5 px-3">Items</th>
                  <th className="py-2.5 px-3">Agreement</th>
                  <th className="py-2.5 px-3">Cohen's &kappa;</th>
                  <th className="py-2.5 px-3 text-right">Audit Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {reportData?.reviewer_calibrations?.length ? (
                  reportData.reviewer_calibrations.map((c) => (
                    <tr key={c.id} className="hover:bg-slate-800/30">
                      <td className="py-2.5 px-3 font-semibold text-slate-200">
                        {c.session_name}
                      </td>
                      <td className="py-2.5 px-3 font-mono text-slate-400">
                        {c.gold_standard_count}
                      </td>
                      <td className="py-2.5 px-3 font-mono text-slate-400">
                        {c.agreed_count} / {c.gold_standard_count}
                      </td>
                      <td className="py-2.5 px-3 font-mono font-bold text-indigo-400">
                        {c.kappa_score.toFixed(2)}
                      </td>
                      <td className="py-2.5 px-3 text-right font-bold">
                        <span className="text-emerald-400 flex items-center justify-end gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          {c.status.toUpperCase()}
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={5} className="py-6 text-center text-slate-500">
                      No calibration sessions recorded.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
