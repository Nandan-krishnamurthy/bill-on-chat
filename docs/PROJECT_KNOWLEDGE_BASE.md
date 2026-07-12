# PROJECT_KNOWLEDGE_BASE.md
## Bill-on-Chat — Complete Technical Knowledge Base

> Written as a permanent engineering reference. Every section references actual files, classes, and functions in the repository. Use this to understand, explain, and defend every design decision during technical interviews.

---

# 1. Project Overview

## 1.1 Business Problem

Small Indian retailers and SMEs spend enormous time on manual billing, GST compliance, invoice generation, and inventory tracking. Most billing software requires navigating complex UIs, training staff, and maintaining desktop installations.

**Bill-on-Chat eliminates the UI.** The shopkeeper just sends a chat message — in plain English, mixed Hindi/Kannada, or shorthand — and the AI agent does everything behind the scenes: creates customers, adds products, generates GST-compliant invoices, records stock levels, and sends reports.

The system is built for **Indian-first** requirements: GST compliance, HSN codes, INR pricing, multi-language input, WhatsApp delivery (Phase 2).

## 1.2 Purpose

Build a conversational GST billing platform where:
- A **shopkeeper** (Owner Mode) manages their entire business through chat
- An **end customer** (Customer Mode) browses products and places orders through the same chat interface
- The same AI agent layer serves both modes — only the persona and permissions change

## 1.3 Target Users

| User | Mode | Example Interaction |
|------|------|---------------------|
| Shop owner / retailer | Owner Mode | "Add product Surf Excel 1kg HSN 3402 Rs 250 GST 18% 50 in stock" |
| Shop owner | Owner Mode | "Add customer Rahul 9876543210" |
| End customer of the shop | Customer Mode | "What detergents do you have?" |

## 1.4 Key Features (Phase 1 — Implemented)

- **Conversational customer creation** via natural language
- **Conversational product creation** with full GST metadata (HSN, GST rate, sell price, stock)
- **Stock update** via natural language
- **Disambiguation flow**: when a product search matches multiple results, the system asks the user to pick by number
- **Multi-tenant isolation**: every business has its own data (business_id FK everywhere)
- **Durable conversation memory**: LangGraph + PostgreSQL checkpointer — the conversation persists across server restarts
- **State trimming + message archival**: keeps conversation history bounded so checkpoint size does not grow unbounded

## 1.5 High-Level Workflow

```
User types message in browser
        ↓
React frontend (Vite + React 19)
        ↓  HTTP POST /chat
FastAPI backend
        ↓
Pydantic validation (ChatRequest)
        ↓
route_message() → LangGraph graph.ainvoke()
        ↓
LangGraph loads checkpoint from PostgreSQL (prior state)
        ↓
intent_classifier node → LLM call → intent label
        ↓
Conditional edge → customer_agent_node | product_agent_node | fallback_node
        ↓
Agent calls LLM (tool calling) → extracts parameters
        ↓
Tool function → Async SQLAlchemy → PostgreSQL INSERT/UPDATE
        ↓
state_trimming_node → archive old messages if needed
        ↓
LangGraph saves checkpoint to PostgreSQL
        ↓
agent_result extracted → ChatResponse returned
        ↓
React displays reply
```

---

# 2. High-Level Architecture

## 2.1 Layer Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    BROWSER (React 19)                   │
│  frontend/src/App.jsx                                   │
│  Vite dev server on :5173                               │
│  fetch() → POST /chat, GET /businesses                  │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTP / JSON
┌─────────────────────────▼───────────────────────────────┐
│                FastAPI (Python 3.x)                     │
│  app/main.py                                            │
│  ├── /chat     app/routes/chat.py                       │
│  └── /businesses  app/routes/business.py               │
│  Middleware: CORS (allow :5173)                         │
│  Startup: AsyncPostgresSaver + LangGraph compile        │
└─────────────────────────┬───────────────────────────────┘
                          │ Python function call
┌─────────────────────────▼───────────────────────────────┐
│              LangGraph Orchestrator                     │
│  app/agents/orchestrator.py                             │
│  StateGraph: START → intent_classifier → router →      │
│    customer_agent_node | product_agent_node | fallback  │
│      → state_trimming_node → END                        │
│  Checkpointer: AsyncPostgresSaver (PostgreSQL)          │
└──────────┬──────────────────────────┬───────────────────┘
           │                          │
┌──────────▼──────────┐  ┌────────────▼──────────────────┐
│  Customer Agent     │  │       Product Agent           │
│  app/agents/        │  │  app/agents/product_agent.py  │
│  customer_agent.py  │  │                               │
│  LLM tool calling   │  │  LLM tool calling             │
│  → create_customer  │  │  → create_product             │
│                     │  │  → update_stock               │
└──────────┬──────────┘  └────────────┬──────────────────┘
           │                          │
┌──────────▼──────────────────────────▼──────────────────┐
│              LLM Service (Groq / llama-3.3-70b)        │
│  app/llm.py → get_llm()                                │
│  app/services/llm_tools.py                             │
│  llm_customer_intent() / llm_product_intent()          │
│  Uses LangChain bind_tools() + tool_calls parsing      │
└─────────────────────────────────────────────────────────┘
           │                          │
┌──────────▼──────────┐  ┌────────────▼──────────────────┐
│  customer_tools.py  │  │  product_tools.py             │
│  create_customer()  │  │  create_product()             │
│                     │  │  update_product()             │
└──────────┬──────────┘  └────────────┬──────────────────┘
           │                          │
┌──────────▼──────────────────────────▼──────────────────┐
│            Async SQLAlchemy + PostgreSQL                │
│  app/db/session.py  (AsyncEngine, AsyncSessionLocal)   │
│  app/db/models/  (Business, Customer, Product,         │
│                   MessageArchive)                      │
│  Tables: businesses, customers, products,              │
│          message_archives, langgraph_checkpoints*      │
└─────────────────────────────────────────────────────────┘

