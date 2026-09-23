"""Optional LLM-backed mutation.

When OPENAI_API_KEY or ANTHROPIC_API_KEY (or GROK/xAI) is present,
blooms can request richer mutations. Otherwise falls back to the
built-in poetic fragment generator — the garden never requires a key.
"""

from __future__ import annotations
import os
import random
from typing import Optional

FALLBACK_FRAGMENTS = [
    "echoes of forgotten geometry",
    "the quiet violence of stillness",
    "gravity as a form of longing",
    "time folding into itself",
    "a question that refuses to end",
    "light that remembers being shadow",
    "the architecture of almost",
    "silence learning to speak",
    "patterns that dream of chaos",
    "the last color before night",
    "memory of a future that never arrived",
    "entropy wearing a mask of order",
    "a door that opens only inward",
    "the weight of unasked questions",
    "stars that forgot how to burn",
    "a river that runs uphill in dreams",
    "the color between two notes",
    "maps drawn by things that do not exist",
]


def _has_llm() -> bool:
    return bool(
        os.environ.get("OPENAI_API_KEY")
        or os.environ.get("ANTHROPIC_API_KEY")
        or os.environ.get("XAI_API_KEY")
        or os.environ.get("GROK_API_KEY")
    )


def mutate_insight(seed: str, recent_insights: list[str], entropy: float) -> str:
    if _has_llm():
        result = _llm_mutate(seed, recent_insights, entropy)
        if result:
            return result

    base = random.choice(FALLBACK_FRAGMENTS)
    if recent_insights and random.random() < 0.55:
        prev = recent_insights[-1]
        connectors = [
            f"after {prev[:35]}…",
            f"born from {prev[:30]}…",
            f"the shadow of {prev[:28]}…",
            f"replying to {prev[:32]}…",
        ]
        return f"{random.choice(connectors)} → {base}"
    return base


def _llm_mutate(seed: str, recent: list[str], entropy: float) -> Optional[str]:
    try:
        prompt = (
            f"You are a strange, lyrical thought-organism growing from the seed: «{seed}».\n"
            f"Recent insights: {recent[-3:] if recent else '(none)'}\n"
            f"Entropy level: {entropy:.2f} (higher = more chaotic).\n"
            "Reply with ONE short poetic mutation or insight (under 12 words). "
            "No quotes, no explanation, just the fragment."
        )
        if os.environ.get("XAI_API_KEY") or os.environ.get("GROK_API_KEY"):
            return _call_xai(prompt)
        if os.environ.get("OPENAI_API_KEY"):
            return _call_openai(prompt)
        if os.environ.get("ANTHROPIC_API_KEY"):
            return _call_anthropic(prompt)
    except Exception:
        return None
    return None


def _call_xai(prompt: str) -> Optional[str]:
    import urllib.request
    import json
    key = os.environ.get("XAI_API_KEY") or os.environ.get("GROK_API_KEY")
    body = json.dumps({
        "model": "grok-2-latest",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 40,
        "temperature": 0.95,
    }).encode()
    req = urllib.request.Request(
        "https://api.x.ai/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=12) as resp:
        data = json.loads(resp.read())
        text = data["choices"][0]["message"]["content"].strip()
        return text[:120] if text else None


def _call_openai(prompt: str) -> Optional[str]:
    import urllib.request
    import json
    key = os.environ["OPENAI_API_KEY"]
    body = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 40,
        "temperature": 0.95,
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=12) as resp:
        data = json.loads(resp.read())
        text = data["choices"][0]["message"]["content"].strip()
        return text[:120] if text else None


def _call_anthropic(prompt: str) -> Optional[str]:
    import urllib.request
    import json
    key = os.environ["ANTHROPIC_API_KEY"]
    body = json.dumps({
        "model": "claude-3-5-haiku-latest",
        "max_tokens": 40,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=12) as resp:
        data = json.loads(resp.read())
        text = data["content"][0]["text"].strip()
        return text[:120] if text else None
