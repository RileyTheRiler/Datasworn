import pytest

from src.audio_manager import AudioManager
from src.audio_types import ZoneType


def test_selects_stems_for_biome_tension_and_combat(tmp_path):
    stems_dir = tmp_path / "stems"
    stems_dir.mkdir()
    for name in ["ship_base.mp3", "ship_tension.mp3", "combat_overlay.mp3"]:
        (stems_dir / name).write_text("stub")

    manager = AudioManager(asset_root=str(tmp_path))
    stems = manager.select_stems(ZoneType.SHIP, tension=0.85, combat_active=True)

    stem_ids = {stem.stem_id for stem in stems}
    assert "ship_tense" in stem_ids
    assert "combat_overlay" in stem_ids


def test_tags_cues_with_asset_manifest(tmp_path):
    (tmp_path / "encounter_alert.mp3").write_text("cue")
    (tmp_path / "combat_hit.mp3").write_text("cue")

    manager = AudioManager(asset_root=str(tmp_path))
    cues = manager.tag_audio_cues(
        category="encounter",
        beat="ambush",
        biome=ZoneType.WILDERNESS,
        tension=0.75,
        combat_active=True,
    )

    filenames = {cue.filename for cue in cues}
    assert any("encounter_alert.mp3" in (name or "") for name in filenames)
    assert any("combat_hit.mp3" in (name or "") for name in filenames)
    assert any("encounter_ambush" == cue.cue_id for cue in cues)


def test_spike_guard_limits_volume_jumps():
    manager = AudioManager()
    manager.state.music_volume = 0.2

    manager.set_volume("music", 0.9)
    assert manager.state.music_volume == pytest.approx(0.4)

    manager.state.sudden_spike_guard = False
    manager.set_volume("music", 0.9)
    assert manager.state.music_volume == pytest.approx(0.9)
