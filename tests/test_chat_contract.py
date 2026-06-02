from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_chat_valid_payload_returns_stub_response() -> None:
    payload = {
        "business_id": "demo-business",
        "mode": "owner",
        "message": "Hello",
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "reply_text": "Stub response: chat contract is active.",
        "attachments": [],
    }


def test_chat_invalid_mode_returns_422() -> None:
    payload = {
        "business_id": "demo-business",
        "mode": "admin",
        "message": "Hello",
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 422


def test_chat_missing_message_returns_422() -> None:
    payload = {
        "business_id": "demo-business",
        "mode": "owner",
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 422


def test_chat_blank_business_id_returns_422() -> None:
    payload = {
        "business_id": "   ",
        "mode": "customer",
        "message": "Need pricing",
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 422
