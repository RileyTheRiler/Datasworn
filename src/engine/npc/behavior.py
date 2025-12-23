"""Behavior planning that respects environment constraints and confidence checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from contextlib import nullcontext

from ..profiling import FrameProfiler
from .personality import PersonalityProfile
from .reasoning import Intention


@dataclass
class ActionPlan:
    action: str
    parameters: dict[str, Any]
    rationale: str


class FactChecker:
    """Rejects low-confidence assertions to reduce hallucinations."""

    def __init__(self, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold

    def validate(self, intention: Intention) -> Intention:
        if intention.confidence < self.confidence_threshold:
            return Intention(
                action="hesitate",
                rationale="Insufficient confidence to act",
                confidence=intention.confidence,
            )
        return intention

    def filter_dialogue(self, text: str, confidence: float) -> str:
        if confidence < self.confidence_threshold:
            return "I'm not sure about that." if confidence > 0.2 else "..."
        return text


class BehaviorPlanner:
    """Selects animations and dialogue while respecting constraints."""

    def __init__(
        self,
        personality: PersonalityProfile,
        fact_checker: FactChecker | None = None,
        debug: bool = False,
        profiler: FrameProfiler | None = None,
    ):
        self.personality = personality
        self.fact_checker = fact_checker or FactChecker()
        self.debug = debug
        self.profiler = profiler

    def plan(self, intention: Intention, environment: dict[str, Any]) -> ActionPlan:
        with (self.profiler.span("behavior.plan") if self.profiler else nullcontext()):
            safe_intention = self.fact_checker.validate(intention)
            if not self._is_reachable(environment):
                safe_intention = Intention(
                    action="reconsider",
                    rationale="Path blocked",
                    confidence=min(safe_intention.confidence, 0.6),
                )

            parameters: dict[str, Any] = {}
            if safe_intention.action.startswith("offer"):
                parameters["dialogue"] = self._safe_dialogue("I can help you.", safe_intention.confidence)
            elif safe_intention.action.startswith("investigate"):
                parameters["animation"] = "scan_area"
            elif safe_intention.action == "seek_cover":
                parameters["animation"] = "run_to_cover"
            else:
                parameters["animation"] = "idle" if safe_intention.action == "idle" else "gesture"

            if self.debug:
                print("[Behavior] action:", safe_intention.action, "params:", parameters)

            return ActionPlan(action=safe_intention.action, parameters=parameters, rationale=safe_intention.rationale)

    def _is_reachable(self, environment: dict[str, Any]) -> bool:
        if environment.get("path_blocked"):
            return False
        affordances = environment.get("affordances", [])
        if affordances and environment.get("required_affordance") and environment["required_affordance"] not in affordances:
            return False
        return True

    def _safe_dialogue(self, text: str, confidence: float) -> str:
        filtered = self.fact_checker.filter_dialogue(text, confidence)
        return self.personality.modulate_dialogue(filtered)
