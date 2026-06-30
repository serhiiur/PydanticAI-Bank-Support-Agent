# Bank-Support-Agent

A bank customer support agent built with PydanticAI. The agent identifies clients by phone number, provides account and card information, handles card deactivation requests, answers currency exchange queries, and returns structured responses that include a support message, a numeric risk level, and recommended follow-up actions.


## Commands

```bash
# Run the agent (CLI mode by default)
uv run agent/main.py

# Run with web UI
uv run agent/main.py --web

# Run both CLI and web simultaneously
uv run agent/main.py --cli --web --host 0.0.0.0 --port 8080

# Seed the database with sample data (run once on first setup)
uv run agent/scripts/seed.py

# Run tests
uv run pytest agent/tests/

# Install dependencies
uv sync --all-groups
```

## Architecture

This is a PydanticAI-based bank customer support agent that can run in CLI or web (FastAPI chat UI) mode. The model and system prompt are configured via `agent.yml`; the active model is `openrouter:openai/gpt-5.4-nano`.

**Request flow:**
1. `main.py` loads the agent from `agent.yml`, wires up tools and instructions, then runs it in CLI and/or web mode using `anyio` task groups.
2. At runtime, `instructions.py` dynamically injects the current client's name into the system prompt (looked up by hardcoded phone `+1 650-253-0000`).
3. The agent calls tools in `tools.py` — two toolsets: `card_toolset` (balance, transactions, deactivate) and `currency_toolset` (exchange rates).
4. All tool calls go through `BaseBankAgentToolset` (`core/tools.py`), which catches domain exceptions and converts them to user-friendly strings, or raises `SkipToolExecution` for unexpected errors.
5. The agent returns a structured `AgentOutput` (support text + numeric risk level 0–10 + follow-up actions list).

**Service layer:**
- `services/bank_db.py` — async SQLModel/SQLAlchemy operations for `Client`, `Card`, `Transaction`
- `services/currency.py` — HTTP client for exchange rate API

**Data model:** `Client` → `Card` (many) → `Transaction` (many). All tables inherit ID and timestamp mixins from `core/database/mixins.py`.

**Configuration:** `core/settings.py` reads from `.env`. Required env vars: `OPENROUTER_API_KEY`, `CURRENCY_API_URL`.
