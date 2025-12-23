"""Goal- and utility-based reasoning for NPCs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from contextlib import nullcontext

from ..profiling import FrameProfiler
from .memory import MemoryEntry
from .personality import EmotionalState, PersonalityProfile


@dataclass
class Goal:
    name: str
    priority: float = 1.0
    desired_outcome: str | None = None


@dataclass
class Intention:
    """Chosen intention and why it matters."""

    action: str
    rationale: str
    confidence: float


@dataclass
class ReasoningInput:
    goals: list[Goal]
    personality: PersonalityProfile
    emotional_state: EmotionalState
    memories: list[MemoryEntry]
    context: dict[str, Any] | None = None


class UtilityReasoner:
    """Combines goals, personality, and memory signals into an intention."""

    def __init__(self, debug: bool = False, profiler: FrameProfiler | None = None):
        self.debug = debug
        self.profiler = profiler

    def choose_intention(self, reasoning_input: ReasoningInput) -> Intention:
        with (self.profiler.span("reasoning.choose_intention") if self.profiler else nullcontext()):
            scored_goals = [self._score_goal(goal, reasoning_input) for goal in reasoning_input.goals]
            if not scored_goals:
                return Intention(action="idle", rationale="No active goals", confidence=0.2)

            best_goal, best_score = max(scored_goals, key=lambda item: item[1])
            action = self._derive_action(best_goal, reasoning_input)
            rationale = f"Pursuing {best_goal.name} with score {best_score:.2f}"

            if self.debug:
                print("[Reasoning] goal scores:", [(g.name, f"{s:.2f}") for g, s in scored_goals])
                print("[Reasoning] chosen action:", action)

            return Intention(action=action, rationale=rationale, confidence=min(1.0, best_score))

    def _score_goal(self, goal: Goal, reasoning_input: ReasoningInput) -> tuple[Goal, float]:
        personality_weight = reasoning_input.personality.utility_modifier(goal)
        emotion_weight = reasoning_input.emotional_state.utility_bias()
        memory_boost = self._memory_support(goal, reasoning_input.memories)
        score = goal.priority * personality_weight * emotion_weight + memory_boost
        return goal, max(0.0, score)

    def _memory_support(self, goal: Goal, memories: list[MemoryEntry]) -> float:
        reinforcing = [m for m in memories if goal.name in m.content]
        if not reinforcing:
            return 0.0
        return min(0.5, sum(m.confidence * m.relevance for m in reinforcing))

    def _derive_action(self, goal: Goal, reasoning_input: ReasoningInput) -> str:
        curiosity = reasoning_input.personality.traits.curiosity
        if goal.name.lower().startswith("investigate") and curiosity > 0.5:
            return "investigate_area"
        if goal.name.lower().startswith("assist") and reasoning_input.personality.traits.empathy > 0.6:
            return "offer_help"
        if goal.name.lower().startswith("flee") or reasoning_input.emotional_state.is_afraid():
            return "seek_cover"
        return goal.desired_outcome or "pursue_goal"
