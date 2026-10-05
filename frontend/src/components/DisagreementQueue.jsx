import React, { useState } from 'react';
import { Scale, CheckCircle, AlertCircle, ArrowRight, UserCheck } from 'lucide-react';

export default function DisagreementQueue({
  disagreements = [],
  onAdjudicate,
}) {
  const [selectedDisagreement, setSelectedDisagreement] = useState(null);
  const [resolvedCategoryL1, setResolvedCategoryL1] = useState('Factual Accuracy');
  const [resolvedCategoryL2, setResolvedCategoryL2] = useState('Unsupported Numerical or Pricing Claim');
  const [resolvedSeverity, setResolvedSeverity] = useState('S1');
  const [notes, setNotes] = useState('');

  const handleResolve = (e) => {
    e.preventDefault();
    if (!selectedDisagreement) return;

    onAdjudicate({
      disagreement_id: selectedDisagreement.id,
      resolved_category_l1: resolvedCategoryL1,
      resolved_category_l2: resolvedCategoryL2,
      resolved_severity: resolvedSeverity,
      resolution_notes: notes,
    });

    setSelectedDisagreement(null);
    setNotes('');
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Scale className="w-5 h-5 text-indigo-400" />
            Double-Review Adjudication Queue
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Cases where Reviewer A and Reviewer B disagreed on taxonomy or severity ratings.
          </p>
        </div>
        <span className="px-3 py-1 bg-amber-950/40 border border-amber-800/80 text-amber-400 text-xs font-semibold rounded-full">
          {disagreements.length} Pending Adjudications
        </span>
      </div>

      {disagreements.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center text-slate-500">
          <CheckCircle className="w-12 h-12 mx-auto mb-3 text-emerald-500/80" />
          <h4 className="text-sm font-semibold text-slate-300">Zero Disagreements</h4>
          <p className="text-xs text-slate-500 mt-1">
            Inter-rater reliability is high. All dual-reviewed conversations achieved consensus.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {disagreements.map((item) => (
            <div
              key={item.id}
              className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-3 text-xs">
                  <span className="font-mono text-indigo-400 font-semibold">
                    Turn Ref: {item.turn_id.slice(0, 8)}...
                  </span>
                  <span className="px-2 py-0.5 rounded bg-rose-950 border border-rose-800 text-rose-400 font-bold">
                    Disagreement
                  </span>
                </div>

                {/* Compare Rater 1 vs Rater 2 */}
                <div className="grid grid-cols-2 gap-3 mb-4">
                  <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800">
                    <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">
                      Reviewer 1 (Alice)
                    </span>
                    <p className="text-xs font-semibold text-slate-200">Factual Accuracy</p>
                    <p className="text-[11px] text-slate-400">Unsupported Numerical Claim</p>
                    <span className="inline-block mt-2 text-[10px] font-bold text-red-400 bg-red-950/60 px-1.5 py-0.5 rounded border border-red-800">
                      Severity S1
                    </span>
                  </div>

                  <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800">
                    <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">
                      Reviewer 2 (Bob)
                    </span>
                    <p className="text-xs font-semibold text-slate-200">Compliance</p>
                    <p className="text-[11px] text-slate-400">Missing RBI Disclaimer</p>
                    <span className="inline-block mt-2 text-[10px] font-bold text-orange-400 bg-orange-950/60 px-1.5 py-0.5 rounded border border-orange-800">
                      Severity S2
                    </span>
                  </div>
                </div>
              </div>

              <button
                onClick={() => setSelectedDisagreement(item)}
                className="w-full py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-semibold rounded-lg text-xs transition-all flex items-center justify-center space-x-1.5"
              >
                <UserCheck className="w-3.5 h-3.5" />
                <span>Adjudicate Case</span>
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Adjudication Modal */}
      {selectedDisagreement && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-lg w-full p-6 shadow-2xl">
            <h3 className="text-base font-bold text-white mb-2 flex items-center gap-2">
              <Scale className="w-5 h-5 text-indigo-400" />
              Supervisor Adjudication Decision
            </h3>
            <p className="text-xs text-slate-400 mb-4">
              Select the definitive taxonomy classification and assign the canonical regression severity.
            </p>

            <form onSubmit={handleResolve} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Authoritative L1 Category
                </label>
                <select
                  value={resolvedCategoryL1}
                  onChange={(e) => setResolvedCategoryL1(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none"
                >
                  <option value="Factual Accuracy">Factual Accuracy</option>
                  <option value="Compliance">Compliance</option>
                  <option value="Prompt Injection & Safety">Prompt Injection & Safety</option>
                  <option value="Tone, Sentiment & Empathy">Tone, Sentiment & Empathy</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Authoritative L2 Subcategory
                </label>
                <input
                  type="text"
                  value={resolvedCategoryL2}
                  onChange={(e) => setResolvedCategoryL2(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Resolved Severity
                </label>
                <div className="grid grid-cols-4 gap-2">
                  {['S1', 'S2', 'S3', 'S4'].map((s) => (
                    <button
                      type="button"
                      key={s}
                      onClick={() => setResolvedSeverity(s)}
                      className={`py-1.5 text-xs font-bold rounded-lg border ${
                        resolvedSeverity === s
                          ? 'border-indigo-500 bg-indigo-950/60 text-indigo-400'
                          : 'border-slate-800 bg-slate-800/40 text-slate-400'
                      }`}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Adjudication Rationale Note
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Explain why this decision was chosen for reviewer calibration tracking..."
                  rows={3}
                  required
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none resize-none"
                />
              </div>

              <div className="flex items-center justify-end space-x-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setSelectedDisagreement(null)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-bold shadow-lg"
                >
                  Confirm & Resolve Case
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
