# RecallDesk — Demo video script (2–5 min)

Record your screen with the app open at http://localhost:5000.
Seed the demo data first (click "Seed demo data", wait ~2-3 min on Groq free tier).

## 0:00–0:20 — The problem (say this over the UI)

> "Every support chatbot has amnesia. A customer reports a slow dashboard on
> Monday, comes back Thursday, and has to explain everything again. Support
> teams drown in repeat tickets, customers get frustrated. We fixed it with
> RecallDesk — a support agent with persistent memory, powered by Hindsight."

## 0:20–1:00 — The pain: memory OFF

1. Select **Priya Sharma**.
2. Make sure the **Agent memory toggle is OFF** (show it clearly).
3. Send: `my dashboard is slow again`
4. Point at the generic reply: *"It asks what dashboard, what browser — it knows
   nothing. This is every chatbot today."*

## 1:00–2:30 — The fix: memory ON

1. Flip the toggle **ON** (show the green MEMORY ON badge).
2. Send the exact same message: `my dashboard is slow again`
3. Read the reply out loud — it should:
   - greet Priya by name
   - reference the **Sep 24** slow-dashboard ticket
   - mention the stuck worker and the Settings → Diagnostics fix
   - optionally flag her API-limit question from Sep 20
4. Say: *"It didn't just remember — it recalled the root cause, the fix that
   worked, and that she was frustrated last time."*

## 2:30–3:30 — Show the memory (the Hindsight part — judges care)

1. Point at the **"What the agent remembered"** panel on the right.
2. Say: *"Every reply starts with a Hindsight recall over Priya's private memory
   bank — world facts, consolidated observations, past experiences. Each customer
   gets their own bank, so memories never leak across customers."*
3. Send: `we upgraded to Enterprise last week`
4. Say: *"That turn is retained right now — the agent just learned something new."*
5. Send: `what's my current plan?` → it answers **Enterprise**.
6. Say: *"Interaction 1: generic. Interaction 5: it knows her. That's the learning
   curve Hindsight gives you."*

## 3:30–4:00 — Close

> "RecallDesk: retain every ticket, recall before every reply, learn from every
> conversation. Support that never forgets. Code and setup are in the repo —
> one pip install, one free Groq key, and it runs."

## Recording tips

- 1080p screen capture, zoom the browser to 125% so text is readable.
- Do the memory-OFF part first (the contrast is the story).
- If a reply is slow, it's Groq/Hindsight thinking — don't cut it, it looks real.
- Keep it under 5 minutes. 3–4 is the sweet spot.
