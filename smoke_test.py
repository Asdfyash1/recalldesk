"""Smoke test — run after putting keys in .env:  python smoke_test.py

Verifies: Hindsight embedded server boots, retain -> recall roundtrip works,
Groq chat works. If all green, the demo will run.
"""
import os

from dotenv import load_dotenv

load_dotenv()

failures = []


def check(name, fn):
    try:
        fn()
        print(f"  [OK] {name}")
    except Exception as e:
        failures.append(name)
        print(f"  [FAIL] {name}: {e}")


print("== RecallDesk smoke test ==")

def t_imports():
    import hindsight, groq, flask  # noqa
check("package imports", t_imports)

def t_groq():
    from groq import Groq
    r = Groq(api_key=os.getenv("GROQ_API_KEY")).chat.completions.create(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        messages=[{"role": "user", "content": "Reply with the word PONG."}],
        max_tokens=10,
    )
    assert "PONG" in r.choices[0].message.content.upper(), r.choices[0].message.content
check("Groq chat", t_groq)

def t_memory_roundtrip():
    from hindsight import HindsightServer, HindsightClient
    with HindsightServer(
        llm_provider=os.getenv("HINDSIGHT_LLM_PROVIDER", "groq"),
        llm_model=os.getenv("HINDSIGHT_LLM_MODEL", "openai/gpt-oss-20b"),
        llm_api_key=os.getenv("GROQ_API_KEY"),
    ) as server:
        client = HindsightClient(base_url=server.url)
        bank = "smoke-test-bank"
        try:
            client.create_bank(bank_id=bank, name="smoke test")
        except Exception:
            pass
        client.retain(bank_id=bank, content="Smoke-test customer uses the Enterprise plan.")
        res = client.recall(bank_id=bank, query="What plan is the customer on?")
        texts = " ".join(r.text for r in res.results).lower()
        assert "enterprise" in texts, f"recall missed it: {texts}"
check("Hindsight retain -> recall", t_memory_roundtrip)

print()
if failures:
    print(f"RESULT: {len(failures)} check(s) failed: {failures}")
    raise SystemExit(1)
print("RESULT: all green — run `python app.py` and open http://localhost:5000")
