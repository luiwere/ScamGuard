# 🛡️ ScamGuard

> **Real-time phone speakerphone fraud protection powered by Fireworks Whisper and Meta Llama 3.3.**

ScamGuard listens to incoming calls over speakerphone, transcribes speech live, checks dialogue against an instantaneous **0ms rules engine** and a **Llama 3.3 semantic intent judge**, accumulates threat velocity, and takes over the screen with a single action: **"Hang up immediately"** while alerting trusted contacts via Telegram.

---

## 🚀 Quickstart (One Command)

### 1. Prerequisites
- Python 3.12+
- Node.js 20+

### 2. Configure Environment
```bash
cp .env.example .env
# Optional: Add your FIREWORKS_API_KEY and TELEGRAM_BOT_TOKEN
```

### 3. Launch Development Servers
```bash
./scripts/dev.sh
```
- **Web App**: [http://localhost:5173](http://localhost:5173)
- **FastAPI Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **WebSocket Endpoint**: `ws://localhost:8000/ws/call`

---

## 🎯 Demo Modes (Hackathon Safety Nets)

ScamGuard includes three demo modes directly in the UI:
1. **Live Microphone**: Uses browser Web Audio `AudioWorklet` to downsample speakerphone audio to 16kHz PCM16 in real time.
2. **Bank Impersonation & OTP Scam**: Scripted replay demonstrating detection of authority claims, urgency, and OTP/passcode theft triggering a full-screen takeover.
3. **Tech Support & Gift Card Scam**: Scripted replay demonstrating AnyDesk remote software detection and gift card payment extortion.
4. **Legitimate Bank Verification**: Replays an automated 2FA bank check proving the system detects benign disclaimers with **zero false alarms**.

---

## 🛠️ Terminal Call Simulation

Test the full WebSocket pipeline directly from your command line:
```bash
./backend/venv/bin/python scripts/simulate_call.py --scenario scam_bank_fraud
```

---

## 🏗️ Architecture & Pipeline

```text
Microphone (Speakerphone)
       │
       ▼
AudioWorklet (Downsamples 48kHz -> 16kHz PCM16 Mono)
       │
       ▼ [Binary WebSocket /ws/call]
FastAPI Session Coordinator
       │
       ├─► Services/STT (Fireworks Whisper API) ──► Live Transcripts
       │
       ├─► Services/Rules (0ms Regex Engine) ─────► Hard Red Lines (OTP, AnyDesk, Cards)
       │
       ├─► Services/LLM (Fireworks Llama 3.3) ──► Psychological Intent & Urgency Judge
       │
       ▼
Services/Scoring (Multi-Factor Risk Accumulator 0-100)
       │
       ├── Score < 40  ──► Safe / Normal Feed
       ├── Score 40-69 ──► Warning / Suspicious Highlights
       └── Score >= 70 ──► CRITICAL ALERT
                                ├── Full-Screen UI Takeover ("Hang Up Now")
                                └── Telegram Bot Emergency Alert to Family
```

---

## 🧪 Testing

Run the complete backend test suite (25 tests covering schemas, regexes, audio conversion, LLM fallbacks, and scenario pipelines):
```bash
backend/venv/bin/pytest
```

Run frontend production build verification:
```bash
cd frontend && npm run build
```

---

## ☁️ Cloud Deployment (Modal)

Deploy ScamGuard onto Modal serverless infrastructure with one command:
```bash
modal deploy backend/modal_app.py
```

Or deploy with Docker:
```bash
docker compose up --build
```

---

## 📄 License
MIT