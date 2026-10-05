import React from 'react';
import { User, Bot, AlertTriangle, CheckCircle2, Clock, Check, Flag } from 'lucide-react';
import Badge from './common/Badge';

export default function TranscriptView({
  turns = [],
  activeTurnIndex,
  onSelectTurn,
  currentTime = 0.0,
  annotations = [],
  onApproveTurn,
  onTagTurn,
}) {
  return (
    <div className="flex flex-col h-full bg-white border border-slate-200/90 rounded-xl overflow-hidden shadow-sm">
      {/* Header */}
      <div className="p-3.5 bg-slate-50/80 border-b border-slate-100 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-semibold text-slate-800 uppercase tracking-wider">
            Synchronized Transcript
          </span>
          <span className="px-2 py-0.5 text-xs font-mono bg-white border border-slate-200 text-slate-600 rounded-full font-medium">
            {turns.length} Turns
          </span>
        </div>
        <div className="flex items-center space-x-2 text-xs text-slate-500">
          <span className="hidden sm:inline">Shortcuts:</span>
          <kbd className="px-1.5 py-0.5 bg-white border border-slate-200 rounded text-slate-700 font-mono text-[11px]">Tab</kbd>
          <span className="hidden sm:inline">Next</span>
          <kbd className="px-1.5 py-0.5 bg-emerald-50 border border-emerald-200 rounded text-emerald-700 font-bold font-mono text-[11px]">A</kbd>
          <span className="hidden sm:inline">Approve</span>
          <kbd className="px-1.5 py-0.5 bg-rose-50 border border-rose-200 rounded text-rose-700 font-bold font-mono text-[11px]">D</kbd>
          <span className="hidden sm:inline">Tag</span>
        </div>
      </div>

      {/* Turn List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50/40">
        {turns.length === 0 ? (
          <div className="text-center py-12 text-slate-400 text-sm">
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
                className={`p-4 rounded-xl border transition-all cursor-pointer relative bg-white ${
                  isSelected
                    ? 'border-[#0066FF] shadow-sm ring-1 ring-[#0066FF]/40'
                    : isPlayingThisTurn
                    ? 'border-amber-400 bg-amber-50/30'
                    : 'border-slate-200/80 hover:border-slate-300 hover:bg-slate-50/50'
                }`}
              >
                {/* Active indicator bar */}
                {isSelected && (
                  <div className="absolute left-0 top-3 bottom-3 w-1 bg-[#0066FF] rounded-r" />
                )}

                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <div
                      className={`p-1.5 rounded-lg ${
                        isUser
                          ? 'bg-sky-50 text-sky-600 border border-sky-100'
                          : 'bg-indigo-50 text-indigo-600 border border-indigo-100'
                      }`}
                    >
                      {isUser ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
                    </div>
                    <span className="text-xs font-semibold text-slate-900">
                      {isUser ? 'Customer' : 'Conversational Agent'}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400 font-medium">
                      Turn #{turn.turn_index}
                    </span>
                  </div>

                  <div className="flex items-center space-x-2 text-[11px] font-mono text-slate-500">
                    <span className="flex items-center gap-1">
                      <Clock className="w-3 h-3 text-slate-400" />
                      {turn.audio_start_time.toFixed(1)}s - {turn.audio_end_time.toFixed(1)}s
                    </span>
                    {turn.asr_confidence !== undefined && (
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] font-semibold border ${
                          turn.asr_confidence >= 0.9
                            ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
                            : 'bg-amber-50 text-amber-700 border-amber-200'
                        }`}
                      >
                        ASR: {(turn.asr_confidence * 100).toFixed(0)}%
                      </span>
                    )}
                  </div>
                </div>

                {/* Transcript text */}
                <p className="text-sm text-slate-800 leading-relaxed font-normal pl-1">
                  {turn.transcript}
                </p>

                {/* Annotation pill if tagged */}
                {turnAnnotation ? (
                  <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-xs">
                    <span className="flex items-center gap-1.5 text-rose-600 font-medium">
                      <AlertTriangle className="w-3.5 h-3.5 text-rose-500" />
                      [{turnAnnotation.severity}] {turnAnnotation.failure_category_l1} &rarr;{' '}
                      {turnAnnotation.failure_category_l2}
                    </span>
                    <Badge variant="purple">Fix: {turnAnnotation.fix_type}</Badge>
                  </div>
                ) : (
                  <div className="mt-3 pt-2 border-t border-slate-100/60 flex items-center justify-end gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (onApproveTurn) onApproveTurn(turn);
                      }}
                      className="px-2.5 py-1 text-xs font-medium text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200/80 rounded-md transition-all flex items-center gap-1"
                    >
                      <Check className="w-3 h-3" /> Approve (A)
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (onTagTurn) onTagTurn(turn);
                      }}
                      className="px-2.5 py-1 text-xs font-medium text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200/80 rounded-md transition-all flex items-center gap-1"
                    >
                      <Flag className="w-3 h-3" /> Tag Issue (D)
                    </button>
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
