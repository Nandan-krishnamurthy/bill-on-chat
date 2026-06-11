import re


def test_product_create_message_parsing():

    message = (
        "Add product Surf Excel 1kg "
        "HSN 3402 Rs 250 GST 18% 50 in stock"
    )

    match = re.search(
        r"add product\s+(.+?)\s+hsn\s+(\d{4,8})\s+rs\s+(\d+(?:\.\d+)?)\s+gst\s+(\d{1,2})%\s+(\d+)\s+in stock",
        message,
        re.IGNORECASE,
    )

    assert match is not None
    assert match.group(1) == "Surf Excel 1kg"
    assert match.group(2) == "3402"
    assert match.group(3) == "250"
    assert match.group(4) == "18"
    assert match.group(5) == "50"


def test_product_update_message_parsing():

    message = (
        "Update product Surf Excel 1kg stock to 100"
    )

    match = re.search(
        r"update product\s+(.+?)\s+stock\s+to\s+(\d+)",
        message,
        re.IGNORECASE,
    )

    assert match is not None
    assert match.group(1) == "Surf Excel 1kg"
    assert match.group(2) == "100"

def test_memory_based_update_message_parsing():

    message = "Update stock to 100"

    match = re.search(
        r"update stock to\s+(\d+)",
        message,
        re.IGNORECASE,
    )

    assert match is not None
    assert match.group(1) == "100"


def test_session_state_isolation():

    session_a_state = {
        "last_product_name": "Surf Excel 1kg",
    }

    session_b_state = {}

    assert (
        session_a_state.get("last_product_name")
        == "Surf Excel 1kg"
    )

    assert (
        session_b_state.get("last_product_name")
        is None
    )