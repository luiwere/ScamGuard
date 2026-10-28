import { useState, useEffect } from 'react';
import { ShieldAlert } from 'lucide-react';
import { useCallSocket } from './hooks/useCallSocket';
import { useMicStream } from './hooks/useMicStream';
import { Scenario } from './types';
import { ScenarioPicker } from './components/ScenarioPicker';
import { TrustedContactForm } from './components/TrustedContactForm';
import { CallControls } from './components/CallControls';
import { RiskMeter } from './components/RiskMeter';
import { LiveTranscript } from './components/LiveTranscript';
import { TacticChips } from './components/TacticChips';
import { AlertOverlay } from './components/AlertOverlay';
import { InlineError } from './components/InlineError';

export default function App() {
  const [selectedScenario, setSelectedScenario] = useState<string>('live');
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [contactName, setContactName] = useState('Sarah (Daughter)');
  const [telegramId, setTelegramId] = useState('123456789');
  const [phone, setPhone] = useState('+1 (555) 019-2834');

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

  // Fetch scenarios from backend
  useEffect(() => {
    fetch('http://localhost:8000/api/scenarios')
      .then((res) => (res.ok ? res.json() : []))
      .then((data) => setScenarios(data))
      .catch((err) => console.log('Scenarios fetch error (backend may still be booting):', err));
  }, []);

  const handleStart = async () => {
    const scenarioId = selectedScenario === 'live' ? null : selectedScenario;
    startCall(
      {
        name: contactName,
        telegram_chat_id: telegramId,
        phone: phone,
      },
      scenarioId
    );

    // If live mic mode, initialize audio capture
    if (selectedScenario === 'live') {
      await startMic();
    }
  };

  const handleStop = () => {
    stopMic();
    stopCall();
  };

  const isCallActive = status === 'connected' || status === 'connecting';
  const activeError = socketError || micError;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-red-500 selection:text-white">
      {/* Top Header */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md px-6 py-4 flex items-center justify-between sticky top-0 z-40">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-2xl bg-red-500/10 text-red-500 border border-red-500/20 shadow-lg shadow-red-500/10">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-xl tracking-tight text-white">ScamGuard</span>
              <span className="text-[10px] px-2 py-0.5 rounded-full font-mono font-bold bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
                Llama 3.3 + Whisper
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Live speakerphone fraud defense & conversational intent judge
            </p>
          </div>
        </div>

        {/* Real-time Connection Status Indicator */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs font-mono px-3.5 py-1.5 rounded-full bg-slate-950 border border-slate-800">
            <span
              className={`w-2 h-2 rounded-full ${
                status === 'connected'
                  ? 'bg-emerald-400 animate-pulse'
                  : status === 'connecting'
                  ? 'bg-amber-400 animate-pulse'
                  : status === 'error'
                  ? 'bg-red-400'
                  : 'bg-slate-600'
              }`}
            />
            <span className="capitalize font-semibold text-slate-300">{status}</span>
          </div>
        </div>
      </header>

      {/* Main Grid Content */}
      <main className="flex-1 max-w-6xl w-full mx-auto p-4 sm:p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Controls, Scenarios, and Guardian Settings */}
        <section className="space-y-6">
          <ScenarioPicker
            selectedScenario={selectedScenario}
            onSelect={setSelectedScenario}
            scenarios={scenarios}
            disabled={isCallActive}
          />

          <TrustedContactForm
            contactName={contactName}
            onContactNameChange={setContactName}
            telegramId={telegramId}
            onTelegramIdChange={setTelegramId}
            phone={phone}
            onPhoneChange={setPhone}
            disabled={isCallActive}
          />

          <CallControls
            status={status}
            isRecording={isRecording}
            audioLevel={audioLevel}
            isLiveMic={selectedScenario === 'live'}
            onStart={handleStart}
            onStop={handleStop}
          />
        </section>

        {/* Center/Right Column: Live Risk Radar, Dialogue Stream & Tactics */}
        <section className="lg:col-span-2 space-y-6">
          <InlineError
            message={activeError}
            onDismiss={() => {
              clearError();
            }}
          />

          <RiskMeter risk={risk} />

          <LiveTranscript
            transcripts={transcripts}
            tactics={tactics}
            isCallActive={isCallActive}
          />

          <TacticChips tactics={tactics} />
        </section>
      </main>

      {/* Critical High-Risk Alert Overlay */}
      {alert && (
        <AlertOverlay
          alert={alert}
          contactName={contactName}
          onHangUp={() => {
            handleStop();
            clearAlert();
          }}
          onDismiss={clearAlert}
        />
      )}
    </div>
  );
}
