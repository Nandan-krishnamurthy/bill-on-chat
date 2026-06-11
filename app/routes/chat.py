from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator
from app.agents.orchestrator import route_message
from app.llm import get_llm_provider
from app.services.conversation_state import (
    load_state,
    save_state,
)

router = APIRouter()


class ChatRequest(BaseModel):
    business_id: str = Field(min_length=1, max_length=128)
    session_id: str = Field(min_length=1, max_length=128)
    mode: Literal["owner", "customer"]
    message: str = Field(min_length=1, max_length=4000)

    @field_validator("business_id", "session_id", "message")
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

    # Day 12 - Load conversation state
    state = load_state(
        int(payload.business_id),
        payload.session_id,
    )

    result = await route_message(
        payload.message,
        int(payload.business_id),
        state,
    )

    # Day 12 - Save conversation state
    save_state(
        int(payload.business_id),
        payload.session_id,
        state,
    )

    if result.get("success"):
        reply_text = result.get(
            "message",
            "Customer created successfully",
        )
    else:
        reply_text = result.get(
            "message",
            "Request failed",
        )

    return ChatResponse(
        reply_text=reply_text,
        attachments=[],
    )