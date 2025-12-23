"""Dynamic difficulty adjustment (DDA) manager for encounter tuning.

The manager tracks player performance signals such as win streaks, resource
burn rates, and time-to-kill. It uses these signals to steer encounter
difficulty toward a target pressure window by adjusting spawn table weights,
AI aggression, and reward scaling multipliers.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Dict, Tuple


@dataclass
class DifficultyTelemetry:
    """Rolling metrics used by the DDA manager."""

    win_streak: int = 0
    loss_streak: int = 0
    recent_time_to_kill: Deque[float] = field(default_factory=lambda: deque(maxlen=6))
    recent_resource_burn: Deque[float] = field(default_factory=lambda: deque(maxlen=6))
    last_outcome: str = "unknown"


class DDAManager:
    """Adaptive difficulty controller.

    Attributes:
        target_pressure: Tuple describing the lower/upper bound of desired
            encounter pressure. Values are normalized between 0 and 1.
        baseline_time_to_kill: Seconds to defeat an even-threat encounter.
        difficulty_index: Current multiplicative difficulty applied to spawns
            and AI behavior. Clamped between 0.65 and 1.35.
    """

    def __init__(
        self, target_pressure: Tuple[float, float] = (0.4, 0.6), baseline_time_to_kill: float = 45.0
    ):
        self.target_pressure = target_pressure
        self.baseline_time_to_kill = baseline_time_to_kill
        self.telemetry = DifficultyTelemetry()
        self.difficulty_index: float = 1.0
        self.last_signal: float = 0.0

    def record_encounter(self, outcome: str, time_to_kill: float, resource_burn: float) -> float:
        """Record encounter telemetry and update the difficulty index.

        Args:
            outcome: "win" or "loss" indicator.
            time_to_kill: Seconds to resolve the encounter.
            resource_burn: Portion of consumables or stamina spent (0-1).

        Returns:
            The signed difficulty signal applied after this encounter.
        """

        normalized_burn = max(0.0, min(resource_burn, 1.5))
        normalized_ttk = max(1.0, time_to_kill)

        if outcome == "win":
            self.telemetry.win_streak += 1
            self.telemetry.loss_streak = 0
        elif outcome == "loss":
            self.telemetry.loss_streak += 1
            self.telemetry.win_streak = 0
        else:
            self.telemetry.win_streak = 0
            self.telemetry.loss_streak = 0

        self.telemetry.recent_resource_burn.append(normalized_burn)
        self.telemetry.recent_time_to_kill.append(normalized_ttk)
        self.telemetry.last_outcome = outcome

        return self._update_difficulty_index()

    def _normalized_ttk(self) -> float:
        """Normalize time-to-kill into 0-1 range based on the baseline."""

        if not self.telemetry.recent_time_to_kill:
            return 0.5

        avg_ttk = sum(self.telemetry.recent_time_to_kill) / len(self.telemetry.recent_time_to_kill)
        normalized = min(avg_ttk / self.baseline_time_to_kill, 2.0) / 2
        return max(0.1, normalized)

    def _pressure(self) -> float:
        """Estimate encounter pressure from recent telemetry and current tuning."""

        avg_burn = sum(self.telemetry.recent_resource_burn) / len(self.telemetry.recent_resource_burn)
        normalized_burn = min(max(avg_burn, 0.0), 1.0) if self.telemetry.recent_resource_burn else 0.5

        normalized_ttk = self._normalized_ttk()

        streak_relief = -min(self.telemetry.win_streak, 6) * 0.008
        streak_pressure = min(self.telemetry.loss_streak, 4) * 0.05
        outcome_pressure = 0.12 if self.telemetry.last_outcome == "loss" else -0.02

        base_pressure = (0.45 * normalized_burn) + (0.35 * normalized_ttk) + streak_pressure + streak_relief
        base_pressure += outcome_pressure

        # Increased difficulty index should feed back into the perceived pressure.
        base_pressure += (self.difficulty_index - 1.0)

        return max(0.0, min(1.2, round(base_pressure, 3)))

    def _update_difficulty_index(self) -> float:
        """Move difficulty toward the target pressure window."""

        pressure = self._pressure()
        low, high = self.target_pressure
        midpoint = (low + high) / 2

        if pressure < low:
            delta = min((low - pressure) * 0.85 + self.telemetry.win_streak * 0.01, 0.35)
        elif pressure > high:
            delta = -min((pressure - high) * 0.85 + self.telemetry.loss_streak * 0.015, 0.35)
        else:
            delta = (midpoint - pressure) * 0.1

        self.difficulty_index = max(0.65, min(1.35, self.difficulty_index + delta))
        self.last_signal = round(delta, 3)
        return self.last_signal

    def adjusted_spawn_table(self, base_spawn_table: Dict[str, float]) -> Dict[str, float]:
        """Scale spawn table weights to reflect the current difficulty index."""

        adjusted = {}
        for enemy, weight in base_spawn_table.items():
            emphasis = 1.2 if ("elite" in enemy.lower() or "boss" in enemy.lower()) else 0.8
            scaled = weight * (1 + (self.difficulty_index - 1.0) * emphasis)
            adjusted[enemy] = max(0.0, round(scaled, 3))

        total = sum(adjusted.values()) or 1.0
        return {enemy: round(weight / total, 4) for enemy, weight in adjusted.items()}

    def ai_aggression_level(self) -> float:
        """Return an aggression multiplier for utility AI planners."""

        return round(max(0.5, 1 + (self.difficulty_index - 1.0) * 0.9 + self.last_signal * 0.5), 3)

    def reward_scalar(self) -> float:
        """Combine difficulty signals into a reward scaling factor."""

        scalar = 1 + (self.difficulty_index - 1.0) * 0.8 + abs(self.last_signal) * 0.3
        return max(0.75, min(1.5, round(scalar, 3)))

    def snapshot(self) -> Dict[str, float]:
        """Expose a debugging snapshot of the current state."""

        return {
            "difficulty_index": round(self.difficulty_index, 3),
            "pressure": self._pressure(),
            "win_streak": self.telemetry.win_streak,
            "loss_streak": self.telemetry.loss_streak,
            "last_signal": self.last_signal,
        }
