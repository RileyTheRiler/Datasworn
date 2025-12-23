import json

from src.cli_runner import CLIRunner
from src.game_state import AssetState, create_new_character
from src.persistence import CURRENT_SCHEMA_VERSION, PersistenceLayer


def test_persistence_round_trip(tmp_path):
    db_path = tmp_path / "game.db"
    snapshot_path = tmp_path / "snapshot.json"
    layer = PersistenceLayer(db_path, snapshot_path)

    character = create_new_character("Rin")
    character.vows[0].ticks = 8
    character.assets.append(AssetState(id="ally", name="Allied Asset", abilities_enabled=[True, True, False]))

    layer.save_character(character)

    snapshot = json.loads(snapshot_path.read_text())
    assert snapshot["schema_version"] == CURRENT_SCHEMA_VERSION

    reloaded = PersistenceLayer(db_path, snapshot_path).load_character("Rin")
    assert reloaded is not None
    assert reloaded.vows[0].ticks == 8
    assert reloaded.assets[0].name == "Allied Asset"


def test_cli_save_and_load_commands(tmp_path):
    db_path = tmp_path / "cli.db"
    persistence = PersistenceLayer(db_path)

    runner = CLIRunner("Nova", persistence=persistence)
    runner.state["character"].condition.health = 3
    runner.state["character"].assets.append(AssetState(id="companion", name="Companion", abilities_enabled=[True, False, False]))

    save_msg = runner._handle_command("save")
    assert "Saved" in save_msg

    new_runner = CLIRunner("Placeholder", persistence=PersistenceLayer(db_path))
    load_msg = new_runner._handle_command("load Nova")
    assert "Loaded" in load_msg
    assert new_runner.state["character"].condition.health == 3
    assert new_runner.state["character"].assets[0].id == "companion"
