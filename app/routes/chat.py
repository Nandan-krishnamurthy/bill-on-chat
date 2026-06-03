from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator

from app.llm import get_llm_provider


router = APIRouter()


class ChatRequest(BaseModel):
    business_id: str = Field(min_length=1, max_length=128)
    mode: Literal["owner", "customer"]
    message: str = Field(min_length=1, max_length=4000)

    @field_validator("business_id", "message")
    @classmethod
    def reject_blank_strings(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value


class ChatResponse(BaseModel):
    reply_text: str
    attachments: list[str] = []


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    print(f"business_id={payload.business_id}")
    print(f"mode={payload.mode}")
    print(f"message={payload.message}")

    provider = get_llm_provider()
    reply_text = provider.generate(payload.message)

    return ChatResponse(reply_text=reply_text, attachments=[])
