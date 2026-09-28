"""Hindsight memory layer for RecallDesk.

Every customer gets their own Hindsight memory bank, so memories never leak
across customers. The agent retains tickets + conversations and recalls them
before every reply.
"""
import asyncio
import atexit
import concurrent.futures
import os
from datetime import datetime

from proxyfix import sanitize_proxy_env

sanitize_proxy_env()

BANK_PREFIX = "recalldesk"

# The Hindsight sync client reuses a cached asyncio event loop across calls;
# once that loop closes, every later call dies with "Timeout context manager
# should be used inside a task". Run each call on a worker thread with a
# fresh loop so repeated retain/recall/inspect calls stay reliable.
_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)


def _hs(fn, *args, **kwargs):
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return fn(*args, **kwargs)
        finally:
            try:
                loop.close()
            except Exception:
                pass
    return _pool.submit(run).result()


class SupportMemory:
    def __init__(self):
        self.mode = os.getenv("HINDSIGHT_MODE", "embedded")  # embedded | cloud | off
        self.server = None
        self._server_ctx = None
        self.client = None
        # Short-term buffer: last few turns per customer, so just-learned facts
        # are in context immediately (async retain lands in Hindsight after).
        self._recent = {}

        if self.mode == "off":
            print("[memory] Hindsight disabled (HINDSIGHT_MODE=off) — running memory-less.")
            return

        if self.mode == "cloud":
            from hindsight_client import Hindsight
            self._client_factory = lambda: Hindsight(
                base_url=os.getenv("HINDSIGHT_URL", "https://api.hindsight.vectorize.io"),
                api_key=os.getenv("HINDSIGHT_API_KEY"),
                timeout=60.0,
            )
            print("[memory] Using Hindsight Cloud.")
        else:
            # Groq free-tier orgs reject service_tier=auto; on_demand works.
            # Override with HINDSIGHT_API_LLM_GROQ_SERVICE_TIER if you need to.
            os.environ.setdefault("HINDSIGHT_API_LLM_GROQ_SERVICE_TIER", "on_demand")
            # Embedded server: no Docker, no separate process. The server runs
            # inside this Python process and uses Groq for memory extraction.
            from hindsight import HindsightServer, HindsightClient
            server_kwargs = dict(
                llm_provider=os.getenv("HINDSIGHT_LLM_PROVIDER", "groq"),
                llm_model=os.getenv("HINDSIGHT_LLM_MODEL", "openai/gpt-oss-20b"),
                llm_api_key=os.getenv("GROQ_API_KEY"),
            )
            # If HINDSIGHT_DB_URL is set, use that Postgres instead of the
            # server's built-in one (handy for CI / sandboxes).
            if os.getenv("HINDSIGHT_DB_URL"):
                server_kwargs["db_url"] = os.environ["HINDSIGHT_DB_URL"]
            self._server_ctx = HindsightServer(**server_kwargs)
            # First boot downloads embedding models; allow up to 10 minutes.
            self.server = self._server_ctx.start(timeout=600)
            atexit.register(self._server_ctx.stop)
            server_url = self.server.url
            self._client_factory = lambda: HindsightClient(base_url=server_url)
            print(f"[memory] Embedded Hindsight server running at {server_url}")

    def _fresh_client(self):
        """A new client per call — the sync client's aiohttp session binds to
        whatever event loop is current, and reused sessions die with
        'Event loop is closed' after the first call."""
        return self._client_factory()

    # ------------------------------------------------------------------ banks
    def bank_id(self, customer_id: str) -> str:
        return f"{BANK_PREFIX}-{customer_id}"

    def ensure_bank(self, customer: dict):
        """Create the customer's memory bank (idempotent)."""
        if not getattr(self, "_client_factory", None):
            return
        try:
            _hs(self._fresh_client().create_bank,
                bank_id=self.bank_id(customer["id"]),
                name=f"Support memory — {customer['name']}",
                mission=(
                    "You are the long-term memory of a customer support agent for "
                    f"Cloudline, a project-management SaaS. Remember everything about "
                    f"{customer['name']} ({customer['email']}): their subscription plan, "
                    "every past ticket, what fixed their issues, their technical "
                    "environment, their preferences, and how satisfied or frustrated "
                    "they have been. Consolidate repeated facts into durable observations."
                ),
                disposition={"skepticism": 2, "literalism": 2, "empathy": 5},
                retain_mission=(
                    "Extract facts about THIS customer's support history: past issues, "
                    "root causes, resolutions that worked, plan or account changes, "
                    "stated preferences, and satisfaction signals (CSAT, frustration). "
                    "Keep ticket IDs, dates, and exact fix steps — they are what make "
                    "a future reply personal."
                ),
                observations_mission=(
                    "Observations are stable facts about this customer: their plan, "
                    "tech stack, integrations, team size, recurring issue patterns. "
                    "Ignore one-off ticket details."
                ),
            )
        except Exception:
            pass  # bank already exists

    # ------------------------------------------------------------------ write
    def seed_ticket(self, customer: dict, ticket: dict):
        """Retain one historical support ticket with its real timestamp."""
        if not getattr(self, "_client_factory", None):
            return
        self.ensure_bank(customer)
        _hs(self._fresh_client().retain,
            bank_id=self.bank_id(customer["id"]),
            content=(
                f"Support ticket {ticket['id']} ({ticket['date']}): {ticket['title']}. "
                f"{ticket['body']} Status: {ticket['status']}. "
                f"Resolution: {ticket['resolution']}"
            ),
            context="support ticket",
            timestamp=datetime.fromisoformat(ticket["date"]),
            document_id=ticket["id"],
            metadata={"ticket_id": ticket["id"], "type": "ticket"},
            retain_async=False,
        )

    def learn(self, customer_id: str, user_msg: str, agent_reply: str):
        """Retain a live conversation turn so the agent learns over time."""
        self.note_turn(customer_id, user_msg, agent_reply)
        if not getattr(self, "_client_factory", None):
            return
        try:
            _hs(self._fresh_client().retain,
                bank_id=self.bank_id(customer_id),
                content=f"Customer said: {user_msg}\nAgent replied: {agent_reply}",
                context="live support conversation",
                metadata={"type": "conversation"},
                retain_async=True,  # don't block the chat reply
            )
        except Exception as e:
            print(f"[memory] learn() failed: {e}")

    # ------------------------------------------------------- short-term cache
    def note_turn(self, customer_id: str, user_msg: str, agent_reply: str):
        buf = self._recent.setdefault(customer_id, [])
        buf.append({"role": "user", "text": user_msg})
        buf.append({"role": "agent", "text": agent_reply})
        self._recent[customer_id] = buf[-8:]  # last ~4 turns

    def recent_turns(self, customer_id: str):
        return list(self._recent.get(customer_id, []))

    # ------------------------------------------------------------------- read
    def recall_context(self, customer_id: str, message: str, max_tokens: int = 2500):
        """Recall everything relevant before answering. Returns list of dicts."""
        if not getattr(self, "_client_factory", None):
            return []
        try:
            res = _hs(self._fresh_client().recall,
                bank_id=self.bank_id(customer_id),
                query=message,
                types=["world", "observation", "experience"],
                max_tokens=max_tokens,
                budget="mid",
            )
            return [{"text": r.text, "type": getattr(r, "fact_type", getattr(r, "type", "?"))} for r in res.results]
        except Exception as e:
            print(f"[memory] recall() failed: {e}")
            return []

    def stats(self, customer_id: str):
        """Memory counts by fact type for the demo header."""
        mems = self.inspect(customer_id, limit=200)
        counts = {}
        for m in mems:
            t = m.get("type", "?")
            counts[t] = counts.get(t, 0) + 1
        return {"total": len(mems), "by_type": counts}

    def inspect(self, customer_id: str, limit: int = 50):
        """List raw memories in the bank (for the demo's memory-inspector panel)."""
        if not getattr(self, "_client_factory", None):
            return []
        try:
            mems = _hs(self._fresh_client().list_memories,bank_id=self.bank_id(customer_id), limit=limit)
            # Return shape varies by version: list, or object with .results/.memories/.items
            items = mems
            for attr in ("results", "memories", "items", "data"):
                if hasattr(mems, attr):
                    items = getattr(mems, attr)
                    break
            out = []
            for m in items or []:
                out.append({
                    "text": getattr(m, "text", str(m)),
                    "type": getattr(m, "fact_type", getattr(m, "type", "?")),
                })
            return out
        except Exception as e:
            print(f"[memory] inspect() failed: {e}")
            return []
