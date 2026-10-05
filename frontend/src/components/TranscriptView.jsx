import React from 'react';
import { User, Bot, AlertTriangle, CheckCircle2, Clock } from 'lucide-react';

export default function TranscriptView({
  turns = [],
  activeTurnIndex,
  onSelectTurn,
  currentTime = 0.0,
  annotations = [],
}) {
  return (
    <div className="flex flex-col h-full bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
      {/* Header */}
      <div className="p-3 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
            Synchronized Transcript
          </span>
          <span className="px-2 py-0.5 text-[11px] font-mono bg-slate-800 text-slate-400 rounded-full">
            {turns.length} Turns
          </span>
        </div>
        <div className="flex items-center space-x-2 text-[11px] text-slate-400">
          <span>Shortcuts:</span>
          <kbd className="px-1.5 py-0.5 bg-slate-800 border border-slate-700 rounded text-slate-300">Tab</kbd>
          <span>Navigate</span>
          <kbd className="px-1.5 py-0.5 bg-slate-800 border border-slate-700 rounded text-emerald-400 font-bold">A</kbd>
          <span>Approve</span>
          <kbd className="px-1.5 py-0.5 bg-slate-800 border border-slate-700 rounded text-rose-400 font-bold">D</kbd>
          <span>Defect</span>
        </div>
      </div>

      {/* Turn List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {turns.length === 0 ? (
          <div className="text-center py-12 text-slate-500 text-sm">
            No turns found for this conversation session.
          </div>
        ) : (
          turns.map((turn, idx) => {
            const isSelected = activeTurnIndex === idx;
            const isPlayingThisTurn =
              currentTime >= turn.audio_start_time && currentTime <= turn.audio_end_time;
            const isUser = turn.speaker.toLowerCase() === 'user';

            // Find any confirmed failure annotation on this turn
            const turnAnnotation = annotations.find((a) => a.turn_id === turn.id);

            return (
              <div
                key={turn.id || idx}
                onClick={() => onSelectTurn(idx, turn)}
                className={`p-3.5 rounded-xl border transition-all cursor-pointer relative ${
                  isSelected
                    ? 'border-indigo-500 bg-indigo-950/30 shadow-lg ring-1 ring-indigo-500/50'
                    : isPlayingThisTurn
                    ? 'border-amber-500/60 bg-amber-950/20'
                    : 'border-slate-800/80 bg-slate-950/40 hover:border-slate-700 hover:bg-slate-800/30'
                }`}
              >
                {/* Active indicator bar */}
                {isSelected && (
                  <div className="absolute left-0 top-3 bottom-3 w-1 bg-indigo-500 rounded-r" />
                )}

                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <div
                      className={`p-1.5 rounded-lg ${
                        isUser ? 'bg-sky-950 text-sky-400 border border-sky-800' : 'bg-purple-950 text-purple-400 border border-purple-800'
                      }`}
                    >
                      {isUser ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
                    </div>
                    <span className="text-xs font-semibold text-slate-200">
                      {isUser ? 'Customer' : 'Conversational Agent'}
                    </span>
                    <span className="text-[10px] font-mono text-slate-500">
                      #{turn.turn_index}
                    </span>
                  </div>

                  <div className="flex items-center space-x-2 text-[10px] font-mono text-slate-400">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3 text-slate-500" />
                      {turn.audio_start_time.toFixed(1)}s - {turn.audio_end_time.toFixed(1)}s
                    </span>
                    {turn.asr_confidence !== undefined && (
                      <span
                        className={`px-1.5 py-0.5 rounded ${
                          turn.asr_confidence >= 0.9
                            ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                            : 'bg-amber-950 text-amber-400 border border-amber-800'
                        }`}
                      >
                        ASR: {(turn.asr_confidence * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                </div>

                {/* Transcript text */}
                <p className="text-sm text-slate-200 leading-relaxed font-normal pl-1">
                  {turn.transcript}
                </p>

                {/* Annotation pill if tagged */}
                {turnAnnotation && (
                  <div className="mt-2.5 pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
                    <span className="flex items-center gap-1.5 text-rose-400 font-medium">
                      <AlertTriangle className="w-3.5 h-3.5 text-rose-500" />
                      [{turnAnnotation.severity}] {turnAnnotation.failure_category_l1} &rarr;{' '}
                      {turnAnnotation.failure_category_l2}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono bg-slate-800 px-2 py-0.5 rounded">
                      Fix: {turnAnnotation.fix_type}
                    </span>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
