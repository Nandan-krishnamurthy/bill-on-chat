# Project Beta - Phased Project Specification (Clean)

Project codename: Project Beta (Bill-on-Chat)
Owner: Sharath
Engineer: Graduate Hire

Phase 1 stack: Web Chat UI + FastAPI + LangGraph + PostgreSQL + pluggable LLM
Phase 2 stack: adds WhatsApp transport via OpenClaw

Estimated build time:
- Phase 1: 6 weeks
- Phase 2: 3 weeks (full-time)

## 0. Why Two Phases

The original spec couples two very different kinds of work: the product (agent reasoning, GST correctness, the data model, PDF generation) and the transport (WhatsApp delivery through OpenClaw, webhooks, media handling, message idempotency). The transport is plumbing. The product is the hard, valuable part.

Splitting the build means we ship and validate the entire billing brain against a simple web chat UI first, with zero transport friction and fast iteration. WhatsApp then becomes a thin adapter layer bolted onto an already-working system. The /chat endpoint and every agent stay byte-for-byte identical between the two phases.

DESIGN PRINCIPLE:
Agents never know which transport they are serving. The frontend (web or WhatsApp) posts { business_id, message } to /chat and receives { reply_text, attachments }. Keeping the transport behind that boundary is what makes Phase 2 cheap.

### Phase Comparison

| Dimension | Phase 1 | Phase 2 |
| --- | --- | --- |
| Interface | Browser chat UI | WhatsApp via OpenClaw |
| Goal | Full billing brain + both modes | Swap transport, add channel features |
| Duration | 6 weeks | 3 weeks |
| Owner/Customer mode | Persona toggle in UI | Inferred from who is messaging |
| PDF delivery | Download link / inline preview | WhatsApp media attachment |
| Tenant key | business_id chosen in UI | whatsapp_number maps to business + mode |
| Voice input | Out of scope | Whisper transcription |
| GST e-invoice / e-way bill | Optional (stretch) | Full GSP sandbox integration |

## 1. What You Are Building

A GST billing platform for small Indian retailers and SMEs where the user just chats and AI agents do the work behind the scenes: creating customers, generating invoices, recording payments, producing GST returns and reports.

In Phase 1 the chat lives in a web page. In Phase 2 the exact same chat lives inside WhatsApp.

### The Experience We Are Aiming For

Shopkeeper: "Bill Ramesh 2 packs of Surf Excel at 250 each"

Bot:
- Done. Invoice INV-0042 created.
- Subtotal: Rs 500
- GST (18%): Rs 90
- Total: Rs 590
- [PDF attached]
- Want to send it to Ramesh?

Shopkeeper: "Yes"

Bot:
- Sent to Ramesh on +91 98765 43210.
- E-Way Bill not required (under Rs 50,000).

### Core Principles

- Zero UI friction: if a feature needs a complex screen, it does not belong in v1.
- Agents over workflows: let the LLM reason about intent; do not hardcode menus.
- Conversational state: remember what was just said, infer what they probably mean.
- Indian-first: GST compliance, INR, mixed Hindi/Kannada/Tamil + English input.
- Transport-agnostic: the agent layer is identical whether the user is on the web or on WhatsApp.

## 2. Two Operating Modes

The same agents and the same data serve two completely different audiences, and the agent's job changes depending on who it is talking to. This is the central concept of Project Beta.

There are two personas: Owner Mode and Customer Mode.

### Owner Mode

The agent is the shopkeeper's back-office assistant. It helps the owner run the business: check stock, see who owes money, record payments, create invoices, send reminders, and pull sales and GST reports. Full trust, full access.

### Customer Mode

The agent is a salesperson acting on the owner's behalf, talking to the owner's end customers. Its job is to sell: answer product questions, quote prices, check availability, and capture an order as a draft. It is not running the business and must never expose owner-only information.

### Side-by-Side

