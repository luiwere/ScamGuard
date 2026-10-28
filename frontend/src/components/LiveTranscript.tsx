import React, { useEffect, useRef } from 'react';
import { FileText, MicOff, CheckCircle2, ShieldAlert } from 'lucide-react';
import { TranscriptEvent, TacticItem } from '../types';

interface LiveTranscriptProps {
  transcripts: TranscriptEvent[];
  tactics: TacticItem[];
  isCallActive: boolean;
}

export const LiveTranscript: React.FC<LiveTranscriptProps> = ({
  transcripts,
  tactics,
  isCallActive,
}) => {
  const scrollRef = useRef<HTMLDivElement | null>(null);

  // Auto-scroll to bottom as new speech arrives
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [transcripts]);

  // Extract all evidence phrases to highlight
  const evidencePhrases = tactics
    .map((t) => t.evidence.trim())
    .filter((e) => e.length > 2);

  // Function to render text with evidence phrases highlighted
  const renderHighlightedText = (text: string) => {
    if (evidencePhrases.length === 0) {
      return text;
    }

    // Escape regex characters
    const escaped = evidencePhrases
      .map((phrase) => phrase.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
      .join('|');

    if (!escaped) return text;

    try {
      const regex = new RegExp(`(${escaped})`, 'gi');
      const parts = text.split(regex);

      return parts.map((part, index) => {
        const isMatch = evidencePhrases.some(
          (phrase) => phrase.toLowerCase() === part.toLowerCase()
        );

        if (isMatch) {
          return (
            <mark
              key={index}
              className="bg-red-500/25 text-red-200 px-1.5 py-0.5 rounded font-semibold border border-red-500/40 inline-block shadow-sm"
            >
              {part}
            </mark>
          );
        }
        return <span key={index}>{part}</span>;
      });
    } catch {
      return text;
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm flex flex-col h-[420px]">
      {/* Transcript Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-3">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-indigo-400" />
          <h3 className="text-sm font-semibold text-slate-200">Live Call Dialogue</h3>
        </div>
        <div className="flex items-center gap-2">
          {evidencePhrases.length > 0 && (
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-red-500/20 text-red-300 border border-red-500/30 flex items-center gap-1">
              <ShieldAlert className="w-2.5 h-2.5" />
              <span>Evidence Highlighted</span>
            </span>
          )}
          <span className="text-xs text-slate-500 font-mono">
            {transcripts.length} {transcripts.length === 1 ? 'event' : 'events'}
          </span>
        </div>
      </div>

      {/* Transcript Body */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-3 pr-2 scroll-smooth">
        {transcripts.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500 text-xs text-center p-6 space-y-2">
            {isCallActive ? (
              <>
                <div className="w-9 h-9 rounded-full border-2 border-indigo-500/30 border-t-indigo-500 animate-spin mb-1" />
                <p className="font-medium text-slate-300">Listening to speakerphone audio...</p>
                <p className="text-slate-500 max-w-xs">
                  Audio chunks are being processed live by Fireworks Whisper STT and Llama 3.3.
                </p>
              </>
            ) : (
              <>
                <div className="w-12 h-12 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-center text-slate-600 mb-1">
                  <MicOff className="w-6 h-6" />
                </div>
                <p className="font-medium text-slate-300">No active call session</p>
                <p className="text-slate-500 max-w-xs">
                  Choose Live Microphone or a Scripted Demo Scenario, then click "Start Real-Time Call Shield".
                </p>
              </>
            )}
          </div>
        ) : (
          transcripts.map((t, idx) => {
            const isSystem = t.speaker === 'system';

            return (
              <div
                key={idx}
                className={`p-3.5 rounded-xl text-xs leading-relaxed transition-all duration-150 ${
                  isSystem
                    ? 'bg-slate-950/80 text-slate-400 font-mono border border-slate-800/80'
                    : 'bg-slate-950/90 text-slate-200 border border-slate-800 shadow-sm'
                }`}
              >
                <div className="flex justify-between items-center text-[10px] text-slate-500 mb-1.5 font-mono uppercase">
                  <span className="font-semibold text-slate-400 flex items-center gap-1.5">
                    <span
                      className={`w-1.5 h-1.5 rounded-full ${
                        isSystem ? 'bg-indigo-400' : 'bg-red-400'
                      }`}
                    />
                    {t.speaker || 'Caller'}
                  </span>
                  {t.is_final && (
                    <span className="text-emerald-500 flex items-center gap-1">
                      <CheckCircle2 className="w-2.5 h-2.5" />
                      verified
                    </span>
                  )}
                </div>
                <div className="text-slate-200 text-sm leading-relaxed">
                  {renderHighlightedText(t.text)}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
