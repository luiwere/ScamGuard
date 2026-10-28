import React from 'react';
import { AlertCircle, Cpu, Zap, Quote } from 'lucide-react';
import { TacticItem } from '../types';

interface TacticChipsProps {
  tactics: TacticItem[];
}

export const TacticChips: React.FC<TacticChipsProps> = ({ tactics }) => {
  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400" />
          <span className="text-sm font-semibold text-slate-200">Flagged Caller Tactics</span>
        </div>
        <span className="text-xs font-mono text-slate-500">
          {tactics.length} {tactics.length === 1 ? 'tactic' : 'tactics'} identified
        </span>
      </div>

      {tactics.length === 0 ? (
        <div className="p-4 rounded-xl border border-dashed border-slate-800 text-center text-xs text-slate-500">
          No manipulative tactics detected yet. Clean call stream.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5">
          {tactics.map((tac, idx) => {
            const isRules = tac.source === 'rules';

            return (
              <div
                key={idx}
                className="p-3 rounded-xl bg-slate-950/70 border border-red-500/30 text-xs space-y-1.5 transition hover:border-red-500/50"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold text-red-300">{tac.name}</span>
                  <div className="flex items-center gap-1.5 shrink-0">
                    <span
                      className={`text-[9px] font-mono px-1.5 py-0.5 rounded font-bold uppercase flex items-center gap-1 ${
                        isRules
                          ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                          : 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                      }`}
                    >
                      {isRules ? <Zap className="w-2.5 h-2.5" /> : <Cpu className="w-2.5 h-2.5" />}
                      {isRules ? 'Rules' : 'Llama 3.3'}
                    </span>
                    <span className="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-red-500/20 text-red-400 border border-red-500/30">
                      {Math.round(tac.confidence * 100)}%
                    </span>
                  </div>
                </div>

                {tac.evidence && (
                  <div className="flex items-start gap-1.5 text-slate-400 text-[11px] italic bg-slate-900/60 p-2 rounded-lg border border-slate-800">
                    <Quote className="w-3 h-3 text-red-400/80 shrink-0 mt-0.5" />
                    <span className="line-clamp-2">"{tac.evidence}"</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