| Dimension | Owner Mode | Customer Mode |
| --- | --- | --- |
| Who is talking | The registered business owner | An end customer of that business |
| Goal of the agent | Help run the business | Sell products on the owner's behalf |
| Tone | Efficient assistant / ops co-pilot | Friendly, helpful salesperson |
| Can create invoices | Yes (with confirmation) | No (draft order only) |
| Can record payments | Yes | No (orders only; payments out of scope) |
| See all customers' dues | Yes | No (never) |
| See sales / GST reports | Yes | No (never) |
| Stock visibility | Exact quantities + low-stock alerts | Availability only, no internal counts |
| Pricing visibility | Cost, margin, everything | Sell price only |
| Scope of data | Whole business | One customer + sellable catalogue |

### 2.1 How the mode is decided

In production, the mode is inferred from identity, never chosen by the user.

- Owner Mode: the message arrives from the owner's registered number (Phase 2) or owner session (Phase 1).
- Customer Mode: the message arrives via a per-business customer entry point (shareable link or a dedicated customer-facing number). The business is resolved from that entry point, and every customer-mode conversation is scoped to a single customer.

PHASE 1 PERSONA TOGGLE (testing only):
The Phase 1 web chat includes a visible Owner / Customer toggle so you can switch personas instantly while testing. This toggle is a development affordance only. In the final product, mode is determined by identity and there is no user-facing switch.

### 2.2 The permission boundary (non-negotiable)

Customer Mode is a hard security boundary, not just a different prompt. A customer must never be able to reach owner data, even by asking cleverly.

- Mode is resolved server-side before the orchestrator runs.
- Active mode selects which tools are bound to the agent.
- Customer mode does not have owner tools available to call.
- Every customer-mode tool is scoped to a single customer_id and business_id.
- Customer mode cannot list other customers, dues, totals, or reports because those tools are not in its toolset.
- Stock and pricing are filtered: sell price only; never internal counts, cost, or margin.
- No prompt-only enforcement: guarantee comes from tool availability and query scoping at the data layer.

### 2.3 Customer-mode order flow (no self-checkout)

A customer can express buying intent, but cannot finalize anything. The owner is always in the loop before an invoice becomes real.

1. Customer chats with the agent, asks about products, gets prices and availability.
2. Agent creates a draft order (a pending quote tied to that customer), confirms items and total back to the customer, and says the shop will confirm.
3. The owner is notified of the pending draft order (in Owner Mode).
4. The owner confirms, edits, or rejects. On confirmation the draft becomes a real invoice through the normal Invoice Agent path, with GST calculation and PDF.
5. Payment is out of scope for customer mode; the order records what the customer wants to buy.

Example:

Customer: "Do you have Surf Excel 1kg? How much?"

Agent:
- Yes, Surf Excel 1kg is available at Rs 250.
- How many would you like?

Customer: "2 please"

Agent:
- Got it. Draft order: 2 x Surf Excel 1kg = Rs 500 (before GST).
- I've sent this to the shop to confirm.
- They'll be in touch shortly.

Owner: "Confirm Ramesh's order"

Agent:
- Done. Invoice INV-0043 created for Ramesh,
- 2 x Surf Excel, total Rs 590 (incl. 18% GST). [PDF]

## 3. Architecture Overview

One backend, one agent layer, two interchangeable transports. The only thing that differs between phases is the transport layer.

### Phase 1 architecture

- Web Chat UI (React or plain HTML)
	- text in / text out
	- renders PDF invoices as inline preview + download
	- business selector + Owner/Customer persona toggle
- POST /chat { business_id, mode, message }
- FastAPI backend (Python, async)
	- Mode resolver (server-side: Owner | Customer)
	- LangGraph orchestrator (binds tools for active mode)
		- OWNER: Customer | Product | Invoice | Payment | Report
		- CUSTOMER: Sales Agent only (scoped, read-filtered)
	- Tools layer (plain Python)
		- DB CRUD (SQLAlchemy)
		- PDF (reportlab)
		- GST calculation
	- LLM provider factory (Claude / OpenAI / Groq / ...)
- PostgreSQL

### Phase 2 architecture

- WhatsApp user
- OpenClaw (small VPS or laptop)
	- receives WhatsApp messages
	- POSTs to the same /chat endpoint
	- sends replies + PDF attachments back to WhatsApp
- Same FastAPI + agents + PostgreSQL stack below transport layer

### Why each piece

