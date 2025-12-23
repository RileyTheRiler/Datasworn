import math

from src.encounters.dda_manager import DDAManager
from src.economy.rewards import DifficultyScaledRewards


def test_win_streak_converges_to_pressure_window():
    manager = DDAManager()
    base_spawn = {"grunt": 0.55, "elite": 0.3, "boss": 0.15}

    for _ in range(6):
        manager.record_encounter(outcome="win", time_to_kill=18, resource_burn=0.12)

    snapshot = manager.snapshot()
    low, high = manager.target_pressure
    assert low <= snapshot["pressure"] <= high

    adjusted_spawns = manager.adjusted_spawn_table(base_spawn)
    assert adjusted_spawns["elite"] > base_spawn["elite"] / sum(base_spawn.values())
    assert manager.ai_aggression_level() > 1.0


def test_wipe_event_relaxes_difficulty_and_rewards():
    manager = DDAManager()
    manager.difficulty_index = 1.2
    scaler = DifficultyScaledRewards(manager)

    # Wipe events drive the system to lower difficulty.
    for _ in range(2):
        manager.record_encounter(outcome="loss", time_to_kill=80, resource_burn=0.95)

    # Simulate the easier follow-up fights the manager should deliver.
    for _ in range(2):
        manager.record_encounter(outcome="win", time_to_kill=40, resource_burn=0.35)

    snapshot = manager.snapshot()
    low, high = manager.target_pressure
    assert low <= snapshot["pressure"] <= high
    assert manager.difficulty_index <= 1.0

    scaled_xp = scaler.scale_xp(10)
    assert 1 <= scaled_xp <= 12

    loot = scaler.scale_loot_table({"medkit": 2, "ammo": 3})
    assert all(amount >= 1 for amount in loot.values())
    assert math.isclose(loot["ammo"], loot["medkit"] + 1, rel_tol=0.5)
