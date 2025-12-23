"""Engine package for NPC systems and other runtime modules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from src.game_director import GamePhase, PhaseController


@dataclass
class EngineTickHooks:
    """Bundle of callables representing each slot in the engine tick."""

    player_input: Callable[[], Any]
    ai_responses: Callable[[], Any]
    world_update: Callable[[], Any]
    narrative_update: Callable[[], Any]
    render_hook: Callable[[], Any]


def run_engine_tick(
    hooks: EngineTickHooks,
    phase_controller: PhaseController | None = None,
) -> dict[GamePhase, Any]:
    """Execute the engine tick in a predictable phase order."""

    controller = phase_controller or PhaseController()
    return {
        GamePhase.PLAYER_INPUT: controller.execute_phase(GamePhase.PLAYER_INPUT, hooks.player_input),
        GamePhase.AI_RESPONSE: controller.execute_phase(GamePhase.AI_RESPONSE, hooks.ai_responses),
        GamePhase.WORLD_UPDATE: controller.execute_phase(GamePhase.WORLD_UPDATE, hooks.world_update),
        GamePhase.NARRATIVE_UPDATE: controller.execute_phase(
            GamePhase.NARRATIVE_UPDATE, hooks.narrative_update
        ),
        GamePhase.RENDER_HOOK: controller.execute_phase(GamePhase.RENDER_HOOK, hooks.render_hook),
    }