- FastAPI: business logic API, async, fast, easy to test.
- LangGraph: agent orchestration with shared memory, retries, and human-in-the-loop checkpoints.
- LLM provider factory: one seam for free dev models and production provider swap via config.
- PostgreSQL: source of truth for customers, products, invoices, payments.
- OpenClaw (Phase 2): WhatsApp transport; do not reinvent that wheel.

## 4. LLM Provider Abstraction

Agents must never call a vendor SDK directly. All model construction goes through one factory so you can develop on free models and flip to Claude or OpenAI for production by changing one environment variable.

### Recommended free / low-cost models for development

| Provider | Model | Free tier | Notes |
| --- | --- | --- | --- |
| Groq | Llama 3.3 70B / 3.1 8B | Generous free rate limits | Best default for dev; very fast, good tool-calling |
| Google | Gemini 2.0 Flash | Free via AI Studio key | Solid quality, large context |
| Cerebras | Llama 3.3 70B | Free tier | Extremely fast inference |
| OpenRouter | Models with :free suffix | Free routing | One key, many models to test against |
| Ollama | Llama / Qwen / Mistral | Fully local, no key | Offline dev, zero cost, privacy |

RECOMMENDATION:
Develop on Groq Llama 3.3 70B (free, fast, reliable tool-calling). Switch to Claude (Sonnet) for production where GST extraction accuracy matters.

### Factory example

app/llm.py

```python
from langchain.chat_models import init_chat_model
from app.config import settings

def get_llm(temperature: float = 0):
		# settings.LLM_MODEL examples:
		# "anthropic:claude-sonnet-4-5"
		# "openai:gpt-4o"
		# "groq:llama-3.3-70b-versatile"
		# "google_genai:gemini-2.0-flash"
		# "ollama:llama3.1"
		return init_chat_model(settings.LLM_MODEL, temperature=temperature)
```

