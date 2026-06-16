"""
Comprehensive NLP variation tests for customer and product intents.

Tests that all natural language variations are correctly understood
by the LLM-driven intent classification system.
"""

import asyncio
import httpx
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 60


# ============================================================================
# CUSTOMER CREATION VARIATIONS
# ============================================================================

CUSTOMER_VARIATIONS = [
    ("Add customer Ramesh 9876543210", "explicit add"),
    ("Create new customer named Ramesh with phone 9876543210", "create with named args"),
    ("Save customer Ramesh 9876543210", "save variation"),
    ("I met a new customer today, add him as Ramesh 9876543210", "narrative style"),
    ("Please add customer Ramesh, phone 9876543210", "polite variation"),
    ("Register customer Ramesh 9876543210", "register variation"),
]


# ============================================================================
# PRODUCT CREATION VARIATIONS
# ============================================================================

PRODUCT_CREATE_VARIATIONS = [
    (
        "Add product Surf Excel 1kg HSN 3402 Rs 250 GST 18% 50 in stock",
        "explicit add with full details",
    ),
    (
        "Create a product called Surf Excel: HSN 3402, price 250, GST 18%, stock 50",
        "named parameters style",
    ),
    (
        "We now sell Surf Excel. HSN 3402, Rs 250, GST 18%, 50 units available",
        "narrative style",
    ),
    (
        "Add Surf Excel to inventory. HSN 3402, Rs 250, GST 18%, 50 packets",
        "inventory notation",
    ),
    (
        "I want to add a product: Surf Excel, HSN 3402, price 250, GST 18%, stock 100",
        "natural language",
    ),
]


# ============================================================================
# STOCK UPDATE VARIATIONS
# ============================================================================

STOCK_UPDATE_VARIATIONS = [
    ("Update Surf stock to 100", "explicit update"),
    ("Increase Surf stock to 100", "increase variation"),
    ("We received 100 Surf packets", "receipt narrative"),
    ("Make Surf inventory 100", "make/set variation"),
    ("Set Surf stock quantity to 100", "set with quantity"),
    ("Surf now has 100 in stock", "status/state notation"),
]


