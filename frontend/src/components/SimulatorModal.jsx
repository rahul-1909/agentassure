import React, { useState, useEffect } from 'react';
import { Users, Play, Mic, AlertTriangle, Bot, User, Sparkles } from 'lucide-react';
import Card from './common/Card';
import Badge from './common/Badge';
import Button from './common/Button';

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
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-4 border-b border-slate-200">
        <div>
          <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2 tracking-tight">
            <Users className="w-5 h-5 text-[#0066FF]" />
            Adversarial Customer Persona Simulator
          </h2>
          <p className="text-xs text-slate-500 mt-1">
            Simulate 10+ edge-case personalities (price-sensitive, confused elderly, hostile debtors, Hinglish code-switchers) to surface hidden defects before production release.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Controls Column */}
        <div className="lg:col-span-4 space-y-4">
          <Card title="Simulation Parameters" subtitle="Configure customer profile and test target">
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Select Synthetic Persona
                </label>
                <select
                  value={selectedKey}
                  onChange={(e) => setSelectedKey(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 focus:bg-white focus:ring-2 focus:ring-[#0066FF]/30 focus:outline-none"
                >
                  {personas.map((p) => (
                    <option key={p.persona_key} value={p.persona_key}>
                      {p.name} ({p.language.toUpperCase()})
                    </option>
                  ))}
                </select>
              </div>

              {activePersona && (
                <div className="p-3 bg-slate-50 rounded-lg border border-slate-200/80 text-xs space-y-2">
                  <span className="text-[10px] uppercase font-bold text-[#0066FF] block">
                    Behavioral Profile
                  </span>
                  <p className="text-slate-700 leading-relaxed">{activePersona.description}</p>
                  <div className="flex flex-wrap gap-1 mt-2">
                    {activePersona.personality_traits?.map((trait) => (
                      <Badge key={trait} variant="neutral">
                        #{trait}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Target Candidate Version
                </label>
                <input
                  type="text"
                  value={agentVersion}
                  onChange={(e) => setAgentVersion(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 focus:bg-white focus:ring-2 focus:ring-[#0066FF]/30 focus:outline-none font-mono"
                />
              </div>

              <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg border border-slate-200/80">
                <div className="flex items-center space-x-2">
                  <Mic className="w-4 h-4 text-[#0066FF]" />
                  <div>
                    <span className="text-xs font-semibold text-slate-800 block">Voice Mode (ASR Simulation)</span>
                    <span className="text-[10px] text-slate-500">Injects acoustic transcription jitter</span>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={voiceMode}
                  onChange={(e) => setVoiceMode(e.target.checked)}
                  className="w-4 h-4 accent-[#0066FF] rounded"
                />
              </div>

              <Button
                variant="primary"
                onClick={handleRun}
                disabled={isLoading}
                icon={Play}
                className="w-full"
              >
                {isLoading ? 'Simulating Dialogue...' : 'Launch Simulation Run'}
              </Button>
            </div>
          </Card>
        </div>

        {/* Live Simulation Transcript */}
        <div className="lg:col-span-8">
          <Card
            title="Dialogue Trace & Edge-Case Detection"
            subtitle="Multi-turn conversation chain generated against agent"
            action={
              simulationResult && (
                <Badge variant={simulationResult.surfaced_failure ? 'error' : 'success'}>
                  {simulationResult.surfaced_failure
                    ? `Failure Surfaced: ${simulationResult.failure_category}`
                    : 'All Turns Compliant'}
                </Badge>
              )
            }
          >
            <div className="flex flex-col h-[460px]">
              <div className="flex-1 overflow-y-auto space-y-3 p-3 bg-slate-50/50 rounded-xl border border-slate-100">
                {!simulationResult ? (
                  <div className="flex flex-col items-center justify-center h-full text-slate-400 space-y-2">
                    <Sparkles className="w-8 h-8 text-slate-300" />
                    <p className="text-sm">Click "Launch Simulation Run" to execute dialogue stress test.</p>
                  </div>
                ) : (
                  simulationResult.transcript_log?.map((turn, i) => {
                    const isCust = turn.speaker.toLowerCase() === 'customer';
                    return (
                      <div
                        key={i}
                        className={`flex gap-3 max-w-[85%] ${
                          isCust ? 'mr-auto' : 'ml-auto flex-row-reverse'
                        }`}
                      >
                        <div
                          className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 text-xs font-bold ${
                            isCust ? 'bg-sky-100 text-sky-700' : 'bg-indigo-100 text-[#0066FF]'
                          }`}
                        >
                          {isCust ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
                        </div>
                        <div
                          className={`p-3 rounded-2xl text-xs leading-relaxed ${
                            isCust
                              ? 'bg-white border border-slate-200 text-slate-800 rounded-tl-none shadow-sm'
                              : 'bg-[#0066FF] text-white rounded-tr-none shadow-sm'
                          }`}
                        >
                          <span className={`text-[10px] font-bold block mb-1 ${isCust ? 'text-sky-600' : 'text-blue-100'}`}>
                            {isCust ? activePersona?.name || 'Customer' : 'Candidate Agent'}
                          </span>
                          <p>{turn.text}</p>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>

              {simulationResult && (
                <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
                  <div className="flex items-center gap-4">
                    <span>Turns: <strong className="text-slate-800">{simulationResult.total_turns}</strong></span>
                    <span>Avg Latency: <strong className="text-slate-800">{simulationResult.latency_avg_ms?.toFixed(0)}ms</strong></span>
                  </div>
                  {simulationResult.surfaced_failure && (
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => onConvertToTest(simulationResult.id)}
                    >
                      Convert to Regression Case
                    </Button>
                  )}
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