* LangGraph creates its own checkpoint tables automatically
```

## 2.2 Component Communication

| From | To | Protocol |
|------|----|----------|
| React | FastAPI | HTTP JSON (`fetch`) |
| FastAPI | LangGraph | Python function call (`graph.ainvoke`) |
| LangGraph nodes | LLM (Groq) | HTTPS API via LangChain (`ainvoke`) |
| LangGraph | PostgreSQL checkpoints | psycopg3 async (`AsyncPostgresSaver`) |
| SQLAlchemy tools | PostgreSQL | asyncpg connection pool |

## 2.3 Data Flow (Single Request)

1. React → `POST /chat` with `{business_id, session_id, mode, message}`
2. FastAPI validates via `ChatRequest` Pydantic model
3. `thread_id = f"{business_id}:{session_id}"` constructed
4. `route_message()` builds a fresh `AgentState` with only the new message
5. `graph.ainvoke(state, config={"configurable":{"thread_id":...}})` called
6. LangGraph merges the fresh state with the persisted checkpoint state from PostgreSQL
7. Graph executes nodes in order, updating state at each step
8. Final state contains `agent_result` dict with `success` and `message`
9. FastAPI returns `ChatResponse(reply_text=..., attachments=[])`
10. React appends the bot reply to the message list

---

# 3. Folder Structure

```
bill-on-chat/
├── app/                    # All Python backend code
│   ├── main.py             # FastAPI app, lifespan, middleware, routers
│   ├── config.py           # Environment variables (LLM_MODEL, GROQ_API_KEY, DATABASE_URL)
│   ├── llm.py              # LLM factory: get_llm() → ChatGroq instance
│   ├── agents/             # Business logic: orchestrator + domain agents
│   │   ├── orchestrator.py # LangGraph graph definition, AgentState, all nodes
│   │   ├── customer_agent.py  # Customer intent handler
│   │   └── product_agent.py   # Product intent handler (with disambiguation)
│   ├── db/                 # Database layer
│   │   ├── session.py      # Async SQLAlchemy engine + session factory
│   │   └── models/         # ORM models
│   │       ├── base.py         # DeclarativeBase
│   │       ├── business.py     # Business model
│   │       ├── customer.py     # Customer model
│   │       ├── product.py      # Product model
│   │       └── message_archive.py  # Message archival model
│   ├── routes/             # FastAPI routers (HTTP endpoints)
│   │   ├── chat.py         # POST /chat
│   │   └── business.py     # GET /businesses
│   ├── schemas/            # Pydantic models (validation + serialization)
│   │   ├── customer.py     # CustomerCreate
│   │   └── product.py      # ProductCreate, ProductUpdate
│   ├── services/           # Supporting services
│   │   ├── langgraph_checkpointer.py  # PostgreSQL checkpointer setup
│   │   ├── llm_tools.py    # LLM tool-calling wrappers
│   │   ├── message_archival.py  # Message archival logic
│   │   └── product_matcher.py   # Fuzzy product search
│   └── tools/              # Database operations called by agents
│       ├── customer_tools.py   # create_customer()
│       └── product_tools.py    # create_product(), update_product()
├── alembic/                # Database migration management
│   ├── env.py              # Alembic config + async migration runner
│   ├── versions/           # Migration scripts (one file per schema change)
│   └── alembic.ini         # Alembic configuration file
├── frontend/               # React 19 single-page application
│   ├── src/
│   │   ├── App.jsx         # Entire frontend UI (single component)
│   │   ├── App.css         # Chat UI styles
│   │   ├── main.jsx        # React DOM root mount
│   │   └── index.css       # Global styles
│   ├── index.html          # HTML shell
│   ├── vite.config.js      # Vite bundler config
│   └── package.json        # Dependencies (react 19, vite 8)
├── tests/                  # Automated test suite
├── prompts/                # Daily development prompt logs
├── docs/                   # Project checklists
└── run_server.py           # Server startup helper
```

### Why each folder exists

| Folder | Why it exists |
|--------|---------------|
| `app/agents/` | Separates AI reasoning logic from HTTP routing and DB operations |
| `app/db/models/` | ORM models are separate from Pydantic schemas — ORM handles persistence, Pydantic handles I/O validation |
| `app/routes/` | Each router file owns one domain's endpoints; clean separation from business logic |
| `app/schemas/` | Pydantic validation schemas are decoupled from ORM models; allows independent evolution |
| `app/services/` | Stateless helper logic that does not belong to a single agent or route |
| `app/tools/` | Atomic DB operations, callable by agents; isolated so they can be tested independently |
| `alembic/versions/` | Each migration is a separate, versioned, reversible script — full audit trail of schema evolution |
| `frontend/src/` | All React code; currently a single-component app because the UI is intentionally minimal |

---

# 4. File-by-File Walkthrough

## 4.1 `app/main.py`

**Purpose:** Creates the FastAPI application, registers middleware, connects routers, and manages startup/shutdown lifecycle.

**Key responsibilities:**
- Sets `WindowsSelectorEventLoopPolicy` on Windows (required for psycopg3 compatibility with asyncio)
- Defines the `lifespan` async context manager which runs startup and shutdown logic
- During startup: initializes `AsyncPostgresSaver`, calls `checkpointer.setup()` (creates checkpoint tables), compiles LangGraph graph, stores both on `app.state`
- During shutdown: clears `app.state` references
- Registers CORS middleware (allows `http://localhost:5173` — the Vite dev server)
- Mounts `chat_router` and `business_router`

**Critical design decision:** The `yield` is *inside* the `async with get_checkpointer_context_manager()` block. If it were outside, the PostgreSQL connection would close before any requests arrived, causing all chat requests to fail. This is the most common LangGraph checkpointer bug.

**Who calls it:** Uvicorn/Hypercorn loads this module as the ASGI application entry point.

**What breaks if removed:** The entire application stops.

---

## 4.2 `app/config.py`

**Purpose:** Loads environment variables using `python-dotenv` and exposes them as Python constants.

