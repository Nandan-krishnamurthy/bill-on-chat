## 2026-06-02 — Week 1 Day 1

Completed:

* Defined /chat request and response contracts.
* Added payload validation.
* Implemented stubbed POST /chat endpoint.
* Added contract tests (4 passing).

Verified:

* /chat responds with expected shape.
* Swagger endpoint available.
* Tests passing (`python -m pytest`).

Files:

* app/main.py
* app/routes/chat.py
* tests/test_chat_contract.py

Status:

* Day 1 complete.

## 2026-06-02 — Week 1 Day 2

## Week 1 Day 2

### Completed

* Created React frontend using Vite.
* Built minimal chat UI (message area, input, send button).
* Connected frontend to POST /chat.
* Added CORS configuration in FastAPI.
* Verified browser ↔ backend communication.

### Smoke Test

Request:

{
"business_id": "demo-business",
"mode": "owner",
"message": "hello"
}

Response:

{
"reply_text": "Stub response: chat contract is active.",
"attachments": []
}

Result:

Frontend successfully completed one full message cycle with the backend.

### Status

Week 1 Day 2 completed.

## 2026-06-02 — Week 1 Day 3

## Week 1 Day 3

### Completed

* Added Business ID input field.
* Added Owner/Customer mode selector.
* Wired business_id and mode into chat request payload.
* Added backend logging for Phase 1 verification.
* Verified end-to-end mode/tenant plumbing.

### Verification

Input:

Business ID: test-store
Mode: customer
Message: hello

Backend Log:

business_id=test-store
mode=customer
message=hello

### Boundary Note

The Owner/Customer toggle is a testing-only control for Phase 1 plumbing verification and is not a security mechanism.

### Status

Week 1 Day 3 completed.


## 2026-06-02 — Week 1 Day 4

## Week 1 Day 4

### Completed

* Added `app/config.py` for env-based settings.
* Added `app/llm.py` provider factory.
* Implemented `StubProvider`.
* Updated `/chat` to use provider factory.
* Added `LLM_PROVIDER` configuration.

### Verification

**Config**

```env
LLM_PROVIDER=stub
```

**Request**

```json
{
  "business_id": "test-shop",
  "mode": "owner",
  "message": "hello"
}
```

**Response**

```json
{
  "reply_text": "Stub response: chat contract is active.",
  "attachments": []
}
```

**Result:** Provider factory correctly routed requests to `StubProvider`.

### Status

✅ Week 1 Day 4 complete.
✅ Provider switching validated.
✅ Chat endpoint functioning through factory layer.



## Week 2 Day 5 - Database Foundation

### Completed

* Installed PostgreSQL 18 locally.
* Created database: `bill_on_chat`.
* Installed:

  * SQLAlchemy
  * asyncpg
  * Alembic
  * python-dotenv
* Added `DATABASE_URL` configuration.
* Created:

  * `app/db/session.py`
  * `app/db/__init__.py`
* Configured:

  * Async SQLAlchemy engine
  * Async sessionmaker
* Initialized Alembic:

  * `alembic/`
  * `alembic.ini`

### Verification

* Database connection test passed.

Output:

```text
Database connection successful
1
```

### Current Architecture

Frontend
↓
FastAPI
↓
Provider Factory
↓
Stub Provider

Database Layer

FastAPI
↓
SQLAlchemy Async Engine
↓
PostgreSQL

### Notes

* Fixed VS Code interpreter issue.
* Added `.env` loading via `python-dotenv`.

### Current State

Project now has a working PostgreSQL connection and migration framework.

No models, tables, or business entities exist yet.

### Next Step

Begin first database-backed application structures according to schedule.
