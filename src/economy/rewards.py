"""Economy helpers for scaling loot and XP using dynamic difficulty signals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from src.encounters.dda_manager import DDAManager


@dataclass
class DifficultyScaledRewards:
    """Map DDA outputs into reward scaling for loot and XP."""

    dda_manager: DDAManager
    minimum_xp: int = 1
    minimum_loot: int = 1

    def scale_xp(self, base_xp: int) -> int:
        """Scale XP payouts using the current difficulty signal."""

        scalar = self.dda_manager.reward_scalar()
        scaled = int(round(base_xp * scalar))
        return max(self.minimum_xp, scaled)

    def scale_loot_table(self, base_loot_table: Dict[str, int]) -> Dict[str, int]:
        """Scale a simple loot table where values represent stack counts."""

        scalar = self.dda_manager.reward_scalar()
        adjusted: Dict[str, int] = {}

        for name, amount in base_loot_table.items():
            adjusted[name] = max(self.minimum_loot, int(round(amount * (0.85 + scalar))))

        return adjusted

    def xp_and_loot_summary(self, base_xp: int, base_loot_table: Dict[str, int]) -> Dict[str, Dict[str, int]]:
        """Convenience wrapper that scales and returns XP and loot together."""

        return {
            "xp": {"base": base_xp, "scaled": self.scale_xp(base_xp)},
            "loot": self.scale_loot_table(base_loot_table),
        }
