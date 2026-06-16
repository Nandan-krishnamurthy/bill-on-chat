"""
Verify core LLM-driven functionality: intent recognition and argument extraction.
"""

import asyncio
from app.services.llm_tools import llm_customer_intent, llm_product_intent


async def test_llm_customer_intent_recognition():
    """Test LLM customer intent recognition for various inputs."""
    print("\n" + "=" * 80)
    print("LLM CUSTOMER INTENT RECOGNITION")
    print("=" * 80)

    test_cases = [
        ("Add customer Ramesh 9876543210", "create_customer", "Ramesh", "9876543210"),
        ("Create new customer named Priya, phone 8765432109", "create_customer", "Priya", "8765432109"),
        ("I met a new customer today, add him as Suresh 9988776655", "create_customer", "Suresh", "9988776655"),
        ("Register customer John 9876543210", "create_customer", "John", "9876543210"),
        ("What's the weather?", "unknown", None, None),
        ("Tell me a joke", "unknown", None, None),
    ]

    passed = 0
    failed = 0

    for message, expected_tool, expected_name, expected_phone in test_cases:
        try:
            result = await llm_customer_intent(message, business_id=1)
            tool = result["tool"]
            params = result["parameters"]
            confidence = result["confidence"]

            if tool == expected_tool:
                if expected_tool == "create_customer":
                    name = params.get("name", "")
                    phone = params.get("phone", "")
                    
                    # Validate extraction
                    if (expected_name.lower() in name.lower() and 
                        phone == expected_phone):
                        print(f"✓ PASS: {message[:50]}...")
                        print(f"        Tool: {tool}, Name: {name}, Phone: {phone}")
                        passed += 1
                    else:
                        print(f"✗ FAIL: {message[:50]}...")
                        print(f"        Expected: {expected_name}, {expected_phone}")
                        print(f"        Got: {name}, {phone}")
                        failed += 1
                else:
                    print(f"✓ PASS: {message[:50]}... → unknown")
                    passed += 1
            else:
                print(f"✗ FAIL: {message[:50]}...")
                print(f"        Expected tool: {expected_tool}, got: {tool}")
                failed += 1
        except Exception as e:
            print(f"✗ ERROR: {message[:50]}... : {e}")
            failed += 1

    print(f"\nCustomer Intent: {passed} passed, {failed} failed")
    return passed, failed


async def test_llm_product_intent_recognition():
    """Test LLM product intent recognition for various inputs."""
    print("\n" + "=" * 80)
    print("LLM PRODUCT INTENT RECOGNITION")
    print("=" * 80)

    test_cases = [
        (
            "Add product Surf Excel 1kg HSN 3402 Rs 250 GST 18% 50 in stock",
            "create_product",
            "Surf Excel",
            "3402",
        ),
        (
            "Create a product called Matic: HSN 3402, price 300, GST 18%, stock 100",
            "create_product",
            "Matic",
            "3402",
        ),
        ("Update Surf stock to 100", "update_stock", "Surf", "100"),
        ("Increase inventory to 100", "update_stock", None, "100"),
        ("We received 100 Matic packets", "update_stock", "Matic", "100"),
        ("What is your name?", "unknown", None, None),
    ]

    passed = 0
    failed = 0

    for message, expected_tool, expected_product, expected_param in test_cases:
        try:
            result = await llm_product_intent(message, business_id=1)
            tool = result["tool"]
            params = result["parameters"]
            confidence = result["confidence"]

            if tool == expected_tool:
                if expected_tool == "create_product":
                    name = params.get("name", "")
                    if expected_product.lower() in name.lower():
                        print(f"✓ PASS: {message[:50]}...")
                        print(f"        Tool: {tool}, Product: {name}")
                        passed += 1
                    else:
                        print(f"✗ FAIL: {message[:50]}...")
                        print(f"        Expected product: {expected_product}, got: {name}")
                        failed += 1
                elif expected_tool == "update_stock":
                    stock = params.get("stock")
                    product = params.get("product_name", "")
                    if str(stock) == expected_param:
                        print(f"✓ PASS: {message[:50]}...")
                        print(f"        Tool: {tool}, Stock: {stock}, Product: {product}")
                        passed += 1
                    else:
                        print(f"✗ FAIL: {message[:50]}...")
                        print(f"        Expected stock: {expected_param}, got: {stock}")
                        failed += 1
                else:
                    print(f"✓ PASS: {message[:50]}... → unknown")
                    passed += 1
            else:
                print(f"✗ FAIL: {message[:50]}...")
                print(f"        Expected tool: {expected_tool}, got: {tool}")
                failed += 1
        except Exception as e:
            print(f"✗ ERROR: {message[:50]}... : {e}")
            failed += 1

    print(f"\nProduct Intent: {passed} passed, {failed} failed")
    return passed, failed


async def test_argument_extraction():
    """Test that argument extraction is accurate."""
    print("\n" + "=" * 80)
    print("ARGUMENT EXTRACTION ACCURACY")
    print("=" * 80)

    # Test customer argument extraction
    print("\nCustomer Arguments:")
    customer_tests = [
        ("Add customer Rajesh 9876543210", "Rajesh", "9876543210"),
        ("Create customer John Smith with phone number 8765432109", "John Smith", "8765432109"),
        ("I want to add customer (Priya) phone 9988776655", "Priya", "9988776655"),
    ]

    passed = 0
    for message, expected_name, expected_phone in customer_tests:
        try:
            result = await llm_customer_intent(message, 1)
            if result["tool"] == "create_customer":
                name = result["parameters"].get("name", "")
                phone = result["parameters"].get("phone", "")
                
                if expected_name.lower() in name.lower() and phone == expected_phone:
                    print(f"✓ Name: {name}, Phone: {phone}")
                    passed += 1
                else:
                    print(
                        f"✗ Expected: {expected_name}/{expected_phone}, "
                        f"got: {name}/{phone}"
                    )
        except Exception as e:
            print(f"✗ Error: {e}")

    print(f"\nArgument Extraction: {passed}/{len(customer_tests)} passed")
    return passed, len(customer_tests)


async def main():
    """Run all LLM functionality tests."""
    print("\n" + "=" * 80)
    print("LLM-DRIVEN FUNCTIONALITY VERIFICATION")
    print("=" * 80)

    try:
        # Test customer intent
        cust_pass, cust_fail = await test_llm_customer_intent_recognition()

        # Test product intent
        prod_pass, prod_fail = await test_llm_product_intent_recognition()

        # Test argument extraction
        arg_pass, arg_total = await test_argument_extraction()

        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        
        total_pass = cust_pass + prod_pass + arg_pass
        total_fail = cust_fail + prod_fail + (arg_total - arg_pass)
        
        print(f"Customer Intent: {cust_pass} passed, {cust_fail} failed")
        print(f"Product Intent: {prod_pass} passed, {prod_fail} failed")
        print(f"Argument Extraction: {arg_pass}/{arg_total} passed")
        print(f"\nTOTAL: {total_pass} passed, {total_fail} failed")

        if total_fail == 0:
            print("\n✓✓✓ ALL LLM TESTS PASSED ✓✓✓")
        else:
            print(f"\n✗✗✗ {total_fail} TEST(S) FAILED ✗✗✗")

    except Exception as e:
        print(f"\nTest error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
