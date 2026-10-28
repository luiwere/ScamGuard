import React from 'react';
import { UserCheck, Send } from 'lucide-react';

interface TrustedContactFormProps {
  contactName: string;
  onContactNameChange: (val: string) => void;
  telegramId: string;
  onTelegramIdChange: (val: string) => void;
  phone: string;
  onPhoneChange: (val: string) => void;
  disabled: boolean;
}

export const TrustedContactForm: React.FC<TrustedContactFormProps> = ({
  contactName,
  onContactNameChange,
  telegramId,
  onTelegramIdChange,
  phone,
  onPhoneChange,
  disabled,
}) => {
  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
          <UserCheck className="w-4 h-4 text-emerald-400" />
          <span>Emergency Contact Alert</span>
        </div>
        <div className="flex items-center gap-1 text-[11px] text-emerald-400 font-mono">
          <Send className="w-3 h-3" />
          <span>Telegram Dispatch</span>
        </div>
      </div>

      <p className="text-xs text-slate-400 leading-relaxed">
        When an urgent scam is verified, ScamGuard sends an automated Telegram intervention message to your trusted guardian.
      </p>

      <div className="space-y-3 text-xs">
        <div>
          <label className="text-slate-400 block mb-1 font-medium">Guardian / Contact Name</label>
          <input
            type="text"
            value={contactName}
            onChange={(e) => onContactNameChange(e.target.value)}
            disabled={disabled}
            placeholder="e.g. Sarah (Daughter)"
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition"
          />
        </div>

        <div>
          <label className="text-slate-400 block mb-1 font-medium">Telegram Chat ID</label>
          <input
            type="text"
            value={telegramId}
            onChange={(e) => onTelegramIdChange(e.target.value)}
            disabled={disabled}
            placeholder="e.g. 123456789 or @user_bot"
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-slate-200 font-mono placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition"
          />
        </div>

        <div>
          <label className="text-slate-400 block mb-1 font-medium">Contact Phone (Optional)</label>
          <input
            type="tel"
            value={phone}
            onChange={(e) => onPhoneChange(e.target.value)}
            disabled={disabled}
            placeholder="+1 (555) 234-5678"
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-slate-200 placeholder-slate-600 focus:outline-none focus:border-indigo-500 transition"
          />
        </div>
      </div>
    </div>
  );
};