app/config.py (pydantic-settings)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
		LLM_MODEL: str = "groq:llama-3.3-70b-versatile"  # dev default
		ANTHROPIC_API_KEY: str | None = None
		OPENAI_API_KEY: str | None = None
		GROQ_API_KEY: str | None = None
		GOOGLE_API_KEY: str | None = None

		model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```

Switching provider is one line in .env:

```env
LLM_MODEL=anthropic:claude-sonnet-4-5
```

Each agent calls get_llm().bind_tools([...]). No agent code changes when providers change.

Install:

```bash
pip install "langchain[anthropic,openai,groq,google-genai]" langgraph
```

GST SAFETY CAVEAT:
Tool-calling reliability varies by model. The LLM must never compute tax itself. It extracts items/quantities and calls deterministic gst_calculator.py. Validate every extracted field with Pydantic.

## 5. The Feature Set (v1 Scope)

Features are tagged by mode. Owner features run the business; Customer features sell on the owner's behalf. In Phase 1 this runs through web chat; in Phase 2 only the channel changes.

| # | Feature | Example phrase | Mode | Phase |
| --- | --- | --- | --- | --- |
| 1 | Customer creation and lookup | "Add customer Ramesh, 9876543210" | Owner | 1 |
| 2 | Product / inventory management | "Add Surf Excel 1kg, Rs 250, GST 18%, 50 in stock" | Owner | 1 |
| 3 | Stock and inventory queries | "What's low on stock?" | Owner | 1 |
| 4 | Outstanding dues / who owes me | "Who still has to pay me?" | Owner | 1 |
| 5 | Invoice creation | "Bill Ramesh 2 Surf Excel" | Owner | 1 |
| 6 | Payment recording | "Ramesh paid Rs 590 today" | Owner | 1 |
| 7 | Payment reminders | "Remind customers with dues over 30 days" | Owner | 1 |
| 8 | Sales and GST reports | "How much did I sell this week?" | Owner | 1 |
| 9 | Product enquiry and price quote | "Do you have Surf Excel? How much?" | Customer | 1 |
| 10 | Availability check | "Is it in stock?" | Customer | 1 |
| 11 | Place a draft order | "I'll take 2 packs" | Customer | 1 |
| 12 | Confirm draft-order into invoice | "Confirm Ramesh's order" | Owner | 1 |
| 13 | E-Invoice generation | "Generate e-invoice for INV-42" | Owner | 2 |
| 14 | E-Way Bill generation | "E-way bill for INV-42, transporter ABC" | Owner | 2 |

NOTE:
Customer-mode features (9-11) never create invoices or touch payments. They produce a draft order that the owner confirms (feature 12). E-Invoice and E-Way Bill (13-14) require a GST Suvidha Provider and sit in Phase 2, but can be pulled forward as stretch because they are transport-independent tool calls.

## 6. The Agents

Every agent has the same shape:
- input = user message + conversation state + DB context
- output = tool call(s) + response message

The orchestrator is mode-aware: active mode (Owner/Customer) decides which agents/tools are reachable.

### 6.1 Orchestrator Agent (mode-aware router)

- Receives active mode (resolved server-side before the LLM runs) and message.
- Binds only tools permitted for that mode.
- Classifies intent and routes to specialist.
- In Customer Mode, only Sales Agent and customer-scoped read-only tools are reachable.
- Owner agents are not bound in Customer Mode.
- Asks clarifying question when intent is unclear (including ambiguous owner read intent).

### 6.2 Customer Agent (Owner Mode)

- Add/update customer
- Fuzzy lookup by partial name
- List customers with outstanding dues

### 6.3 Product Agent (Owner Mode)

- Add/update product (name, HSN, price, GST rate, stock)
- Stock updates
- Low-stock alerts
- Inventory queries

### 6.4 Invoice Agent (Owner Mode)

- Create invoice
- Quote/draft-order to invoice conversion
- Discounts
- Correct GST: CGST+SGST (intra-state), IGST (inter-state)
- Generate PDF
- In Phase 2, trigger E-Invoice / E-Way Bill when conditions are met
- Confirm customer-mode draft orders into real invoices when owner approves

### 6.5 Payment Agent (Owner Mode)

- Record full/partial payments
- Auto-update invoice status
- Outstanding dues
- Scheduled reminders

### 6.6 Report Agent (Owner Mode)

- Sales by day/week/month
- GSTR-1 and GSTR-3B summaries
- Top customers and top products

### 6.7 Sales Agent (Customer Mode)

- Only agent reachable in Customer Mode
- Acts as salesperson on owner's behalf
- Answers product questions
- Quotes sell price
- Checks availability (in stock / not)
- Never reveals internal quantities, cost, or margin
- Creates draft order scoped to single customer
- Notifies owner for confirmation
- Cannot create invoices, record payments, see other customers, dues, or reports

TOOLSET BY MODE:
- Owner Mode: Customer, Product, Invoice, Payment, Report agents + read/write tools.
- Customer Mode: Sales Agent only + read-only catalogue lookups (availability + sell price) + create_draft_order scoped to one customer.
- Boundary is enforced by bound tools, not prompt wording.

## 7. Read & Query Operations

The write-heavy flow needs explicit retrieval tools. Most read tools are in Owner Mode. Customer Mode gets only two filtered catalogue reads.

### 7.1 Owner-mode read tools

| Tool | Answers | Owning agent |
| --- | --- | --- |
| get_inventory(filter) | "What do I have / what's low?" | Product |
| get_product(name) | "How many Surf Excel left?" | Product |
| get_outstanding_dues() | "Who still has to pay me?" | Payment / Report |
| get_customer_balance(name) | "What does Ramesh owe?" | Payment |
| list_customers(filter) | "Show my customers" | Customer |
| get_invoice(number_or_customer) | "Show INV-42 / Ramesh's last bill" | Invoice |
| get_sales_summary(period) | "Sales this week?" | Report |
| get_gst_summary(period) | "GSTR-1 for April" | Report |
| get_top(customers|products) | "My top 5 customers" | Report |

CROSS-TABLE QUERIES:
Queries like dues join customers, invoices, and payments. Put composite reads in Report/Payment as dedicated query functions (not LLM-assembled SQL), so results remain correct and fast.

### 7.2 Customer-mode read tools (filtered)

- check_availability(product_name): available / not available only, never count.
- get_sell_price(product_name): sell price only, never cost or margin.

This is the full customer-mode read surface. Anything else (dues, other customers, reports, exact stock) is unreachable because the tool does not exist in that mode.

## 8. Data Model (PostgreSQL)

Nine tables, SQLAlchemy 2.0 async. Every row carries business_id for multi-tenancy. Model is identical across both phases; only business_id/mode resolution changes by transport.

| Table | Purpose |
| --- | --- |
| businesses | Tenant root: name, GSTIN, state_code, whatsapp_number (nullable in Phase 1) |
| customers | Per-business customers: name, phone, GSTIN, state, address |
| products | Per-business catalogue: name, HSN, sell price, cost, GST rate, stock, unit |
| draft_orders | Customer-mode pending orders: customer, items, status (pending/confirmed/rejected) |
| invoices | Header: number, customer, totals, CGST/SGST/IGST, status, IRN, e-way bill, pdf_url |
| invoice_items | Line items: product, qty, unit price, GST rate, line total |
| payments | Payments against invoices: amount, date, method, reference |
| conversations | Per-tenant chat state + active mode (LangGraph snapshot, JSONB) |
| message_log | Inbound / outbound message history |

PHASE 1 SCHEMA NOTE:
- businesses.whatsapp_number is nullable in Phase 1 (no WhatsApp yet).
- Conversation key is business_id + web session id.
- In Phase 2, backfill/set WhatsApp number and add number-to-business lookup.
- No destructive migration required.

## 9. Phase 1 Build (Week by Week)

Each week ends with something demoable in web chat. Do not skip steps.

### Week 1 - Foundations & Hello World in browser

Goal: type a message in a web page and get a reply from FastAPI.

6. Set up FastAPI + virtualenv; install fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, pydantic-settings, langgraph, langchain, reportlab, httpx.
7. Install LLM extras (langchain[groq] for dev; add anthropic/openai when needed).
8. Build /chat accepting { business_id, mode, message } and returning { reply_text, attachments }.
9. Build minimal web chat UI (React or plain HTML + fetch): message list, input, file/PDF preview, Owner/Customer persona toggle.
10. Add server-side mode resolution: /chat accepts active mode; toggle sets mode in Phase 1, identity sets mode in Phase 2.
11. Get free Groq key and wire LLM factory; echo intent initially.

WEEK 1 CHECKPOINT

### Week 2 - Database & first real agent (Customer)

Goal: "Add customer Ramesh, 9876543210" creates a row in Postgres.

12. Spin up Postgres with Docker; write SQLAlchemy models from Section 8; set up Alembic migrations.
13. Build Customer Agent starting with create_customer(...).
14. Wire into LangGraph as one node; model decides whether/with what args to call tool; return friendly confirmation.
15. Add business selector in UI (pick existing or create new business) so business_id flows with every message.

WEEK 2 CHECKPOINT
Customers can be created entirely from web chat.

### Week 3 - Product Agent + conversational memory

Goal: products work, and bot remembers context across turns.

16. Build Product Agent similarly to Customer Agent.
17. Ensure multi-turn slot filling works (price? GST rate? stock?).
18. Add fuzzy lookup with ILIKE '%name%'; if multiple matches, ask user to disambiguate.

WEEK 3 CHECKPOINT
A multi-turn conversation feels like talking to a real assistant.

### Week 4 - Invoice Agent

Goal: generate real GST-compliant invoice PDF and show it in chat.

19. Build invoice tools: lookup_customer, lookup_product, calculate_gst, create_invoice, generate_invoice_pdf.
20. Implement deterministic GST logic: same state -> CGST + SGST (half each); different state -> IGST (full); round each line to 2 dp. Add pure unit tests for intra-state, inter-state, multiple slabs, exempt items, rounding.
21. Generate clean PDF with reportlab (business header, customer block, items table, GST breakdown, total in words).
22. Serve PDF over URL and render inline in web chat + download link (Phase 1 stand-in for WhatsApp attachment).

WEEK 4 CHECKPOINT
A real invoice PDF flows out of web chat.

### Week 5 - Payments, reminders, reports & query tools

Goal: close billing loop and make business queryable.

23. Payment Agent: full/partial payments; auto-update invoice status when paid >= total.
24. Scheduled reminders with APScheduler (for example daily 10:00 IST) for overdue unpaid invoices; in Phase 1 surface in chat/reminders view.
25. Report Agent: sales summary, GSTR-1 summary (taxable value, CGST, SGST, IGST), top customers.
26. Build owner-mode read tools from Section 7 (get_inventory, get_outstanding_dues, get_customer_balance, list_customers, get_invoice, get_sales_summary, get_gst_summary, get_top).
27. Confirmation gates before irreversible actions; Pydantic validation on every tool input; trim active conversation state to last ~10 turns and log the rest.

WEEK 5 CHECKPOINT
Full owner-mode billing cycle and day-to-day queries work in browser.

### Week 6 - Customer Mode & Sales Agent

Goal: agent can sell on owner's behalf with hard permission boundary.

28. Implement mode-aware tool binding in orchestrator: Owner Mode binds owner agents; Customer Mode binds only Sales Agent. Resolve mode server-side before LLM runs.
29. Build Sales Agent with filtered read tools (check_availability, get_sell_price) and create_draft_order scoped to one customer.
30. Add draft_orders table and flow.
31. Write boundary tests: customer mode cannot reach dues, other customers, reports, or exact stock, even with adversarial prompts.
32. Wire Phase 1 persona toggle end-to-end for side-by-side owner and customer demos.

PHASE 1 CHECKPOINT
Both modes work end-to-end in browser: owner runs business, customer is sold to and places draft order that owner confirms, with no transport dependency.

## 10. Phase 2 Build - WhatsApp Integration

Swap web frontend for WhatsApp. /chat endpoint and all agents stay unchanged. Web UI survives as dev/debug harness and fallback channel.

### Week 7 - OpenClaw transport & tenant mapping

33. Install OpenClaw on laptop or small droplet and connect to WhatsApp via integration guide.
34. Write custom OpenClaw skill that POSTs every WhatsApp message to existing /chat and posts reply back.
35. Map whatsapp_number -> business_id + mode: owner number resolves to Owner Mode; shared customer entry resolves to Customer Mode scoped to that caller. First-time owner numbers trigger onboarding: business name, GSTIN, state.
36. Idempotency: dedupe repeated deliveries using client_message_id; every tool call must be idempotent.

WEEK 7 CHECKPOINT
WhatsApp message reaches full agent stack in correct mode.

### Week 8 - Media, voice & GST compliance

37. Send PDF invoices as WhatsApp media attachments via OpenClaw callback.
38. Voice notes: transcribe incoming audio with Whisper and feed text to orchestrator.
39. Sign up for GSP sandbox (for example Masters India / ClearTax). Implement E-Invoice (IRN + signed QR, embed in PDF) and E-Way Bill (value > Rs 50,000 with goods movement).

WEEK 8 CHECKPOINT
Invoices are delivered on WhatsApp and are legally GST-compliant.

### Week 9 - Polish & edge cases

40. Mixed-language handling: verify prompts allow Hindi/Kannada/Tamil + English.
41. Robust error handling: GST API down, hallucinated customer, retries and fallbacks.
42. Confirmation gates on WhatsApp before money actions; final end-to-end test of full Definition of Done.

PHASE 2 CHECKPOINT
A shopkeeper completes the entire workflow using only WhatsApp.

## 11. Suggested Folder Structure

```text
bill-on-chat/
	app/
		main.py              # FastAPI entrypoint
		config.py            # Settings (env vars, API keys, LLM_MODEL)
		llm.py               # LLM provider factory (the switch seam)
		db/
			models.py          # SQLAlchemy models
			session.py
			migrations/        # Alembic
		agents/
			orchestrator.py    # LangGraph entry, mode-aware tool binding
			customer_agent.py  # owner mode
			product_agent.py   # owner mode
			invoice_agent.py   # owner mode
			payment_agent.py   # owner mode
			report_agent.py    # owner mode
			sales_agent.py     # customer mode (sell on owner's behalf)
		auth/
			mode.py            # resolves Owner vs Customer mode server-side
		tools/
			customer_tools.py
			product_tools.py
			invoice_tools.py
			payment_tools.py
			query_tools.py     # owner-mode reads (dues, inventory, balances)
			sales_tools.py     # customer-mode: availability, sell price, draft order
			pdf_generator.py
			gst_api.py         # E-Invoice + E-Way Bill (Phase 2)
			transport.py       # reply/attachment adapter (web | whatsapp)
		routes/
			chat.py            # /chat endpoint (shared by both phases)
		services/
			gst_calculator.py  # deterministic, unit-tested
	web/                   # Phase 1 chat UI (React or static HTML)
	openclaw-skills/
		billing/             # Phase 2 custom OpenClaw skill
	tests/
		test_gst_calculation.py
		test_agents.py
		test_mode_boundary.py  # customer mode cannot reach owner data
		test_e2e.py
	docker-compose.yml     # Postgres + FastAPI
	pyproject.toml
	README.md
