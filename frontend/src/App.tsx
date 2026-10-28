import { useState, useEffect } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  Mic,
  MicOff,
  PhoneCall,
  PhoneOff,
  AlertTriangle,
  UserCheck,
  Radio,
  FileText,
} from 'lucide-react';
import { useCallSocket } from './hooks/useCallSocket';
import { useMicStream } from './hooks/useMicStream';
import { Scenario } from './types';

export default function App() {
  const [selectedScenario, setSelectedScenario] = useState<string>('live');
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [contactName, setContactName] = useState('Sarah (Daughter)');
  const [telegramId, setTelegramId] = useState('123456789');

  const {
    status,
    transcripts,
    tactics,
    risk,
    alert,
    error: socketError,
    startCall,
    stopCall,
    sendAudioChunk,
    clearAlert,
    clearError,
  } = useCallSocket();

  const {
    isRecording,
    audioLevel,
    error: micError,
    startMic,
    stopMic,
  } = useMicStream({
    onAudioChunk: sendAudioChunk,
  });

  // Fetch scenarios on load
  useEffect(() => {
    fetch('http://localhost:8000/api/scenarios')
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => setScenarios(data))
      .catch((err) => console.log('Scenarios fetch error (backend may not be running yet):', err));
  }, []);

  const handleStart = async () => {
    const scenarioId = selectedScenario === 'live' ? null : selectedScenario;
    startCall(
      {
        name: contactName,
        telegram_chat_id: telegramId,
      },
      scenarioId
    );

    // If live mode, start mic
    if (selectedScenario === 'live') {
      await startMic();
    }
  };

  const handleStop = () => {
    stopMic();
    stopCall();
  };

  const isCallActive = status === 'connected' || status === 'connecting';

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur px-6 py-4 flex items-center justify-between sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-red-500/10 text-red-500 border border-red-500/20 shadow-lg shadow-red-500/5">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight">ScamGuard</span>
              <span className="text-xs px-2 py-0.5 rounded-full font-mono bg-blue-500/10 text-blue-400 border border-blue-500/20">
                Phase 1 Active
              </span>
            </div>
            <p className="text-xs text-slate-400">Real-time speakerphone scam shield & intent judge</p>
          </div>
        </div>

        {/* Server & Call Status Badge */}
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-xs font-mono px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700">
            <span
              className={`w-2 h-2 rounded-full ${
                status === 'connected'
                  ? 'bg-emerald-400 animate-pulse'
                  : status === 'connecting'
                  ? 'bg-amber-400 animate-pulse'
                  : status === 'error'
                  ? 'bg-red-400'
                  : 'bg-slate-500'
              }`}
            />
            <span className="capitalize">{status}</span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-6xl w-full mx-auto p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Controls & Setup */}
        <section className="space-y-6">
          {/* Mode / Scenario Picker */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
              <Radio className="w-4 h-4 text-indigo-400" />
              <span>Input Mode</span>
            </div>

            <div className="space-y-2">
              <label
                className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition ${
                  selectedScenario === 'live'
                    ? 'border-indigo-500 bg-indigo-500/10 text-white'
                    : 'border-slate-800 hover:border-slate-700 text-slate-300'
                }`}
              >
                <input
                  type="radio"
                  name="scenario"
                  value="live"
                  checked={selectedScenario === 'live'}
                  onChange={() => setSelectedScenario('live')}
                  disabled={isCallActive}
                  className="mt-1"
                />
                <div>
                  <div className="text-sm font-medium flex items-center gap-1.5">
                    <Mic className="w-3.5 h-3.5 text-indigo-400" />
                    <span>Live Microphone</span>
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Listens to phone speakerphone in real time via 16kHz PCM16 AudioWorklet.
                  </p>
                </div>
              </label>

              {scenarios.map((sc) => (
                <label
                  key={sc.id}
                  className={`flex items-start gap-3 p-3 rounded-xl border cursor-pointer transition ${
                    selectedScenario === sc.id
                      ? 'border-indigo-500 bg-indigo-500/10 text-white'
                      : 'border-slate-800 hover:border-slate-700 text-slate-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="scenario"
                    value={sc.id}
                    checked={selectedScenario === sc.id}
                    onChange={() => setSelectedScenario(sc.id)}
                    disabled={isCallActive}
                    className="mt-1"
                  />
                  <div>
                    <div className="text-sm font-medium flex items-center gap-1.5">
                      <FileText className="w-3.5 h-3.5 text-slate-400" />
                      <span>{sc.title}</span>
                      <span
                        className={`text-[10px] px-1.5 py-0.2 rounded font-mono uppercase ${
                          sc.category === 'scam'
                            ? 'bg-red-500/20 text-red-400'
                            : 'bg-emerald-500/20 text-emerald-400'
                        }`}
                      >
                        {sc.category}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400 mt-0.5">{sc.description}</p>
                  </div>
                </label>
              ))}
            </div>

            {/* Audio Level Visualizer */}
            {selectedScenario === 'live' && isRecording && (
              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1.5">
                <div className="flex justify-between text-xs text-slate-400">
                  <span>Mic Input Level</span>
                  <span className="font-mono">{audioLevel}%</span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                  <div
                    className="h-full bg-emerald-500 transition-all duration-75"
                    style={{ width: `${audioLevel}%` }}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Trusted Contact Setup */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 shadow-sm space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-200">
              <UserCheck className="w-4 h-4 text-emerald-400" />
              <span>Emergency Contact</span>
            </div>
            <div className="space-y-2 text-xs">
              <div>
                <label className="text-slate-400 block mb-1">Contact Name</label>
                <input
                  type="text"
                  value={contactName}
                  onChange={(e) => setContactName(e.target.value)}
                  disabled={isCallActive}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Telegram Chat ID</label>
                <input
                  type="text"
                  value={telegramId}
                  onChange={(e) => setTelegramId(e.target.value)}
                  disabled={isCallActive}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 font-mono focus:outline-none focus:border-indigo-500"
                  placeholder="e.g. 123456789"
                />
              </div>
            </div>
          </div>

          {/* Action Button */}
          <div>
            {!isCallActive ? (
              <button
                onClick={handleStart}
                className="w-full py-4 px-6 rounded-2xl font-semibold flex items-center justify-center gap-2 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white shadow-lg shadow-red-500/20 active:scale-[0.99] transition"
              >
                <PhoneCall className="w-5 h-5" />
                <span>Start Call Shield</span>
              </button>
            ) : (
              <button
                onClick={handleStop}
                className="w-full py-4 px-6 rounded-2xl font-semibold flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 active:scale-[0.99] transition"
              >
                <PhoneOff className="w-5 h-5 text-red-400" />
                <span>End Call Session</span>
              </button>
            )}
          </div>
        </section>

        {/* Center & Right Column: Real-time Transcript & Threat Radar */}
        <section className="lg:col-span-2 space-y-6">
          {/* Error Banner */}
          {(socketError || micError) && (
            <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 flex items-start justify-between gap-3 text-xs">
              <div className="flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
                <span>{socketError || micError}</span>
              </div>
              <button
                onClick={() => {
                  clearError();
                }}
                className="underline hover:text-red-300 font-mono"
              >
                dismiss
              </button>
            </div>
          )}

          {/* Threat Meter Bar */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                <span className="font-semibold text-sm">Call Threat Score</span>
              </div>
              <div className="text-right">
                <span className="text-2xl font-bold font-mono text-emerald-400">{risk.score}</span>
                <span className="text-xs text-slate-400">/100</span>
              </div>
            </div>

            <div className="w-full h-3 bg-slate-950 rounded-full overflow-hidden p-0.5 border border-slate-800">
              <div
                className={`h-full rounded-full transition-all duration-300 ${
                  risk.score < 30
                    ? 'bg-emerald-500'
                    : risk.score < 70
                    ? 'bg-amber-500'
                    : 'bg-red-500'
                }`}
                style={{ width: `${Math.max(5, risk.score)}%` }}
              />
            </div>
            <div className="flex justify-between text-[11px] text-slate-500 uppercase font-mono">
              <span>Safe</span>
              <span>Suspicious</span>
              <span>High Risk (Alert @ 70)</span>
            </div>
          </div>

          {/* Live Transcript Stream */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 flex flex-col h-[400px]">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-3">
              <div className="flex items-center gap-2 text-sm font-semibold">
                <FileText className="w-4 h-4 text-indigo-400" />
                <span>Live Call Transcript</span>
              </div>
              <span className="text-xs text-slate-500 font-mono">
                {transcripts.length} {transcripts.length === 1 ? 'event' : 'events'}
              </span>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 pr-2">
              {transcripts.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-500 text-xs text-center p-6">
                  {isCallActive ? (
                    <>
                      <div className="w-8 h-8 rounded-full border-2 border-indigo-500/40 border-t-indigo-500 animate-spin mb-3" />
                      <p>Listening to audio stream...</p>
                      <p className="text-slate-600 mt-1">Transcripts and tactics will appear in real time</p>
                    </>
                  ) : (
                    <>
                      <MicOff className="w-8 h-8 text-slate-600 mb-2" />
                      <p>No active call session.</p>
                      <p className="text-slate-600 mt-1">Click "Start Call Shield" to begin monitoring.</p>
                    </>
                  )}
                </div>
              ) : (
                transcripts.map((t, idx) => (
                  <div
                    key={idx}
                    className={`p-3 rounded-xl text-xs leading-relaxed ${
                      t.speaker === 'system'
                        ? 'bg-slate-950/80 text-slate-400 font-mono border border-slate-800/80'
                        : 'bg-slate-800/60 text-slate-200 border border-slate-700/60'
                    }`}
                  >
                    <div className="flex justify-between items-center text-[10px] text-slate-500 mb-1 font-mono uppercase">
                      <span>{t.speaker || 'Caller'}</span>
                      {t.is_final && <span className="text-emerald-500">finalized</span>}
                    </div>
                    <div>{t.text}</div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Detected Tactics Chips */}
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-5 space-y-3">
            <span className="text-sm font-semibold text-slate-200 block">Identified Scam Tactics</span>
            {tactics.length === 0 ? (
              <p className="text-xs text-slate-500">No high-risk tactics detected yet.</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {tactics.map((tac, idx) => (
                  <div
                    key={idx}
                    className="px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/30 text-red-300 text-xs flex items-center gap-2"
                  >
                    <span className="font-semibold">{tac.name}</span>
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-red-500/20 text-red-400">
                      {Math.round(tac.confidence * 100)}%
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>
      </main>

      {/* Critical Alert Overlay Modal */}
      {alert && (
        <div className="fixed inset-0 bg-red-950/90 backdrop-blur-md z-50 flex items-center justify-center p-6 animate-in fade-in duration-200">
          <div className="max-w-md w-full bg-slate-900 border-2 border-red-500 rounded-3xl p-6 shadow-2xl space-y-5 text-center">
            <div className="mx-auto w-16 h-16 rounded-full bg-red-500/20 border-2 border-red-500 flex items-center justify-center text-red-500 animate-pulse">
              <ShieldAlert className="w-8 h-8" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white tracking-tight">HIGH THREAT DETECTED</h2>
              <p className="text-sm text-red-400 mt-1">{alert.advice}</p>
            </div>
            <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-4 text-left">
              <div className="text-xs uppercase font-mono text-red-300 font-bold mb-1">Recommended Action</div>
              <p className="text-sm text-white font-medium">{alert.action}</p>
            </div>
            {alert.contact_notified && (
              <p className="text-xs text-emerald-400 flex items-center justify-center gap-1">
                <UserCheck className="w-3.5 h-3.5" />
                <span>Alert sent to {contactName} via Telegram</span>
              </p>
            )}
            <div className="pt-2 flex gap-3">
              <button
                onClick={() => {
                  handleStop();
                  clearAlert();
                }}
                className="flex-1 py-3 px-4 rounded-xl bg-red-600 hover:bg-red-500 text-white font-bold text-sm shadow-lg shadow-red-600/30 transition"
              >
                Hang Up Call
              </button>
              <button
                onClick={clearAlert}
                className="py-3 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm transition"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
