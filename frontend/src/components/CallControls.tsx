import React from 'react';
import { PhoneCall, PhoneOff, Volume2 } from 'lucide-react';
import { SocketStatus } from '../hooks/useCallSocket';

interface CallControlsProps {
  status: SocketStatus;
  isRecording: boolean;
  audioLevel: number;
  isLiveMic: boolean;
  onStart: () => void;
  onStop: () => void;
}

export const CallControls: React.FC<CallControlsProps> = ({
  status,
  isRecording,
  audioLevel,
  isLiveMic,
  onStart,
  onStop,
}) => {
  const isCallActive = status === 'connected' || status === 'connecting';

  return (
    <div className="space-y-4">
      {/* Audio Level Visualizer for live microphone */}
      {isLiveMic && isRecording && (
        <div className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
          <div className="flex justify-between items-center text-xs text-slate-400">
            <span className="flex items-center gap-1.5 font-medium">
              <Volume2 className="w-3.5 h-3.5 text-emerald-400" />
              Microphone Sensitivity
            </span>
            <span className="font-mono text-emerald-400 font-semibold">{audioLevel}%</span>
          </div>

          <div className="w-full h-2.5 rounded-full bg-slate-950 overflow-hidden p-0.5 border border-slate-800">
            <div
              className={`h-full rounded-full transition-all duration-75 ${
                audioLevel > 60
                  ? 'bg-amber-400'
                  : audioLevel > 15
                  ? 'bg-emerald-400'
                  : 'bg-emerald-600'
              }`}
              style={{ width: `${Math.min(100, Math.max(4, audioLevel))}%` }}
            />
          </div>
        </div>
      )}

      {/* Main Action Button */}
      {!isCallActive ? (
        <button
          onClick={onStart}
          className="w-full py-4 px-6 rounded-2xl font-bold flex items-center justify-center gap-2.5 bg-gradient-to-r from-red-600 via-rose-600 to-red-600 hover:from-red-500 hover:to-rose-500 text-white shadow-xl shadow-red-600/25 active:scale-[0.99] transition duration-150 cursor-pointer text-base"
        >
          <PhoneCall className="w-5 h-5 text-white" />
          <span>Start Real-Time Call Shield</span>
        </button>
      ) : (
        <button
          onClick={onStop}
          className="w-full py-4 px-6 rounded-2xl font-bold flex items-center justify-center gap-2.5 bg-slate-900 hover:bg-slate-800 text-red-400 border border-red-500/30 hover:border-red-500/60 shadow-lg shadow-red-500/10 active:scale-[0.99] transition duration-150 cursor-pointer text-base"
        >
          <PhoneOff className="w-5 h-5" />
          <span>End Active Call Session</span>
        </button>
      )}
    </div>
  );
};