```

## 12. Key Things to Get Right

43. Transport seam.
Keep all channel-specific code in transport.py. Agents only return text + attachment references.

44. Idempotency.
Messages can arrive twice (especially on WhatsApp). Dedupe with client_message_id; keep tool calls idempotent.

45. Mode is a security boundary.
Resolve Owner vs Customer mode server-side before LLM runs, bind only that mode's tools. Customer mode must be unable to reach dues, other customers, reports, or exact stock because tools are absent, not because prompts say so. Test adversarially.

46. Tenant boundary.
State is keyed per business. In Phase 2, WhatsApp number -> business + mode mapping is the boundary.

47. Validate tool inputs.
LLM will try invalid inputs. Validate every input with Pydantic before touching DB.

48. Confirmations for money actions.
Require explicit confirmation before irreversible actions, including creating invoices, recording payments, or sending reminders.

49. GST math is unforgiving.
Pure unit tests for gst_calculator.py are mandatory: intra-state, inter-state, multiple slabs, rounding, exempt items. LLM never does arithmetic.

50. Secrets.
Never commit keys. Use .env with pydantic-settings.

51. Trim state.
LangGraph state grows; keep last ~10 turns active and log the rest.

## 13. Free / Cheap APIs and Tools

| Need | Service | Free tier / cost notes |
| --- | --- | --- |
| LLM (dev) | Groq (Llama 3.3 70B) | Free, generous rate limits |
| LLM (alt dev) | Google Gemini 2.0 Flash / Cerebras / Ollama | Free tiers / fully local |
| LLM (prod) | Anthropic Claude or OpenAI | Pay-as-you-go; switch via LLM_MODEL |
| Voice to text (Phase 2) | Groq (Whisper) | Free with rate limits |
| Postgres | Docker locally / Neon.tech | Neon: free tier |
| Hosting (dev) | Local laptop | Free |
| Hosting (prod) | Railway / Render | Low-cost starter tiers |
| WhatsApp transport (Phase 2) | OpenClaw (self-hosted) | Free, OSS |
| GST e-invoice sandbox (Phase 2) | Masters India / ClearTax | Free dev sandbox |

## 14. Definition of Done

### Phase 1 (web chat)

Owner Mode (using only web chat, persona = Owner):

- Create/select a business (name, GSTIN, state).
- Add 5 customers and 10 products.
- Create invoice with 3 line items and receive GST-compliant PDF in chat.
- Record a full and a partial payment.
- Get sales summary and GSTR-1 summary for the month.

Customer Mode (persona = Customer):

- Ask whether a product is available and what it costs (and see nothing else).
- Place a draft order, which owner sees and confirms into a real invoice.
- Not reach other customer data, dues, reports, or exact stock (verified by boundary tests).

### Phase 2 (WhatsApp)

Everything in Phase 1, plus, using only WhatsApp:

- Onboard new business from first-time WhatsApp owner number.
- Customer on shared entry point is automatically served in Customer Mode.
- Receive invoice PDF as WhatsApp attachment.
- Generate E-Invoice and receive IRN; generate E-Way Bill when required.
- Send payment reminder to customer on WhatsApp.
- Drive flow with voice note and mixed-language text.

SHIP TEST:

- Phase 1 done: full billing cycle works without WhatsApp.
- Phase 2 done: same cycle works without opening a browser.

## 15. Weekly Reporting Cadence

Every Friday, send:

Note: Source text is truncated in the provided raw extract after this line.

