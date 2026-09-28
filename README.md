# RecallDesk — Customer support that never forgets

An AI support agent with **persistent memory** powered by [Hindsight](https://hindsight.vectorize.io/).
It remembers every customer's tickets, what fixed their issues, their plan, and how
they felt — so returning customers never have to repeat their story.

Built for HackwithHyderabad 3.0 (finale at Microsoft, Hyderabad).

## The problem

Support agents (human or AI) start every conversation from zero. A customer who
reported a slow dashboard 3 days ago has to re-explain everything on their next
visit. That repetition is the #1 driver of support frustration.

## The fix

Every customer gets their own **Hindsight memory bank**. Before each reply the agent:

1. **Recalls** — queries the customer's bank (`recall`) for relevant facts, observations, and experiences
2. **Responds** — Groq LLM answers with those memories in context
3. **Learns** — the conversation turn is `retain`ed, so the agent is smarter next time

Turn memory **off** in the UI and the same agent becomes a generic bot — the
before/after is the whole demo.

## Architecture

```
┌─────────────┐      ┌──────────────────────────────────┐
│  Chat UI    │─────▶│  Flask (app.py)                  │
│  (browser)  │◀─────│                                  │
└─────────────┘      │  ┌────────────┐  ┌─────────────┐ │
                     │  │ agent.py   │  │ memory.py   │ │
                     │  │ Groq LLM   │◀─│ Hindsight   │ │
                     │  │ gpt-oss    │  │ retain/     │ │
                     │  │ -20b       │  │ recall      │ │
                     │  └────────────┘  └──────┬──────┘ │
                     └────────────────────────┼────────┘
                                              ▼
                                   Hindsight memory banks
                                   (one per customer:
                                    world facts, observations,
                                    experience facts)
```

Hindsight runs **embedded** (`hindsight-all`) — no Docker, no separate server.
It uses Groq (`openai/gpt-oss-20b`) for memory extraction. Switch to
Hindsight Cloud via `HINDSIGHT_MODE=cloud` if you prefer the hosted dashboard.

## Setup (5 minutes)

```bash
# 1. Install
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Keys — free, no credit card:
#    Groq:  https://console.groq.com  -> API keys
cp .env.example .env
#    then paste your GROQ_API_KEY into .env

# 3. Run
python app.py
#    open http://localhost:5000
#    NOTE: first run takes a few minutes — Hindsight downloads embedding
#    models on first boot. Later starts are fast.

# 4. In the UI, click "Seed demo data" (one time, ~2-3 min on Groq free tier).
#    This retains the synthetic ticket history into Hindsight.
#    The seed paces itself and retries on 429s so the free tier survives it.
```

**Notes**
- `HINDSIGHT_API_LLM_GROQ_SERVICE_TIER` defaults to `on_demand` (some Groq
  orgs reject `auto`). Override in `.env` if your org differs.
- If you run behind a proxy and see `httpx.InvalidURL`, `proxyfix.py`
  sanitizes the proxy env vars at startup.

## Demo flow (60 seconds)

1. Select **Priya Sharma**. Toggle memory **OFF**. Send: *"my dashboard is slow again"*
   → generic bot, asks for details. This is the pain.
2. Toggle memory **ON**. Send the same message →
   *"Hi Priya — this looks like the same slow-dashboard issue from Sep 24…"*
   It recalls the stuck worker, the fix, her frustration, and her API-limit question.
3. Open the **"What the agent remembered"** panel — the recalled Hindsight facts are visible.
4. Send: *"we upgraded to Enterprise last week"* → retained; ask *"what's my plan?"* later → *"Enterprise"*. The agent learned.

Full script: [DEMO_SCRIPT.md](DEMO_SCRIPT.md)

## How Hindsight memory is used (submission summary)

- **Retain**: historical tickets (with real timestamps) + every live conversation turn
- **Recall**: before every reply — semantic + keyword + graph + temporal search over the customer's bank
- **Reflect-ready**: banks carry a mission ("remember everything about this customer") and high-empathy disposition
- **Consolidation**: repeated facts become durable observations (e.g. "Priya's workspace had a stuck worker before")
- Per-customer banks = per-user memory isolation

## Project structure

```
recalldesk/
├── app.py            # Flask server + API
├── agent.py          # Groq chat agent (memory injected into prompt)
├── memory.py         # Hindsight wrapper: banks, retain/recall/learn/inspect
├── seed_data.py      # Synthetic customers + ticket history
├── static/index.html # Chat UI with memory toggle + memory inspector
├── DEMO_SCRIPT.md    # Exact 2–5 min video script
├── SUBMISSION_NOTES.md # "How Hindsight is used" writeup for the form
└── requirements.txt
```

## Team

Team Nexra — Yashwanth & Harshini
