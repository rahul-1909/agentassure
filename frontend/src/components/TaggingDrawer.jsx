import React, { useState, useEffect } from 'react';
import { Tag, AlertCircle, CheckCircle, ShieldAlert, Wrench, Send, Timer } from 'lucide-react';
import Button from './common/Button';

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

  // Timer for turnaround tracking
  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedSeconds((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [selectedTurn]);

  // Reset timer on turn change
  useEffect(() => {
    setElapsedSeconds(0);
    setRootCauseNotes('');
  }, [selectedTurn?.id]);

  const handleL1Change = (newCategory) => {
    setCategoryL1(newCategory);
    const subCategories = TAXONOMY_TREE[newCategory] || [];
    setCategoryL2(subCategories[0] || 'General Failure');
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
      root_cause_notes: rootCauseNotes || `Observed failure in turn #${selectedTurn.turn_index}: ${categoryL2}`,
      fix_type: fixType,
      is_confirmed_failure: true,
      review_duration_seconds: Math.max(1, elapsedSeconds),
    });
  };

  if (!selectedTurn) {
    return (
      <div className="bg-white border border-slate-200/90 rounded-xl p-6 text-center text-slate-400 flex flex-col items-center justify-center h-full shadow-sm">
        <Tag className="w-10 h-10 mb-3 text-slate-300" />
        <h4 className="text-sm font-semibold text-slate-700 mb-1">No Turn Selected</h4>
        <p className="text-xs text-slate-500 max-w-xs leading-relaxed">
          Click any conversational turn in the transcript or use <kbd className="px-1.5 py-0.5 bg-slate-100 border border-slate-200 rounded font-mono text-[11px] text-slate-700">Tab</kbd> to inspect and tag failures.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200/90 rounded-xl p-5 shadow-sm flex flex-col h-full overflow-y-auto">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
        <div className="flex items-center space-x-2">
          <ShieldAlert className="w-5 h-5 text-[#0066FF]" />
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
            Failure Classification
          </h3>
        </div>
        <div className="flex items-center space-x-1.5 text-xs font-mono text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
          <Timer className="w-3.5 h-3.5 text-slate-500" />
          <span>{elapsedSeconds}s</span>
        </div>
      </div>

      {/* Selected turn reference */}
      <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80 text-xs mb-4">
        <span className="text-[11px] text-slate-500 font-semibold block mb-1">
          Turn #{selectedTurn.turn_index} ({selectedTurn.speaker.toUpperCase()}):
        </span>
        <p className="text-slate-800 italic leading-relaxed line-clamp-2">
          "{selectedTurn.transcript}"
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4 flex-1 flex flex-col justify-between">
        <div className="space-y-3.5">
          {/* L1 Category */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              L1 Failure Taxonomy
            </label>
            <select
              value={categoryL1}
              onChange={(e) => handleL1Change(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 focus:bg-white focus:ring-2 focus:ring-[#0066FF]/30 focus:outline-none"
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
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              L2 Specific Subtype
            </label>
            <select
              value={categoryL2}
              onChange={(e) => setCategoryL2(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 focus:bg-white focus:ring-2 focus:ring-[#0066FF]/30 focus:outline-none"
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
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Failure Severity Level
            </label>
            <div className="grid grid-cols-4 gap-1.5">
              {[
                { id: 'S1', label: 'S1 (Critical)', color: 'border-rose-300 text-rose-700 bg-rose-50' },
                { id: 'S2', label: 'S2 (Major)', color: 'border-amber-300 text-amber-700 bg-amber-50' },
                { id: 'S3', label: 'S3 (Mod)', color: 'border-blue-300 text-blue-700 bg-blue-50' },
                { id: 'S4', label: 'S4 (Minor)', color: 'border-slate-300 text-slate-700 bg-slate-50' },
              ].map((s) => (
                <button
                  type="button"
                  key={s.id}
                  onClick={() => setSeverity(s.id)}
                  className={`py-1.5 px-2 text-center text-xs font-bold rounded-lg border transition-all ${
                    severity === s.id
                      ? `${s.color} ring-2 ring-[#0066FF]/30 shadow-sm`
                      : 'border-slate-200 text-slate-600 bg-slate-50 hover:bg-slate-100'
                  }`}
                >
                  {s.id}
                </button>
              ))}
            </div>
          </div>

          {/* Fix Suggestion Type */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center gap-1.5">
              <Wrench className="w-3.5 h-3.5 text-[#0066FF]" />
              Prescribed Fix Recommendation
            </label>
            <select
              value={fixType}
              onChange={(e) => setFixType(e.target.value)}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 focus:bg-white focus:ring-2 focus:ring-[#0066FF]/30 focus:outline-none"
            >
              <option value="prompt_patch">Prompt Patch (Prompt instructions/constraints)</option>
              <option value="kb_entry">KB Entry (Grounding document in vector store)</option>
              <option value="tool_retry">Tool Retry / API Logic (Function calling)</option>
              <option value="asr_vocab_boost">ASR Vocab Boost (Acoustic language model)</option>
            </select>
          </div>

          {/* Root Cause Notes */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">
              Root Cause & Engineering Note
            </label>
            <textarea
              value={rootCauseNotes}
              onChange={(e) => setRootCauseNotes(e.target.value)}
              placeholder="Explain what the agent did wrong and why this failure occurred..."
              rows={3}
              className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:bg-white focus:ring-2 focus:ring-[#0066FF]/30 focus:outline-none resize-none"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="pt-4 border-t border-slate-100 space-y-2">
          <button
            type="submit"
            className="w-full py-2.5 px-4 bg-[#0066FF] hover:bg-[#0052CC] text-white font-semibold rounded-lg shadow-sm transition-all flex items-center justify-center space-x-2 text-xs active:scale-[0.99]"
          >
            <Send className="w-3.5 h-3.5" />
            <span>Confirm Defect & Queue Regression (Enter)</span>
          </button>

          <button
            type="button"
            onClick={() => onApproveTurn(selectedTurn.id)}
            className="w-full py-2 px-4 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 font-semibold rounded-lg transition-all flex items-center justify-center space-x-2 text-xs"
          >
            <CheckCircle className="w-3.5 h-3.5" />
            <span>Approve Turn as Compliant (A)</span>
          </button>
        </div>
      </form>
    </div>
  );
}
