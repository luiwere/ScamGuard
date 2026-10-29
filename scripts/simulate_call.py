#!/usr/bin/env python3
"""
ScamGuard Terminal Call Simulator
Connects to ws://localhost:8000/ws/call to simulate real-time call protection from the CLI.
"""

import sys
import json
import asyncio
import argparse
from pathlib import Path

try:
    import websockets
except ImportError:
    print("Error: websockets library is required. Run in backend/venv or install websockets.")
    sys.exit(1)

# ANSI Color Codes
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_banner():
    print(f"{RED}{BOLD}===================================================={RESET}")
    print(f"{RED}{BOLD}       🛡️  ScamGuard Terminal Call Simulator        {RESET}")
    print(f"{RED}{BOLD}===================================================={RESET}\n")


def print_alert_box(alert_data: dict):
    print(f"\n{RED}{BOLD}╔══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{RED}{BOLD}║               🚨 CRITICAL SCAM DETECTED 🚨               ║{RESET}")
    print(f"{RED}{BOLD}╠══════════════════════════════════════════════════════════╣{RESET}")
    advice = alert_data.get("advice", "")
    action = alert_data.get("action", "")
    notified = alert_data.get("contact_notified", False)

    print(f"{RED}║ Advice: {RESET}{advice[:48]}")
    print(f"{RED}║ Action: {BOLD}{action[:48]}{RESET}")
    if notified:
        print(f"{GREEN}║ ✓ Telegram alert dispatched to trusted contact          ║{RESET}")
    print(f"{RED}{BOLD}╚══════════════════════════════════════════════════════════╝{RESET}\n")


async def run_simulation(ws_url: str, scenario: str, contact_name: str, telegram_id: str):
    print(f"{CYAN}Connecting to ScamGuard stream at {ws_url}...{RESET}")
    try:
        async with websockets.connect(ws_url) as ws:
            print(f"{GREEN}✓ Connected to WebSocket!{RESET}")
            print(f"Starting scenario: {BOLD}{scenario}{RESET}\n")

            # Send Start message
            start_payload = {
                "type": "start",
                "contact": {
                    "name": contact_name,
                    "telegram_chat_id": telegram_id
                },
                "scenario": scenario
            }
            await ws.send(json.dumps(start_payload))

            # Listen for server events
            async for raw_msg in ws:
                try:
                    event = json.loads(raw_msg)
                    etype = event.get("type")

                    if etype == "transcript":
                        speaker = event.get("speaker", "caller").upper()
                        text = event.get("text", "")
                        print(f"[{CYAN}{speaker}{RESET}] {text}")

                    elif etype == "tactics":
                        items = event.get("items", [])
                        for item in items:
                            name = item.get("name")
                            conf = int(item.get("confidence", 0) * 100)
                            source = item.get("source", "rules").upper()
                            evidence = item.get("evidence", "")
                            print(
                                f"  {YELLOW}↳ Flagged Tactic:{RESET} {BOLD}{name}{RESET} "
                                f"({conf}%, via {source}) - \"{evidence}\""
                            )

                    elif etype == "risk":
                        score = event.get("score", 0)
                        level = event.get("level", "safe").upper()
                        color = RED if score >= 70 else (YELLOW if score >= 40 else GREEN)
                        bar = "█" * (score // 5) + "░" * (20 - (score // 5))
                        print(f"  {color}[RISK: {score}/100 {level}] [{bar}]{RESET}")

                    elif etype == "alert":
                        print_alert_box(event)
                        # On alert, we can choose to stop
                        await ws.send(json.dumps({"type": "stop"}))
                        break

                    elif etype == "error":
                        print(f"{RED}Error: {event.get('message')}{RESET}")

                except json.JSONDecodeError:
                    print(f"Non-JSON message: {raw_msg}")

            print(f"\n{GREEN}Call simulation completed.{RESET}")

    except Exception as e:
        print(f"{RED}Connection failed: {e}{RESET}")
        print("Ensure the ScamGuard backend is running (scripts/dev.sh or uvicorn app.main:app).")


def main():
    parser = argparse.ArgumentParser(description="ScamGuard CLI Call Simulator")
    parser.add_argument(
        "--scenario",
        default="scam_bank_fraud",
        choices=["scam_bank_fraud", "scam_gift_card", "legit_bank_verification"],
        help="Demo scenario to replay"
    )
    parser.add_argument(
        "--url",
        default="ws://localhost:8000/ws/call",
        help="WebSocket URL"
    )
    parser.add_argument(
        "--contact",
        default="Sarah (Daughter)",
        help="Trusted contact name"
    )
    parser.add_argument(
        "--telegram-id",
        default="123456789",
        help="Telegram chat ID"
    )

    args = parser.parse_args()
    print_banner()
    asyncio.run(run_simulation(args.url, args.scenario, args.contact, args.telegram_id))


if __name__ == "__main__":
    main()
