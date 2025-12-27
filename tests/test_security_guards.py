import pytest

from src.asset_ingestion import ingest_asset_bytes
from src.auto_save import AutoSaveSystem


def test_save_blocks_traversal(tmp_path):
    system = AutoSaveSystem(save_directory=tmp_path)
    with pytest.raises(ValueError):
        system.save_game({"character": {"name": "A"}, "world": {}, "session": {}}, slot_name="../escape")


def test_save_blocks_oversized_payload(tmp_path):
    system = AutoSaveSystem(save_directory=tmp_path, max_payload_bytes=64)
    large_state = {"character": {"name": "A", "bio": "x" * 200}, "world": {}, "session": {}}
    with pytest.raises(ValueError):
        system.save_game(large_state, slot_name="bigsave")


def test_ingest_asset_blocks_traversal(tmp_path):
    with pytest.raises(ValueError):
        ingest_asset_bytes(tmp_path, "../secret.png", b"1234")


def test_ingest_asset_blocks_oversized_payload(tmp_path):
    with pytest.raises(ValueError):
        ingest_asset_bytes(tmp_path, "sprite.png", b"x" * 2048, max_bytes=1024)
