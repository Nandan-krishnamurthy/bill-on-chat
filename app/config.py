import os


LLM_PROVIDER = os.getenv("LLM_PROVIDER", "stub").strip().lower() or "stub"
