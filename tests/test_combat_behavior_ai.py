from src.ai.behavior import BehaviorOption, PositionScorer, ScoreContext, ThreatScorer, UtilityBehaviorController
from src.combat.encounter_manager import CombatantState, EncounterManager, EncounterState
from src.goap import GOAPGoal, WorldState, create_combat_planner


def test_cover_preference_when_exposed():
    manager = EncounterManager()
    actor = CombatantState(
        id="p1",
        name="Scout",
        health=0.6,
        ammo=0.5,
        threat=0.7,
        position=(0, 0),
        in_cover=False,
        cover_quality=0.0,
        allies_nearby=0,
    )
    encounter = EncounterState(
        enemies=[CombatantState(id="e1", name="Raider", position=(1, 0))],
        party=[actor],
        map_control=0.3,
        cover_density=0.4,
        objective_pressure=0.8,
    )

    decision = manager.evaluate_turn(actor, encounter, dump_debug=True)
    scores = {b.action: b.score for b in decision.ranked}

    assert decision.chosen.action in {"take_cover", "regroup"}
    assert scores["take_cover"] >= scores["focus_fire"]


def test_focus_fire_when_safe():
    manager = EncounterManager()
    actor = CombatantState(
        id="p2",
        name="Marksman",
        health=0.95,
        ammo=0.9,
        threat=0.3,
        position=(0, 0),
        in_cover=True,
        cover_quality=1.0,
        allies_nearby=2,
    )
    encounter = EncounterState(
        enemies=[CombatantState(id="e2", name="Stalker", position=(0.0, 0.0))],
        party=[actor],
        map_control=0.7,
        cover_density=0.9,
        objective_pressure=0.4,
    )

    decision = manager.evaluate_turn(actor, encounter)
    assert decision.chosen.action == "focus_fire"


def test_goap_heuristic_prefers_cover():
    manager = EncounterManager()
    actor = CombatantState(
        id="p3",
        name="Guardian",
        health=0.4,
        ammo=0.7,
        threat=0.8,
        position=(0, 0),
        in_cover=False,
        cover_quality=0.1,
        allies_nearby=1,
    )
    encounter = EncounterState(
        enemies=[CombatantState(id="e3", name="Sniper", position=(2.0, 0.0))],
        party=[actor],
        map_control=0.5,
        cover_density=0.6,
        objective_pressure=0.6,
    )

    decision_log: list[str] = []
    planner = create_combat_planner(
        action_heuristic=manager.build_action_heuristic(actor, encounter),
        decision_log=decision_log,
    )

    state = WorldState(
        facts={
            "has_weapon": True,
            "weapon_drawn": True,
            "target_visible": True,
            "target_in_range": True,
            "has_cover": True,
            "in_cover": False,
            "has_allies": True,
            "has_ammo": True,
            "ammo_loaded": True,
        }
    )
    goal = GOAPGoal(name="stabilize", conditions={"in_cover": True})

    plan = planner.plan(state, goal)
    assert plan, "Planner should find a viable plan"
    assert plan[0].name == "take_cover"
    assert any(entry.startswith("take_cover") for entry in decision_log)


def test_pluggable_scorer_can_be_swapped():
    context = ScoreContext(threat_level=0.5, health=0.5, ammo=0.5, cover_value=0.5)
    defensive_option = BehaviorOption(
        action="defend",
        scorers=[ThreatScorer(weight=1.0), PositionScorer(weight=1.0)],
    )
    aggressive_option = BehaviorOption(
        action="charge",
        scorers=[ThreatScorer(weight=0.5), PositionScorer(weight=0.2)],
        bias=0.2,
    )
    controller = UtilityBehaviorController([defensive_option, aggressive_option])
    top, ranked = controller.evaluate(context)

    assert top.action == "defend"
    assert ranked[0].score >= ranked[1].score
