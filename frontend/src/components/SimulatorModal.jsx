import React, { useState, useEffect } from 'react';
import { Users, Play, Mic, AlertTriangle, CheckCircle, ShieldAlert, Bot, User, Sparkles } from 'lucide-react';

export default function SimulatorModal({
  personas = [],
  onRunSimulation,
  onConvertToTest,
  isLoading = false,
}) {
  const [selectedKey, setSelectedKey] = useState('price_sensitive_haggler');
  const [agentVersion, setAgentVersion] = useState('v2.5.0-candidate');
  const [maxTurns, setMaxTurns] = useState(4);
  const [voiceMode, setVoiceMode] = useState(false);
  const [simulationResult, setSimulationResult] = useState(null);

  useEffect(() => {
    if (personas.length > 0 && !selectedKey) {
      setSelectedKey(personas[0].persona_key);
    }
  }, [personas]);

  const activePersona = personas.find((p) => p.persona_key === selectedKey) || personas[0];

  const handleRun = async (e) => {
    e.preventDefault();
    const result = await onRunSimulation({
      persona_key: selectedKey,
      agent_version: agentVersion,
      max_turns: maxTurns,
      voice_mode: voiceMode,
    });
    if (result) {
      setSimulationResult(result);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Users className="w-5 h-5 text-indigo-400" />
            Adversarial Customer Persona Simulator
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Simulate 10+ edge-case personalities (price-sensitive, confused elderly, hostile debtors, Hinglish code-switchers) to surface hidden defects before production release.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls Column */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl space-y-4">
          <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2">
            Simulation Parameters
          </h3>

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Select Synthetic Customer Persona
            </label>
            <select
              value={selectedKey}
              onChange={(e) => setSelectedKey(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none"
            >
              {personas.map((p) => (
                <option key={p.persona_key} value={p.persona_key}>
                  {p.name} ({p.language.toUpperCase()})
                </option>
              ))}
            </select>
          </div>

          {activePersona && (
            <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800 text-xs space-y-2">
              <span className="text-[10px] uppercase font-bold text-indigo-400 block">
                Personality Profile
              </span>
              <p className="text-slate-300 leading-relaxed">{activePersona.description}</p>
              <div className="flex flex-wrap gap-1 mt-2">
                {activePersona.personality_traits?.map((trait) => (
                  <span
                    key={trait}
                    className="px-2 py-0.5 bg-slate-800 text-slate-300 text-[10px] rounded-full border border-slate-700"
                  >
                    #{trait}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Target Candidate Version
            </label>
            <input
              type="text"
              value={agentVersion}
              onChange={(e) => setAgentVersion(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none font-mono"
            />
          </div>

          <div className="flex items-center justify-between p-3 bg-slate-950/60 rounded-lg border border-slate-800">
            <div className="flex items-center space-x-2">
              <Mic className="w-4 h-4 text-indigo-400" />
              <div>
                <span className="text-xs font-semibold text-slate-200 block">Voice Mode (ASR Simulation)</span>
                <span className="text-[10px] text-slate-500">Injects realistic acoustic transcription jitter</span>
              </div>
            </div>
            <input
              type="checkbox"
              checked={voiceMode}
              onChange={(e) => setVoiceMode(e.target.checked)}
              className="w-4 h-4 accent-indigo-600 rounded"
            />
          </div>

          <button
            onClick={handleRun}
            disabled={isLoading}
            className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold rounded-lg text-xs shadow-lg transition-all flex items-center justify-center space-x-2"
          >
            <Play className={`w-3.5 h-3.5 ${isLoading ? 'animate-pulse' : ''}`} />
            <span>{isLoading ? 'Simulating Dialogue...' : 'Launch Simulation Run'}</span>
          </button>
        </div>

        {/* Live Simulation Transcript */}
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl flex flex-col h-[520px]">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-3">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                Dialogue Trace & Edge-Case Detection
              </h3>
            </div>
            {simulationResult && (
              <span
                className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                  simulationResult.surfaced_failure
                    ? 'bg-rose-950 text-rose-400 border border-rose-800'
                    : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                }`}
              >
                {simulationResult.surfaced_failure
                  ? `Failure Detected: ${simulationResult.failure_category}`
                  : 'Goal Satisfied (Compliant)'}
              </span>
            )}
          </div>

          <div className="flex-1 overflow-y-auto space-y-3 p-1">
            {!simulationResult ? (
              <div className="text-center py-20 text-slate-500 text-xs">
                Select a persona on the left and click "Launch Simulation Run" to begin testing.
              </div>
            ) : (
              simulationResult.transcript_log?.map((turn, i) => {
                const isCustomer = turn.speaker === 'customer';
                return (
                  <div
                    key={i}
                    className={`p-3 rounded-xl border text-xs ${
                      isCustomer
                        ? 'bg-slate-950/70 border-slate-800 ml-4 text-slate-200'
                        : 'bg-indigo-950/20 border-indigo-900/60 mr-4 text-slate-200'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5 text-[11px] font-semibold text-slate-400">
                      <span className="flex items-center gap-1.5">
                        {isCustomer ? <User className="w-3.5 h-3.5 text-sky-400" /> : <Bot className="w-3.5 h-3.5 text-indigo-400" />}
                        {isCustomer ? activePersona?.name || 'Customer' : 'Candidate Agent'}
                      </span>
                      {turn.latency_ms && (
                        <span className="font-mono text-[10px] text-slate-500">
                          {turn.latency_ms}ms
                        </span>
                      )}
                    </div>
                    <p className="leading-relaxed">{turn.text}</p>
                  </div>
                );
              })
            )}
          </div>

          {simulationResult && simulationResult.surfaced_failure && (
            <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
              <span className="text-xs text-rose-400 font-semibold flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-rose-500" />
                Edge defect surfaced during simulation.
              </span>
              <button
                onClick={() => onConvertToTest(simulationResult)}
                className="px-3 py-1.5 bg-rose-600 hover:bg-rose-500 text-white rounded text-xs font-bold transition-all shadow-md"
              >
                Add as Regression Test Case
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