async def test_customer_variations():
    """Test customer creation with natural language variations."""
    print("\n" + "=" * 80)
    print("CUSTOMER CREATION NLP VARIATIONS")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Get business
        business_response = await client.get(f"{BASE_URL}/businesses")
        if business_response.status_code != 200:
            print("FAILED: Could not get business")
            return

        businesses = business_response.json()
        if not businesses:
            print("FAILED: No businesses found")
            return

        business_id = str(businesses[0]["id"])
        print(f"Using business: {business_id}\n")

        passed = 0
        failed = 0

        for message, description in CUSTOMER_VARIATIONS:
            session_id = f"cust_nlp_{datetime.now().timestamp()}"

            try:
                response = await client.post(
                    f"{BASE_URL}/chat",
                    json={
                        "business_id": business_id,
                        "session_id": session_id,
                        "message": message,
                        "mode": "owner",
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    reply = data.get("reply_text", "").lower()

                    # Check if response indicates understanding
                    if (
                        "customer" in reply
                        or "exist" in reply
                        or "success" in reply
                        or "added" in reply
                        or "already" in reply
                    ):
                        print(f"✓ PASS: {description}")
                        print(f"        Message: {message}")
                        print(f"        Response: {reply[:80]}...")
                        passed += 1
                    else:
                        print(f"✗ FAIL: {description}")
                        print(f"        Message: {message}")
                        print(f"        Response: {reply}")
                        failed += 1
                else:
                    print(f"✗ FAIL: {description} (Status {response.status_code})")
                    failed += 1
            except Exception as e:
                print(f"✗ ERROR: {description}: {e}")
                failed += 1

            await asyncio.sleep(0.5)  # Rate limit

        print(f"\nCustomer Variations: {passed} passed, {failed} failed")
        return passed, failed


async def test_product_create_variations():
    """Test product creation with natural language variations."""
    print("\n" + "=" * 80)
    print("PRODUCT CREATION NLP VARIATIONS")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Get business
        business_response = await client.get(f"{BASE_URL}/businesses")
        if business_response.status_code != 200:
            print("FAILED: Could not get business")
            return

        businesses = business_response.json()
        if not businesses:
            print("FAILED: No businesses found")
            return

        business_id = str(businesses[0]["id"])
        print(f"Using business: {business_id}\n")

        passed = 0
        failed = 0

        for message, description in PRODUCT_CREATE_VARIATIONS:
            session_id = f"prod_nlp_{datetime.now().timestamp()}"

            try:
                response = await client.post(
                    f"{BASE_URL}/chat",
                    json={
                        "business_id": business_id,
                        "session_id": session_id,
                        "message": message,
                        "mode": "owner",
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    reply = data.get("reply_text", "").lower()

                    # Check if response indicates understanding
                    if (
                        "product" in reply
                        or "success" in reply
                        or "created" in reply
                        or "added" in reply
                        or "surf" in reply
                    ):
                        print(f"✓ PASS: {description}")
                        print(f"        Message: {message[:70]}...")
                        print(f"        Response: {reply[:80]}...")
                        passed += 1
                    else:
                        print(f"✗ FAIL: {description}")
                        print(f"        Message: {message[:70]}...")
                        print(f"        Response: {reply[:80]}...")
                        failed += 1
                else:
                    print(f"✗ FAIL: {description} (Status {response.status_code})")
                    failed += 1
            except Exception as e:
                print(f"✗ ERROR: {description}: {e}")
                failed += 1

            await asyncio.sleep(0.5)  # Rate limit

        print(f"\nProduct Creation Variations: {passed} passed, {failed} failed")
        return passed, failed


async def test_stock_update_variations():
    """Test stock updates with natural language variations."""
    print("\n" + "=" * 80)
    print("STOCK UPDATE NLP VARIATIONS")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Get business
        business_response = await client.get(f"{BASE_URL}/businesses")
        if business_response.status_code != 200:
            print("FAILED: Could not get business")
            return

        businesses = business_response.json()
        if not businesses:
            print("FAILED: No businesses found")
            return

        business_id = str(businesses[0]["id"])
        print(f"Using business: {business_id}\n")

        passed = 0
        failed = 0

        for message, description in STOCK_UPDATE_VARIATIONS:
            session_id = f"stock_nlp_{datetime.now().timestamp()}"

            try:
                response = await client.post(
                    f"{BASE_URL}/chat",
                    json={
                        "business_id": business_id,
                        "session_id": session_id,
                        "message": message,
                        "mode": "owner",
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    reply = data.get("reply_text", "").lower()

                    # Check if response indicates understanding (either success or product not found)
                    # We don't have 'Surf' in this business, so we expect "not found" or ambiguity
                    if (
                        "product" in reply
                        or "not found" in reply
                        or "multiple" in reply
                        or "stock" in reply
                        or "select" in reply
                    ):
                        print(f"✓ PASS: {description}")
                        print(f"        Message: {message}")
                        print(f"        Response: {reply[:80]}...")
                        passed += 1
                    else:
                        print(f"✗ FAIL: {description}")
                        print(f"        Message: {message}")
                        print(f"        Response: {reply}")
                        failed += 1
                else:
                    print(f"✗ FAIL: {description} (Status {response.status_code})")
                    failed += 1
            except Exception as e:
                print(f"✗ ERROR: {description}: {e}")
                failed += 1

            await asyncio.sleep(0.5)  # Rate limit

        print(f"\nStock Update Variations: {passed} passed, {failed} failed")
        return passed, failed


async def test_unknown_intent():
    """Test that unknown intents are properly rejected."""
    print("\n" + "=" * 80)
    print("UNKNOWN INTENT HANDLING")
    print("=" * 80)

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        # Get business
        business_response = await client.get(f"{BASE_URL}/businesses")
        if business_response.status_code != 200:
            print("FAILED: Could not get business")
            return

        businesses = business_response.json()
        business_id = str(businesses[0]["id"])

        unknown_messages = [
            "What's the weather today?",
            "Tell me a joke",
            "Who is the CEO?",
            "Sing a song",
        ]

        passed = 0
        failed = 0

        for message in unknown_messages:
            session_id = f"unknown_{datetime.now().timestamp()}"

            try:
                response = await client.post(
                    f"{BASE_URL}/chat",
                    json={
                        "business_id": business_id,
                        "session_id": session_id,
                        "message": message,
                        "mode": "owner",
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    reply = data.get("reply_text", "").lower()

                    # Check if response indicates unknown intent
                    if (
                        "unsupported" in reply
                        or "didn't understand" in reply
                        or "unknown" in reply
                        or "not understand" in reply
                    ):
                        print(f"✓ PASS: Rejected: {message}")
                        print(f"        Response: {reply[:70]}...")
                        passed += 1
                    else:
                        print(f"✗ FAIL: Should reject: {message}")
                        print(f"        Response: {reply}")
                        failed += 1
                else:
                    print(f"✗ FAIL: {message} (Status {response.status_code})")
                    failed += 1
            except Exception as e:
                print(f"✗ ERROR: {message}: {e}")
                failed += 1

            await asyncio.sleep(0.5)

        print(f"\nUnknown Intent: {passed} passed, {failed} failed")
        return passed, failed


async def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("NLP VARIATION TESTS - All Natural Language Variants")
    print("=" * 80)

    try:
        results = []

        # Test customer variations
        result = await test_customer_variations()
        if result:
            results.append(("Customer Variations", result[0], result[1]))

        # Test product creation variations
        result = await test_product_create_variations()
        if result:
            results.append(("Product Creation", result[0], result[1]))

        # Test stock update variations
        result = await test_stock_update_variations()
        if result:
            results.append(("Stock Updates", result[0], result[1]))

        # Test unknown intent handling
        result = await test_unknown_intent()
        if result:
            results.append(("Unknown Intent", result[0], result[1]))

        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        total_passed = 0
        total_failed = 0
        for name, passed, failed in results:
            total_passed += passed
            total_failed += failed
            status = "PASS" if failed == 0 else "FAIL"
            print(f"{name}: {passed} passed, {failed} failed [{status}]")

        print(f"\nTOTAL: {total_passed} passed, {total_failed} failed")

        if total_failed == 0:
            print("\n✓✓✓ ALL TESTS PASSED ✓✓✓")
        else:
            print(f"\n✗✗✗ {total_failed} TEST(S) FAILED ✗✗✗")

    except Exception as e:
        print(f"\nTest error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
