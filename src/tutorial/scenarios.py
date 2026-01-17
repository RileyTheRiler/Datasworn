"""Structured tutorial scenarios with gated objectives and contextual prompts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional

CompletionCheck = Callable[[dict], bool]


@dataclass
class TutorialStep:
    """A single tutorial beat with gating and comprehension prompts."""

    id: str
    title: str
    objective: str
    prompt: str
    comprehension_check: str
    requires: List[str] = field(default_factory=list)
    hints: List[str] = field(default_factory=list)
    completion_check: Optional[CompletionCheck] = None

    def is_available(self, completed: Iterable[str]) -> bool:
        return all(req in completed for req in self.requires)

    def is_complete(self, context: dict) -> bool:
        if self.completion_check:
            try:
                return bool(self.completion_check(context))
            except Exception:
                return False
        return False


@dataclass
class TutorialScenario:
    """Ordered scenario for guiding a player through onboarding."""

    id: str
    title: str
    steps: List[TutorialStep]

    def get_step(self, step_id: str) -> Optional[TutorialStep]:
        return next((step for step in self.steps if step.id == step_id), None)

    def next_step(self, state: "TutorialState") -> Optional[TutorialStep]:
        completed = set(state.completed_steps + state.skipped_steps)
        available = state.completed_steps + state.skipped_steps
        for step in self.steps:
            if step.id in completed:
                continue
            if step.is_available(available):
                return step
        return None


@dataclass
class TutorialState:
    """Runtime state for a tutorial scenario."""

    scenario_id: str = "new_player_onboarding"
    current_step_id: Optional[str] = None
    completed_steps: List[str] = field(default_factory=list)
    skipped_steps: List[str] = field(default_factory=list)
    comprehension_notes: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "scenario_id": self.scenario_id,
            "current_step_id": self.current_step_id,
            "completed_steps": list(self.completed_steps),
            "skipped_steps": list(self.skipped_steps),
            "comprehension_notes": dict(self.comprehension_notes),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TutorialState":
        return cls(
            scenario_id=data.get("scenario_id", "new_player_onboarding"),
            current_step_id=data.get("current_step_id"),
            completed_steps=list(data.get("completed_steps", [])),
            skipped_steps=list(data.get("skipped_steps", [])),
            comprehension_notes=dict(data.get("comprehension_notes", {})),
        )


class TutorialEngine:
    """Lightweight controller that tracks progress and affords repeats/skips."""

    def __init__(self, scenario: TutorialScenario):
        self.scenario = scenario

    def start(self, state: TutorialState) -> TutorialState:
        if not state.current_step_id:
            step = self.scenario.next_step(state)
            state.current_step_id = step.id if step else None
        return state

    def current_step(self, state: TutorialState) -> Optional[TutorialStep]:
        if not state.current_step_id:
            self.start(state)
        if state.current_step_id:
            return self.scenario.get_step(state.current_step_id)
        return None

    def evaluate_progress(self, state: TutorialState, context: dict) -> Optional[str]:
        step = self.current_step(state)
        if not step:
            return None
        if step.is_complete(context):
            self.complete_step(state, comprehension=context.get("comprehension"))
            return step.id
        return None

    def complete_step(self, state: TutorialState, comprehension: Optional[str] = None) -> TutorialState:
        if state.current_step_id and state.current_step_id not in state.completed_steps:
            state.completed_steps.append(state.current_step_id)
        if comprehension and state.current_step_id:
            state.comprehension_notes[state.current_step_id] = comprehension
        state.current_step_id = None
        self.start(state)
        return state

    def skip_step(self, state: TutorialState) -> TutorialState:
        if state.current_step_id and state.current_step_id not in state.skipped_steps:
            state.skipped_steps.append(state.current_step_id)
        state.current_step_id = None
        self.start(state)
        return state

    def repeat_step(self, state: TutorialState) -> TutorialState:
        # Repeat keeps the current step ID but refreshes it as the active step.
        if not state.current_step_id:
            step = self.scenario.next_step(state)
            state.current_step_id = step.id if step else None
        return state

    def progress_percent(self, state: TutorialState) -> float:
        total = len(self.scenario.steps)
        if total == 0:
            return 0.0
        done = len(set(state.completed_steps + state.skipped_steps))
        return round((done / total) * 100, 2)

    def overlay_text(self, state: TutorialState) -> str:
        step = self.current_step(state)
        if not step:
            return "Tutorial complete — you can toggle overlays off in settings." if state.completed_steps else "No tutorial steps configured."

        progress = self.progress_percent(state)
        lines = [
            f"**{self.scenario.title}** — {progress}% complete",
            f"Step {len(state.completed_steps) + 1}/{len(self.scenario.steps)}: **{step.title}**",
            f"Objective: {step.objective}",
            f"Prompt: {step.prompt}",
        ]
        if step.hints:
            lines.append("Hints:")
            lines.extend([f"- {hint}" for hint in step.hints])
        lines.append(f"Comprehension check: {step.comprehension_check}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Default scenario
# ---------------------------------------------------------------------------

def get_new_player_scenario() -> TutorialScenario:
    """Default onboarding flow for new players."""

    steps = [
        TutorialStep(
            id="create-character",
            title="Create your hero",
            objective="Fill in the character sheet fields and start the session.",
            prompt="Name your character and confirm their stats to begin.",
            comprehension_check="Can you see your stats and starting vow in the sidebar?",
            hints=["Use the character creation form before sending chat messages."],
            completion_check=lambda ctx: bool(ctx.get("character_created")),
        ),
        TutorialStep(
            id="submit-action",
            title="Try an action",
            objective="Submit your first in-fiction action or question.",
            prompt="Type a short action like 'secure an advantage at the derelict station.'",
            comprehension_check="Did the system echo your action into the chat history?",
            requires=["create-character"],
            hints=["Keep it short and let the GM elaborate."],
            completion_check=lambda ctx: bool(ctx.get("submitted_action")),
        ),
        TutorialStep(
            id="review-outcome",
            title="Review the response",
            objective="Read the narrated result and note whether you want to accept or retry it.",
            prompt="Scan the generated outcome and decide what to do next.",
            comprehension_check="Do you understand how to accept, edit, or retry a response?",
            requires=["submit-action"],
            hints=["Use the accept/retry/edit buttons or CLI commands to control the flow."],
            completion_check=lambda ctx: bool(ctx.get("received_narrative")),
        ),
        TutorialStep(
            id="checkpoint",
            title="Confirm understanding",
            objective="Acknowledge what the controls do and proceed to free play.",
            prompt="Summarize the controls in your own words or invoke the status command.",
            comprehension_check="Can you explain the difference between accept and retry?",
            requires=["review-outcome"],
            hints=["Use the repeat control if you want to see these notes again."],
            completion_check=lambda ctx: bool(ctx.get("acknowledged_guidance")),
        ),
    ]

    return TutorialScenario(id="new_player_onboarding", title="New player tutorial", steps=steps)
