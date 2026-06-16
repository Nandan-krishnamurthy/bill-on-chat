from app.llm import get_llm

llm = get_llm()

response = llm.invoke(
    "Reply with exactly: Bill-on-Chat AI is working"
)

print(response.content)