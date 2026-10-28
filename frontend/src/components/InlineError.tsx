import React from 'react';
import { AlertTriangle, X } from 'lucide-react';

interface InlineErrorProps {
  message: string | null;
  onDismiss: () => void;
}

export const InlineError: React.FC<InlineErrorProps> = ({ message, onDismiss }) => {
  if (!message) return null;

  return (
    <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-300 flex items-start justify-between gap-3 text-xs animate-in fade-in duration-150">
      <div className="flex items-start gap-2.5">
        <AlertTriangle className="w-4 h-4 shrink-0 text-red-400 mt-0.5" />
        <span className="leading-relaxed">{message}</span>
      </div>
      <button
        onClick={onDismiss}
        className="p-1 rounded-md text-red-400 hover:text-red-200 hover:bg-red-500/20 transition shrink-0"
        aria-label="Dismiss error"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};
