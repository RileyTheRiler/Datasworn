"""Lightweight cognition loop utilities for NPC simulation.

The module is intentionally deterministic and free of network calls so it can
be stress-tested in CI.  It focuses on three pillars:
- Perception filtering with confidence scoring (sight + hearing).
- Short-term memory with TTL and decay-based relevance ordering.
- A budget-aware cognition loop with knobs for tick frequency and LOD.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Sequence
import math
import time


@dataclass
class Stimulus:
    """A sensory input the NPC might react to."""

    id: str
    position: tuple[float, float]
    volume: float = 0.0
    occluded: bool = False
    fact: str | None = None


class PerceptionSystem:
    """Applies visibility/hearing filters and scores confidence."""

    def __init__(self, vision_range: float = 12.0, hearing_range: float = 8.0):
        self.vision_range = vision_range
        self.hearing_range = hearing_range

    @staticmethod
    def _distance(a: tuple[float, float], b: tuple[float, float]) -> float:
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def can_see(self, observer: tuple[float, float], stimulus: Stimulus) -> bool:
        if stimulus.occluded:
            return False
        return self._distance(observer, stimulus.position) <= self.vision_range

    def can_hear(self, observer: tuple[float, float], stimulus: Stimulus) -> bool:
        if stimulus.volume <= 0:
            return False
        return self._distance(observer, stimulus.position) <= self.hearing_range

    def filter(self, observer: tuple[float, float], stimuli: Iterable[Stimulus]) -> list[Stimulus]:
        """Return stimuli that are either visible or audible."""

        allowed: list[Stimulus] = []
        for stim in stimuli:
            if self.can_see(observer, stim) or self.can_hear(observer, stim):
                allowed.append(stim)
        return allowed

    def confidence(self, observer: tuple[float, float], stimulus: Stimulus) -> float:
        """Combine sensory channels into a confidence score."""

        score = 0.0
        if self.can_see(observer, stimulus):
            score += 0.65
        if self.can_hear(observer, stimulus):
            score += 0.35 if stimulus.occluded else 0.25
        return min(1.0, score)


@dataclass(order=True)
class MemoryTrace:
    """A decaying memory of a stimulus."""

    sort_index: float = field(init=False, repr=False)
    stimulus: Stimulus
    stored_at: float
    ttl: float
    relevance: float = 1.0

    def __post_init__(self) -> None:
        self.sort_index = -self.relevance

    def apply_decay(self, now: float, decay_rate: float) -> None:
        elapsed = max(0.0, now - self.stored_at)
        self.relevance = max(0.0, self.relevance - elapsed * decay_rate)
        self.sort_index = -self.relevance

    def is_expired(self, now: float) -> bool:
        return now - self.stored_at >= self.ttl or self.relevance <= 0.0


class WorkingMemory:
    """Short-term memory with TTL and decay-based ordering."""

    def __init__(self, decay_rate: float = 0.05):
        self.decay_rate = decay_rate
        self._traces: list[MemoryTrace] = []

    def remember(self, stimulus: Stimulus, ttl: float = 5.0, relevance: float = 1.0, now: float | None = None) -> None:
        timestamp = time.perf_counter() if now is None else now
        self._traces.append(MemoryTrace(stimulus=stimulus, stored_at=timestamp, ttl=ttl, relevance=relevance))

    def advance_time(self, now: float | None = None) -> None:
        current = time.perf_counter() if now is None else now
        for trace in list(self._traces):
            trace.apply_decay(current, self.decay_rate)
            if trace.is_expired(current):
                self._traces.remove(trace)

    def ordered_traces(self) -> list[MemoryTrace]:
        return sorted(self._traces)

    @property
    def count(self) -> int:
        return len(self._traces)


@dataclass
class SceneContext:
    """Simple container for reachability and knowledge checks used in tests."""

    reachable_tiles: set[tuple[float, float]]
    known_facts: set[str]

    def is_reachable(self, position: tuple[float, float]) -> bool:
        return position in self.reachable_tiles

    def knows_fact(self, fact: str | None) -> bool:
        return fact is None or fact in self.known_facts


class DialogueEngine:
    """Scripted dialogue generator that respects personality tone and guardrails."""

    def __init__(self, tone: str = "stoic"):
        self.tone = tone
        self.banned_phrases = {"video game", "player", "fourth wall", "tutorial"}

    def _strip_fourth_wall(self, text: str) -> str:
        lowered = text.lower()
        for phrase in self.banned_phrases:
            if phrase in lowered:
                text = text.replace(phrase, "")
        return text

    def _apply_tone(self, text: str) -> str:
        if self.tone == "stoic":
            return f"(measured) {text}".strip()
        if self.tone == "cheerful":
            return f"(warm) {text}".strip()
        return text

    def compose(self, fact: str, hallucination: bool = False) -> str:
        if hallucination:
            return ""

        safe = self._strip_fourth_wall(fact)
        return self._apply_tone(safe)


class CognitionLoop:
    """Budget-aware cognition loop with perception and memory integration."""

    def __init__(
        self,
        observer: tuple[float, float] = (0.0, 0.0),
        frame_budget_ms: float = 4.0,
        tick_frequency: float = 30.0,
        lod_factor: float = 1.0,
        time_provider=time.perf_counter,
    ):
        self.observer = observer
        self.frame_budget_ms = frame_budget_ms
        self.tick_frequency = tick_frequency
        self.lod_factor = max(1.0, lod_factor)
        self.time_provider = time_provider
        self.perception = PerceptionSystem()
        self.memory = WorkingMemory()
        self.dialogue_engine = DialogueEngine()
        self._last_tick = None

    def _should_tick(self, now: float) -> bool:
        if self._last_tick is None:
            return True
        min_interval = 1.0 / self.tick_frequency
        return (now - self._last_tick) >= min_interval

    def _apply_lod(self, stimuli: Sequence[Stimulus]) -> list[Stimulus]:
        step = int(round(self.lod_factor))
        if step <= 1:
            return list(stimuli)
        return list(stimuli)[::step]

    def tick(self, stimuli: Sequence[Stimulus], context: SceneContext, now: float | None = None) -> dict:
        start = self.time_provider() if now is None else now
        if not self._should_tick(start):
            return {"actions": [], "dialogue": [], "within_budget": True}

        actions: List[str] = []
        dialogue: List[str] = []

        visible = self.perception.filter(self.observer, self._apply_lod(stimuli))
        for stim in visible:
            self.memory.remember(stim, ttl=3.5, relevance=self.perception.confidence(self.observer, stim), now=start)
            if not context.is_reachable(stim.position):
                continue
            actions.append(f"investigate:{stim.id}")
            if not stim.occluded and context.knows_fact(stim.fact):
                line = self.dialogue_engine.compose(stim.fact or stim.id)
                if line:
                    dialogue.append(line)

        self.memory.advance_time(start)
        elapsed_ms = (self.time_provider() - start) * 1000.0
        self._last_tick = start

        return {"actions": actions, "dialogue": dialogue, "within_budget": elapsed_ms <= self.frame_budget_ms}

    def update_tick_frequency(self, hz: float) -> None:
        self.tick_frequency = max(1.0, hz)

    def update_lod(self, lod_factor: float) -> None:
        self.lod_factor = max(1.0, lod_factor)

    def set_tone(self, tone: str) -> None:
        self.dialogue_engine.tone = tone
