from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_chat_valid_payload_returns_response_contract() -> None:
    payload = {
        "business_id": "1",
        "mode": "owner",
        "message": "Hello",
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert "reply_text" in data
    assert "attachments" in data
    assert isinstance(data["reply_text"], str)
    assert isinstance(data["attachments"], list)


def test_chat_invalid_mode_returns_422() -> None:
    payload = {
        "business_id": "1",
        "mode": "admin",
        "message": "Hello",
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 422


def test_chat_missing_message_returns_422() -> None:
    payload = {
        "business_id": "1",
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