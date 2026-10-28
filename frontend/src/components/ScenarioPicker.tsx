import React from 'react';
import { Radio, Mic, FileText, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { Scenario } from '../types';

interface ScenarioPickerProps {
  selectedScenario: string;
  onSelect: (id: string) => void;
  scenarios: Scenario[];
  disabled: boolean;
}

export const ScenarioPicker: React.FC<ScenarioPickerProps> = ({
  selectedScenario,
  onSelect,
  scenarios,
  disabled,
}) => {
  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
          <Radio className="w-4 h-4 text-indigo-400" />
          <span>Call Source Mode</span>
        </div>
        <span className="text-[11px] text-slate-500 font-mono">
          {disabled ? 'Locked during call' : 'Select mode'}
        </span>
      </div>

      <div className="space-y-2">
        {/* Live Mic Option */}
        <label
          className={`flex items-start gap-3 p-3.5 rounded-xl border cursor-pointer transition ${
            selectedScenario === 'live'
              ? 'border-indigo-500 bg-indigo-500/10 text-white shadow-sm shadow-indigo-500/10'
              : 'border-slate-800 hover:border-slate-700 text-slate-300 bg-slate-950/40'
          } ${disabled ? 'opacity-60 cursor-not-allowed' : ''}`}
        >
          <input
            type="radio"
            name="scenario"
            value="live"
            checked={selectedScenario === 'live'}
            onChange={() => onSelect('live')}
            disabled={disabled}
            className="mt-1 accent-indigo-500"
          />
          <div className="flex-1">
            <div className="text-sm font-medium flex items-center justify-between">
              <span className="flex items-center gap-1.5 text-indigo-300 font-semibold">
                <Mic className="w-3.5 h-3.5 text-indigo-400" />
                Live Microphone
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                16kHz PCM16
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Streams phone speakerphone audio directly through client AudioWorklet to STT & AI judge.
            </p>
          </div>
        </label>

        {/* Demo Scenarios */}
        {scenarios.map((sc) => {
          const isSelected = selectedScenario === sc.id;
          const isScam = sc.category === 'scam';

          return (
            <label
              key={sc.id}
              className={`flex items-start gap-3 p-3.5 rounded-xl border cursor-pointer transition ${
                isSelected
                  ? 'border-indigo-500 bg-indigo-500/10 text-white shadow-sm shadow-indigo-500/10'
                  : 'border-slate-800 hover:border-slate-700 text-slate-300 bg-slate-950/40'
              } ${disabled ? 'opacity-60 cursor-not-allowed' : ''}`}
            >
              <input
                type="radio"
                name="scenario"
                value={sc.id}
                checked={isSelected}
                onChange={() => onSelect(sc.id)}
                disabled={disabled}
                className="mt-1 accent-indigo-500"
              />
              <div className="flex-1">
                <div className="text-sm font-medium flex items-center justify-between">
                  <span className="flex items-center gap-1.5 text-slate-200">
                    <FileText className="w-3.5 h-3.5 text-slate-400" />
                    {sc.title}
                  </span>
                  <span
                    className={`text-[10px] font-mono px-2 py-0.5 rounded uppercase flex items-center gap-1 border ${
                      isScam
                        ? 'bg-red-500/15 text-red-400 border-red-500/30'
                        : 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
                    }`}
                  >
                    {isScam ? (
                      <ShieldAlert className="w-2.5 h-2.5" />
                    ) : (
                      <CheckCircle2 className="w-2.5 h-2.5" />
                    )}
                    {sc.category}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-1">{sc.description}</p>
              </div>
            </label>
          );
        })}
      </div>
    </div>
  );
};
