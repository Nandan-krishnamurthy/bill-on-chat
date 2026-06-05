import os

from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "stub").strip().lower() or "stub"
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()