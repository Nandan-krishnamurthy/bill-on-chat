import re


def test_customer_message_parsing():

    message = "Add customer Ramesh 9876543210"

    match = re.search(
        r"add customer\s+(.+?)\s+(\d{10})",
        message,
        re.IGNORECASE,
    )

    assert match is not None
    assert match.group(1) == "Ramesh"
    assert match.group(2) == "9876543210"