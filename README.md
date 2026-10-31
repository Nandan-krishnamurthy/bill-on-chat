# Bill-on-Chat

A chat-based back-office assistant for small Indian retailers. The shop owner types plain-English messages, in a web chat or on WhatsApp, and an LLM-driven LangGraph workflow turns them into database actions: adding customers, adding products and updating stock.

> **Status: early prototype.** Customer and product management work. GST invoicing, tax calculation, PDFs, payments, reports and the customer-facing mode are planned (see `docs/`) but **not built yet**. See [Current status](#current-status).

## What works today

| Feature | Example message |
|---|---|
| Add a customer (name + 10-digit phone, duplicate check per business) | `Add customer Ramesh 9876543210` |
| Add a product (name, HSN, price, GST rate, stock) | `Add product Surf Excel 1kg HSN 3402 Rs 250 GST 18% 50 in stock` |
| Update stock by partial product name | `Update product Surf stock to 100` |
| Pick from a numbered list when several products match | `1` |
| Conversation state saved in PostgreSQL per business + session (survives restarts) | — |
| WhatsApp Cloud API: receive text messages, reply in the same chat | — |
| Web chat UI (React + Vite) with a business picker | — |

Phrasing doesn't have to be exact. The LLM pulls the fields out of free-form text, and simple keyword matching takes over if the LLM call fails.

## How it works

```
WhatsApp user ──► Meta Cloud API ──► POST /webhook ─┐
                                                    ├─► route_message() ──► LangGraph graph
Web chat (React) ─────────────────► POST /chat ─────┘          │
                                                               ▼
        intent_classifier ──► customer_agent_node ─┐   (Groq LLM extracts intent + fields)
                          ├─► product_agent_node  ─┼─► state_trimming_node ──► END
                          └─► fallback_node       ─┘
                                     │
                                     ▼
                    app/tools/*  ──► PostgreSQL (SQLAlchemy async)
        Graph state checkpointed per thread "<business_id>:<session_id>" (AsyncPostgresSaver)
```

- **`/chat`** takes `{business_id, session_id, mode, message}` and returns `{reply_text, attachments}`.
- **`/webhook`** answers Meta's verification handshake (GET), returns 200 straight away on POST, and handles the message in a background task. The sender's phone number becomes the session ID. Every WhatsApp message goes to the business set by `WHATSAPP_BUSINESS_ID`.

### Project layout

```
app/
  main.py                  FastAPI app; startup creates the checkpointer and compiles the graph
  config.py                Reads environment variables
  llm.py                   ChatGroq client
  agents/orchestrator.py   LangGraph StateGraph: classify → route → agent → trim
  agents/customer_agent.py Customer creation flow
  agents/product_agent.py  Product create / stock update / numbered disambiguation
  services/llm_tools.py    LLM tool-calling prompts used for intent + field extraction
  services/langgraph_checkpointer.py  AsyncPostgresSaver setup
  services/message_archival.py        Moves old messages to message_archives
  services/product_matcher.py         Partial (ILIKE) product name search
  tools/                   Database operations (create_customer, create_product, update_product)
  routes/                  /chat, /businesses, /webhook
  db/models/               SQLAlchemy models
  schemas/                 Pydantic validation models
alembic/                   Database migrations
frontend/                  React + Vite chat UI
tests/                     Pytest tests (see Testing)
docs/                      Spec, roadmap and implementation notes
```

## Tech stack

Pinned in `requirements.txt` / `frontend/package.json`:

- **Python 3.12** (Docker base image `python:3.12-slim`)
- FastAPI 0.136.3, Uvicorn 0.48.0, Pydantic 2.13.4
- LangGraph 1.2.5, langgraph-checkpoint-postgres 3.1.0, LangChain 1.3.9, langchain-groq 1.1.3
- SQLAlchemy 2.0.50 (asyncpg 0.31.0), Alembic 1.18.4, psycopg 3.3.4, psycopg2-binary 2.9.12
- httpx 0.28.1, python-dotenv 1.2.2, pytest 9.0.3
- PostgreSQL (version not pinned)
- Frontend: React ^19.2.6, Vite ^8.0.12

LLM: Groq, default model `llama-3.3-70b-versatile`.

## Database

| Table | Key columns | Relationships |
|---|---|---|
| `businesses` | name, gstin, state_code, whatsapp_number | — |
| `customers` | name, phone, gstin, state, address | `business_id` → `businesses.id` |
| `products` | name, hsn, sell_price, cost, gst_rate, stock, low_stock_threshold, unit | `business_id` → `businesses.id` |
| `message_archives` | session_id, thread_id, role, content | `business_id` (no foreign key) |

On startup, LangGraph's `checkpointer.setup()` also creates its own checkpoint tables.

## Setup

### Requirements

- A PostgreSQL server you can reach
- A Groq API key
- Docker Desktop (for the Docker route) or Python 3.12
- Node.js + npm (for the web UI)
- For WhatsApp: a Meta developer app with the WhatsApp product, and a public HTTPS URL that forwards to port 8000

### 1. Configure

```bash
cp .env.example .env
# fill in DATABASE_URL, POSTGRES_USER, POSTGRES_PASSWORD, GROQ_API_KEY
# and (optionally) the WHATSAPP_* values
```

Create an empty database, for example `bill_on_chat`.

### 2a. Run with Docker

The Compose file starts **only the API**. It does not start PostgreSQL. It expects Postgres on your host machine at `host.docker.internal:5432`.

> Inside the container, `localhost` means the container itself, so the `DATABASE_URL` in `.env` won't work there. `docker-compose.yml` builds the container's own `DATABASE_URL` from `POSTGRES_USER` and `POSTGRES_PASSWORD` in `.env`, pointing at `host.docker.internal:5432/bill_on_chat`. If your database has a different name, change it in `docker-compose.yml`.

```bash
docker compose build
docker compose run --rm bill-on-chat alembic upgrade head   # create tables
docker compose up
```

On Linux, `host.docker.internal` doesn't resolve by default. Add `extra_hosts: ["host.docker.internal:host-gateway"]` to the service, or change the host in the `DATABASE_URL` line of `docker-compose.yml`.

### 2b. Run without Docker

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --port 8000  # Windows: python run_server.py
```

On Windows, use `run_server.py`. psycopg's async mode needs a selector event loop, and the script sets one up.

### 3. Add a business

The API has no endpoint for creating a business yet, and customers and products can't be saved without one. Insert a row by hand:

```sql
INSERT INTO businesses (name, gstin, state_code)
VALUES ('Demo Store', '29ABCDE1234F1Z5', '29');
```

Check it with `curl http://localhost:8000/businesses`. Interactive API docs are at `http://localhost:8000/docs`.

### 4. Web chat UI

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

The UI calls the API at `http://127.0.0.1:8000` (hardcoded in `frontend/src/App.jsx`). The API only accepts browser requests from `http://localhost:5173`.

### 5. WhatsApp (optional)

1. Expose port 8000 over HTTPS.
2. In the Meta app dashboard, set the webhook URL to `https://<your-host>/webhook` and the verify token to your `WHATSAPP_VERIFY_TOKEN`.
3. Subscribe to the `messages` webhook field.
4. Set `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID` and `WHATSAPP_BUSINESS_ID` (the ID of an existing business row), then restart.

Only text messages are handled. Images, audio, location and delivery receipts are ignored.

## Testing

```bash
# Offline tests: schema validation and regex checks
pytest tests/test_customer_creation.py tests/test_product_schema.py \
       tests/test_customer_agent.py tests/test_product_agent.py
```

Most other files in `tests/` (and the `test_*.py` scripts in the repo root) send real requests to a running server at `http://127.0.0.1:8000`. They need a database, a Groq key and the `pytest-asyncio` plugin, which is **not** in `requirements.txt`. Known issue: `tests/test_chat_contract.py::test_chat_valid_payload_returns_response_contract` fails because the test client doesn't run the app's startup, so the graph is never built.

## Current status

**Not built yet** (planned in `docs/PROJECT_SPEC_CLEAN.md`):
- Invoices, GST tax calculation (CGST/SGST/IGST), PDF generation
- Payments, reminders, reports
- Customer mode / sales agent. `/chat` accepts `mode`, but it's currently ignored and every request runs as owner.
- Authentication on the API, and signature verification on the WhatsApp webhook

**Known limitations:**
- GST data is stored, not calculated. Products store an HSN code (4–8 characters) and a whole-number GST rate from 0 to 28. Businesses store a GSTIN and a 2-character state code. Customers store a free-text state (defaults to "Karnataka").
- Creating a product with 0% GST or 0 stock through chat is currently rejected.
- Each chat request sends only the latest message to the LLM. Earlier turns aren't used as context; only the product-selection state carries over between turns.
- Each message makes 2–3 LLM calls.