**Variables:**
- `LLM_MODEL` — defaults to `"llama-3.3-70b-versatile"` (Groq's Llama model)
- `GROQ_API_KEY` — Groq API key for LLM calls
- `DATABASE_URL` — PostgreSQL connection string in SQLAlchemy `asyncpg` format: `postgresql+asyncpg://user:pass@host/db`

**Who calls it:** `app/llm.py`, `app/db/session.py`, `app/services/langgraph_checkpointer.py`

**What breaks if removed:** Every module that touches the LLM or database will raise an `ImportError` or a runtime error.

---

## 4.3 `app/llm.py`

**Purpose:** Factory function that returns a configured LangChain `ChatGroq` instance.

**Function:** `get_llm()` — creates `ChatGroq(api_key=..., model=..., temperature=0)`

**Why `temperature=0`:** Deterministic output. For tool-calling and parameter extraction, we want the LLM to always produce the same structured output for the same input. Randomness would cause flaky behavior.

**Who calls it:** `app/services/llm_tools.py` — both `llm_customer_intent()` and `llm_product_intent()`.

**What breaks if removed:** All LLM calls fail.

---

## 4.4 `app/routes/chat.py`

**Purpose:** Defines the `POST /chat` endpoint — the single entry point for all conversational interactions.

**Classes:**
- `ChatRequest(BaseModel)` — Pydantic request model with fields: `business_id`, `session_id`, `mode`, `message`. Each field has strict validation (min/max length, not blank). Uses `@field_validator` to reject whitespace-only strings.
- `ChatResponse(BaseModel)` — Response model: `reply_text: str`, `attachments: list[str]`

**Function:** `chat_endpoint(request: Request, payload: ChatRequest) → ChatResponse`
- Constructs `thread_id = f"{business_id}:{session_id}"`
- Retrieves compiled graph from `request.app.state.orchestrator_graph`
- Calls `route_message()` from orchestrator
- Wraps result in `ChatResponse`

**Why `request: Request`:** To access `app.state` where the graph and checkpointer are stored. This is FastAPI's mechanism for sharing app-level state.

**Who calls it:** React frontend via `fetch("http://127.0.0.1:8000/chat", {method:"POST",...})`

---

## 4.5 `app/routes/business.py`

**Purpose:** Exposes `GET /businesses` — returns list of all businesses for the frontend dropdown.

**Function:** `list_businesses()` — async, directly queries `Business` table via `AsyncSessionLocal`, returns `[{id, name}]`.

**Who calls it:** React's `useEffect` hook on component mount.

**What breaks if removed:** The business selector dropdown in the UI will be empty.

---

## 4.6 `app/agents/orchestrator.py`

**Purpose:** The core of the system. Defines the LangGraph `StateGraph`, all nodes, routing logic, and the `route_message()` entry function.

**`AgentState` (TypedDict):**
```python
messages: list[BaseMessage]     # LangChain message history
mode: str                       # "owner" | "customer"
business_id: int                # Tenant ID
session_id: str                 # Session identifier
intent: str                     # Classified intent label
last_product_name: str          # Last product touched (disambiguation)
awaiting_product_selection: bool  # Disambiguation in progress?
pending_candidates: list        # Candidate products for disambiguation
pending_stock: int              # Stock value pending disambiguation
archived_message_count: int     # Count of archived messages
agent_result: dict              # Final result (success, message)
```

**Nodes:**

| Node | Function | Responsibility |
|------|----------|----------------|
| `intent_classifier` | `intent_classifier(state)` | Calls LLM to classify intent; falls back to regex on failure |
| `customer_agent_node` | `customer_agent_node(state)` | Delegates to `handle_customer_request()` |
| `product_agent_node` | `product_agent_node(state)` | Delegates to `handle_product_request()` |
| `fallback_node` | `fallback_node(state)` | Returns "Unsupported command" |
| `state_trimming_node` | `state_trimming_node(state)` | Archives old messages, trims state |

**`build_orchestrator_graph(checkpointer)`** — Constructs and compiles the `StateGraph`:
```
START → intent_classifier → [conditional] → customer/product/fallback → state_trimming_node → END
```

**`route_message(message, business_id, session_id, thread_id, graph)`** — Entry point called by the chat route. Builds a minimal `AgentState` with only the new message, then calls `graph.ainvoke()` with the `thread_id` config so LangGraph merges it with the persisted checkpoint.

---

## 4.7 `app/agents/customer_agent.py`

**Purpose:** Handles customer-related requests using LLM tool calling.

**Function:** `handle_customer_request(message, business_id)`
1. Calls `llm_customer_intent(message, business_id)` — LLM decides tool + parameters
2. If tool is `create_customer`: validates phone (10 digits, numeric), builds `CustomerCreate` schema, calls `create_customer()` tool
3. Returns `{success, message}` dict

**Key validation:** Phone must be exactly 10 digits. This is an explicit business rule for Indian phone numbers.

---

## 4.8 `app/agents/product_agent.py`

**Purpose:** Handles product creation, stock updates, and disambiguation.

**Function:** `handle_product_request(message, business_id, state)`

**Two execution paths:**

**Path 1 — Disambiguation (state.awaiting_product_selection is True):**
- Extracts numeric input (`^\s*(\d+)\s*$`)
- Validates against `pending_candidates` list
- Calls `update_product()` with the selected candidate
- Clears disambiguation state

**Path 2 — Normal flow:**
- Calls `llm_product_intent()` → intent is `create_product` or `update_stock`
- `create_product`: validates all required fields, converts types, builds `ProductCreate`, calls `create_product()` tool
- `update_stock`: calls `find_product_candidates()` for fuzzy search; if 1 match → direct update; if multiple matches → sets `awaiting_product_selection=True`, returns disambiguation prompt; if 0 matches → error

---

## 4.9 `app/services/llm_tools.py`

**Purpose:** LLM tool-calling wrappers. The LLM is given tool schemas and decides which tool to call and with what arguments.

**`llm_customer_intent(message, business_id) → dict`:**
- Binds `create_customer` tool schema to the LLM
- Sends system prompt + user message
- Parses `response.tool_calls[0]` to extract tool name and arguments
- Returns `{tool, parameters, confidence}`

**`llm_product_intent(message, business_id) → dict`:**
- Binds `create_product` and `update_stock` tool schemas
- Same pattern as above
- Returns tool name + extracted parameters

**Why tool calling instead of simple prompting:** Tool calling with schemas forces the LLM to return structured JSON that matches the expected parameter shapes. Plain prompting with "extract the parameters" produces inconsistent formats.

---

## 4.10 `app/services/product_matcher.py`

**Purpose:** Fuzzy product search using SQL `ILIKE`.

**Function:** `find_product_candidates(business_id, search_term)`
- Queries `products` table with `Product.name.ilike(f"%{search_term}%")`
- Returns all matching products for the given business

**Why ILIKE:** Case-insensitive partial match. "surf" matches "Surf Excel 1kg", "Surf Excel Matic", "Surf Excel 500g".

---

## 4.11 `app/services/message_archival.py`

**Purpose:** Keeps LangGraph checkpoint state bounded by archiving old messages to the `message_archives` table.

**Configuration:**
- `ACTIVE_MESSAGE_LIMIT = 20` — keep last 20 messages in active state
- `ARCHIVE_MESSAGE_BATCH_SIZE = 10` — archive in batches of 10

**`archive_old_messages(business_id, session_id, thread_id, messages, archived_message_count)`:**
- If `len(messages) <= 20`: no-op, return unchanged
- Otherwise: slice off oldest messages, batch-insert to `message_archives`, return trimmed list + updated count

**Failure handling:** Archival errors are caught and logged but do not fail the request. Archival is a "best effort" operation — missing archive records are recoverable, but blocking the user's request is not acceptable.

---

## 4.12 `app/services/langgraph_checkpointer.py`

**Purpose:** Creates and returns the `AsyncPostgresSaver` as an async context manager.

**`get_postgres_uri()`:** Converts SQLAlchemy's `postgresql+asyncpg://...` URL to `postgresql://...` which psycopg3 requires.

**`get_checkpointer_context_manager()`:** Returns `AsyncPostgresSaver.from_conn_string(postgres_uri)` — this is a synchronous call that returns a context manager object. The actual connection is established when you `async with` it.

---

## 4.13 `app/db/session.py`

**Purpose:** Creates the async SQLAlchemy engine and session factory.

- `engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)` — asyncpg-backed engine with connection health checks
- `AsyncSessionLocal = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)` — session factory

**`expire_on_commit=False`:** After a commit, the ORM objects stay accessible without triggering a lazy-load query. Critical for async code because lazy loading requires a synchronous operation.

**`pool_pre_ping=True`:** Before using a pooled connection, SQLAlchemy sends a quick `SELECT 1` to verify it's still alive. Prevents "connection reset" errors after PostgreSQL restarts.

---

## 4.14 `app/db/models/` — ORM Models

### `base.py`
```python
class Base(DeclarativeBase): pass
```
All models inherit from this. `DeclarativeBase` is the modern SQLAlchemy 2.x style.

### `business.py` — `Business`
Table: `businesses`
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| name | String(255) | |
| gstin | String(15) | GST Identification Number |
| state_code | String(2) | Indian state code (e.g. "KA") |
| whatsapp_number | String(20) | Nullable; for Phase 2 |
| created_at / updated_at | DateTime TZ | Auto-managed |

### `customer.py` — `Customer`
Table: `customers`
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| business_id | FK → businesses.id | Indexed; tenant isolation |
| name | String(255) | |
| phone | String(20) | |
| gstin | String(15) | Nullable |
| state | String(100) | Indian state name |
| address | Text | Nullable |
| created_at / updated_at | DateTime TZ | |

### `product.py` — `Product`
Table: `products`
| Column | Type | Notes |
|--------|------|-------|
| id | Integer PK | |
| business_id | FK → businesses.id | Indexed; tenant isolation |
| name | String(255) | |
| hsn | String(8) | HSN code for GST |
| sell_price | Numeric(12,2) | |
| cost | Numeric(12,2) | Nullable (margin calc) |
| gst_rate | Integer | 0–28 |
| stock | Integer | Current inventory |
| low_stock_threshold | Integer | Default 5 |
| unit | String(50) | Default "pcs" |
| created_at / updated_at | DateTime TZ | |

### `message_archive.py` — `MessageArchive`
Table: `message_archives`
Stores trimmed conversation history. Columns: `id`, `business_id`, `session_id`, `thread_id`, `role`, `content`, `created_at`, `archived_at`.

---

## 4.15 `app/schemas/`

### `customer.py` — `CustomerCreate`
Pydantic model for customer creation input validation. Fields: `business_id`, `name` (2–100 chars), `phone` (10–15 chars), `gstin` (optional), `state` (optional), `address` (optional).

### `product.py` — `ProductCreate`, `ProductUpdate`
- `ProductCreate`: all required fields with strict validation (`sell_price gt=0`, `gst_rate 0-28`, `stock ge=0`, etc.)
- `ProductUpdate`: all optional fields, same validation rules — used for partial updates with `model_dump(exclude_unset=True)`

---

## 4.16 `app/tools/customer_tools.py`

**`create_customer(customer_data: CustomerCreate) → dict`:**
1. Check for existing customer with same `(business_id, phone)` — returns early if duplicate
2. Create `Customer` ORM object, `session.add()`, `await session.commit()`, `await session.refresh()`
3. Returns `{success: True, customer_id, message}`

---

## 4.17 `app/tools/product_tools.py`

**`create_product(product_data: ProductCreate) → dict`:**
- Duplicate check: `func.lower(Product.name) == product_data.name.lower()` within same business
- Insert, commit, refresh, return result

**`update_product(business_id, product_name, product_data: ProductUpdate) → dict`:**
- Exact name match (case-insensitive) within business
- `model_dump(exclude_unset=True)` — only update fields that were explicitly set
- `setattr` loop to apply changes, commit, refresh

---

## 4.18 `frontend/src/App.jsx`

**Purpose:** The entire frontend UI in a single React component.

**State variables:**
- `message` — current text input value
- `messages` — chat history array `[{sender, text}]`
- `businessId` — selected business ID from dropdown
- `mode` — `"owner"` | `"customer"` (toggle)
- `businesses` — list fetched from `/businesses`

**`useEffect`:** On mount, fetches `/businesses` and populates dropdown.

**`handleSend()`:** Validates input, appends user message to chat, `POST /chat`, appends bot reply.

**Rendering:** Chat bubbles for user and bot messages, business selector dropdown, mode toggle, text input, send button.

---

# 5. Complete Request Lifecycle

**Example:** User types `"Add customer Rahul 9876543210"` and clicks Send.

## Step 1 — React captures input and sends request

File: `frontend/src/App.jsx`, function `handleSend()`

```
message state = "Add customer Rahul 9876543210"
businessId = "1"   (selected from dropdown)
mode = "owner"
```

React appends `{sender:"You", text:"Add customer Rahul 9876543210"}` to the `messages` array immediately (optimistic UI update), then fires:

```http
POST http://127.0.0.1:8000/chat
Content-Type: application/json

{
  "business_id": "1",
  "session_id": "test-session",
  "mode": "owner",
  "message": "Add customer Rahul 9876543210"
}
```

## Step 2 — FastAPI receives and validates

File: `app/routes/chat.py`, function `chat_endpoint()`

FastAPI deserializes the JSON body into `ChatRequest`. Pydantic validates:
- `business_id` is non-empty string, max 128 chars, not blank
- `session_id` same
- `mode` is Literal `"owner"` or `"customer"`
- `message` min 1, max 4000 chars, not blank

If any validation fails → FastAPI auto-returns HTTP 422 Unprocessable Entity.

On success, the route constructs:
```python
thread_id = "1:test-session"
graph = request.app.state.orchestrator_graph   # compiled at startup
```

## Step 3 — route_message() initializes state

File: `app/agents/orchestrator.py`, function `route_message()`

```python
agent_state = {
    "messages": [HumanMessage(content="Add customer Rahul 9876543210")],
    "mode": "owner",
    "business_id": 1,
    "session_id": "test-session",
}
```

Note: only the new message is injected. Prior conversation state (like `awaiting_product_selection`) will be loaded from PostgreSQL checkpoints.

## Step 4 — LangGraph loads checkpoint from PostgreSQL

`graph.ainvoke(agent_state, config={"configurable":{"thread_id":"1:test-session"}})`

LangGraph's `AsyncPostgresSaver` queries the `checkpoints` table for thread_id `"1:test-session"`. If a prior state exists, it is **merged** with the incoming `agent_state`. Fields in the incoming state take precedence for `messages`, but prior state wins for conversation fields like `awaiting_product_selection`, `pending_candidates`, etc.

On the **very first message**, no checkpoint exists, so the state is just what we provided.

## Step 5 — intent_classifier node

Function: `intent_classifier(state)` in `app/agents/orchestrator.py`

First checks: `if state.get("awaiting_product_selection")` → if True, short-circuits to `"product_selection"` intent. *(Not triggered here.)*

Then checks for pure numeric input regex → not matched here.

Then calls LLM:
```python
llm_customer_result = await llm_customer_intent("Add customer Rahul 9876543210", 1)
```

The LLM (Groq llama-3.3-70b) receives:
- System prompt: "You are a customer management assistant..."
- User message: "Add customer Rahul 9876543210"
- Tool schema: `create_customer(name, phone, state)`

LLM responds with a tool call: `{"name":"create_customer","args":{"name":"Rahul","phone":"9876543210","state":"Karnataka"}}`

`llm_customer_intent()` returns `{"tool":"create_customer","parameters":{...},"confidence":0.95}`

Since `confidence > 0.5`, state is updated: `state["intent"] = "create_customer"`

## Step 6 — intent_router selects the next node

Function: `intent_router(state)` in `app/agents/orchestrator.py`

```python
intent == "create_customer" → returns "customer_agent_node"
```

LangGraph's conditional edge routes execution to `customer_agent_node`.

## Step 7 — customer_agent_node runs

Function: `customer_agent_node(state)` in `app/agents/orchestrator.py`

Extracts `message` from last entry in `state["messages"]`, extracts `business_id=1`.

Calls:
```python
result = await handle_customer_request("Add customer Rahul 9876543210", 1)
```

## Step 8 — handle_customer_request processes with LLM

File: `app/agents/customer_agent.py`

Calls `llm_customer_intent()` again (the orchestrator already classified intent but the agent re-classifies independently — this is a redundancy in the current implementation).

LLM returns: `{"tool":"create_customer","parameters":{"name":"Rahul","phone":"9876543210","state":"Karnataka"},"confidence":0.95}`

Validates phone: `"9876543210".isdigit()` → True, `len == 10` → True.

Builds:
```python
CustomerCreate(
    business_id=1,
    name="Rahul",
    phone="9876543210",
    state="Karnataka"
)
```

Calls `await create_customer(customer)`.

## Step 9 — create_customer() hits the database

File: `app/tools/customer_tools.py`

```python
async with AsyncSessionLocal() as session:
    # Check duplicate: SELECT * FROM customers WHERE business_id=1 AND phone='9876543210'
    existing = result.scalar_one_or_none()  # None — new customer
    
    # INSERT INTO customers (business_id, name, phone, state) VALUES (1, 'Rahul', '9876543210', 'Karnataka')
    session.add(customer)
    await session.commit()
    await session.refresh(customer)   # reload to get generated id
```

Returns: `{"success": True, "customer_id": 42, "message": "Customer Rahul created successfully"}`

## Step 10 — State propagates back through graph

`customer_agent_node` sets `state["agent_result"] = {"success":True, "customer_id":42, "message":"Customer Rahul created successfully"}`

## Step 11 — state_trimming_node runs

File: `app/agents/orchestrator.py`, function `state_trimming_node()`

Checks `len(messages) <= 20` → True (only 1 message so far) → no archival needed.
Returns state unchanged.

## Step 12 — LangGraph saves checkpoint

`AsyncPostgresSaver` serializes the final `AgentState` and saves it to PostgreSQL checkpoint tables under `thread_id = "1:test-session"`.

## Step 13 — graph.ainvoke() returns

`result_state = await graph.ainvoke(...)` completes. `route_message()` extracts `result_state.get("agent_result")`.

Returns: `{"success": True, "customer_id": 42, "message": "Customer Rahul created successfully"}`

## Step 14 — FastAPI constructs ChatResponse

```python
reply_text = "Customer Rahul created successfully"
return ChatResponse(reply_text=reply_text, attachments=[])
```

HTTP 200 response:
```json
{"reply_text": "Customer Rahul created successfully", "attachments": []}
```

## Step 15 — React displays reply

`handleSend()` receives the response, calls `setMessages(prev => [...prev, {sender:"Bot", text:"Customer Rahul created successfully"}])`. The chat window shows the reply.

**Total execution order summary:**

```
1  React handleSend()
2  HTTP POST /chat
3  Pydantic ChatRequest validation
4  chat_endpoint() → route_message()
5  LangGraph loads PostgreSQL checkpoint
6  intent_classifier → llm_customer_intent() → Groq API call
7  intent_router → "customer_agent_node"
8  customer_agent_node → handle_customer_request()
9  handle_customer_request → llm_customer_intent() → Groq API call
10 Phone validation
11 CustomerCreate Pydantic schema
12 create_customer() → AsyncSessionLocal → duplicate check query
13 INSERT INTO customers
14 session.commit() + refresh()
15 agent_result set in state
16 state_trimming_node (no-op here)
17 LangGraph saves checkpoint to PostgreSQL
18 graph.ainvoke() returns
19 ChatResponse returned
20 React updates messages state
```

---

# 6. FastAPI Deep Dive

## 6.1 Why FastAPI (not Flask or Django)?

| Criterion | FastAPI | Flask | Django |
|-----------|---------|-------|--------|
| Async support | Native (asyncio) | Add-on (Quart) | Limited (ASGI add-on) |
| Request validation | Pydantic built-in | Manual | Django Forms / DRF Serializers |
| Auto API docs | Swagger + Redoc auto-generated | Manual | DRF browseable API |
| Type hints | First-class (used for validation) | Not used | Not used |
| Performance | High (Starlette + asyncio) | Moderate | Moderate |
| LangGraph compatibility | Full async support | Problematic | Problematic |
| Learning curve | Low-medium | Low | High |

**Primary reason FastAPI was chosen:** LangGraph uses asyncio throughout. `graph.ainvoke()`, `AsyncPostgresSaver`, and all database operations are `async`. Flask does not natively support async request handlers in the same process. FastAPI is built on Starlette (an ASGI framework), which means every request handler can be a Python coroutine — matching the async model perfectly.

## 6.2 Async Architecture

FastAPI runs under an ASGI server (Uvicorn with asyncio event loop). The event loop processes multiple requests concurrently:

```
Request A arrives:     await llm_call()     ← yields control
Request B arrives:  → handled concurrently
Request A resumes:  ← LLM returned
```

Without async: one LLM call (1–3 seconds) would block all other requests.
With async: while waiting for Groq's API response, the event loop handles other requests.

**Important Windows-specific detail** (in `app/main.py`):
```python
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
```
psycopg3 (used by `AsyncPostgresSaver`) does not support Windows's default `ProactorEventLoop`. This line switches to `SelectorEventLoop` before any async operations begin.

## 6.3 Routing

Routes are registered in separate files using `APIRouter`:

```python
# app/routes/chat.py
router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(...): ...
```

In `app/main.py`:
```python
app.include_router(chat_router)
app.include_router(business_router)
```

This keeps each domain's endpoints isolated. Adding a new domain (e.g. invoices) means creating `app/routes/invoices.py` and one `include_router()` call.

## 6.4 Dependency Injection

FastAPI uses function parameter injection. In `chat_endpoint(request: Request, payload: ChatRequest)`:
- `payload: ChatRequest` — FastAPI automatically parses the JSON body and validates it against `ChatRequest`
- `request: Request` — FastAPI injects the raw Starlette request object, used here to access `request.app.state`

For database sessions, the standard pattern (used in `business.py`) is:
```python
async with AsyncSessionLocal() as session:
    ...
```

A more formal DI pattern would use `Depends()`:
```python
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get(...)
async def endpoint(db: AsyncSession = Depends(get_db)):
    ...
```

The current code uses the direct `async with` pattern for simplicity, which is equivalent but less reusable.

## 6.5 Middleware

**CORS Middleware** (in `app/main.py`):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- **Why CORS?** Browsers block cross-origin requests by default. Vite serves the frontend on `:5173`, FastAPI on `:8000`. Without CORS middleware, the browser would refuse the `POST /chat` request.
- `allow_origins=["http://localhost:5173"]` — explicitly whitelist the frontend origin. Using `"*"` would be insecure for a production system with credentials.

## 6.6 Request Validation

**Double-layer validation:**

Layer 1 — Pydantic on request body (`ChatRequest`):
```python
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
```

Layer 2 — Business logic validation (in agents):
- Phone number format validation in `customer_agent.py`
- GST rate range validation in `product_agent.py`
- Price negativity check in `product_agent.py`

## 6.7 Response Models

`response_model=ChatResponse` on the route decorator:
- FastAPI serializes the return value through `ChatResponse`
- Extra fields in the internal dict are stripped
- Ensures the API contract is enforced regardless of what `route_message()` returns

## 6.8 Exception Handling

Currently handled by:
1. Pydantic validation errors → FastAPI returns HTTP 422 automatically
2. `try/except` blocks in agents (LLM failure → regex fallback)
3. `try/except` in `message_archival.py` (archival failure → log and continue)

FastAPI also provides a global exception handler that catches unhandled exceptions and returns HTTP 500.

**Production gap:** There is no custom `@app.exception_handler` registered for business errors. All business failures are returned as HTTP 200 with `{"success": false, "message": "..."}` in the body rather than using HTTP 4xx status codes.

## 6.9 Lifespan — Startup and Shutdown

`app/main.py` uses the modern FastAPI `lifespan` context manager pattern:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with get_checkpointer_context_manager() as checkpointer:
        await checkpointer.setup()
        app.state.checkpointer = checkpointer
        app.state.orchestrator_graph = build_orchestrator_graph(checkpointer)
        yield   # ← app runs here
        # cleanup on shutdown
```

This replaces the deprecated `@app.on_event("startup")` pattern. The `yield` being inside the `async with` block is critical — the PostgreSQL connection stays open for the entire app lifetime.

---

# 7. React Architecture

## 7.1 Why React?

- **Component model**: the UI is a set of composable, stateful components
- **React 19**: latest version with improved concurrent rendering
- **Vite**: fast hot-module replacement during development, optimized production build
- **Familiarity**: ubiquitous in industry; easy to hand off

For this project, the frontend is intentionally minimal — the intelligence is in the backend. React is used here as a thin chat shell, not a complex SPA.

## 7.2 Structure

The entire frontend is a single component: `frontend/src/App.jsx`. This is a deliberate choice for Phase 1 — the spec says "zero UI friction". A single-file UI is easy to understand, deploy, and replace.

```
frontend/
├── src/
│   ├── App.jsx      # Single component: all state, effects, and rendering
│   ├── App.css      # Chat UI styles
│   ├── main.jsx     # ReactDOM.createRoot + <App />
│   └── index.css    # Body/global styles
├── index.html       # HTML shell with <div id="root">
├── vite.config.js   # Vite + @vitejs/plugin-react
└── package.json     # react 19, react-dom, vite
```

## 7.3 State

| State variable | Type | Purpose |
|----------------|------|---------|
| `message` | `string` | Current text in the input box |
| `messages` | `Array<{sender, text}>` | Chat history displayed in UI |
| `businessId` | `string` | Selected business ID (FK for all API calls) |
| `mode` | `"owner" \| "customer"` | Persona toggle |
| `businesses` | `Array<{id, name}>` | List for dropdown, fetched from API |

All state is managed with React's `useState` hook. There is no external state manager (Redux, Zustand) — the app is simple enough that local component state is sufficient.

## 7.4 API Communication

**On mount** (`useEffect` with `[]` dependency):
```javascript
const response = await fetch("http://127.0.0.1:8000/businesses");
const data = await response.json();
setBusinesses(data);
```

**On send** (`handleSend`):
```javascript
const response = await fetch("http://127.0.0.1:8000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ business_id: businessId, session_id: "test-session", mode, message })
});
const data = await response.json();
setMessages(prev => [...prev, { sender: "Bot", text: data.reply_text }]);
```

**Hardcoded session_id:** `"test-session"` is a placeholder. In production, this should be a unique session identifier (UUID) per browser session.

## 7.5 Rendering

The component renders:
1. A title bar
2. Controls area: business dropdown + mode toggle
3. Chat window: `messages.map()` → chat bubbles (different styles for "You" vs "Bot")
4. Input area: text field + Send button

## 7.6 Why Not a More Complex Frontend?

The project spec explicitly states: "Zero UI friction: if a feature needs a complex screen, it does not belong in v1." The frontend is a thin transport layer. Phase 2 replaces it with WhatsApp — the `/chat` endpoint and agents are identical.

---

# 8. LangGraph Deep Dive

## 8.1 Why LangGraph?

**The problem with a simple Python function:**
- A plain async function can route a single message
- But it cannot remember what happened in previous messages
- You would need to manually pass state, serialize/deserialize it, handle crashes, etc.
- Multi-step conversations (disambiguation: "which Surf Excel did you mean?") require state that persists across multiple HTTP requests

**What LangGraph provides:**
- A directed graph where each node is a Python function that processes state
- Automatic state persistence (checkpoints) to PostgreSQL via `AsyncPostgresSaver`
- Conditional routing (if intent=customer → customer_agent, else → product_agent)
- Crash recovery: on server restart, the next message loads the prior state from PostgreSQL
- A clean, visual mental model of the conversation flow

## 8.2 The Graph

Defined in `app/agents/orchestrator.py`, `build_orchestrator_graph()`:

```
START
  │
  ▼
