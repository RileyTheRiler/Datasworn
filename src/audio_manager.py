"""Audio manager for coordinating stems, cues, and accessibility controls."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, List, Literal, Optional

from src.audio_types import MusicMood, ZoneType


@dataclass
class AudioStem:
    """Represents a layerable audio stem."""

    stem_id: str
    filename: Optional[str]
    biome: Optional[ZoneType]
    min_tension: float = 0.0
    max_tension: float = 1.0
    combat_only: bool = False

    def matches(self, biome: ZoneType, tension: float, combat_active: bool) -> bool:
        tension_match = self.min_tension <= tension <= self.max_tension
        biome_match = self.biome in (None, biome)
        combat_match = (not self.combat_only) or combat_active
        return tension_match and biome_match and combat_match

    def to_dict(self, asset_root: Path, manifest: Dict[str, str]) -> Dict[str, Optional[str]]:
        filename = self.filename
        if filename:
            lookup_key = Path(filename).stem
            filename = manifest.get(lookup_key, filename)
            filename = str(asset_root.joinpath(filename)) if not filename.startswith(str(asset_root)) else filename
        return {
            "stem_id": self.stem_id,
            "filename": filename,
            "biome": self.biome.value if self.biome else None,
            "min_tension": self.min_tension,
            "max_tension": self.max_tension,
            "combat_only": self.combat_only,
        }


@dataclass
class AudioCue:
    """Represents an audio cue tied to an encounter or narrative beat."""

    cue_id: str
    category: Literal["encounter", "narrative", "system"]
    filename: Optional[str]
    tags: List[str]

    def to_dict(self) -> Dict[str, object]:
        return {
            "cue_id": self.cue_id,
            "category": self.category,
            "filename": self.filename,
            "tags": self.tags,
        }


class AudioManager:
    """Chooses stems and cues based on biome/tension/combat state."""

    def __init__(
        self,
        state: Optional[object] = None,
        asset_root: str = "assets/audio",
    ) -> None:
        self.state = state or SimpleNamespace(
            ambient_volume=0.5,
            music_volume=0.6,
            effects_volume=0.7,
            voice_volume=0.8,
            master_volume=1.0,
            muted=False,
            sudden_spike_guard=True,
            max_volume_step=0.2,
        )
        self.asset_root = Path(asset_root)
        self.asset_manifest = self._load_asset_manifest()
        self.music_mood: Optional[MusicMood] = None
        self.stem_library = self._default_stem_library()
        self.cue_templates = {
            "encounter": "encounter_alert",
            "narrative": "narrative_swirl",
            "combat": "combat_hit",
            "low_tension": "soft_shift",
            "high_tension": "danger_shift",
        }

    def _load_asset_manifest(self) -> Dict[str, str]:
        if not self.asset_root.exists():
            return {}
        manifest: Dict[str, str] = {}
        for path in self.asset_root.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".mp3", ".wav", ".ogg"}:
                manifest[path.stem] = str(path.relative_to(self.asset_root))
        return manifest

    def _default_stem_library(self) -> List[AudioStem]:
        return [
            AudioStem("ship_base", "stems/ship_base.mp3", ZoneType.SHIP, 0.0, 0.6, False),
            AudioStem("ship_tense", "stems/ship_tension.mp3", ZoneType.SHIP, 0.6, 1.0, False),
            AudioStem("wilderness_base", "stems/wilderness_base.mp3", ZoneType.WILDERNESS, 0.0, 0.5, False),
            AudioStem("wilderness_intense", "stems/wilderness_intense.mp3", ZoneType.WILDERNESS, 0.5, 1.0, False),
            AudioStem("derelict_eerie", "stems/derelict_eerie.mp3", ZoneType.DERELICT, 0.25, 1.0, False),
            AudioStem("combat_overlay", "stems/combat_overlay.mp3", None, 0.0, 1.0, True),
        ]

    def _normalize_biome(self, biome: str | ZoneType) -> ZoneType:
        try:
            return biome if isinstance(biome, ZoneType) else ZoneType(str(biome).lower())
        except ValueError:
            return ZoneType.SHIP

    def select_stems(self, biome: str | ZoneType, tension: float, combat_active: bool) -> List[AudioStem]:
        biome_enum = self._normalize_biome(biome)
        stems = [
            stem
            for stem in self.stem_library
            if stem.matches(biome_enum, tension, combat_active)
        ]
        if combat_active:
            combat_stems = [stem for stem in self.stem_library if stem.combat_only]
            stems.extend(stem for stem in combat_stems if stem not in stems)
        if not stems:
            stems.append(AudioStem("fallback", None, biome_enum))
        return stems

    def _resolve_cue_filename(self, key: str) -> Optional[str]:
        manifest_key = self.cue_templates.get(key, key)
        filename = self.asset_manifest.get(manifest_key)
        if filename:
            return str(self.asset_root.joinpath(filename))
        return None

    def tag_audio_cues(
        self,
        category: Literal["encounter", "narrative", "system"],
        beat: str,
        biome: str | ZoneType,
        tension: float,
        combat_active: bool,
    ) -> List[AudioCue]:
        biome_enum = self._normalize_biome(biome)
        cues: List[AudioCue] = []
        tension_tag = "high_tension" if tension >= 0.6 else "low_tension"
        cue_tags = [category, beat, biome_enum.value, "combat" if combat_active else "ambient", tension_tag]

        for tag in {category, tension_tag, biome_enum.value, "combat" if combat_active else "ambient"}:
            cues.append(
                AudioCue(
                    cue_id=tag,
                    category=category,
                    filename=self._resolve_cue_filename(tag),
                    tags=sorted(set(cue_tags)),
                )
            )

        cues.append(
            AudioCue(
                cue_id=f"{category}_{beat}",
                category=category,
                filename=self._resolve_cue_filename(category),
                tags=sorted(set(cue_tags + [beat])),
            )
        )
        return cues

    def build_mix(
        self,
        biome: str | ZoneType,
        tension: float,
        combat_active: bool,
        narrative_tag: str,
    ) -> Dict[str, object]:
        stems = [stem.to_dict(self.asset_root, self.asset_manifest) for stem in self.select_stems(biome, tension, combat_active)]
        cues = [cue.to_dict() for cue in self.tag_audio_cues("encounter" if combat_active else "narrative", narrative_tag, biome, tension, combat_active)]
        return {
            "stems": stems,
            "cues": cues,
            "music_mood": self.music_mood.value if self.music_mood else None,
        }

    def apply_spike_guard(self, current: float, target: float) -> float:
        if not getattr(self.state, "sudden_spike_guard", False):
            return target
        max_step = getattr(self.state, "max_volume_step", 0.2)
        delta = max_step if target > current else -max_step
        if abs(target - current) <= max_step:
            return target
        return max(0.0, min(1.0, current + delta))

    def set_volume(self, channel: str, volume: float) -> None:
        attribute = f"{channel}_volume" if channel != "master" else "master_volume"
        if not hasattr(self.state, attribute):
            return
        current = getattr(self.state, attribute)
        guarded = self.apply_spike_guard(current, volume)
        setattr(self.state, attribute, guarded)

    def toggle_mute(self, muted: bool) -> None:
        if hasattr(self.state, "muted"):
            self.state.muted = muted

    def update_music_mood(self, mood: MusicMood) -> None:
        self.music_mood = mood
