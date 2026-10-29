# ScamGuard: Hackathon Pitch & Stage Demo Playbook

This guide contains everything you need to deliver a flawless, high-scoring hackathon presentation to judges.

---

## 1. The 2-Minute Pitch Script

### **Opening (0:00 - 0:30) — The Human Problem**
> *"Every single day, thousands of elderly parents and vulnerable people lose their life savings to phone scams. In 2024 alone, financial losses to impersonation scams exceeded \$10 Billion.*  
>  
> *The tragedy isn't that victims are careless; it's that scammers use coordinated psychological panic: artificial urgency, legal threats, and authority impersonation to shut down rational thought.*  
>  
> *Existing spam blockers only check caller ID numbers—which are trivially spoofed. Once the phone is answered, the user is completely on their own.*  
>  
> *Until now. Meet **ScamGuard**—a real-time phone speakerphone shield powered by Fireworks Whisper and Meta's Llama 3.3."*

### **The Technology & Architecture (0:30 - 1:00)**
> *"ScamGuard runs in your browser or phone, listening over speakerphone via an off-thread **16kHz PCM16 AudioWorklet**.*  
>  
> *Audio streams over WebSocket to our dual-track intelligence pipeline:*  
> 1. *A **0ms in-memory Rules Engine** flags immediate red lines like OTP/passcode harvesting, AnyDesk remote access, and gift card extortion.*  
> 2. *A **Fireworks-hosted Llama 3.3 Intent Judge** continuously analyzes the sliding dialogue window for covert manipulation—isolation tactics, urgency, and false authority.*  
> 3. *Our **Risk Accumulation Engine** combines tactic velocity and legitimacy dampeners to build a composite threat score (0–100)."*

### **Live Demonstration (1:00 - 1:45)**
> *"Let's see it in action:*  
>  
> 1. ***First: Legit Bank Verification***  
>    *Notice that when a real bank calls with standard fraud warnings, ScamGuard recognizes the benign disclaimers—threat score stays green. **Zero false alarms**.*  
>  
> 2. ***Second: Impersonation Scam***  
>    *Now, an imposter calls claiming to be from Chase fraud prevention. Watch the radar:*  
>    - *Authority claim detected (+15)*  
>    - *Artificial panic & urgency detected (+20)*  
>    - *The moment the caller asks to 'read back the 6-digit passcode', the critical threshold breaches 70.*  
>    - *The screen immediately takes over with one single, clear instruction: **'HANG UP NOW'**.*  
>    - *Simultaneously, a Telegram emergency alert lands on my daughter's phone with full incident context."*

### **Closing & Impact (1:45 - 2:00)**
> *"ScamGuard gives vulnerable people a digital guardian angel whispering in their ear when adrenaline takes over. Built with Fireworks AI, Meta Llama, and Modal. Thank you!"*

---

## 2. Stage Presentation Setup Checklist

| Item | Status | Action |
| :--- | :--- | :--- |
| **Backend & Frontend Running** | 🟢 Ready | Run `./scripts/dev.sh` |
| **Screen Layout** | 📱 Split Screen | Left half: ScamGuard UI (`localhost:5173`).<br>Right half: Telegram Web or mobile phone screen mirror. |
| **Safety Net** | 🛡️ Guaranteed | Use **Demo Scenarios** in the UI picker to eliminate venue noise / microphone echo on stage. |

---

## 3. How Sponsor Credits Were Leveraged

- **Fireworks AI**:
  - `whisper-v3-turbo` audio transcription API for ultra-low latency speech-to-text.
  - `llama-v3p3-70b-instruct` inference for real-time JSON structured psychological intent detection with near-instant Time-To-First-Token (<200ms).
- **Meta AI (Llama Ecosystem)**:
  - Llama 3.3 70B as the reasoning judge assessing conversational intent, manipulation techniques, and urgency indicators.
- **Modal**:
  - Serverless ASGI backend deployment (`backend/modal_app.py`) allowing zero-cold-start cloud scaling.
- **Baseten**:
  - Model fallback architecture for dedicated private GPU serving (`faster-whisper` + `vLLM`).

---

## 4. Telegram Emergency Alerting Setup (Optional Live Phone Demo)

To have alerts land directly on your (or a judge's) phone during the demo:

1. Open Telegram and search for `@BotFather`.
2. Send `/newbot`, choose a name (e.g. `ScamGuardAlertsBot`), and copy the **API Token**.
3. Open Telegram and start a chat with `@userinfobot` to get your numeric **Chat ID**.
4. Update your `.env` file:
   ```env
   TELEGRAM_BOT_TOKEN="your_bot_token_here"
   TELEGRAM_DEFAULT_CHAT_ID="your_chat_id_here"
   ```
5. In the ScamGuard web UI, input your Telegram Chat ID in the **Emergency Contact Alert** box.
6. When the threat score crosses 70, you will hear your phone buzz with a full Telegram notification!
