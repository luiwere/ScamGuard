import React from 'react';
import { ShieldAlert, PhoneOff, Send, AlertOctagon } from 'lucide-react';
import { AlertEvent } from '../types';

interface AlertOverlayProps {
  alert: AlertEvent;
  contactName: string;
  onHangUp: () => void;
  onDismiss: () => void;
}

export const AlertOverlay: React.FC<AlertOverlayProps> = ({
  alert,
  contactName,
  onHangUp,
  onDismiss,
}) => {
  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 bg-red-950/90 backdrop-blur-lg z-50 flex items-center justify-center p-4 sm:p-6 animate-in fade-in duration-200"
    >
      <div className="max-w-lg w-full bg-slate-950 border-2 border-red-500 rounded-3xl p-6 sm:p-8 shadow-2xl shadow-red-500/30 space-y-6 text-center relative overflow-hidden">
        {/* Urgent Glowing Header Ring */}
        <div className="relative mx-auto w-20 h-20">
          <div className="absolute inset-0 rounded-full bg-red-500/30 animate-ping" />
          <div className="relative w-20 h-20 rounded-full bg-red-500/20 border-2 border-red-500 flex items-center justify-center text-red-500">
            <ShieldAlert className="w-10 h-10" />
          </div>
        </div>

        {/* Warning Title */}
        <div className="space-y-2">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-500/20 text-red-400 border border-red-500/40 text-xs font-mono font-bold tracking-wider uppercase">
            <AlertOctagon className="w-3.5 h-3.5" />
            High Threat Scam Detected
          </div>
          <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            DO NOT COMPLY
          </h2>
          <p className="text-sm text-red-300 max-w-md mx-auto leading-relaxed">
            {alert.advice}
          </p>
        </div>

        {/* Recommended Action Box */}
        <div className="bg-red-500/10 border border-red-500/40 rounded-2xl p-4 sm:p-5 text-left space-y-1">
          <span className="text-[10px] font-mono font-bold uppercase tracking-wider text-red-400">
            Mandatory Action:
          </span>
          <p className="text-sm sm:text-base text-white font-bold leading-snug">
            {alert.action}
          </p>
        </div>

        {/* Telegram Guardian Notification Notice */}
        {alert.contact_notified && (
          <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center justify-center gap-2">
            <Send className="w-4 h-4 shrink-0 text-emerald-400" />
            <span>
              Telegram alert dispatched to <b>{contactName}</b>. Help is on the way.
            </span>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 pt-2">
          <button
            onClick={onHangUp}
            className="flex-1 py-4 px-6 rounded-2xl bg-gradient-to-r from-red-600 via-rose-600 to-red-600 hover:from-red-500 hover:to-rose-500 text-white font-bold text-base shadow-xl shadow-red-600/40 active:scale-[0.99] transition duration-150 flex items-center justify-center gap-2 cursor-pointer"
          >
            <PhoneOff className="w-5 h-5" />
            <span>Hang Up Immediately</span>
          </button>
          <button
            onClick={onDismiss}
            className="py-4 px-5 rounded-2xl bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-800 text-sm font-medium transition cursor-pointer"
          >
            Dismiss
          </button>
        </div>
      </div>
    </div>
  );
};
