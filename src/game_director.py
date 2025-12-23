"""Dynamic game director for balancing engagement in real time.

The controller listens to player performance metrics and stress indicators, then
adjusts encounter pacing, rewards, and guidance to keep sessions inside target
engagement bands.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol

from src.spawner import EncounterDirector


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp a numeric value into a range."""
    return max(min_value, min(max_value, value))


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class PerformanceMetrics:
    """Snapshot of player performance and stress."""

    deaths: int = 0
    average_dps: float = 0.0
    average_completion_time: float = 0.0  # seconds per encounter/mission
    stress_index: float = 0.0  # 0-1 subjective stress or HRV proxy
    encounters_cleared: int = 0
    recent_damage_taken: float = 0.0


@dataclass(slots=True)
class DirectorKnobs:
    """Tunable knobs the director can manipulate."""

    enemy_spawn_rate: float = 1.0
    patrol_density: float = 1.0
    resource_drop_rate: float = 1.0
    hint_frequency: float = 1.0

    def clamped(self) -> "DirectorKnobs":
        """Return a copy with values clamped to safe ranges."""
        return DirectorKnobs(
            enemy_spawn_rate=clamp(self.enemy_spawn_rate, 0.25, 2.5),
            patrol_density=clamp(self.patrol_density, 0.25, 2.5),
            resource_drop_rate=clamp(self.resource_drop_rate, 0.25, 3.0),
            hint_frequency=clamp(self.hint_frequency, 0.1, 3.0),
        )


@dataclass(slots=True)
class TelemetrySnapshot:
    """State captured whenever the director intervenes."""

    metrics: PerformanceMetrics
    knobs: DirectorKnobs
    engagement_score: float
    note: str


class EventSchedulerHook(Protocol):
    """Interface for schedulers that can receive tuning from the director."""

    event_density_multiplier: float
    hint_frequency: float
    resource_bonus_multiplier: float


# ---------------------------------------------------------------------------
# Game director controller
# ---------------------------------------------------------------------------


