from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class CraftResult:
    success: bool
    materials_spent: Dict[str, int]
    outputs: Dict[str, int]
    salvage_returned: Dict[str, int]
    roll: float
    chance: float
    message: str = ""


@dataclass
class CraftingRecipe:
    id: str
    name: str
    tier: int
    inputs: Dict[str, int]
    outputs: Dict[str, int]
    base_success: float
    fail_salvage: float = 0.0
    description: str = ""
    tags: List[str] = field(default_factory=list)

    def success_chance(self, crafter_skill: int) -> float:
        """
        Calculate the success chance incorporating tier pressure and crafter skill.

        Skill provides a small linear bonus while tiers impose a modest penalty
        so that higher tiers remain risky without feeling impossible.
        """
        tier_penalty = 0.05 * max(0, self.tier - 1)
        skill_bonus = 0.03 * max(0, crafter_skill)
        raw = self.base_success - tier_penalty + skill_bonus
        return max(0.05, min(0.97, raw))

    def attempt_craft(
        self,
        crafter_skill: int,
        rng: Optional[random.Random] = None,
    ) -> Tuple[bool, float, float]:
        """Roll an attempt and return (success, roll, chance)."""
        roller = rng or random
        chance = self.success_chance(crafter_skill)
        roll = roller.random()
        return roll <= chance, roll, chance


class CraftingBook:
    """Collection of tiered crafting recipes with convenience helpers."""

    def __init__(self, recipes: Dict[str, CraftingRecipe]):
        self._recipes = recipes

    @classmethod
    def from_file(cls, path: str | Path) -> "CraftingBook":
        recipe_path = Path(path)
        with recipe_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        parsed = {
            entry["id"]: CraftingRecipe(
                id=entry["id"],
                name=entry.get("name", entry["id"]),
                tier=entry.get("tier", 1),
                inputs=entry.get("inputs", {}),
                outputs=entry.get("outputs", {}),
                base_success=entry.get("base_success", 0.75),
                fail_salvage=entry.get("fail_salvage", 0.0),
                description=entry.get("description", ""),
                tags=entry.get("tags", []),
            )
            for entry in data
        }
        return cls(parsed)

    def recipe_ids(self) -> List[str]:
        return list(self._recipes.keys())

    def get(self, recipe_id: str) -> Optional[CraftingRecipe]:
        return self._recipes.get(recipe_id)

    def craft(
        self,
        recipe_id: str,
        crafter_skill: int,
        materials: Dict[str, int],
        rng: Optional[random.Random] = None,
    ) -> CraftResult:
        """
        Attempt to craft the recipe, mutating the provided materials pool.

        Materials are consumed up-front; on failure a percentage can be salvaged
        back into the pool to model partial recovery of components.
        """
        recipe = self.get(recipe_id)
        if not recipe:
            raise ValueError(f"Unknown recipe: {recipe_id}")

        if not self._has_materials(materials, recipe.inputs):
            missing = {k: v for k, v in recipe.inputs.items() if materials.get(k, 0) < v}
            raise ValueError(f"Insufficient materials for {recipe_id}: {missing}")

        self._spend_materials(materials, recipe.inputs)

        success, roll, chance = recipe.attempt_craft(crafter_skill, rng)
        if success:
            for item, qty in recipe.outputs.items():
                materials[item] = materials.get(item, 0) + qty
            return CraftResult(
                success=True,
                materials_spent=dict(recipe.inputs),
                outputs=dict(recipe.outputs),
                salvage_returned={},
                roll=roll,
                chance=chance,
                message="Crafting succeeded",
            )

        salvage = self._salvage_materials(materials, recipe.inputs, recipe.fail_salvage)
        return CraftResult(
            success=False,
            materials_spent=dict(recipe.inputs),
            outputs={},
            salvage_returned=salvage,
            roll=roll,
            chance=chance,
            message="Crafting failed",
        )

    @staticmethod
    def _has_materials(pool: Dict[str, int], cost: Dict[str, int]) -> bool:
        return all(pool.get(item, 0) >= qty for item, qty in cost.items())

    @staticmethod
    def _spend_materials(pool: Dict[str, int], cost: Dict[str, int]) -> None:
        for item, qty in cost.items():
            pool[item] = pool.get(item, 0) - qty

    @staticmethod
    def _salvage_materials(
        pool: Dict[str, int], cost: Dict[str, int], salvage_rate: float
    ) -> Dict[str, int]:
        salvage: Dict[str, int] = {}
        for item, qty in cost.items():
            returned = int(math.floor(qty * salvage_rate))
            if returned:
                pool[item] = pool.get(item, 0) + returned
                salvage[item] = returned
        return salvage
