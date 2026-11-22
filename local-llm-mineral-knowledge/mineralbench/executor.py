"""Executor module: prompt construction, model inference over an OpenAI-compatible endpoint,
output collection with per-request latency and bounded retries (paper Sec. 3.4, Table 4).
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

from .metrics import INFERENCE


class ChatClient:
    def __init__(self, base_url: str, model: str, timeout: float = 180.0, extra: dict | None = None):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.extra = extra or {}

    def chat(self, messages: list[dict]) -> tuple[str, float, str | None, dict]:
        """-> (content, latency_seconds, error, usage). Max 2 retries (Table 4 failure handling).

        `usage` also carries `finish_reason` so truncated generations are visible.
        """
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": INFERENCE["temperature"],
            "top_p": INFERENCE["top_p"],
            "max_tokens": INFERENCE["max_tokens"],
            "stream": False,
        }
        if INFERENCE["top_k"] is not None:
            body["top_k"] = INFERENCE["top_k"]
        if INFERENCE["repetition_penalty"] is not None:
            body["repetition_penalty"] = INFERENCE["repetition_penalty"]
        body.update(self.extra)
        data = json.dumps(body).encode()
        last_err = None
        for attempt in range(INFERENCE["max_retries"] + 1):
            t0 = time.perf_counter()
            try:
                req = urllib.request.Request(
                    f"{self.base_url}/v1/chat/completions",
                    data=data,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    raw = resp.read().decode("utf-8", "replace")
                dt = time.perf_counter() - t0
                obj = json.loads(raw)
                choice = (obj.get("choices") or [{}])[0]
                msg = choice.get("message") or {}
                content = msg.get("content") or ""
                usage = dict(obj.get("usage") or {})
                usage["finish_reason"] = choice.get("finish_reason")
                return content, dt, None, usage
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as e:
                last_err = f"{type(e).__name__}: {e}"
                time.sleep(1.0 + attempt)
        return "", 0.0, last_err, {}
