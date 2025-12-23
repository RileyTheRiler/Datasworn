"""Utility-based behavior selection built on modular scorers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Tuple

from .scorers import ScoreContext, Scorer


@dataclass
class DecisionBreakdown:
    """Captures how a single behavior was scored."""

    action: str
    score: float
    rationale: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"action": self.action, "score": self.score, "rationale": list(self.rationale)}


@dataclass
class BehaviorOption:
    """A candidate action with a set of scorers."""

    action: str
    scorers: list[Scorer]
    bias: float = 0.0

    def evaluate(self, context: ScoreContext) -> DecisionBreakdown:
        score = self.bias
        rationale: list[str] = []
        for scorer in self.scorers:
            value, reason = scorer.score(context)
            score += value
            rationale.append(f"{scorer.name}:{value:.2f} -> {reason}")
        return DecisionBreakdown(action=self.action, score=score, rationale=rationale)


class UtilityBehaviorController:
    """Evaluate behavior options and surface a ranked decision."""

    def __init__(self, options: Iterable[BehaviorOption]):
        self.options: List[BehaviorOption] = list(options)
        self.history: list[DecisionBreakdown] = []

    def evaluate(self, context: ScoreContext) -> Tuple[DecisionBreakdown, list[DecisionBreakdown]]:
        breakdowns = [opt.evaluate(context) for opt in self.options]
        breakdowns.sort(key=lambda b: b.score, reverse=True)
        if breakdowns:
            self.history.append(breakdowns[0])
        return breakdowns[0], breakdowns

    def last_summary(self) -> str:
        if not self.history:
            return "No decisions recorded."
        last = self.history[-1]
        reasons = " | ".join(last.rationale)
        return f"{last.action}: {last.score:.2f} ({reasons})"
