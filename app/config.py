import os

from dotenv import load_dotenv

load_dotenv()

LLM_MODEL = os.getenv(
    "LLM_MODEL",
    "llama-3.3-70b-versatile"
).strip()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()