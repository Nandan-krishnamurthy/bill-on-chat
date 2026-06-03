from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator


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

    # Day 1 stub response to lock the API contract before agent/tool integration.
    return ChatResponse(reply_text="Stub response: chat contract is active.", attachments=[])
