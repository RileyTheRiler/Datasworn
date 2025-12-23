import pytest

from src.auto_save import AutoSaveSystem
from src.game_state import create_new_character
from src.persistence import PersistenceLayer
from src.phase_controller import PhaseController
from src.persistent_world import PersistentWorldEngine
from src.session_continuity import SessionTracker


def test_snapshot_integrity_recovers_from_partial_write(tmp_path):
    db_path = tmp_path / "world.db"
    snapshot_path = tmp_path / "world.json"
    layer = PersistenceLayer(db_path, snapshot_path)

    character = create_new_character("Lio")
    layer.save_character(character)

    # Simulate a mid-save truncation that left an invalid snapshot
    snapshot_path.write_text("{\"header\":{\"format\":\"datasworn-snapshot\"}}", encoding="utf-8")
    # Remove the database to force snapshot usage
    db_path.unlink()

    recovered = PersistenceLayer(db_path, snapshot_path).load_character("Lio")
    assert recovered is None  # integrity check should prevent loading corrupted data


def test_phase_boundary_autosave_with_backoff(tmp_path, monkeypatch):
    controller = PhaseController()
    system = AutoSaveSystem(save_directory=tmp_path)

    # First save attempt fails, second succeeds
    attempts = {"count": 0}
    original_perform = system._perform_save

    def flaky_save(game_state, slot_name, description, is_auto):
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise IOError("simulated busy disk")
        return original_perform(game_state, slot_name, description, is_auto)

    monkeypatch.setattr(system, "_perform_save", flaky_save)

    delays: list[float] = []
    monkeypatch.setattr("src.auto_save.time.sleep", lambda seconds: delays.append(seconds))

    state = {"character": {"name": "Hale"}, "session": {"turn_count": 2}}
    system.bind_to_phase_controller(controller, lambda: state)

    controller.complete_phase("downtime")

    assert attempts["count"] == 2
    assert delays and pytest.approx(delays[0], rel=1e-3) == 0.05
    assert system._get_save_path("autosave").exists()


def test_world_and_session_schema_migrations(tmp_path):
    old_world_state = {
        "entities": {
            "captain": {"entity_id": "Captain", "entity_type": "npc", "status": "dead"}
        },
        "dead_npcs": ["captain"],
    }

    migrated_world = PersistentWorldEngine.from_dict(old_world_state)
    world_payload = migrated_world.to_dict()

    assert world_payload["schema_version"] == 1
    assert "relationships" in world_payload["entities"]["captain"]

    old_tracker_state = {"events": [{"description": "A roll", "event_type": "roll"}]}
    migrated_tracker = SessionTracker.from_dict(old_tracker_state)
    tracker_payload = migrated_tracker.to_dict()

    assert tracker_payload["schema_version"] == 1
    assert migrated_tracker.session_start
