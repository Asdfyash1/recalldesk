"""Groq-powered support agent. Recalled Hindsight memories are injected into
the system prompt, so the agent answers with full customer context."""
import os

from groq import Groq

from proxyfix import sanitize_proxy_env

sanitize_proxy_env()

MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

SYSTEM_TEMPLATE = """You are RecallDesk, a customer support agent for Cloudline, a project-management SaaS.
You are chatting with {name} ({email}), currently on the {plan} plan.

{memory_block}
{recent_block}

Rules:
- Be warm, concise, and specific. Reference past tickets by date when relevant.
- If the customer reports an issue similar to a past one, LEAD with it:
  "This happened before on <date> — <what worked>." Then apply that fix.
- If they share new facts (plan change, new team size, new tools), acknowledge
  them clearly so the customer sees you registered it.
- Never invent ticket history. Only use the memories provided above.
- Keep replies under 120 words unless the customer asks for detail."""


def build_memory_block(memories: list) -> str:
    if not memories:
        return ("You have no prior memories of this customer. "
                "Treat this as a first contact and ask clarifying questions.")
    lines = "\n".join(f"- [{m.get('type', 'memory')}] {m.get('text', '')}" for m in memories)
    return ("What you remember about this customer "
            "(from past tickets and conversations — use it):\n" + lines)


def build_recent_block(recent: list) -> str:
    if not recent:
        return ""
    lines = "\n".join(
        f"- {'Customer' if t['role'] == 'user' else 'You'}: {t['text']}" for t in recent
    )
    return "Just now in this conversation:\n" + lines


def respond(customer: dict, message: str, memories: list, history: list, recent: list = None) -> str:
    """history: list of {"role": "user"|"assistant", "content": str} (last ~10 turns).
    recent: short-term turns (incl. just-learned facts) merged into the prompt."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    system = SYSTEM_TEMPLATE.format(
        name=customer["name"],
        email=customer["email"],
        plan=customer["plan"],
        memory_block=build_memory_block(memories),
        recent_block=build_recent_block(recent or []),
    )
    messages = [{"role": "system", "content": system}]
    messages += history[-10:]
    messages.append({"role": "user", "content": message})
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.4,
        max_tokens=600,
    )
    return resp.choices[0].message.content.strip()
