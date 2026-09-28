"""Sanitize proxy env vars that crash httpx's URL parser.

Some environments set no_proxy/NO_PROXY with bare IPv6 entries (e.g. ::1,
[::1]) which make the OpenAI/Groq client's proxy handling raise
httpx.InvalidURL at import/client-creation time. This drops only the entries
that fail to parse, keeping everything else intact.
"""
import os


def sanitize_proxy_env():
    try:
        from httpx import URL
    except ImportError:
        return
    for var in ("no_proxy", "NO_PROXY"):
        val = os.environ.get(var)
        if not val:
            continue
        kept = []
        for part in val.split(","):
            part = part.strip()
            if not part:
                continue
            try:
                URL(part if "://" in part else "http://" + part)
                kept.append(part)
            except Exception:
                continue
        os.environ[var] = ",".join(kept)
