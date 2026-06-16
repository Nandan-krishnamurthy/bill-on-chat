from langchain_groq import ChatGroq

from app.config import GROQ_API_KEY, LLM_MODEL


def get_llm():
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=LLM_MODEL,
        temperature=0,
    )