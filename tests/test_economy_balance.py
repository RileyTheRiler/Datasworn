from __future__ import annotations

import random
from pathlib import Path

from src.crafting import CraftingBook
from src.economy.shops import ShopItem, ShopManager
from src.economy.upkeep import UpkeepCalculator


def _prepare_materials(balance: int, materials: dict, recipe_inputs: dict, material_costs: dict) -> int:
    for item, qty in recipe_inputs.items():
        available = materials.get(item, 0)
        if available < qty:
            needed = qty - available
            balance -= needed * material_costs.get(item, 10)
            materials[item] = materials.get(item, 0) + needed
    return balance


def test_gold_flow_produces_sinks_over_sessions():
    rng = random.Random(2024)
    book = CraftingBook.from_file(Path("data/items/recipes.json"))

    shop_pool = [
        ShopItem("foraged_herbs", price=6, stock=4),
        ShopItem("protein_paste", price=5, stock=4),
        ShopItem("alloy_scraps", price=14, stock=6),
        ShopItem("micro_circuit", price=18, stock=4),
        ShopItem("resonance_mesh", price=28, stock=2),
    ]
    shop_manager = ShopManager(shop_pool, rotation_size=2, rotation_duration=3, service_fee_pct=0.12)
    upkeep = UpkeepCalculator(base_per_tier=6, durability_loss=0.05)

    equipment = [
        {"name": "rifle", "tier": 2, "durability": 0.85},
        {"name": "armor", "tier": 3, "durability": 0.8},
    ]
    consumables = {
        "ammo": {"uses_per_mission": 2, "stock": 1, "cost_per_use": 3},
        "medpack": {"uses_per_mission": 1, "stock": 0, "cost_per_use": 6},
    }
    material_costs = {
        "foraged_herbs": 2,
        "protein_paste": 3,
        "alloy_scraps": 8,
        "micro_circuit": 12,
        "resonance_mesh": 15,
    }
    sale_values = {"repair_kit": 40, "armor_plating": 70}

    balance = 1000
    materials: dict = {}
    rotations_seen = set()

    for session in range(1, 11):
        # Limited-time shop interactions with NPC service fees
        recipe_id = "field_kit" if session % 3 else "covert_armor"
        if balance < 300:
            recipe_id = "survival_rations"
        recipe = book.get(recipe_id)
        shop_manager.ensure_rotation(session)
        rotations_seen.add(tuple(sorted(shop_manager.active_inventory.keys())))
        for item in shop_manager.list_items(session).values():
            if (
                item.item_id in recipe.inputs
                and materials.get(item.item_id, 0) < recipe.inputs[item.item_id] + 1
                and balance > item.price * 2
            ):
                balance, _ = shop_manager.purchase(item.item_id, balance, session)
                materials[item.item_id] = materials.get(item.item_id, 0) + 1

        balance = _prepare_materials(balance, materials, recipe.inputs, material_costs)
        craft_result = book.craft(recipe_id, crafter_skill=2, materials=materials, rng=rng)

        if craft_result.success:
            for item, qty in craft_result.outputs.items():
                balance += sale_values.get(item, 0) * qty

        balance, costs = upkeep.process_mission(balance, equipment, consumables, missions=1)
        assert costs["maintenance"] > 0
        assert balance < 1000  # sinks are applied every loop

    assert balance > 200  # sinks should not be punitive enough to bankrupt the player outright
    assert len(rotations_seen) >= 2  # inventories should rotate over time


def test_higher_tier_recipes_fail_more_often():
    rng = random.Random(99)
    book = CraftingBook.from_file(Path("data/items/recipes.json"))
    low_tier = book.get("survival_rations")
    high_tier = book.get("signal_interceptor")

    materials = {k: 400 for k in ["foraged_herbs", "protein_paste", "quantum_array", "micro_circuit", "alloy_scraps"]}
    low_success = 0
    high_success = 0
    attempts = 50

    for _ in range(attempts):
        if book.craft(low_tier.id, crafter_skill=1, materials=materials, rng=rng).success:
            low_success += 1
        if book.craft(high_tier.id, crafter_skill=1, materials=materials, rng=rng).success:
            high_success += 1

    low_rate = low_success / attempts
    high_rate = high_success / attempts
    assert low_rate > high_rate
    assert high_rate < 0.7  # high-tier recipes should retain meaningful failure risk
