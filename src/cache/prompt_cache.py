from __future__ import annotations

import hashlib
from typing import Any, TYPE_CHECKING

from src.cache.persistent_cache import PersistentTTLCache

if TYPE_CHECKING:
    from src.prompting import PromptContext


class PromptResultCache(PersistentTTLCache):
    """Cache for prompt/results with TTL persistence."""

    def __init__(self, ttl_seconds: int = 1800, directory: str | None = None):
        super().__init__("prompt_results", ttl_seconds=ttl_seconds, directory=directory)

    def make_key(self, prompt: str, context: "PromptContext" | None = None) -> str:
        context_text = context.formatted_context() if context else ""
        payload = f"{prompt}\n---\n{context_text}".encode("utf-8", errors="ignore")
        return hashlib.sha256(payload).hexdigest()

    def get_prompt(self, prompt: str, context: "PromptContext" | None = None) -> Any:
        return self.get(self.make_key(prompt, context))

    def store_prompt(self, prompt: str, context: "PromptContext" | None, value: Any) -> None:
        self.set(self.make_key(prompt, context), value)
