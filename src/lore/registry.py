"""Lore registry and codex search utilities.

The registry is responsible for loading lore entries from ``data/lore`` and
providing simple search/filter capabilities for both the CLI codex and the
front-end codex browser.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Sequence, TYPE_CHECKING
import json


@dataclass
class NarrativeCallback:
    """Callback text surfaced when a matching narrative trigger fires."""

    trigger: str
    response: str
    weight: float = 1.0

    @classmethod
    def from_dict(cls, raw: dict) -> "NarrativeCallback":
        return cls(
            trigger=raw.get("trigger", ""),
            response=raw.get("response", ""),
            weight=float(raw.get("weight", 1.0)),
        )


@dataclass
class LoreEntry:
    """Single lore entry in the codex."""

    id: str
    title: str
    category: str
    summary: str
    factions: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    items: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    discoveries: List[str] = field(default_factory=list)
    callbacks: List[NarrativeCallback] = field(default_factory=list)
    discovered: bool = False
    discovery_notes: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, raw: dict) -> "LoreEntry":
        callbacks = [NarrativeCallback.from_dict(cb) for cb in raw.get("callbacks", [])]
        return cls(
            id=raw.get("id", raw.get("title", "")).strip(),
            title=raw.get("title", "Untitled"),
            category=raw.get("category", "misc"),
            summary=raw.get("summary", ""),
            factions=list(raw.get("factions", [])),
            locations=list(raw.get("locations", [])),
            items=list(raw.get("items", [])),
            keywords=[kw.lower() for kw in raw.get("keywords", [])],
            discoveries=list(raw.get("discoveries", [])),
            callbacks=callbacks,
            discovered=raw.get("discovered", False),
            discovery_notes=list(raw.get("discovery_notes", [])),
        )

    def matches_text(self, query: str) -> bool:
        if not query:
            return True
        q = query.lower()
        haystacks = [
            self.title.lower(),
            self.summary.lower(),
            " ".join(self.keywords),
            " ".join(self.factions).lower(),
            " ".join(self.locations).lower(),
            " ".join(self.items).lower(),
        ]
        return any(q in hay for hay in haystacks)

    def matches_filters(
        self,
        factions: Iterable[str] | None = None,
        locations: Iterable[str] | None = None,
        items: Iterable[str] | None = None,
    ) -> bool:
        def _subset(filter_values: Iterable[str] | None, haystack: Sequence[str]) -> bool:
            if not filter_values:
                return True
            normalized = {v.lower() for v in filter_values if v}
            if not normalized:
                return True
            return normalized.issubset({h.lower() for h in haystack})

        return (
            _subset(factions, self.factions)
            and _subset(locations, self.locations)
            and _subset(items, self.items)
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "summary": self.summary,
            "factions": self.factions,
            "locations": self.locations,
            "items": self.items,
            "keywords": self.keywords,
            "discoveries": self.discoveries,
            "callbacks": [cb.__dict__ for cb in self.callbacks],
            "discovered": self.discovered,
            "discovery_notes": self.discovery_notes,
        }

    def mark_discovered(self, note: str | None = None) -> None:
        if not self.discovered:
            self.discovered = True
        if note:
            self.discovery_notes.append(note)


if TYPE_CHECKING:  # pragma: no cover
    from src.persistent_world import WorldChange


class LoreRegistry:
    """Load and search lore entries from disk."""

    def __init__(self, lore_path: Path | str = Path("data/lore")):
        self.lore_path = Path(lore_path)
        self.entries: list[LoreEntry] = []
        self._load_entries()

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------
    def _load_entries(self) -> None:
        if not self.lore_path.exists():
            return

        for path in sorted(self.lore_path.glob("*.json")):
            try:
                raw = json.loads(path.read_text())
            except Exception:
                continue

            records = raw if isinstance(raw, list) else raw.get("entries", [])
            for entry_raw in records:
                entry = LoreEntry.from_dict(entry_raw)
                if entry.id:
                    self.entries.append(entry)

    # ------------------------------------------------------------------
    # Search + Filters
    # ------------------------------------------------------------------
    def search(
        self,
        query: str = "",
        factions: Iterable[str] | None = None,
        locations: Iterable[str] | None = None,
        items: Iterable[str] | None = None,
    ) -> list[LoreEntry]:
        results = [
            entry
            for entry in self.entries
            if entry.matches_text(query)
            and entry.matches_filters(factions=factions, locations=locations, items=items)
        ]
        # Sort discovered entries first, then alphabetically
        return sorted(results, key=lambda e: (not e.discovered, e.title.lower()))

    def get_entry(self, entry_id: str) -> LoreEntry | None:
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None

    # ------------------------------------------------------------------
    # Discovery/Narrative integration
    # ------------------------------------------------------------------
    def link_world_change(self, change: "WorldChange") -> list[LoreEntry]:
        """Mark entries as discovered when world changes reference them."""

        matched: list[LoreEntry] = []
        for entry in self.entries:
            if self._change_matches_entry(change, entry):
                entry.mark_discovered(change.description)
                matched.append(entry)
        return matched

    def _change_matches_entry(self, change: "WorldChange", entry: LoreEntry) -> bool:
        entity = change.entity_id.lower()
        return (
            entity in (id.lower() for id in entry.discoveries)
            or entity in (f.lower() for f in entry.factions)
            or entity in (loc.lower() for loc in entry.locations)
            or entity in (item.lower() for item in entry.items)
        )

    def narrative_callbacks(self, trigger: str, include_undiscovered: bool = False) -> list[str]:
        """Collect callback text for a given narrative trigger."""

        callbacks: list[str] = []
        for entry in self.entries:
            if not include_undiscovered and not entry.discovered:
                continue
            for cb in entry.callbacks:
                if cb.trigger.lower() == trigger.lower():
                    callbacks.append(cb.response)
        return callbacks
