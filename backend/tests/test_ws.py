from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_scenarios():
    response = client.get("/api/scenarios")
    assert response.status_code == 200
    scenarios = response.json()
    assert len(scenarios) >= 2
    scenario_ids = [s["id"] for s in scenarios]
    assert "scam_bank_fraud" in scenario_ids
    assert "legit_bank_verification" in scenario_ids


def test_websocket_call_lifecycle():
    with client.websocket_connect("/ws/call") as websocket:
        # 1. Send start command
        start_payload = {
            "type": "start",
            "contact": {
                "name": "Sarah",
                "telegram_chat_id": "999888"
            },
            "scenario": None
        }
        websocket.send_json(start_payload)

        # 2. Expect initial events from server
        first_event = websocket.receive_json()
        assert first_event["type"] == "risk"
        assert first_event["score"] == 0

        second_event = websocket.receive_json()
        assert second_event["type"] == "transcript"
        assert "ScamGuard active" in second_event["text"]

        # 3. Send 5 binary PCM16 chunks (e.g. 500 samples each = 1000 bytes)
        fake_pcm16_chunk = b"\x00\x00" * 500
        for _ in range(5):
            websocket.send_bytes(fake_pcm16_chunk)

        # 4. Send stop command
        websocket.send_json({"type": "stop"})
        stop_event = websocket.receive_json()
        assert stop_event["type"] == "transcript"
        assert "disconnected" in stop_event["text"]
