# 🚀 Deploying ScamGuard to Render (render.com)

This guide walks you through deploying **ScamGuard** to Render in just a few minutes using the included `render.yaml` Blueprint or via the Render Web Dashboard.

---

## Method 1: Automatic Blueprint Deployment (Recommended)

Render Blueprints allow you to provision both the **FastAPI Backend** and the **React Frontend** with a single click.

### Steps:
1. Push your repository to **GitHub** or **GitLab**.
2. Log into your [Render Dashboard](https://dashboard.render.com).
3. Click **New +** in the top navigation and select **Blueprint**.
4. Connect your `ScamGuard` repository.
5. Render will automatically parse [`render.yaml`](file:///home/luiwere/Desktop/ScamGuard/render.yaml) and display the two services:
   - `scamguard-backend` (Web Service / Python)
   - `scamguard-frontend` (Static Site / Node)
6. Under **Environment Variables**, fill in your secret keys:
   - `GROQ_API_KEY`: Your Groq API Key (starts with `gsk_`, e.g. from groq.com) **OR**
   - `FIREWORKS_API_KEY`: Your Fireworks API Key (from fireworks.ai)
   - `TELEGRAM_BOT_TOKEN`: (Optional) Your Telegram bot token
   - `TELEGRAM_DEFAULT_CHAT_ID`: (Optional) Your default Telegram chat ID
7. Click **Apply**.
8. Render will build and deploy both services!

---

## Method 2: Manual Dashboard Setup

If you prefer configuring services manually in the Render UI:

### Step 1: Deploy Backend (Web Service)
1. Click **New +** $\rightarrow$ **Web Service**.
2. Connect your repository.
3. Configure settings:
   - **Name**: `scamguard-backend`
   - **Language**: `Python`
   - **Region**: `Oregon (US West)` (or closest to you)
   - **Branch**: `main`
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`
4. Add Environment Variables:
   - `PYTHON_VERSION`: `3.12.3`
   - `CORS_ORIGINS`: `*`
   - `GROQ_API_KEY`: `<your_groq_key>` (or `FIREWORKS_API_KEY`: `<your_fireworks_key>`)
   - `GROQ_STT_MODEL`: `whisper-large-v3-turbo`
   - `GROQ_LLM_MODEL`: `llama-3.3-70b-versatile`
   - `TELEGRAM_BOT_TOKEN`: `<your_bot_token>`
   - `TELEGRAM_DEFAULT_CHAT_ID`: `<your_chat_id>`
5. Click **Create Web Service** and note your backend URL (e.g., `https://scamguard-backend.onrender.com`).

---

### Step 2: Deploy Frontend (Static Site)
1. Click **New +** $\rightarrow$ **Static Site**.
2. Connect the same repository.
3. Configure settings:
   - **Name**: `scamguard-frontend`
   - **Branch**: `main`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
4. Add Environment Variable:
   - `VITE_API_URL`: `https://scamguard-backend.onrender.com` (replace with your backend URL from Step 1)
   *(Note: ScamGuard automatically derives the `wss://` WebSocket endpoint from `VITE_API_URL`)*
5. Add **Rewrite / Redirect Rule** (for Single Page App routing):
   - **Type**: `Rewrite`
   - **Source**: `/*`
   - **Destination**: `/index.html`
6. Click **Create Static Site**.

---

## 🔒 Verification & Health Check

Once deployed:
1. Open your backend health URL:
   ```
   https://scamguard-backend.onrender.com/health
   ```
   Should return: `{"status": "healthy", "app": "ScamGuard", "version": "0.1.0"}`

2. Open your frontend URL:
   ```
   https://scamguard-frontend.onrender.com
   ```
   - Check the top right status badge: it should turn green (`connected`).
   - Run the **Bank Impersonation** scenario or speak over the **Live Microphone** to verify real-time alerts!
