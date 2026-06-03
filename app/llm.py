from app.config import LLM_PROVIDER


class StubProvider:
    def generate(self, message: str) -> str:
        return "Stub response: chat contract is active."


def get_llm_provider():
    if LLM_PROVIDER == "stub":
        return StubProvider()

    raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")
