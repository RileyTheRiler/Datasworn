from pathlib import Path

from src.cli_runner import CLIRunner
from src.lore import LoreRegistry
from src.persistent_world import ChangeType, PersistentWorldEngine, WorldChange


def test_registry_search_and_filters():
    registry = LoreRegistry(Path("data/lore"))
    assert registry.entries, "Expected sample lore entries to load"

    text_results = registry.search("Shadowport")
    assert any(entry.title == "Shadowport Expanse" for entry in text_results)

    faction_results = registry.search(factions=["Veiled Syndicate"])
    assert all("Veiled Syndicate" in entry.factions for entry in faction_results)

    item_results = registry.search(items=["Black Cipher"])
    assert item_results, "Filter by item should return codex entries"


def test_world_change_links_discovery_and_callbacks():
    registry = LoreRegistry(Path("data/lore"))
    engine = PersistentWorldEngine()
    engine.attach_lore_registry(registry)

    change = WorldChange(
        change_type=ChangeType.LOCATION_DISCOVERED,
        entity_id="Shadowport Expanse",
        entity_type="location",
        description="Uncovered a hidden dock network"
    )
    engine.record_change(change)

    entry = registry.get_entry("location.shadowport_expanse")
    assert entry and entry.discovered
    callbacks = registry.narrative_callbacks(ChangeType.LOCATION_DISCOVERED.value)
    assert callbacks and any("catwalks" in cb for cb in callbacks)


def test_cli_codex_command_uses_filters():
    runner = CLIRunner("Tester")
    response = runner._handle_command("codex Black faction:Veiled Syndicate item:Black Cipher")
    assert "Codex results" in response
    assert "Veiled Syndicate" in response
