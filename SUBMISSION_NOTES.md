# How Hindsight memory is used in RecallDesk
*(Paste/adapt this into the submission form's "Hindsight explanation" field.)*

## Memory architecture

Each customer gets a dedicated **Hindsight memory bank** (`recalldesk-<customer_id>`),
configured with a mission ("remember everything about this customer: plan, tickets,
fixes, environment, sentiment") and a high-empathy disposition. Banks are per-user,
so memories never leak across customers.

## The three operations, in every conversation turn

1. **Retain (write)**
   - Historical support tickets are retained with their real timestamps, ticket IDs
     as document IDs, and metadata — giving the bank temporal grounding
     ("the slow-dashboard ticket from Sep 24").
   - Every live conversation turn is retained asynchronously (`retain_async=True`),
     so the agent learns continuously without blocking replies.
2. **Recall (read)**
   - Before generating each reply, the agent calls `recall()` with the customer's
     message over their bank (world + observation + experience facts, mid budget).
     Hindsight's 4-way search (semantic, keyword, graph, temporal) finds the
     relevant memories, which are injected into the LLM system prompt.
   - The demo UI exposes exactly what was recalled per reply in the
     "What the agent remembered" panel.
3. **Reflect (reasoning)**
   - The bank's mission, directives, and disposition shape how recalled memories
     are interpreted — e.g. high empathy makes the agent acknowledge past
     frustration before jumping to solutions.

## Why memory is the product, not a feature

- **Before/after is visceral**: with memory off, the agent is a generic bot that
  re-asks everything; with memory on, it greets the customer by name, references
  the Sep 24 incident's root cause (stuck worker w-8812), suggests the fix that
  worked (Settings → Diagnostics re-queue), and proactively flags related context
  (API rate limits discussed Sep 20).
- **Consolidation**: repeated facts become durable observations — e.g. "Priya's
  workspace has a history of stuck background workers" — so the agent gets
  sharper over weeks, not just within one chat.
- **Learning curve demo**: a mid-demo plan change ("we upgraded to Enterprise")
  is retained and correctly recalled minutes later — interaction 1 is generic,
  interaction 5 feels personal.

## Deployment

Hindsight runs embedded via `hindsight-all` (no Docker/server ops), using Groq's
`openai/gpt-oss-20b` for memory extraction; the chat agent uses the same model.
One environment variable (`HINDSIGHT_MODE=cloud`) switches to Hindsight Cloud
with an API key.
