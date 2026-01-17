"""Tactical encounter manager that blends utility scoring with cover heuristics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List

from src.ai.behavior import (
    BehaviorOption,
    DecisionBreakdown,
    PositionScorer,
    ResourceScorer,
    ScoreContext,
    ThreatScorer,
    UtilityBehaviorController,
)


@dataclass
class CombatantState:
    """State for a single participant in combat."""

    id: str
    name: str
    health: float = 1.0
    ammo: float = 1.0
    threat: float = 0.5
    position: tuple[float, float] = (0.0, 0.0)
    in_cover: bool = False
    cover_quality: float = 0.0
    allies_nearby: int = 0
    distance_to_objective: float = 0.5


@dataclass
class EncounterState:
    """Aggregate state for the current encounter."""

    enemies: list[CombatantState]
    party: list[CombatantState]
    map_control: float = 0.5
    cover_density: float = 0.5
    objective_pressure: float = 0.5


@dataclass
class EncounterDecision:
    """Selected action and full ranking for a single actor."""

    chosen: DecisionBreakdown
    ranked: list[DecisionBreakdown]
    debug_log: list[str] = field(default_factory=list)


class EncounterManager:
    """Evaluate tactical options for combatants."""

    def __init__(self):
        self._logs: list[str] = []

    def build_context(self, actor: CombatantState, encounter: EncounterState) -> ScoreContext:
        nearest_enemy = min(encounter.enemies, key=lambda e: self._distance(actor.position, e.position), default=None)
        distance = self._distance(actor.position, nearest_enemy.position) if nearest_enemy else 0.5
        flank_exposure = 1.0 - actor.cover_quality if not actor.in_cover else max(0.0, 0.6 - actor.cover_quality)
        return ScoreContext(
            threat_level=actor.threat,
            health=actor.health,
            ammo=actor.ammo,
            cover_value=actor.cover_quality,
            distance_to_target=min(1.0, distance),
            flank_exposure=flank_exposure,
            allies_nearby=actor.allies_nearby,
            resources_available=actor.ammo,
            objective_pressure=encounter.objective_pressure,
            map_control=encounter.map_control,
        )

    def _distance(self, a: tuple[float, float], b: tuple[float, float]) -> float:
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5

    def _behavior_options(self) -> list[BehaviorOption]:
        return [
            BehaviorOption(
                action="take_cover",
                scorers=[PositionScorer(weight=1.0), ThreatScorer(weight=0.8)],
                bias=0.05,
            ),
            BehaviorOption(
                action="focus_fire",
                scorers=[ThreatScorer(weight=1.15), PositionScorer(weight=0.65)],
                bias=0.05,
            ),
            BehaviorOption(
                action="advance",
                scorers=[PositionScorer(weight=0.9)],
                bias=-0.1,
            ),
            BehaviorOption(
                action="reload",
                scorers=[ResourceScorer(weight=1.2), ThreatScorer(weight=0.4)],
                bias=0.0,
            ),
            BehaviorOption(
                action="regroup",
                scorers=[ThreatScorer(weight=1.0), PositionScorer(weight=0.7)],
                bias=0.05,
            ),
        ]

    def evaluate_turn(self, actor: CombatantState, encounter: EncounterState, *, dump_debug: bool = False) -> EncounterDecision:
        context = self.build_context(actor, encounter)
        controller = UtilityBehaviorController(self._behavior_options())
        chosen, ranked = controller.evaluate(context)

        if dump_debug:
            debug_lines = [f"{b.action}: {b.score:.2f} -> {' | '.join(b.rationale)}" for b in ranked]
            self._logs.extend(debug_lines)
        else:
            debug_lines = []

        return EncounterDecision(chosen=chosen, ranked=ranked, debug_log=debug_lines)

    def build_action_heuristic(self, actor: CombatantState, encounter: EncounterState):
        def _heuristic(action, state) -> tuple[float, str]:
            context = self.build_context(actor, encounter)
            controller = UtilityBehaviorController(self._behavior_options())
            _, ranked = controller.evaluate(context)
            ranked_map = {b.action: b for b in ranked}
            breakdown = ranked_map.get(action.name)
            if breakdown:
                return min(0.9, breakdown.score / 5.0), " | ".join(breakdown.rationale)
            return 0.0, ""

        return _heuristic

    def debug_log(self) -> List[str]:
        return list(self._logs)


def summarize_decisions(decisions: Iterable[EncounterDecision]) -> str:
    lines = []
    for decision in decisions:
        lines.append(f"- {decision.chosen.action}: {decision.chosen.score:.2f}")
    return "\n".join(lines)
