# ConnectX Telecom - Customer Support Chatbot

A production-grade, multi-turn AI customer support chatbot built for ConnectX Telecom as specified in Practical Test 1.

---

## Quick Start

### 1. Prerequisites & Virtual Environment
If not already set up, create and activate a virtual environment:
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
By default, the project runs locally with **Ollama** (free, no API key needed, auto-detects `phi3:latest` or `llama3.2`).
You can also connect Anthropic Claude, OpenAI, or xAI Grok by updating `.env`:

```env
# Local Ollama (Active default)
LLM_BACKEND=ollama
MAIN_MODEL=phi3:latest
ROUTER_MODEL=phi3:latest

# Or OpenAI:
# LLM_BACKEND=openai
# OPENAI_API_KEY=sk-...
# MAIN_MODEL=gpt-4o-mini
# ROUTER_MODEL=gpt-4o-mini

# Or Anthropic Claude:
# LLM_BACKEND=anthropic
# ANTHROPIC_API_KEY=sk-ant-...
# MAIN_MODEL=claude-3-5-sonnet-20241022
# ROUTER_MODEL=claude-3-5-haiku-20241022
```

---

## Running & Testing

### Option A: Run the Practical Test Suite (Stages 1–3)
Executes all prompt scenarios from the test brief:
```bash
python run_tests.py
```
This runs:
- **Stage 1**: Single-turn account lookup (`"What is my current plan and how much do I pay each month?"`).
- **Stage 2**: Multi-turn memory conversation (`"What plan am I on?"` ➔ `"Is there a faster option?"` ➔ `"How much more would that cost?"`).
- **Stage 3**: Out-of-scope guardrail filtering (Competitor comparison, Personal writing advice, General weather query, and In-scope billing control).

### Option B: Interactive Terminal Chat (CLI)
Chat interactively with the assistant in your console:
```bash
python chat_cli.py
```
- Type `/account` to view Priya Sharma's account data.
- Type `/reset` to clear conversation memory.
- Type `quit` or `exit` to end the session.

### Option C: ConnectX Customer Portal Web Application
Launch the web interface simulating the ConnectX website:
```bash
python web_server.py
```
Open [http://localhost:8000](http://localhost:8000) in your browser:
- Live Account Dashboard with verified customer card (Priya Sharma, ConnectX Pro - 150 Mbps, ₹999/mo, Active).
- Available Upgrade Plans matrix (ConnectX Basic ₹599, Pro ₹999, Max ₹1,399, Ultra ₹1,999).
- Modern Glassmorphic Chat Widget with real-time classification tag pills (`[IN_SCOPE]`, `[COMPETITOR]`, `[PERSONAL]`, `[UNRELATED]`).
- One-click test scenario chips to immediately test any test stage.

### Option D: Fast Offline Test (No API Key / No Ollama Needed)
Validates all bot logic, memory compaction, and guardrail routing instantaneously using a deterministic mock client:
```bash
python test_offline.py
```

---

## Architecture & How Each Stage Works

### STAGE 1: Core Assistant (`ask_once`)
- Takes the customer's account context (name, plan, monthly charge, billing date, payment status, outages, contract end date) and available plans into a strict, structured system prompt.
- Answers user inquiries truthfully with ₹ (INR) currency formatting and zero hallucinations.
- Addresses the customer by their first name ("Priya").

### STAGE 2: Multi-Turn Conversation Memory (`SupportBot`)
- **State Management**: History is maintained as an array of message turns (`{"role": "user"|"assistant", "content": "..."}`) in the `SupportBot` session instance.
- **Sliding Window + Rolling Summary**:
  - To prevent unbounded token growth and latency in long sessions, when history exceeds `max_messages` (default: 12), older turns are compacted into an incremental rolling summary (`under 100 words`).
  - The most recent `keep_recent` turns (default: 6) are preserved verbatim.
  - The prompt dynamically combines the rolling summary + recent verbatim turns so the LLM retains full context without context window overflow.

### STAGE 3: Out-of-Scope Control & Dual-Layer Guardrails
- **Dual-Layer Defense**:
  1. **Layer 1 (Fast Classifier Router)**: Analyzes the latest query alongside recent context to categorize it into:
     - `IN_SCOPE`: Billing, plans, upgrades, outages, or contextual follow-ups.
     - `COMPETITOR`: Competitor telecom comparison (e.g., Airtel, Jio).
     - `PERSONAL`: Personal writing, landlord emails, life advice.
     - `UNRELATED`: Weather, news, trivia, coding.
     Out-of-scope queries immediately return a courteous, deterministic, on-brand decline without invoking unnecessary model inference.
  2. **Layer 2 (Prompt-Level Guardrail / Fail-Open Protection)**:
     If the router fails or is disabled, Rule #2 in the system prompt enforces a polite, on-brand decline directly inside the LLM prompt.

### STAGE 4: Web Portal Deployment & Observability
- Built-in lightweight HTTP REST API and modern frontend portal (`web_server.py` + `web/index.html`).
- REST endpoints:
  - `GET /api/account`: Customer account & available plans.
  - `GET /api/status`: Active backend, model name, and memory length.
  - `POST /api/chat`: Runs conversation turn with router tag observability.
  - `POST /api/reset`: Session memory reset.
