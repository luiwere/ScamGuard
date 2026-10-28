import os
import json
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.ws.call_stream import router as ws_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("scamguard")

app = FastAPI(
    title="ScamGuard API",
    version="0.1.0",
    description="Real-time call protection against social engineering & phone scams"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount WebSocket router
app.include_router(ws_router)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app": "ScamGuard",
        "version": "0.1.0"
    }


@app.get("/api/scenarios")
async def get_scenarios():
    """List available demo scenarios for scripted replay."""
    scenarios = []
    scenarios_dir = Path(__file__).resolve().parent.parent / "data" / "scenarios"
    if scenarios_dir.exists():
        for file in scenarios_dir.glob("*.json"):
            try:
                with open(file, "r") as f:
                    data = json.load(f)
                    scenarios.append({
                        "id": data.get("id", file.stem),
                        "title": data.get("title", file.stem),
                        "description": data.get("description", ""),
                        "category": data.get("category", "scam")
                    })
            except Exception as e:
                logger.error(f"Error loading scenario {file}: {e}")
    return scenarios
