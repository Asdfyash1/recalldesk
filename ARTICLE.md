# The Support Bot That Actually Remembers You

## How persistent memory turns a generic chatbot into a support agent with a past

Every support conversation starts the same way: "Can you describe the issue?" You explain. They ask for details you already gave last week. You repeat yourself. By the third exchange, you're not frustrated with the product anymore — you're frustrated with the *conversation*.

I built RecallDesk to kill that loop. It's a customer-support agent that remembers every customer: their past tickets, what fixed their issues, their plan, even how they felt about the last resolution. When a returning customer says "my dashboard is slow again," it doesn't ask for details — it says "this looks like the same issue from September 24th, when worker w-8812 got stuck. Let's check Settings → Diagnostics."

The difference between those two responses is **persistent memory**. Here's how I built it.

## Why chatbots forget (and why it's a architecture problem, not a prompt problem)

Most AI support bots are stateless by design. Each conversation is a fresh API call with a system prompt and a short context window. You can stuff recent messages into the prompt, but the moment the session ends, everything evaporates.

The usual workarounds don't scale:

- **Bigger context windows** just delay the forgetting, and they get expensive fast.
- **Summary chains** ("summarize this conversation for next time") lose the specifics that matter — ticket IDs, exact error messages, the weird workaround that actually worked.
- **Vector databases with raw embeddings** retrieve semantically similar text, but they don't *understand* what to remember. They'll surface a vaguely related doc when you needed the exact fix from last month.

What a support agent actually needs is closer to human memory: durable facts ("Priya's dashboard broke on Sep 24"), observations ("she's on the Scale plan, uses the Jira integration"), and experiences ("the re-queue fix worked, she rated it 2/5 and was still frustrated"). Different kinds of knowledge, with different lifespans and different retrieval patterns.

## Hindsight: memory as infrastructure

That's what [Hindsight by Vectorize](https://hindsight.vectorize.io/) provides — persistent memory as infrastructure, not as a prompt hack. The mental model is simple:

- **Retain**: feed it content (tickets, conversation turns). It extracts structured facts, typed as *world* (stable truths), *observation* (durable patterns), or *experience* (episodic events with timestamps).
- **Recall**: query it in natural language. It searches semantically, by keyword, across the knowledge graph, and temporally — then reranks.
- **Banks**: each customer gets an isolated memory bank, so Priya's history never leaks into Arjun's session. Memory isolation isn't a feature here; it's the architecture.

I run Hindsight **embedded** — the server spins up inside the Flask process, no Docker, no separate deploy. For the demo that means `python app.py` is the entire infrastructure.

## The three-step loop

Every message in RecallDesk flows through the same loop:

1. **Recall** — before the LLM sees anything, the agent queries the customer's Hindsight bank for relevant facts. The query is the customer's message; the results are memories with types, timestamps, and activation scores.
2. **Respond** — those memories are injected into the system prompt as a "what I remember about this customer" block. The LLM (Groq's gpt-oss-20b) answers with full context: past incidents, the fixes that worked, the customer's plan and preferences.
3. **Learn** — after replying, the turn is retained back into the bank. If the customer mentions a plan upgrade mid-conversation, the next "what's my plan?" gets the new answer. The agent genuinely learns during the chat.

The UI has a memory toggle that makes the value visceral: flip it off and the same agent becomes a generic bot asking "when did the slowdown start?" Flip it on and it opens with the incident history. The before/after *is* the demo.

## What the memory actually looks like

Here's what got extracted from one synthetic ticket — a dashboard slowdown on September 24th:

> Customer reported dashboard load times of 40+ seconds. Root cause: background worker w-8812 stuck on a queue. Fix: re-queued via Settings → Diagnostics. Load time returned to ~3 seconds. CSAT: 2/5, customer frustrated, follow-up promised.

Hindsight broke that into typed facts: the incident as an *experience* (with the date), the fix as a durable *observation*, the CSAT score as a satisfaction signal. When the customer returns and says "slow again," recall surfaces the incident, the worker ID, and the exact fix path — not a fuzzy summary, the specifics.

There's also a memory inspector panel in the UI that shows the raw recalled facts, so the "AI remembered" moment is auditable, not magic.

## The unglamorous lessons

**Free-tier rate limits shape your architecture.** Groq's free tier allows 8,000 tokens/minute, and each ticket's fact extraction burns a few thousand. Seeding seven tickets naively hits 429s immediately. The fix was boring but essential: pace the seeds, retry with backoff, and set `service_tier=on_demand` (some Groq orgs reject the default `auto`). The seed endpoint now survives the free tier instead of dying on it.

**Sync wrappers around async clients are a minefield.** The Hindsight Python client's synchronous methods reuse a cached asyncio event loop; after the first call closes it, every subsequent call fails. I ended up running each client call on a worker thread with a fresh event loop *and* a fresh client per call (the aiohttp session binds to its creation loop). Ugly, but it made retain/recall/inspect reliable across hundreds of calls. If you're building on Hindsight's sync client in a long-lived server process, plan for this.

**Memory quality is a retrieval-ranking problem.** My first recall test surfaced the wrong ticket — a semantically adjacent API-limits ticket instead of the dashboard incident. Widening the fact-type filter from just `experience` to all types fixed it, but the lesson stands: the demo moment lives or dies on retrieval ranking, so test it with the actual queries your demo uses, not just "does recall return something."

**Isolation must be structural.** Per-customer banks (not per-customer filters on a shared store) mean a bug in my query logic can't leak one customer's history to another. For anything touching real customer data, that's the only acceptable shape.

## What I'd build next

The honest gaps: the agent doesn't yet *reflect* — it stores and retrieves, but it doesn't proactively consolidate ("Priya has had three dashboard-adjacent issues; maybe there's a deeper pattern"). Hindsight's bank missions and consolidation pipeline point in that direction; I have the missions configured but haven't tuned the consolidation loop yet.

I'd also add memory *editing* — customers correct the record ("actually we're on Enterprise now, the upgrade finished"), and the agent should supersede the old fact rather than accumulate contradictions. The observation mission handles some of this via consolidation, but explicit correction flows would be stronger.

And the real test isn't synthetic tickets — it's messy, typo-ridden, multi-threaded human conversations where the "fact" is buried in paragraph three of a rant. That's where typed extraction either earns its keep or falls apart.

## The takeaway

The gap between "a chatbot" and "an agent" isn't reasoning power — it's continuity. A model that remembers your last three tickets, what fixed them, and how you felt about it doesn't need to be smarter. It just needs to not start from zero.

Persistent memory turns support from interrogation into conversation. The customer stops repeating themselves. The agent stops asking questions it should know the answers to. And "my dashboard is slow again" gets the response it deserves: "I remember. Let's fix it the way that worked last time."

---

*RecallDesk is open source. It uses Hindsight by Vectorize for persistent memory, Groq for inference, and Flask for the demo UI. Every customer gets an isolated memory bank; every reply is grounded in recalled history.*
