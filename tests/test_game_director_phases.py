from src.datasworn import DataswornTurnEngine
from src.engine import EngineTickHooks, run_engine_tick
from src.game_director import GamePhase, PhaseController


def test_phase_controller_runs_in_order():
    controller = PhaseController(tracing_enabled=False)
    execution_order: list[str] = []

    controller.register(GamePhase.PLAYER_INPUT, lambda: execution_order.append("player"))
    controller.register(GamePhase.AI_RESPONSE, lambda: execution_order.append("ai"))
    controller.register(GamePhase.WORLD_UPDATE, lambda: execution_order.append("world"))
    controller.register(GamePhase.NARRATIVE_UPDATE, lambda: execution_order.append("narrative"))
    controller.register(GamePhase.RENDER_HOOK, lambda: execution_order.append("render"))

    controller.run_cycle()

    assert execution_order == ["player", "ai", "world", "narrative", "render"]
    assert controller.history == list(GamePhase)


def test_turn_engine_advances_state_across_turns():
    controller = PhaseController(tracing_enabled=False)
    engine = DataswornTurnEngine(controller)

    engine.tick("strike", "counter")
    assert engine.state.turn_counter == 1

    engine.tick("defend", "advance")

    assert engine.state.turn_counter == 2
    assert engine.state.economy_balance == 10
    assert engine.state.combat_log == ["player:strike", "ai:counter", "player:defend", "ai:advance"]
    assert engine.state.narrative_log[-1] == "Turn 2: defend / advance"
    assert len(engine.state.render_queue) == 2

    expected_history = [phase for _ in range(2) for phase in GamePhase]
    assert controller.history == expected_history


def test_engine_tick_helpers_follow_phase_order():
    controller = PhaseController(tracing_enabled=False)
    steps: list[str] = []

    hooks = EngineTickHooks(
        player_input=lambda: steps.append("player"),
        ai_responses=lambda: steps.append("ai"),
        world_update=lambda: steps.append("world"),
        narrative_update=lambda: steps.append("narrative"),
        render_hook=lambda: steps.append("render"),
    )

    results = run_engine_tick(hooks, controller)

    assert steps == ["player", "ai", "world", "narrative", "render"]
    assert list(results.keys()) == list(GamePhase)
    assert controller.history[-5:] == list(GamePhase)
