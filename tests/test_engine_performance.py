import time

from src.engine.profiling import FrameProfiler
from src.engine.npc.controller import NPCController
from src.engine.npc.personality import EmotionalState, PersonalityProfile
from src.engine.npc.reasoning import Goal
from src.goap import GOAPGoal, GOAPPlanner, WorldState, create_combat_planner
from src.starmap import StarmapGenerator, StarMap


def _build_controller_with_profiler() -> tuple[NPCController, FrameProfiler]:
    profiler = FrameProfiler(max_samples=120)
    controller = NPCController(
        personality=PersonalityProfile(),
        goals=[Goal(name="Investigate anomaly", priority=1.0)],
        emotional_state=EmotionalState(current_state="calm", intensity=0.3),
        profiler=profiler,
    )
    return controller, profiler


def test_npc_controller_stays_within_frame_budget():
    controller, profiler = _build_controller_with_profiler()

    scene_graph = {
        "actors": [{"id": f"crew_{i}", "distance": 5.0 + i, "bearing": 0.1 * i} for i in range(4)],
        "objects": [{"id": f"crate_{i}", "distance": 2.0 + i, "bearing": -0.05 * i} for i in range(3)],
        "lighting": 0.9,
        "time_of_day": "noon",
    }
    environment = {"path_blocked": False, "affordances": ["open"]}

    for _ in range(60):
        controller.tick(scene_graph, environment)

    summary = profiler.summary()
    assert summary["controller.total"]["p95_ms"] < 5.0, summary


def test_goap_planner_avoids_excessive_allocations():
    planner: GOAPPlanner = create_combat_planner()
    start_state = WorldState(facts={"has_weapon": True, "weapon_drawn": False, "target_in_range": False})
    goal = GOAPGoal(name="eliminate", conditions={"target_damaged": True})

    timings: list[float] = []
    for _ in range(5):
        start = time.perf_counter()
        actions = planner.plan(start_state, goal)
        timings.append((time.perf_counter() - start) * 1000.0)
        assert actions, "Planner should find a path"

    assert sum(timings) / len(timings) < 2.5, timings
    assert len(planner._state_pool._pool) > 0  # Pool should retain recycled states


def test_worldgen_faction_assignment_budget():
    generator = StarmapGenerator(seed=99)
    sector = generator.generate_sector("Perf", num_systems=50)
    factions = [{"id": f"f_{i}", "influence": 0.3 + i * 0.05} for i in range(5)]

    map_tools = StarMap()

    start = time.perf_counter()
    map_tools.assign_faction_territories(sector, factions)
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    assert elapsed_ms < 25.0, elapsed_ms
