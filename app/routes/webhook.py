import logging
from typing import Optional

import httpx
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel, Field

from app.agents.orchestrator import route_message
from app.config import (
    WHATSAPP_ACCESS_TOKEN,
    WHATSAPP_API_VERSION,
    WHATSAPP_BUSINESS_ID,
    WHATSAPP_PHONE_NUMBER_ID,
    WHATSAPP_VERIFY_TOKEN,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Constructed once at import time; changes require a server restart (expected behaviour)
_WHATSAPP_SEND_URL = (
    f"https://graph.facebook.com/{WHATSAPP_API_VERSION}"
    f"/{WHATSAPP_PHONE_NUMBER_ID}/messages"
)


# ---------------------------------------------------------------------------
# Pydantic models for WhatsApp Cloud API webhook payload
# ---------------------------------------------------------------------------

class _TextBody(BaseModel):
    body: str


class _Message(BaseModel):
    """A single message inside a WhatsApp webhook entry."""
    # "from" is a Python keyword, so we use an alias
    from_number: str = Field(alias="from")
    id: str
    timestamp: str
    type: str
    text: Optional[_TextBody] = None

    model_config = {"populate_by_name": True}


class _ChangeValue(BaseModel):
    messaging_product: str
    # statuses (delivery receipts) are intentionally not modelled — we ignore them
    messages: Optional[list[_Message]] = None


class _Change(BaseModel):
    value: _ChangeValue
    field: str


class _Entry(BaseModel):
    id: str
    changes: list[_Change]


class _WebhookPayload(BaseModel):
    object: str
    entry: list[_Entry]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

async def _send_whatsapp_reply(to: str, body: str) -> None:
    """
    Send a text message back to a WhatsApp user via the Cloud API.

    Errors are logged but not re-raised — a failed send must not crash
    the background task or affect Meta's delivery of future messages.
    """
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": body},
    }
    logger.info("Payload: %s", payload)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            print("=" * 60)
            print("WHATSAPP SEND DEBUG")
            print("URL:", _WHATSAPP_SEND_URL)
            print("PHONE ID:", WHATSAPP_PHONE_NUMBER_ID)
            print("TOKEN PREFIX:", WHATSAPP_ACCESS_TOKEN[:20])
            print("PAYLOAD:", payload)
            print("=" * 60)
            
            response = await client.post(_WHATSAPP_SEND_URL, json=payload, headers=headers)
        if response.status_code != 200:
            logger.error(
                "WhatsApp send failed: status=%s body=%s",
                response.status_code,
                response.text,
            )
        else:
            logger.info("WhatsApp reply sent to %s", to)
    except Exception:
        logger.exception("Exception while sending WhatsApp reply to %s", to)


async def _process_message(sender: str, text: str, graph) -> None:
    """
    Run the incoming message through the existing LangGraph pipeline
    and send the AI reply back via WhatsApp.

    Uses the sender's phone number as session_id so conversation memory
    (stored in PostgreSQL via AsyncPostgresSaver) persists across turns.
    """
    session_id = sender
    thread_id = f"{WHATSAPP_BUSINESS_ID}:{session_id}"

    try:
        result = await route_message(
            text,
            WHATSAPP_BUSINESS_ID,
            session_id,
            thread_id,
            graph,
        )
        reply = result.get("message") or "Sorry, I could not process your request."
    except Exception:
        logger.exception("Error processing WhatsApp message from %s", sender)
        reply = "An error occurred. Please try again later."

    logger.info("Sender number: %s", sender)
    logger.info("Reply: %s", reply)
    await _send_whatsapp_reply(sender, reply)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/webhook", response_class=PlainTextResponse)
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge"),
):
    """
    Meta webhook verification handshake (GET).
    Meta sends this once when you configure the webhook URL in the dashboard.
    """
    if hub_mode == "subscribe" and hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        return hub_challenge
    raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Receive incoming WhatsApp messages from Meta (POST).

    Meta requires a 200 OK response within 20 seconds or it will retry.
    We return 200 immediately and process the message in a background task.

    Events we silently ignore:
    - Status updates and delivery receipts (no "messages" key in value)
    - Non-text message types (images, audio, location, etc.)
    - Malformed / unrecognised payloads
    """
    try:
        body = await request.json()
        logger.info("FULL WEBHOOK PAYLOAD: %s", body)
    except Exception:
        logger.warning("Webhook received a non-JSON body — ignoring")
        # Still return 200 so Meta does not retry an unsupported payload type
        return JSONResponse({"status": "ignored"}, status_code=200)

    # Top-level guard: only handle WhatsApp Business Account notifications
    if body.get("object") != "whatsapp_business_account":
        return JSONResponse({"status": "ignored"}, status_code=200)

    try:
        payload = _WebhookPayload.model_validate(body)
    except Exception:
        logger.warning("Failed to parse WhatsApp webhook payload", exc_info=True)
        return JSONResponse({"status": "ignored"}, status_code=200)

    graph = request.app.state.orchestrator_graph

    for entry in payload.entry:
        for change in entry.changes:
            # Only process message-field changes; skip read-receipts etc.
            if change.field != "messages":
                continue

            messages = change.value.messages
            if not messages:
                # Delivery / read status update — no messages array present
                continue

            for msg in messages:
                if msg.type != "text" or msg.text is None:
                    logger.info(
                        "Ignoring unsupported WhatsApp message type=%s", msg.type
                    )
                    continue

                text = msg.text.body.strip()
                if not text:
                    continue

                sender = msg.from_number
                logger.info("Incoming WhatsApp message from %s: %r", sender, text)

                # Schedule processing — response is sent from inside the task
                background_tasks.add_task(_process_message, sender, text, graph)

    # Always return 200 immediately
    return JSONResponse({"status": "ok"}, status_code=200)
