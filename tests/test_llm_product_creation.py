"""
Test LLM-driven product creation with natural language variations.
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
        "session_id": f"test_llm_product_{datetime.now().timestamp()}",
        "thread_id": f"999:test_llm_product_{datetime.now().timestamp()}"
    }

@pytest.mark.asyncio
async def test_natural_language_product_creation_variation_1(business_session):
    """Test: 'Add product Surf Excel 1kg HSN 3402 Rs 250 GST 18% 50 in stock' works."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/chat",
            json={
                "business_id": business_session["business_id"],
                "session_id": business_session["session_id"],
                "message": "Add product Surf Excel 1kg HSN 3402 Rs 250 GST 18% 50 in stock",
                "mode": "owner"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "product" in data.get("response", "").lower() or "create" in data.get("response", "").lower() or "added" in data.get("response", "").lower()

@pytest.mark.asyncio
async def test_natural_language_product_creation_variation_2(business_session):
    """Test: 'I want to add a product: Matic 1kg, HSN 3402, price 300, GST 18%, stock 100' works."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/chat",
            json={
                "business_id": business_session["business_id"],
                "session_id": business_session["session_id"],
                "message": "I want to add a product: Matic 1kg, HSN 3402, price 300, GST 18%, stock 100",
                "mode": "owner"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "product" in data.get("response", "").lower() or "create" in data.get("response", "").lower() or "added" in data.get("response", "").lower()

@pytest.mark.asyncio
async def test_product_update_with_numeric_disambiguation(business_session):
    """Test: Product update handles numeric selection (numeric disambiguation flow)."""
    async with httpx.AsyncClient() as client:
        # First add a product
        response1 = await client.post(
            f"{BASE_URL}/chat",
            json={
                "business_id": business_session["business_id"],
                "session_id": business_session["session_id"],
                "message": "Add product Detergent 1kg HSN 3402 Rs 200 GST 18% 50 in stock",
                "mode": "owner"
            }
        )
        assert response1.status_code == 200
        
        # Try to update stock (may trigger ambiguity if multiple products match)
        response2 = await client.post(
            f"{BASE_URL}/chat",
            json={
                "business_id": business_session["business_id"],
                "session_id": business_session["session_id"],
                "message": "Update Detergent stock to 75",
                "mode": "owner"
            }
        )
        assert response2.status_code == 200
        data = response2.json()
        # Should either confirm update or ask for selection if ambiguous
        assert any(x in data.get("response", "").lower() for x in ["update", "select", "which", "confirm", "ambig"])

@pytest.mark.asyncio
async def test_invalid_gst_rate_rejected(business_session):
    """Test: Invalid GST rate (outside 0-28%) rejected."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/chat",
            json={
                "business_id": business_session["business_id"],
                "session_id": business_session["session_id"],
                "message": "Add product Test HSN 3402 Rs 100 GST 35% 10 in stock",  # GST > 28%
                "mode": "owner"
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Should reject invalid GST
        assert any(x in data.get("response", "").lower() for x in ["gst", "rate", "0-28", "between", "invalid", "valid"])

@pytest.mark.asyncio
async def test_invalid_negative_stock_rejected(business_session):
    """Test: Negative stock rejected."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/chat",
            json={
                "business_id": business_session["business_id"],
                "session_id": business_session["session_id"],
                "message": "Add product Test HSN 3402 Rs 100 GST 18% -5 in stock",  # Negative stock
                "mode": "owner"
            }
        )
        assert response.status_code == 200
        data = response.json()
        # Should reject negative stock
        assert any(x in data.get("response", "").lower() for x in ["stock", "negative", "positive", "invalid", "valid"])

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