intent_classifier   ← classifies intent using LLM
  │
  ▼ (conditional edge via intent_router)
  ├─ "customer_agent_node"   → handles customer creation
  ├─ "product_agent_node"    → handles product create/update/disambig
  └─ "fallback_node"         → returns "Unsupported command"
  │
  ▼
state_trimming_node   ← archives old messages
  │
  ▼
END
```

## 8.3 StateGraph and AgentState

`StateGraph(AgentState)` — the graph is typed to `AgentState`, a `TypedDict`. Every node receives the full state dict and returns an updated state dict. LangGraph merges returned state with the prior state (values you don't return are preserved).

`AgentState` fields serve different purposes:
- **Input fields** set per-request: `messages`, `mode`, `business_id`, `session_id`
- **Routing fields** set by classifier: `intent`
- **Conversation fields** persisted across requests: `awaiting_product_selection`, `pending_candidates`, `pending_stock`, `last_product_name`
- **Archival tracking**: `archived_message_count`
- **Output**: `agent_result`

## 8.4 Nodes

Each node is an `async def` function with signature `(state: AgentState) -> AgentState`. Nodes read from state, perform work, and return an updated state dict.

**Key design:** Nodes do not communicate directly. They only communicate through state. This makes nodes independently testable and replaceable.

## 8.5 Edges

**Regular edges:** `graph.add_edge("customer_agent_node", "state_trimming_node")` — always go to that node.

**Conditional edges:**
```python
graph.add_conditional_edges(
    "intent_classifier",
    intent_router,          # function that returns node name
    {
        "customer_agent_node": "customer_agent_node",
        "product_agent_node": "product_agent_node",
        "fallback_node": "fallback_node",
    }
)
```
`intent_router(state)` reads `state["intent"]` and returns the node name string. The dict maps those strings to actual node names.

## 8.6 Checkpointer and PostgreSQL Saver

`AsyncPostgresSaver` (from `langgraph.checkpoint.postgres.aio`) is LangGraph's built-in PostgreSQL persistence backend.

**How it works:**
1. Before a graph run, `AsyncPostgresSaver` loads the checkpoint for the given `thread_id`
2. The checkpoint contains the serialized `AgentState` from the last run
3. LangGraph merges the new input with the loaded state
4. After the run, `AsyncPostgresSaver` serializes the final `AgentState` and saves it

**Tables created by `checkpointer.setup()`:**
- `checkpoints` — one row per thread per checkpoint
- `checkpoint_blobs` — the actual serialized state blobs
- `checkpoint_writes` — write-ahead log for reliability

These tables are managed entirely by LangGraph. You never write to them directly.

## 8.7 Thread IDs

`thread_id = f"{business_id}:{session_id}"` (e.g. `"1:test-session"`)

The thread ID is the key that identifies a conversation. All state for a single conversation is stored under one thread ID. Different businesses or sessions get different thread IDs and therefore completely isolated state.

**Design implication:** If two users share the same `session_id` for the same `business_id`, they share state. This is a known limitation of the current `"test-session"` hardcoded session ID in the frontend.

## 8.8 Durable Memory and Crash Recovery

**Scenario:** Server crashes in the middle of a product disambiguation conversation.

Without LangGraph: the user's pending selection state is lost. The server has no idea the user was in the middle of picking "Surf Excel 1kg vs Surf Excel 500g". The conversation is broken.

With LangGraph + PostgreSQL checkpointer: the state `{awaiting_product_selection: True, pending_candidates: [...], pending_stock: 100}` is saved after every graph run. When the server restarts and the user sends "1", the `intent_classifier` checks `state.get("awaiting_product_selection")` → True → routes to `product_agent_node` → correctly handles the selection.

## 8.9 State Trimming

LangGraph stores the full `messages` list in the checkpoint on every run. If a conversation lasts 1000 turns, the checkpoint contains 1000 messages. This makes checkpoints large and slow.

`state_trimming_node` runs after every agent node. It calls `archive_old_messages()` which:
1. If `len(messages) > 20`: moves the oldest messages to `message_archives` table
2. Returns a trimmed list of the most recent 20 messages
3. The checkpoint then stores only 20 messages

This keeps checkpoint size O(1) instead of O(n) with conversation length.

## 8.10 Advantages Over a Simple Python Workflow

| Feature | Simple Python Function | LangGraph |
|---------|----------------------|-----------|
| State across requests | Manual: load/save JSON | Automatic: PostgreSQL checkpoint |
| Multi-step conversations | Custom code per case | Built-in: state persists |
| Crash recovery | Impossible without custom infra | Automatic: next request loads prior state |
| Conditional routing | if/elif chains | Declarative: `add_conditional_edges` |
| Visualization | None | Graph structure is inspectable |
| Testability | Test entire function | Test each node independently |

---

# 9. LLM Architecture

## 9.1 Why LLM?

The core problem is **natural language input**. A shopkeeper might say:
- "Add customer Ramesh 9876543210"
- "New customer: Priya, 8765432109"
- "I need to add a customer named Suresh (9988776655)"

All three mean the same thing. A regex cannot handle all variations. An LLM can understand all of them and extract the same structured output: `{name: "Ramesh", phone: "9876543210"}`.

## 9.2 The LLM Provider

**Provider:** Groq  
**Model:** `llama-3.3-70b-versatile` (configurable via `LLM_MODEL` env var)  
**API library:** `langchain-groq` (`ChatGroq`)  
**Temperature:** 0 — deterministic, no creativity

**Why Groq:** Extremely fast inference (Groq's LPU hardware). LLM calls are on the critical path of every request. Speed matters. Groq regularly achieves 500–800 tokens/second.

**Why Llama 3.3 70B:** Strong performance on instruction-following and tool calling. Open-weights model. Groq hosts it.

## 9.3 Where the LLM is Used

| Location | File | What LLM does |
|----------|------|---------------|
| Intent classification | `orchestrator.py` `intent_classifier` | Classifies message as `create_customer`, `update_product`, or `unknown` |
| Customer intent | `llm_tools.py` `llm_customer_intent()` | Extracts `{name, phone, state}` from natural language |
| Product intent | `llm_tools.py` `llm_product_intent()` | Extracts create/update parameters from natural language |

## 9.4 Where Deterministic Logic is Preferred

| Decision | Why LLM is NOT used |
|----------|---------------------|
| Numeric disambiguation (user types "1") | Pure regex: `re.match(r"^\s*\d+\s*$")` — there is no ambiguity |
| Phone number format validation | `phone.isdigit() and len(phone) == 10` — business rule, not language understanding |
| Duplicate customer check | SQL query — deterministic business rule |
| GST rate range validation | `0 <= gst_rate <= 28` — domain constraint |

**Rule:** Use LLM only where the problem is language understanding. Use deterministic code for everything where the rule is known and fixed.

## 9.5 Tool Calling (Function Calling)

LangChain's `bind_tools()` sends tool schemas to the LLM alongside the message. The LLM responds not with text but with a structured JSON "tool call":

```python
llm.bind_tools(tools).ainvoke([SystemMessage(...), HumanMessage(content="Add customer Rahul 9876543210")])

