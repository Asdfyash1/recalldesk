"""RecallDesk demo server.

Endpoints:
  GET  /                          -> chat UI
  GET  /api/customers             -> list demo customers
  POST /api/chat                  -> {customer_id, message, memory_on} -> {reply, memories_used}
  GET  /api/memories/<cid>        -> raw memories in the customer's bank
  POST /api/seed                  -> seed synthetic ticket history into Hindsight
  POST /api/reset                 -> clear chat history (keeps Hindsight banks)
"""
import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

load_dotenv()

from agent import respond
from memory import SupportMemory
from seed_data import CUSTOMERS, TICKETS

app = Flask(__name__, static_folder="static", static_url_path="")
memory = SupportMemory()
histories: dict[str, list] = {}  # customer_id -> [{"role","content"}]


@app.get("/")
def index():
    return send_from_directory("static", "index.html")


@app.get("/api/customers")
def customers():
    return jsonify([
        {"id": c["id"], "name": c["name"], "email": c["email"], "plan": c["plan"]}
        for c in CUSTOMERS
    ])


@app.post("/api/chat")
def chat():
    data = request.get_json(force=True)
    customer_id = data.get("customer_id", "priya")
    message = data.get("message", "").strip()
    memory_on = bool(data.get("memory_on", True))
    if not message:
        return jsonify({"error": "empty message"}), 400

    customer = next(c for c in CUSTOMERS if c["id"] == customer_id)
    history = histories.setdefault(customer_id, [])

    memories = memory.recall_context(customer_id, message) if memory_on else []
    recent = memory.recent_turns(customer_id) if memory_on else []
    try:
        reply = respond(customer, message, memories, history, recent)
    except Exception as e:
        return jsonify({"error": f"LLM call failed: {e}. Check GROQ_API_KEY in .env."}), 502

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})

    if memory_on:
        memory.learn(customer_id, message, reply)  # agent learns over time

    return jsonify({"reply": reply, "memories_used": memories})


@app.get("/api/memories/<customer_id>")
def memories(customer_id):
    return jsonify(memory.inspect(customer_id))


@app.get("/api/stats/<customer_id>")
def stats(customer_id):
    return jsonify(memory.stats(customer_id))


@app.post("/api/seed")
def seed():
    """One-time: retain the synthetic ticket history for every customer.

    Groq's free tier is 8k tokens/min, and each ticket's fact extraction uses
    a few thousand — so we pace the seeds and retry on 429s instead of dying.
    """
    import time

    count = 0
    for customer in CUSTOMERS:
        for ticket in TICKETS.get(customer["id"], []):
            for attempt in range(4):
                try:
                    memory.seed_ticket(customer, ticket)
                    count += 1
                    break
                except Exception as e:
                    msg = str(e).lower()
                    if ("429" in msg or "rate limit" in msg or "quota" in msg) and attempt < 3:
                        wait = 40 * (attempt + 1)
                        print(f"[seed] rate-limited, waiting {wait}s (attempt {attempt + 1})")
                        time.sleep(wait)
                    else:
                        raise
            time.sleep(8)  # stay under the free-tier token rate
    return jsonify({"seeded_tickets": count})


@app.post("/api/reset")
def reset():
    histories.clear()
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    print(f"\n  RecallDesk running at http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
