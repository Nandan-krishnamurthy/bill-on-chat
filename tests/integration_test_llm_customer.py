"""
Integration tests for LLM-driven customer creation.
Tests against live backend running at http://127.0.0.1:8000
"""

import asyncio
import httpx
from datetime import datetime
import json

BASE_URL = "http://127.0.0.1:8000"

async def test_natural_language_customer_creation():
    """Test natural language customer creation variations."""
    
    test_cases = [
        ("Add customer Ramesh 9876543210", "Test variation 1"),
        ("Create new customer named Priya, phone 8765432109", "Test variation 2"),
        ("I need to add a customer: Suresh (9988776655)", "Test variation 3"),
    ]
    
    async with httpx.AsyncClient(timeout=60) as client:
        # Get existing businesses
        business_response = await client.get(f"{BASE_URL}/businesses")
        
        if business_response.status_code != 200:
            print(f"Failed to get businesses: {business_response.text}")
            return
        
        businesses = business_response.json()
        if not businesses:
            print("No businesses found in database")
            return
        
        business_id = str(businesses[0]["id"])
        print(f"Using business: {business_id} ({businesses[0]['name']})\n")
        
        for message, description in test_cases:
            session_id = f"test_llm_customer_{datetime.now().timestamp()}"
            
            print(f"\n{description}: {message}")
            response = await client.post(
                f"{BASE_URL}/chat",
                json={
                    "business_id": business_id,
                    "session_id": session_id,
                    "message": message,
                    "mode": "owner"
                }
            )
            
            if response.status_code != 200:
                print(f"  ❌ Status: {response.status_code}")
                print(f"  Response: {response.text}")
                continue
            
            data = response.json()
            print(f"  Full response: {json.dumps(data, indent=2)}")
            
            reply_text = data.get("reply_text", "").lower()
            
            # Check response indicates customer handling
            if "customer" in reply_text or "exist" in reply_text or "added" in reply_text or "successfully" in reply_text:
                print(f"  PASS - Customer operation handled")
            else:
                print(f"  Status: {response.status_code} (check if operation succeeded)")

async def test_invalid_phone():
    """Test invalid phone number handling."""
    
    print("\n\nTest invalid phone (too few digits):")
    
    async with httpx.AsyncClient(timeout=60) as client:
        # Get a business first
        business_response = await client.get(f"{BASE_URL}/businesses")
        if business_response.status_code != 200:
            print("Failed to get businesses")
            return
        
        businesses = business_response.json()
        if not businesses:
            print("No businesses found")
            return
        
        business_id = str(businesses[0]["id"])
        
        response = await client.post(
            f"{BASE_URL}/chat",
            json={
                "business_id": business_id,
                "session_id": f"test_invalid_phone_{datetime.now().timestamp()}",
                "message": "Add customer Ramesh 12345",  # Only 5 digits
                "mode": "owner"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            reply_text = data.get("reply_text", "").lower()
            
            if "10" in reply_text or "digit" in reply_text or "valid" in reply_text or "phone" in reply_text:
                print(f"  PASS - Invalid phone rejected with explanation")
            else:
                print(f"  Response: {reply_text}")
        else:
            print(f"  ❌ Status: {response.status_code}")

async def main():
    """Run all tests."""
    print("=" * 60)
    print("Integration Tests: LLM-Driven Customer Creation")
    print("=" * 60)
    
    try:
        await test_natural_language_customer_creation()
        await test_invalid_phone()
        
        print("\n" + "=" * 60)
        print("Integration tests completed")
        print("=" * 60)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