class GameDirectorController:
    """Feedback controller that keeps player engagement in a target band."""

    def __init__(self):
        self.targets = {
            "stress": (0.35, 0.65),  # Too low = boredom, too high = burnout
            "lethality": (0, 2),  # deaths allowed per session slice
            "completion_time": (120, 420),  # desired range in seconds
        }
        self.knobs = DirectorKnobs()
        self.listeners: list[Callable[[DirectorKnobs, PerformanceMetrics], None]] = []
        self.telemetry: list[TelemetrySnapshot] = []
        self.developer_toggles = {
            "freeze_adjustments": False,
            "verbose_telemetry": True,
            "force_hints": False,
        }
        self._engagement_score: float = 0.5

    # -------------------------- Subscription --------------------------
    def subscribe(self, callback: Callable[[DirectorKnobs, PerformanceMetrics], None]) -> None:
        """Subscribe to knob updates (spawners, schedulers, UI overlays)."""

        self.listeners.append(callback)

    # -------------------------- Metrics ingest ------------------------
    def update_metrics(self, snapshot: PerformanceMetrics) -> DirectorKnobs:
        """Update the director with a new performance snapshot and adjust knobs."""

        if self.developer_toggles["freeze_adjustments"]:
            return self.knobs

        self._engagement_score = self._calculate_engagement(snapshot)
        self._adjust_knobs(snapshot)
        tuned = self.knobs.clamped()
        self.knobs = tuned

        for callback in self.listeners:
            callback(tuned, snapshot)

        self._record_telemetry(snapshot, "metrics_ingest")
        return tuned

    def _calculate_engagement(self, snapshot: PerformanceMetrics) -> float:
        """Blend stress, lethality, and pace into a single engagement score."""

        stress_score = clamp(snapshot.stress_index, 0.0, 1.2)
        lethality_pressure = clamp(snapshot.deaths / max(1, snapshot.encounters_cleared + 1), 0.0, 1.0)
        pace = snapshot.average_completion_time
        pace_score = 0.5
        if pace > 0:
            target_low, target_high = self.targets["completion_time"]
            if pace < target_low:
                pace_score = 0.3
            elif pace > target_high:
                pace_score = 0.8

        engagement_score = clamp((stress_score * 0.5) + (lethality_pressure * 0.3) + (pace_score * 0.2), 0.0, 1.0)
        return engagement_score

    # -------------------------- Feedback loops ------------------------
    def _adjust_knobs(self, snapshot: PerformanceMetrics) -> None:
        """Adjust knobs to push metrics back into the target band."""

        stress_min, stress_max = self.targets["stress"]
        lethality_max = self.targets["lethality"][1]
        target_low, target_high = self.targets["completion_time"]

        if snapshot.stress_index > stress_max or snapshot.deaths > lethality_max:
            self.knobs.enemy_spawn_rate *= 0.9
            self.knobs.patrol_density *= 0.85
            self.knobs.resource_drop_rate *= 1.15
            self.knobs.hint_frequency *= 1.25 if self.developer_toggles["force_hints"] else 1.1
            adjustment_note = "easing_pressure"
        elif snapshot.stress_index < stress_min and snapshot.average_dps > 0:
            self.knobs.enemy_spawn_rate *= 1.15
            self.knobs.patrol_density *= 1.1
            self.knobs.resource_drop_rate *= 0.95
            self.knobs.hint_frequency *= 0.9
            adjustment_note = "increase_challenge"
        else:
            adjustment_note = "maintain"

        if snapshot.average_completion_time > target_high:
            self.knobs.hint_frequency *= 1.1
        elif 0 < snapshot.average_completion_time < target_low:
            self.knobs.hint_frequency *= 0.9

        self._record_telemetry(snapshot, adjustment_note)

    # ----------------------- Integration points -----------------------
    def apply_to_spawner(self, encounter_director: EncounterDirector) -> None:
        """Push tuning into the encounter director."""

        encounter_director.spawn_rate_bias = self.knobs.enemy_spawn_rate
        encounter_director.patrol_density_bias = self.knobs.patrol_density
        encounter_director.resource_drop_bias = self.knobs.resource_drop_rate
        encounter_director.hint_frequency_bias = self.knobs.hint_frequency

    def apply_to_scheduler(self, scheduler: EventSchedulerHook) -> None:
        """Push tuning into an event scheduler if it supports the hook."""

        scheduler.event_density_multiplier = self.knobs.enemy_spawn_rate
        scheduler.resource_bonus_multiplier = self.knobs.resource_drop_rate
        scheduler.hint_frequency = self.knobs.hint_frequency

    # ----------------------- Telemetry & UI ---------------------------
    def _record_telemetry(self, snapshot: PerformanceMetrics, note: str) -> None:
        """Store telemetry so playtesters can audit interventions."""

        if not self.developer_toggles.get("verbose_telemetry", True) and note == "metrics_ingest":
            return

        self.telemetry.append(
            TelemetrySnapshot(
                metrics=snapshot,
                knobs=self.knobs.clamped(),
                engagement_score=self._engagement_score,
                note=note,
            )
        )
        # Keep telemetry bounded to avoid bloating notebooks or UI
        if len(self.telemetry) > 50:
            self.telemetry = self.telemetry[-50:]

    def get_recent_telemetry(self, count: int = 5) -> list[TelemetrySnapshot]:
        """Return the most recent telemetry rows for UI display."""

        return self.telemetry[-count:]

    def get_developer_toggles(self) -> dict:
        """Return editable developer flags for UI checkboxes."""

        return self.developer_toggles.copy()

    def set_developer_toggle(self, flag: str, enabled: bool) -> None:
        """Enable or disable a developer control (e.g., freeze adjustments)."""

        if flag not in self.developer_toggles:
            raise ValueError(f"Unknown developer toggle: {flag}")
        self.developer_toggles[flag] = enabled

    def summarize_state(self) -> dict:
        """Expose a compact snapshot for telemetry overlays."""

        return {
            "engagement_score": round(self._engagement_score, 3),
            "knobs": self.knobs.clamped().__dict__,
            "toggles": self.get_developer_toggles(),
        }
