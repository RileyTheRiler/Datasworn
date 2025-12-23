"""NPC memory subsystem with working and semantic buffers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable
import time

from .perception import PerceivedFact


@dataclass
class MemoryEntry:
    """A memory record tied to perceptual confidence and relevance."""

    content: str
    confidence: float
    relevance: float = 1.0
    ttl: float = 10.0
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def alive(self, now: float | None = None) -> bool:
        now = now or time.time()
        return (now - self.created_at) <= self.ttl

    def decay(self, amount: float) -> None:
        self.ttl = max(0.0, self.ttl - amount)
        self.relevance = max(0.0, self.relevance - amount * 0.1)


class WorkingMemory:
    """Short-term buffer with TTL-based eviction."""

    def __init__(self, base_ttl: float = 10.0):
        self.base_ttl = base_ttl
        self._entries: list[MemoryEntry] = []

    def record(self, fact: PerceivedFact) -> MemoryEntry:
        ttl = self.base_ttl * fact.confidence
        entry = MemoryEntry(
            content=f"{fact.category}:{fact.identifier}",
            confidence=fact.confidence,
            relevance=fact.confidence,
            ttl=ttl,
            metadata={"details": fact.details},
        )
        self._entries.append(entry)
        return entry

    def tick(self, amount: float = 1.0) -> None:
        for entry in list(self._entries):
            entry.decay(amount)
            if not entry.alive():
                self._entries.remove(entry)

    def salient_entries(self, threshold: float = 0.4) -> list[MemoryEntry]:
        return [entry for entry in self._entries if entry.confidence >= threshold and entry.alive()]


class SemanticMemory:
    """Long-term storage informed by working memory salience and relevance."""

    def __init__(self, decay_rate: float = 0.01):
        self.decay_rate = decay_rate
        self._entries: list[MemoryEntry] = []

    def consolidate(self, working_entries: Iterable[MemoryEntry]) -> None:
        for entry in working_entries:
            existing = self._find_existing(entry.content)
            if existing:
                existing.relevance = min(1.0, existing.relevance + entry.relevance * 0.5)
                existing.confidence = max(existing.confidence, entry.confidence)
            elif entry.confidence > 0.5:
                promoted = MemoryEntry(
                    content=entry.content,
                    confidence=entry.confidence,
                    relevance=min(1.0, entry.relevance + 0.2),
                    ttl=float("inf"),
                    metadata=entry.metadata,
                )
                self._entries.append(promoted)

    def retrieve(self, limit: int = 5) -> list[MemoryEntry]:
        sorted_entries = sorted(self._entries, key=lambda e: (e.relevance, e.confidence), reverse=True)
        return sorted_entries[:limit]

    def decay(self) -> None:
        for entry in list(self._entries):
            entry.decay(self.decay_rate)
            if entry.relevance <= 0:
                self._entries.remove(entry)

    def _find_existing(self, content: str) -> MemoryEntry | None:
        for entry in self._entries:
            if entry.content == content:
                return entry
        return None
