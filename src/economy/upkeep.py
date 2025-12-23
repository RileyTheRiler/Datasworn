from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Tuple


@dataclass
class EquipmentState:
    name: str
    tier: int
    durability: float = 1.0  # 0-1 scale


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def maintenance_cost(equipment: Iterable[Dict], base_per_tier: int = 8) -> int:
    """Calculate the upkeep cost for equipment based on tier and wear."""
    total = 0.0
    for gear in equipment:
        tier = max(1, gear.get("tier", 1))
        durability = _clamp(gear.get("durability", 1.0))
        wear_multiplier = 1 + (1 - durability)
        total += base_per_tier * tier * wear_multiplier
    return int(round(total))


def consumable_upkeep(consumables: Dict[str, Dict], missions: int = 1) -> Tuple[int, Dict[str, int]]:
    """
    Determine how many consumables must be replenished for the upcoming missions.

    Returns a tuple of (cost, replenished_items) where replenished_items tracks how
    many uses were purchased for each consumable.
    """
    total_cost = 0
    replenished: Dict[str, int] = {}
    for name, bundle in consumables.items():
        uses_per_mission = bundle.get("uses_per_mission", 1)
        stock = bundle.get("stock", 0)
        cost_per_use = bundle.get("cost_per_use", 0)
        projected_use = uses_per_mission * missions

        if stock < projected_use:
            needed = projected_use - stock
            purchase_cost = needed * cost_per_use
            replenished[name] = needed
            total_cost += purchase_cost
            bundle["stock"] = projected_use  # reset to mission-ready stock

        # Consume the stock now that replenishment has been handled
        bundle["stock"] = max(0, bundle.get("stock", 0) - projected_use)
    return int(total_cost), replenished


class UpkeepCalculator:
    """Coordinates equipment maintenance and consumable replenishment."""

    def __init__(self, base_per_tier: int = 8, durability_loss: float = 0.08):
        self.base_per_tier = base_per_tier
        self.durability_loss = durability_loss

    def process_mission(
        self,
        balance: int,
        equipment: Iterable[Dict],
        consumables: Dict[str, Dict],
        missions: int = 1,
    ) -> Tuple[int, Dict[str, int]]:
        maintenance = maintenance_cost(equipment, base_per_tier=self.base_per_tier)
        consumable_cost, replenished = consumable_upkeep(consumables, missions=missions)
        total_cost = maintenance + consumable_cost

        self._degrade_equipment(equipment, missions)
        updated_balance = balance - total_cost
        return updated_balance, {"maintenance": maintenance, "consumables": consumable_cost, "replenished": replenished}

    def _degrade_equipment(self, equipment: Iterable[Dict], missions: int) -> None:
        for gear in equipment:
            gear["durability"] = _clamp(gear.get("durability", 1.0) - self.durability_loss * missions)
