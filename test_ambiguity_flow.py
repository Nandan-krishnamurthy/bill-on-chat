#!/usr/bin/env python3
"""
Test: Product Ambiguity Flow
Verify that numeric selection works for multiple product matches.
"""

import asyncio
import httpx

BACKEND_URL = "http://localhost:8000"


async def send_chat(business_id: str, session_id: str, message: str):
    """Send chat message and return response."""
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
                data = response.json()
                return True, data.get('reply_text', 'OK')
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
        except Exception as e:
            return False, str(e)


async def test_ambiguity_flow():
    """Test the product ambiguity flow with numeric selection."""
    
    print("\n" + "=" * 80)
    print("TEST: Product Ambiguity Flow with Numeric Selection")
    print("=" * 80)
    
    business_id = "1"
    session_id = f"ambiguity-test-{int(asyncio.get_event_loop().time() * 1000)}"
    
    # Step 1: Create test products with similar names
    print("\n[Step 1] Creating test products...")
    
    products = [
        ("add product Surf Excel 1kg HSN 3402 Rs 250 GST 18% 100 in stock", "Surf Excel 1kg"),
        ("add product Surf Excel 500g HSN 3402 Rs 150 GST 18% 50 in stock", "Surf Excel 500g"),
        ("add product Surf Excel Matic HSN 3402 Rs 300 GST 18% 75 in stock", "Surf Excel Matic"),
    ]
    
    for create_cmd, name in products:
        success, response = await send_chat(business_id, session_id, create_cmd)
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"  Create {name}: {status}")
        if not success:
            print(f"    Error: {response}")
    
    # Step 2: Trigger ambiguity by updating product with fuzzy match
    print("\n[Step 2] Triggering ambiguity with 'Update product Surf stock to 100'...")
    success, response = await send_chat(business_id, session_id, "Update product Surf stock to 100")
    
    if not success:
        print(f"✗ FAIL: {response}")
        return False
    
    print(f"✓ PASS")
    print(f"\nBot response:\n{response}")
    
    # Verify response contains multiple products
    if "Multiple products found" not in response:
        print(f"\n✗ FAIL: Response should indicate multiple products found")
        return False
    
    # Verify formatting (should have line breaks)
    if "\n\n" not in response:
        print(f"\n✗ FAIL: Response formatting should have proper line breaks")
        return False
    
    # Verify all 3 products are listed
    if not all(prod[1] in response for prod in products):
        print(f"\n✗ FAIL: Response should list all 3 products")
        return False
    
    print(f"\n✓ Response format verified (includes all 3 products with line breaks)")
    
    # Step 3: User selects product 1 (should be Surf Excel 1kg)
    print("\n[Step 3] User selects product 1...")
    success, response = await send_chat(business_id, session_id, "1")
    
    if not success:
        print(f"✗ FAIL: {response}")
        return False
    
    print(f"✓ PASS")
    print(f"Bot response: {response}")
    
    # Verify it didn't say "Unsupported command"
    if "Unsupported command" in response:
        print(f"\n✗ FAIL: Got 'Unsupported command' instead of product selection handling")
        return False
    
    # Step 4: Test selection 2 (should be Surf Excel 500g)
    print("\n[Step 4] Testing another ambiguity with selection 2...")
    success, response = await send_chat(business_id, session_id, "Update product Surf stock to 200")
    print(f"Ambiguity trigger: {'✓ PASS' if success else '✗ FAIL'}")
    
    success, response = await send_chat(business_id, session_id, "2")
    
    if success and "Unsupported command" not in response:
        print(f"Product selection 2: ✓ PASS")
    else:
        print(f"Product selection 2: ✗ FAIL")
        return False
    
    # Step 5: Test selection 3 (should be Surf Excel Matic)
    print("\n[Step 5] Testing another ambiguity with selection 3...")
    success, response = await send_chat(business_id, session_id, "Update product Surf stock to 300")
    print(f"Ambiguity trigger: {'✓ PASS' if success else '✗ FAIL'}")
    
    success, response = await send_chat(business_id, session_id, "3")
    
    if success and "Unsupported command" not in response:
        print(f"Product selection 3: ✓ PASS")
    else:
        print(f"Product selection 3: ✗ FAIL")
        return False
    
    # Step 6: Test invalid selection (out of range)
    print("\n[Step 6] Testing invalid selection (out of range)...")
    success, response = await send_chat(business_id, session_id, "Update product Surf stock to 400")
    print(f"Ambiguity trigger: {'✓ PASS' if success else '✗ FAIL'}")
    
    success, response = await send_chat(business_id, session_id, "99")
    
    if success and "Invalid selection" in response:
        print(f"Invalid selection handling: ✓ PASS")
    else:
        print(f"Invalid selection handling: ✗ FAIL (expected 'Invalid selection' message)")
        return False
    
    print("\n" + "=" * 80)
    print("✓✓✓ ALL TESTS PASSED ✓✓✓")
    print("=" * 80)
    print("\nProduct ambiguity flow is working correctly:")
    print("  ✓ Multiple products detected")
    print("  ✓ Proper response formatting with line breaks")
    print("  ✓ Numeric selections 1, 2, 3 processed correctly")
    print("  ✓ Invalid selections rejected")
    print("  ✓ No 'Unsupported command' errors")
    
    return True


if __name__ == "__main__":
    result = asyncio.run(test_ambiguity_flow())
    exit(0 if result else 1)
