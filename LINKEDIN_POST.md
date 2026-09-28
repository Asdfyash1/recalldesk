I built a support agent that never asks "can you describe the issue?" twice.

RecallDesk gives every customer their own persistent memory bank (Hindsight by Vectorize). Past tickets, what fixed them, plan changes, CSAT scores — all retained as typed facts, recalled before every reply.

The demo moment: toggle memory OFF, say "my dashboard is slow again" → generic bot, asks for details. Toggle it ON, same message → "this looks like the Sep 24 incident — worker w-8812 was stuck, we re-queued it via Settings → Diagnostics."

Same agent. Same LLM. The only difference is memory.

Hardest lessons were unglamorous: Groq free-tier rate limits forced paced seeding with backoff, and Hindsight's sync client needed fresh event loops per call in a long-lived server. Retrieval ranking made or broke the demo — test with your actual demo queries.

Continuity is what turns a chatbot into an agent. The customer stops repeating themselves.

#AI #CustomerSupport #LLM #PersistentMemory #BuildInPublic
