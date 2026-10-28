import React from 'react';
import { ShieldAlert, ShieldCheck, AlertTriangle, Clock, Flag, Cpu } from 'lucide-react';
import { RiskEvent } from '../types';

interface RiskMeterProps {
  risk: RiskEvent;
}

export const RiskMeter: React.FC<RiskMeterProps> = ({ risk }) => {
  const score = risk.score;

  const getScoreColor = () => {
    if (score >= 85) return 'text-red-500';
    if (score >= 70) return 'text-rose-500';
    if (score >= 40) return 'text-amber-400';
    if (score >= 20) return 'text-yellow-400';
    return 'text-emerald-400';
  };

  const getBarGradient = () => {
    if (score >= 70) return 'from-amber-500 via-rose-500 to-red-600';
    if (score >= 40) return 'from-emerald-500 via-amber-500 to-rose-500';
    return 'from-emerald-600 to-emerald-400';
  };

  const getBadgeStyle = () => {
    switch (risk.level) {
      case 'critical':
        return 'bg-red-500/20 text-red-400 border-red-500/40 animate-pulse';
      case 'high':
        return 'bg-rose-500/20 text-rose-400 border-rose-500/40';
      case 'medium':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
      case 'low':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40';
      default:
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40';
    }
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return '0s';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
      {/* Top Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          {score >= 70 ? (
            <ShieldAlert className="w-5 h-5 text-red-500 animate-bounce" />
          ) : score >= 40 ? (
            <AlertTriangle className="w-5 h-5 text-amber-400" />
          ) : (
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
          )}
          <div>
            <h3 className="font-semibold text-sm text-slate-200">Call Threat Radar</h3>
            <p className="text-[11px] text-slate-400">Continuous multimodal risk accumulation</p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <span
            className={`text-xs px-2.5 py-1 rounded-full font-mono uppercase font-bold border ${getBadgeStyle()}`}
          >
            {risk.level}
          </span>
          <div className="text-right pl-2 border-l border-slate-800">
            <span className={`text-2xl font-black font-mono tracking-tight ${getScoreColor()}`}>
              {score}
            </span>
            <span className="text-xs text-slate-500 font-mono">/100</span>
          </div>
        </div>
      </div>

      {/* Progress Bar Container with 70 Threshold Marker */}
      <div className="relative pt-1">
        <div className="w-full h-3.5 bg-slate-950 rounded-full overflow-hidden p-0.5 border border-slate-800">
          <div
            className={`h-full rounded-full bg-gradient-to-r ${getBarGradient()} transition-all duration-300 ease-out`}
            style={{ width: `${Math.max(4, score)}%` }}
          />
        </div>

        {/* 70% Alert Trigger Line Marker */}
        <div
          className="absolute top-0 bottom-0 w-0.5 bg-red-400/80 pointer-events-none"
          style={{ left: '70%' }}
        >
          <div className="absolute -top-3.5 -translate-x-1/2 text-[9px] font-mono text-red-400 uppercase font-bold tracking-wider">
            Alert (70)
          </div>
        </div>
      </div>

      {/* Scale Labels */}
      <div className="flex justify-between text-[10px] text-slate-500 uppercase font-mono tracking-wider">
        <span>0 Safe</span>
        <span>20 Low</span>
        <span>40 Warning</span>
        <span className="text-red-400 font-bold">70 Alert</span>
        <span>100 Critical</span>
      </div>

      {/* Live Breakdown Badges */}
      {risk.breakdown && (
        <div className="grid grid-cols-3 gap-2 pt-2 border-t border-slate-800 text-xs">
          <div className="p-2 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center gap-2">
            <Flag className="w-3.5 h-3.5 text-red-400" />
            <div>
              <div className="text-[10px] text-slate-500 uppercase font-mono">Hard Flags</div>
              <div className="font-semibold text-slate-200">{risk.breakdown.hard_flags}</div>
            </div>
          </div>

          <div className="p-2 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center gap-2">
            <Cpu className="w-3.5 h-3.5 text-purple-400" />
            <div>
              <div className="text-[10px] text-slate-500 uppercase font-mono">Llama Tactics</div>
              <div className="font-semibold text-slate-200">{risk.breakdown.llm_tactics}</div>
            </div>
          </div>

          <div className="p-2 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center gap-2">
            <Clock className="w-3.5 h-3.5 text-indigo-400" />
            <div>
              <div className="text-[10px] text-slate-500 uppercase font-mono">Call Duration</div>
              <div className="font-semibold text-slate-200 font-mono">
                {formatDuration(risk.breakdown.call_duration_seconds)}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
