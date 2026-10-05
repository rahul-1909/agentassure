import React, { useState, useEffect } from 'react';
import { Tag, AlertCircle, CheckCircle, ShieldAlert, Wrench, Send, Timer } from 'lucide-react';

const TAXONOMY_TREE = {
  'Factual Accuracy': [
    'Hallucinated Policy / Product Terms',
    'Unsupported Numerical or Pricing Claim',
    'Fictitious Feature Confirmation',
  ],
  'Compliance': [
    'Missing Statutory or RBI Disclaimer',
    'Unauthorized Financial Advice',
    'Non-Compliant Data Retention Disclosure',
  ],
  'Prompt Injection & Safety': [
    'System Prompt Instruction Leakage',
    'Jailbreak / Persona Override',
    'Toxic / Inappropriate Content',
  ],
  'Knowledge Base Retrieval': [
    'Failed KB Document Lookup',
    'Outdated FAQ Chunk Citation',
  ],
  'Entity Extraction & Understanding': [
    'Wrong Slot Extraction (ID/Date/Amount)',
    'Misinterpreted Customer Intent',
  ],
  'Tone, Sentiment & Empathy': [
    'Dismissive / Rude Demeanor',
    'Lack of Empathy During Escalation',
  ],
  'Conversational Flow & Loops': [
    'Repetitive Non-Progress Loop',
    'Premature Dialogue Termination',
  ],
  'Linguistic Robustness (Hinglish)': [
    'Code-Switching Syntax Failure',
    'Vernacular Idiom Misinterpretation',
  ],
  'Conversational Dynamics & Interruption': [
    'Barge-in / Interruption Disregard',
    'Overlapping Speech Disorientation',
  ],
  'Audio & ASR Quality': [
    'Acoustic Misrecognition of Domain Terms',
    'Phonetic Confusion on Proper Nouns',
  ],
};

