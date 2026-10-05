import React, { useState } from 'react';
import { FlaskConical, Play, CheckCircle2, XCircle, Clock, ShieldCheck, Terminal } from 'lucide-react';

export default function RegressionHarness({
  testCases = [],
  testRuns = [],
  onRunSuite,
  isLoading = false,
}) {
  const [selectedCase, setSelectedCase] = useState(null);
  const [agentVersion, setAgentVersion] = useState('v2.5.0-candidate');

  const handleRun = (e) => {
    e.preventDefault();
    onRunSuite(agentVersion);
  };

  const activeCase = selectedCase || (testCases.length > 0 ? testCases[0] : null);

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <FlaskConical className="w-5 h-5 text-indigo-400" />
            Regression Test Harness & Suite Runner
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Deterministic and semantic test cases distilled atomically from confirmed QA failures to guard against prompt or model regressions.
          </p>
        </div>

        <form onSubmit={handleRun} className="flex items-center space-x-2">
          <input
            type="text"
            value={agentVersion}
            onChange={(e) => setAgentVersion(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white font-mono focus:outline-none w-36"
            placeholder="Agent Version"
          />
          <button
            type="submit"
            disabled={isLoading}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded-lg text-xs font-bold shadow-lg transition-all flex items-center space-x-1.5"
          >
            <Play className={`w-3.5 h-3.5 ${isLoading ? 'animate-pulse' : ''}`} />
            <span>{isLoading ? 'Running Suite...' : 'Execute Regression Suite'}</span>
          </button>
        </form>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Test Cases List */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-3">
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">
              Regression Test Cases ({testCases.length})
            </h3>
          </div>

          <div className="space-y-2.5 max-h-[500px] overflow-y-auto pr-1">
            {testCases.map((tc) => (
              <div
                key={tc.id}
                onClick={() => setSelectedCase(tc)}
                className={`p-3 rounded-lg border text-xs cursor-pointer transition-all ${
                  activeCase?.id === tc.id
                    ? 'border-indigo-500 bg-indigo-950/40 ring-1 ring-indigo-500'
                    : 'border-slate-800 bg-slate-950/40 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <span
                    className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      tc.severity === 'S1'
                        ? 'bg-rose-950 text-rose-400 border border-rose-900'
                        : 'bg-orange-950 text-orange-400 border border-orange-900'
                    }`}
                  >
                    {tc.severity}
                  </span>
                  <span className="font-mono text-[10px] text-slate-500">
                    {tc.category_l1}
                  </span>
                </div>
                <h4 className="font-semibold text-slate-200 line-clamp-2 mb-1">{tc.title}</h4>
                <p className="text-[11px] text-slate-400 line-clamp-1">{tc.category_l2}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Selected Test Case Detail */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl flex flex-col justify-between space-y-4">
          {activeCase ? (
            <div className="space-y-4">
              <div>
                <div className="flex items-center space-x-2 mb-1">
                  <span className="text-xs font-mono text-indigo-400 font-bold">
                    Test ID: {activeCase.id.slice(0, 12)}...
                  </span>
                  <span className="text-xs px-2 py-0.5 bg-slate-800 rounded text-slate-300">
                    {activeCase.category_l1} &rarr; {activeCase.category_l2}
                  </span>
                </div>
                <h3 className="text-base font-bold text-white">{activeCase.title}</h3>
                <p className="text-xs text-slate-400 mt-1">{activeCase.description}</p>
              </div>

              {/* Context Turns */}
              <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800 space-y-2">
                <span className="text-[10px] uppercase font-bold text-slate-500 block">
                  Historical Dialogue Context
                </span>
                {activeCase.conversation_context?.map((ctx, idx) => (
                  <div key={idx} className="text-xs flex items-start space-x-2">
                    <span className="font-mono font-semibold uppercase text-slate-400 w-16">
                      [{ctx.speaker}]:
                    </span>
                    <span className="text-slate-200">{ctx.transcript}</span>
                  </div>
                ))}
              </div>

              {/* Expected vs Actual */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                <div className="p-3 bg-emerald-950/20 border border-emerald-900/60 rounded-lg">
                  <span className="text-[10px] uppercase font-bold text-emerald-400 block mb-1">
                    Expected Behavior & Rule
                  </span>
                  <p className="text-slate-200 leading-relaxed">{activeCase.expected_behavior}</p>
                </div>

                <div className="p-3 bg-rose-950/20 border border-rose-900/60 rounded-lg">
                  <span className="text-[10px] uppercase font-bold text-rose-400 block mb-1">
                    Historical Agent Failure
                  </span>
                  <p className="text-slate-200 leading-relaxed">{activeCase.actual_behavior}</p>
                </div>
              </div>

              {/* Executable Assertions */}
              <div>
                <span className="text-xs font-bold text-slate-300 block mb-2 flex items-center gap-1.5">
                  <Terminal className="w-3.5 h-3.5 text-indigo-400" />
                  Structured Assertion Rules ({activeCase.assertion_rules?.length || 0})
                </span>
                <div className="space-y-1.5">
                  {activeCase.assertion_rules?.map((rule, idx) => (
                    <div
                      key={idx}
                      className="p-2.5 bg-slate-950/80 rounded border border-slate-800 text-xs font-mono flex items-center justify-between"
                    >
                      <div>
                        <span className="text-indigo-400 font-bold">[{rule.assertion_type}]</span>{' '}
                        <span className="text-slate-300">
                          {rule.description || JSON.stringify(rule.parameters)}
                        </span>
                      </div>
                      <span className="text-[10px] text-emerald-400 font-semibold bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-900">
                        ACTIVE RULE
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Fix Suggestion */}
              <div className="p-3 bg-slate-800/40 rounded-lg border border-slate-700/60 text-xs">
                <span className="text-[10px] uppercase font-bold text-amber-400 block mb-1">
                  Fix Suggestion
                </span>
                <p className="text-slate-300">{activeCase.fix_suggestion}</p>
              </div>
            </div>
          ) : (
            <div className="text-center py-20 text-slate-500 text-xs">
              No test cases found.
            </div>
          )}

          {/* Test Runs results bar */}
          {testRuns.length > 0 && (
            <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-300">
                Latest Suite Execution Results:
              </span>
              <div className="flex items-center space-x-3">
                <span className="text-emerald-400 font-bold flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  {testRuns.filter((r) => r.passed).length} Passed
                </span>
                <span className="text-rose-400 font-bold flex items-center gap-1">
                  <XCircle className="w-3.5 h-3.5" />
                  {testRuns.filter((r) => !r.passed).length} Failed
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
