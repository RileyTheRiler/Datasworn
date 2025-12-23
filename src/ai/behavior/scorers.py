"""Reusable scoring primitives for tactical AI decisions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class ScoreContext:
    """Normalized state passed into scorers.

    Values are expected to be in the 0-1 range where possible so they can be
    combined across multiple scorers without bespoke scaling logic in callers.
    """

    threat_level: float = 0.0
    health: float = 1.0
    ammo: float = 1.0
    cover_value: float = 0.0
    distance_to_target: float = 0.5
    flank_exposure: float = 0.3
    allies_nearby: int = 0
    resources_available: float = 0.5
    objective_pressure: float = 0.5
    map_control: float = 0.5

    def clamp(self) -> "ScoreContext":
        """Clamp all numeric values to 0-1 to keep scoring stable."""

        def _c(val: float) -> float:
            return max(0.0, min(1.0, val))

        return ScoreContext(
            threat_level=_c(self.threat_level),
            health=_c(self.health),
            ammo=_c(self.ammo),
            cover_value=_c(self.cover_value),
            distance_to_target=_c(self.distance_to_target),
            flank_exposure=_c(self.flank_exposure),
            allies_nearby=self.allies_nearby,
            resources_available=_c(self.resources_available),
            objective_pressure=_c(self.objective_pressure),
            map_control=_c(self.map_control),
        )


class Scorer(Protocol):
    """Protocol for scoring strategies."""

    name: str

    def score(self, context: ScoreContext) -> tuple[float, str]:
        ...


@dataclass
class ThreatScorer:
    """Score based on enemy threat and survivability."""

    name: str = "threat"
    weight: float = 1.0

    def score(self, context: ScoreContext) -> tuple[float, str]:
        ctx = context.clamp()
        survival_pressure = (1.0 - ctx.health) * 0.6
        ally_confidence = min(0.5, 0.1 * ctx.allies_nearby)
        raw = ctx.threat_level + survival_pressure - ally_confidence
        return self.weight * raw, (
            f"threat={ctx.threat_level:.2f} health_pressure={survival_pressure:.2f} "
            f"ally_relief={ally_confidence:.2f}"
        )


@dataclass
class ResourceScorer:
    """Score based on consumables and reload pressure."""

    name: str = "resources"
    weight: float = 1.0

    def score(self, context: ScoreContext) -> tuple[float, str]:
        ctx = context.clamp()
        scarcity = 1.0 - ctx.resources_available
        ammo_pressure = 1.0 - ctx.ammo
        raw = max(0.0, scarcity * 0.6 + ammo_pressure * 0.4)
        return self.weight * raw, (
            f"resource_scarcity={scarcity:.2f} ammo_pressure={ammo_pressure:.2f}"
        )


@dataclass
class PositionScorer:
    """Score based on positional advantage such as cover and flanking."""

    name: str = "position"
    weight: float = 1.0

    def score(self, context: ScoreContext) -> tuple[float, str]:
        ctx = context.clamp()
        cover_bonus = 1.0 - ctx.cover_value
        distance_penalty = ctx.distance_to_target * 0.5
        flank_penalty = ctx.flank_exposure * 0.5
        raw = max(0.0, cover_bonus + distance_penalty + flank_penalty)
        return self.weight * raw, (
            f"cover_gap={cover_bonus:.2f} distance_penalty={distance_penalty:.2f} "
            f"flank_penalty={flank_penalty:.2f}"
        )


@dataclass
class CompositeScorer:
    """Combine multiple scorers for aggregate insight."""

    name: str
    scorers: list[Scorer]
    weight: float = 1.0

    def score(self, context: ScoreContext) -> tuple[float, str]:
        details: list[str] = []
        total = 0.0
        for scorer in self.scorers:
            value, reason = scorer.score(context)
            total += value
            details.append(f"{scorer.name}:{value:.2f} ({reason})")
        return self.weight * total, " | ".join(details)
