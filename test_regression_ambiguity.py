#!/usr/bin/env python3
"""
Regression Test: Exact scenario from bug report

User: "Update product Surf stock to 100"
Bot: [shows multiple products]
User: "1"
Bot: [should process selection, NOT "Unsupported command"]
"""

import asyncio
import httpx

BACKEND_URL = "http://localhost:8000"


async def send_chat(business_id: str, session_id: str, message: str):
    """Send chat message."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BACKEND_URL}/chat",
                json={
                    'business_id': business_id,
                    'session_id': session_id,
                    'mode': 'owner',
                    'message': message
                },
                timeout=5.0
            )
            
            if response.status_code == 200:
                return True, response.json().get('reply_text', '')
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)


async def main():
    print("\n" + "=" * 80)
    print("REGRESSION TEST: Exact Bug Report Scenario")
    print("=" * 80)
    
    session_id = f"regression-{int(asyncio.get_event_loop().time() * 1000)}"
    
    # Setup: Create two Surf products
    print("\nSetup: Creating two Surf products...")
    
    await send_chat("1", session_id, "add product Surf Excel 1kg HSN 3402 Rs 250 GST 18% 100 in stock")
    await send_chat("1", session_id, "add product Surf Excel 500g HSN 3402 Rs 150 GST 18% 50 in stock")
    
    print("✓ Products created\n")
    
    # The Bug Scenario
    print("User: Update product Surf stock to 100")
    success, response = await send_chat("1", session_id, "Update product Surf stock to 100")
    
    if not success:
        print(f"✗ FAIL: {response}")
        return False
    
    print(f"Bot:\n{response}\n")
    
    if "Multiple products found" not in response:
        print("✗ FAIL: Should find multiple products")
        return False
    
    # The Bug - User selects "1"
    print("User: 1")
    success, response = await send_chat("1", session_id, "1")
    
    if not success:
        print(f"✗ FAIL: {response}")
        return False
    
    print(f"Bot: {response}\n")
    
    # THE BUG: This used to return "Unsupported command"
    if "Unsupported command" in response:
        print("✗✗✗ BUG STILL EXISTS ✗✗✗")
        print("Expected: Product selection to be processed")
        print("Got: 'Unsupported command'")
        return False
    
    if "updated successfully" in response.lower() or "selected" in response.lower():
        print("✓✓✓ BUG FIXED ✓✓✓")
        print("Numeric selection was processed correctly!")
        return True
    else:
        print("? UNEXPECTED RESPONSE")
        print(f"Expected update confirmation, got: {response}")
        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    exit(0 if result else 1)
