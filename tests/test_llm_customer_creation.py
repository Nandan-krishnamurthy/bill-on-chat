"""
Test LLM-driven customer creation with natural language variations.
"""

import asyncio
import httpx
import pytest
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

# Test fixtures
@pytest.fixture
def business_session():
    """Setup: business and session for testing."""
    return {
        "business_id": 999,  # Test business
        "session_id": f"test_llm_customer_{datetime.now().timestamp()}",
        "thread_id": f"999:test_llm_customer_{datetime.now().timestamp()}"
    }

@pytest.mark.asyncio
async def test_natural_language_customer_creation_variation_1(business_session):
    """Test: 'Add customer Ramesh 9876543210' works."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/chat",
            json={
                "business_id": business_session["business_id"],
                "session_id": business_session["session_id"],
                "message": "Add customer Ramesh 9876543210",
                "mode": "owner"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "customer" in data.get("response", "").lower() or "create" in data.get("response", "").lower()

@pytest.mark.asyncio
async def test_natural_language_customer_creation_variation_2(business_session):
    """Test: 'Create new customer named Priya, phone 8765432109' works."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/chat",
            json={
                "business_id": business_session["business_id"],
                "session_id": business_session["session_id"],
                "message": "Create new customer named Priya, phone 8765432109",
                "mode": "owner"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "customer" in data.get("response", "").lower() or "create" in data.get("response", "").lower()

@pytest.mark.asyncio
async def test_natural_language_customer_creation_variation_3(business_session):
    """Test: 'I need to add a customer: Suresh (9988776655)' works."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/chat",
            json={
                "business_id": business_session["business_id"],
                "session_id": business_session["session_id"],
                "message": "I need to add a customer: Suresh (9988776655)",
                "mode": "owner"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "customer" in data.get("response", "").lower() or "create" in data.get("response", "").lower()

@pytest.mark.asyncio
async def test_invalid_phone_rejected(business_session):
    """Test: Invalid phone (not 10 digits) is rejected."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/chat",
            json={
                "business_id": business_session["business_id"],
                "session_id": business_session["session_id"],
                "message": "Add customer Ramesh 12345",  # Only 5 digits
                "mode": "owner"
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Either should ask for clarification or reject invalid phone
        assert "10" in data.get("response", "") or "digit" in data.get("response", "").lower()

@pytest.mark.asyncio
async def test_missing_parameters_handled(business_session):
    """Test: Missing required parameters (name or phone) handled gracefully."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/chat",
            json={
                "business_id": business_session["business_id"],
                "session_id": business_session["session_id"],
                "message": "Add customer with phone 9876543210 only",  # No name
                "mode": "owner"
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Should ask for name or indicate missing information
        assert "name" in data.get("response", "").lower() or "inform" in data.get("response", "").lower() or "please" in data.get("response", "").lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