# LLM responds:
# tool_calls = [{"name": "create_customer", "args": {"name": "Rahul", "phone": "9876543210", "state": "Karnataka"}}]
```

This is more reliable than asking the LLM to format its response as JSON because:
- The LLM is explicitly trained to produce tool calls in the correct format
- LangChain parses `response.tool_calls` reliably
- Parameters are validated against the tool schema by the LLM itself

## 9.6 Prompt Design

**Customer intent system prompt** (`llm_tools.py`):
```
You are a customer management assistant.
Analyze the user's message to determine what action to take.
If the user wants to create a new customer, use the create_customer tool.
Extract the customer name and 10-digit phone number.
If state is not mentioned, use 'Karnataka'.
Only use the create_customer tool if the user explicitly wants to ADD or CREATE a customer.
Do not infer customer creation from ambiguous statements.
```

Key principles:
- **Role assignment**: "You are a customer management assistant" — narrows the LLM's focus
- **Explicit instructions**: "only use the tool if explicitly wants to ADD or CREATE" — prevents false positives
- **Default value**: "If state is not mentioned, use Karnataka" — reduces missing parameter issues

## 9.7 Fallback to Regex

In `intent_classifier`:
```python
try:
    customer_result = await llm_customer_intent(message, business_id)
    # ...
except Exception as e:
    print(f"LLM classification failed: {e}, using regex fallback")
    if "add customer" in message_lower:
        state["intent"] = "create_customer"
    # ...
```

If the Groq API is down or rate-limited, the system degrades gracefully to regex matching. The regex covers common explicit patterns. This is a defense-in-depth approach — the LLM handles natural variations, regex handles the fallback.

## 9.8 Hallucination Prevention

| Risk | Prevention |
|------|-----------|
| LLM invents a phone number | Post-LLM validation: `phone.isdigit() and len(phone) == 10` |
| LLM invents a product that doesn't exist | Database query confirms existence before update |
| LLM returns wrong tool format | `if hasattr(response, 'tool_calls') and response.tool_calls:` — explicit check |
| LLM returns wrong confidence | Hard confidence threshold: `confidence > 0.5` before routing |

The LLM is never trusted for database mutations without validation. Its output is always validated before being used.

---
