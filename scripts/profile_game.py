"""Profile a representative NPC update loop and emit flamegraph-friendly data.

This script exercises the NPC controller with a predictable scene so the
resulting profiles are stable. It captures:
* A cProfile dump (``--profile-out``)
* A collapsed stack text file suitable for flamegraph viewers
  (``--flamegraph-out``)
* A JSON summary of the lightweight FrameProfiler spans (``--summary-out``)
"""

from __future__ import annotations

import argparse
import cProfile
import json
import pstats
from pathlib import Path

from src.engine.profiling import FrameProfiler
from src.engine.npc.behavior import FactChecker
from src.engine.npc.controller import NPCController
from src.engine.npc.personality import EmotionalState, PersonalityProfile
from src.engine.npc.reasoning import Goal


def _func_label(func: tuple[str, int, str]) -> str:
    filename, line, name = func
    return f"{Path(filename).name}:{line}:{name}"


def write_flamegraph(stats: pstats.Stats, output_path: Path) -> None:
    """Convert pstats output into a simple collapsed stack file."""

    stats.calc_callees()
    callers = {func: data[4] for func, data in stats.stats.items()}
    callees = stats.all_callees
    roots = [func for func in stats.stats if not callers.get(func)]
    collapsed: dict[str, float] = {}

    def walk(func: tuple[str, int, str], stack: list[str]):
        frame = _func_label(func)
        next_stack = stack + [frame]
        children = callees.get(func, {})
        if children:
            for child in children:
                walk(child, next_stack)
        self_time = stats.stats[func][2]
        if self_time > 0:
            key = ";".join(next_stack)
            collapsed[key] = collapsed.get(key, 0.0) + self_time

    for root in roots:
        walk(root, [])

    output_lines = [f"{stack} {duration * 1000:.3f}" for stack, duration in collapsed.items()]
    output_path.write_text("\n".join(sorted(output_lines)), encoding="utf-8")


def build_controller(profiler: FrameProfiler) -> NPCController:
    goals = [
        Goal(name="Investigate anomaly", priority=1.2, desired_outcome="investigate_area"),
        Goal(name="Assist crew", priority=0.8, desired_outcome="offer_help"),
    ]
    personality = PersonalityProfile()
    emotional_state = EmotionalState(current_state="curious", intensity=0.4)
    fact_checker = FactChecker(confidence_threshold=0.35)
    return NPCController(
        personality=personality,
        goals=goals,
        emotional_state=emotional_state,
        fact_checker=fact_checker,
        profiler=profiler,
    )


def run_iterations(controller: NPCController, iterations: int) -> None:
    scene_graph = {
        "actors": [
            {"id": "crew_1", "name": "Lena", "distance": 6.0, "bearing": 0.15, "state": "idle"},
            {"id": "crew_2", "name": "Raj", "distance": 11.0, "bearing": -0.2, "state": "working"},
        ],
        "objects": [
            {"id": "crate", "name": "Supply Crate", "distance": 4.0, "bearing": 0.05, "state": "closed"},
            {"id": "console", "name": "Console", "distance": 3.0, "bearing": -0.4, "state": "online"},
        ],
        "sounds": [
            {"id": "alarm", "source": "alarm", "distance": 7.0, "description": "klaxon"}
        ],
        "lighting": 0.8,
        "time_of_day": "dusk",
    }
    environment = {"path_blocked": False, "affordances": ["open", "scan"]}

    for _ in range(iterations):
        controller.tick(scene_graph, environment)


def main():
    parser = argparse.ArgumentParser(description="Profile the NPC update loop")
    parser.add_argument("--iterations", type=int, default=120, help="How many ticks to run")
    parser.add_argument("--profile-out", type=Path, default=Path("profile_game.prof"))
    parser.add_argument("--flamegraph-out", type=Path, default=Path("profile_game.flamegraph.txt"))
    parser.add_argument("--summary-out", type=Path, default=Path("profile_game.summary.json"))
    args = parser.parse_args()

    profiler = FrameProfiler(max_samples=args.iterations)
    controller = build_controller(profiler)

    capture = cProfile.Profile()
    capture.enable()
    run_iterations(controller, args.iterations)
    capture.disable()

    args.profile_out.parent.mkdir(parents=True, exist_ok=True)
    capture.dump_stats(args.profile_out)

    stats = pstats.Stats(capture)
    stats.strip_dirs()
    write_flamegraph(stats, args.flamegraph_out)

    args.summary_out.write_text(json.dumps(profiler.summary(), indent=2), encoding="utf-8")
    print(f"Saved profile to {args.profile_out}")
    print(f"Saved flamegraph stacks to {args.flamegraph_out}")
    print(f"Saved frame summary to {args.summary_out}")


if __name__ == "__main__":
    main()
