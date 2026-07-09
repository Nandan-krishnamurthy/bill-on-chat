import os

from dotenv import load_dotenv

load_dotenv(override=True)

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "llama-3.3-70b-versatile"
).strip()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# WhatsApp Cloud API
# WHATSAPP_ACCESS_TOKEN: Bearer token from Meta app dashboard (temporary or permanent)
# WHATSAPP_PHONE_NUMBER_ID: Numeric ID of the sending phone number (not the phone number itself)
# WHATSAPP_VERIFY_TOKEN: Arbitrary secret you set in Meta webhook config
# WHATSAPP_API_VERSION: Graph API version to use (e.g. v21.0)
# WHATSAPP_BUSINESS_ID: Your internal business tenant ID — all WhatsApp messages route here
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "").strip()
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "").strip()
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "bill-on-chat-webhook").strip()
WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v21.0").strip()
WHATSAPP_BUSINESS_ID = int(os.getenv("WHATSAPP_BUSINESS_ID", "1"))