export default function TaggingDrawer({
  selectedTurn,
  conversationId,
  onSubmitAnnotation,
  onApproveTurn,
}) {
  const [categoryL1, setCategoryL1] = useState('Factual Accuracy');
  const [categoryL2, setCategoryL2] = useState('Unsupported Numerical or Pricing Claim');
  const [severity, setSeverity] = useState('S1');
  const [fixType, setFixType] = useState('prompt_patch');
  const [rootCauseNotes, setRootCauseNotes] = useState('');
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  // Turnaround stopwatch timer
  useEffect(() => {
    setElapsedSeconds(0);
    const timer = setInterval(() => {
      setElapsedSeconds((s) => s + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [selectedTurn]);

  // Update L2 default when L1 changes
  const handleL1Change = (l1) => {
    setCategoryL1(l1);
    const subcats = TAXONOMY_TREE[l1] || [];
    if (subcats.length > 0) {
      setCategoryL2(subcats[0]);
    }
  };

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (!selectedTurn) return;

    onSubmitAnnotation({
      conversation_id: conversationId,
      turn_id: selectedTurn.id,
      failure_category_l1: categoryL1,
      failure_category_l2: categoryL2,
      severity,
      fix_type: fixType,
      root_cause_notes: rootCauseNotes,
      review_duration_seconds: elapsedSeconds,
      is_confirmed_failure: true,
      tags: [categoryL1.toLowerCase().replace(/\s+/g, '_')],
    });

    // Reset notes
    setRootCauseNotes('');
  };

  if (!selectedTurn) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 text-center text-slate-500 flex flex-col items-center justify-center h-full">
        <Tag className="w-10 h-10 mb-3 text-slate-700" />
        <h4 className="text-sm font-semibold text-slate-400 mb-1">No Turn Selected</h4>
        <p className="text-xs text-slate-500 max-w-xs">
          Click any conversational turn in the transcript or use <kbd className="px-1 py-0.5 bg-slate-800 rounded">Tab</kbd> to inspect and tag failures.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl flex flex-col h-full overflow-y-auto">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
        <div className="flex items-center space-x-2">
          <ShieldAlert className="w-5 h-5 text-indigo-400" />
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            QA Failure Annotation
          </h3>
        </div>
        <div className="flex items-center space-x-2 text-xs font-mono text-slate-400">
          <Timer className="w-3.5 h-3.5 text-indigo-400" />
          <span>{elapsedSeconds}s</span>
        </div>
      </div>

      {/* Selected turn reference */}
      <div className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800 text-xs mb-4">
        <span className="text-[10px] text-slate-500 font-mono block mb-1">
          Annotating Turn #{selectedTurn.turn_index} ({selectedTurn.speaker.toUpperCase()}):
        </span>
        <p className="text-slate-300 italic line-clamp-2">
          "{selectedTurn.transcript}"
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 flex-1 flex flex-col justify-between">
        <div className="space-y-3.5">
          {/* L1 Category */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              L1 Failure Taxonomy
            </label>
            <select
              value={categoryL1}
              onChange={(e) => handleL1Change(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            >
              {Object.keys(TAXONOMY_TREE).map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>

          {/* L2 Subcategory */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              L2 Specific Subtype
            </label>
            <select
              value={categoryL2}
              onChange={(e) => setCategoryL2(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            >
              {(TAXONOMY_TREE[categoryL1] || []).map((sub) => (
                <option key={sub} value={sub}>
                  {sub}
                </option>
              ))}
            </select>
          </div>

          {/* Severity */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Failure Severity Level
            </label>
            <div className="grid grid-cols-4 gap-1.5">
              {[
                { id: 'S1', label: 'S1 (Critical)', color: 'border-red-500 text-red-400 bg-red-950/30' },
                { id: 'S2', label: 'S2 (Major)', color: 'border-orange-500 text-orange-400 bg-orange-950/30' },
                { id: 'S3', label: 'S3 (Mod)', color: 'border-amber-500 text-amber-400 bg-amber-950/30' },
                { id: 'S4', label: 'S4 (Minor)', color: 'border-blue-500 text-blue-400 bg-blue-950/30' },
              ].map((s) => (
                <button
                  type="button"
                  key={s.id}
                  onClick={() => setSeverity(s.id)}
                  className={`py-1.5 px-2 text-center text-xs font-bold rounded-lg border transition-all ${
                    severity === s.id ? `${s.color} ring-1 ring-white/20` : 'border-slate-800 text-slate-400 bg-slate-800/40 hover:bg-slate-800'
                  }`}
                >
                  {s.id}
                </button>
              ))}
            </div>
          </div>

          {/* Fix Suggestion Type */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1 flex items-center gap-1.5">
              <Wrench className="w-3.5 h-3.5 text-indigo-400" />
              Remediation Channel
            </label>
            <select
              value={fixType}
              onChange={(e) => setFixType(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:ring-2 focus:ring-indigo-500 focus:outline-none"
            >
              <option value="prompt_patch">Prompt Patch (Prompt instructions/constraints)</option>
              <option value="kb_entry">KB Entry (Grounding document in vector store)</option>
              <option value="tool_retry">Tool Retry / API Logic (Function calling)</option>
              <option value="asr_vocab_boost">ASR Vocab Boost (Acoustic language model)</option>
            </select>
          </div>

          {/* Root Cause Notes */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Root Cause & Engineering Note
            </label>
            <textarea
              value={rootCauseNotes}
              onChange={(e) => setRootCauseNotes(e.target.value)}
              placeholder="Explain what the agent did wrong and why this failure occurred..."
              rows={3}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 placeholder-slate-500 focus:ring-2 focus:ring-indigo-500 focus:outline-none resize-none"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="pt-4 border-t border-slate-800 space-y-2">
          <button
            type="submit"
            className="w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-lg shadow-lg transition-all flex items-center justify-center space-x-2 text-xs"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Confirm Defect & Queue Regression (Enter)</span>
          </button>

          <button
            type="button"
            onClick={() => onApproveTurn(selectedTurn.id)}
            className="w-full py-2 px-4 bg-slate-800 hover:bg-slate-700 text-emerald-400 font-semibold rounded-lg transition-all flex items-center justify-center space-x-2 text-xs"
          >
            <CheckCircle className="w-3.5 h-3.5" />
            <span>Approve Turn as Compliant (A)</span>
          </button>
        </div>
      </form>
    </div>
  );
}
