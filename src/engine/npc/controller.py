"""NPC controller orchestrating perception, memory, reasoning, and behavior."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from contextlib import nullcontext

from src.game_director import GamePhase, PhaseController
from ..profiling import FrameProfiler
from .behavior import ActionPlan, BehaviorPlanner, FactChecker
from .memory import SemanticMemory, WorkingMemory
from .perception import PerceptionSystem, WorldState
from .personality import EmotionalState, PersonalityProfile
from .reasoning import Goal, Intention, ReasoningInput, UtilityReasoner


FORBIDDEN_TOPICS = {"player", "hardware", "engine", "developer", "fourth wall"}


def sanitize_dialogue(text: str) -> str:
    lowered = text.lower()
    if any(topic in lowered for topic in FORBIDDEN_TOPICS):
        return "..."
    return text


@dataclass
class NPCController:
    personality: PersonalityProfile
    goals: list[Goal]
    emotional_state: EmotionalState
    perception: PerceptionSystem = field(default_factory=PerceptionSystem)
    working_memory: WorkingMemory = field(default_factory=WorkingMemory)
    semantic_memory: SemanticMemory = field(default_factory=SemanticMemory)
    reasoner: UtilityReasoner = field(default_factory=UtilityReasoner)
    fact_checker: FactChecker = field(default_factory=FactChecker)
    profiler: FrameProfiler | None = None
    debug: bool = False

    def __post_init__(self) -> None:
        self.behavior = BehaviorPlanner(
            self.personality,
            self.fact_checker,
            debug=self.debug,
            profiler=self.profiler,
        )
        # Propagate profiler to subsystems if provided
        if self.profiler:
            self.perception.profiler = self.profiler
            self.working_memory.profiler = self.profiler
            self.semantic_memory.profiler = self.profiler
            self.reasoner.profiler = self.profiler

    def _profile(self, label: str):
        if not self.profiler:
            return nullcontext()
        return self.profiler.span(label)

    def tick(
        self,
        scene_graph: dict[str, Any],
        environment: dict[str, Any],
        phase_controller: PhaseController | None = None,
    ) -> ActionPlan:
        def _execute() -> ActionPlan:
    def tick(self, scene_graph: dict[str, Any], environment: dict[str, Any]) -> ActionPlan:
        with self._profile("controller.total"):
            world_state = self.perception.perceive(scene_graph)
            self._update_memory(world_state)

            reasoning_input = ReasoningInput(
                goals=self.goals,
                personality=self.personality,
                emotional_state=self.emotional_state,
                memories=self._collect_memories(),
                context={"lighting": world_state.lighting, "time_of_day": world_state.time_of_day},
            )
            intention = self.reasoner.choose_intention(reasoning_input)
            plan = self.behavior.plan(intention, environment)
            plan = self._apply_dialogue_rules(plan)
            self._log_debug(world_state, intention, plan)
            return plan

        if phase_controller:
            return phase_controller.execute_phase(GamePhase.AI_RESPONSE, _execute)
        return _execute()

    def _update_memory(self, world_state: WorldState) -> None:
        with self._profile("controller.memory"):
            for fact in world_state.actors + world_state.objects + world_state.sounds:
                self.working_memory.record(fact)
            self.semantic_memory.consolidate(self.working_memory.salient_entries())
            self.working_memory.tick(1.0)
            self.semantic_memory.decay()

    def _collect_memories(self) -> list:
        short_term = self.working_memory.salient_entries()
        long_term = self.semantic_memory.retrieve()
        return short_term + long_term

    def _apply_dialogue_rules(self, plan: ActionPlan) -> ActionPlan:
        with self._profile("controller.dialogue_rules"):
            dialogue = plan.parameters.get("dialogue")
            if dialogue:
                dialogue = sanitize_dialogue(dialogue)
                plan.parameters["dialogue"] = dialogue
            return plan

    def _log_debug(self, world_state: WorldState, intention: Intention, plan: ActionPlan) -> None:
        if not self.debug:
            return
        print("[Controller] WorldState actors:", [(f.identifier, f.confidence) for f in world_state.actors])
        print("[Controller] WorldState objects:", [(f.identifier, f.confidence) for f in world_state.objects])
        print("[Controller] WorldState sounds:", [(f.identifier, f.confidence) for f in world_state.sounds])
        print("[Controller] Intention:", intention)
        print("[Controller] Plan:", plan)
