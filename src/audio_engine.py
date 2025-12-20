"""
Audio Engine for Starforged AI Game Master.
Manages dynamic soundscapes, adaptive music, and audio state.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal, Optional
from enum import Enum


# ============================================================================
# Zone Types & Audio Presets
# ============================================================================

class ZoneType(str, Enum):
    """Zone types for soundscape matching."""
    BAR = "bar"
    DERELICT = "derelict"
    WILDERNESS = "wilderness"
    SHIP = "ship"
    STATION = "station"
    COMBAT = "combat"
    VOID = "void"
    SETTLEMENT = "settlement"


class MusicMood(str, Enum):
    """Music moods based on tension/narrative state."""
    AMBIENT = "ambient"
    EXPLORATION = "exploration"
    TENSION = "tension"
    COMBAT = "combat"
    VICTORY = "victory"
    DEFEAT = "defeat"
    MYSTERY = "mystery"
    EMOTIONAL = "emotional"


# ============================================================================
# Soundscape Presets
# ============================================================================

@dataclass
class SoundscapePreset:
    """Defines ambient audio layers for a zone type."""
    zone_type: ZoneType
    ambient_tracks: list[str]  # Track IDs to layer
    volume: float = 0.6
    description: str = ""


# Preset library
SOUNDSCAPE_PRESETS = {
    ZoneType.BAR: SoundscapePreset(
        zone_type=ZoneType.BAR,
        ambient_tracks=["ambient_chatter", "glasses_clinking", "bar_music"],
        volume=0.5,
        description="Busy bar atmosphere with conversation and music"
    ),
    ZoneType.DERELICT: SoundscapePreset(
        zone_type=ZoneType.DERELICT,
        ambient_tracks=["creaking_metal", "distant_echoes", "alarm_distant"],
        volume=0.4,
        description="Eerie abandoned ship with mechanical sounds"
    ),
    ZoneType.WILDERNESS: SoundscapePreset(
        zone_type=ZoneType.WILDERNESS,
        ambient_tracks=["wind_howling", "alien_calls", "environmental_hum"],
        volume=0.5,
        description="Alien wilderness with wind and creature sounds"
    ),
    ZoneType.SHIP: SoundscapePreset(
        zone_type=ZoneType.SHIP,
        ambient_tracks=["ship_hum", "engine_rumble", "life_support"],
        volume=0.4,
        description="Active ship interior with systems running"
    ),
    ZoneType.STATION: SoundscapePreset(
        zone_type=ZoneType.STATION,
        ambient_tracks=["station_ambient", "crowd_distant", "announcements"],
        volume=0.5,
        description="Space station with crowds and announcements"
    ),
    ZoneType.VOID: SoundscapePreset(
        zone_type=ZoneType.VOID,
        ambient_tracks=["void_silence", "suit_breathing", "radio_static"],
        volume=0.3,
        description="Deep space EVA with minimal sound"
    ),
    ZoneType.SETTLEMENT: SoundscapePreset(
        zone_type=ZoneType.SETTLEMENT,
        ambient_tracks=["settlement_life", "machinery", "voices_distant"],
        volume=0.5,
        description="Living settlement with activity"
    ),
}


# ============================================================================
# Music System
# ============================================================================

@dataclass
class MusicTrack:
    """Defines a music track."""
    track_id: str
    mood: MusicMood
    intensity: float  # 0.0-1.0
    filename: str
    description: str = ""


# Music library (to be populated with actual tracks)
MUSIC_LIBRARY = [
    MusicTrack("explore_calm", MusicMood.EXPLORATION, 0.3, "music/exploration_calm.mp3", "Calm exploration"),
    MusicTrack("explore_tense", MusicMood.EXPLORATION, 0.6, "music/exploration_tense.mp3", "Tense exploration"),
    MusicTrack("tension_low", MusicMood.TENSION, 0.4, "music/tension_low.mp3", "Building tension"),
    MusicTrack("tension_high", MusicMood.TENSION, 0.8, "music/tension_high.mp3", "High tension"),
    MusicTrack("combat_light", MusicMood.COMBAT, 0.6, "music/combat_light.mp3", "Light combat"),
    MusicTrack("combat_intense", MusicMood.COMBAT, 0.9, "music/combat_intense.mp3", "Intense combat"),
    MusicTrack("victory", MusicMood.VICTORY, 0.7, "music/victory.mp3", "Victory sting"),
    MusicTrack("defeat", MusicMood.DEFEAT, 0.6, "music/defeat.mp3", "Defeat sting"),
    MusicTrack("mystery", MusicMood.MYSTERY, 0.5, "music/mystery.mp3", "Mysterious atmosphere"),
    MusicTrack("emotional", MusicMood.EMOTIONAL, 0.5, "music/emotional.mp3", "Emotional moment"),
]


# ============================================================================
# Audio Engine
# ============================================================================

@dataclass
class AudioState:
    """Current audio playback state."""
    current_ambient: Optional[str] = None  # Zone type
    current_music: Optional[str] = None  # Track ID
    ambient_volume: float = 0.5
    music_volume: float = 0.6
    voice_volume: float = 0.8
    master_volume: float = 1.0
    muted: bool = False


class AudioEngine:
    """
    Manages audio state and provides directives for frontend playback.
    Does not handle actual playback - that's done by frontend AudioManager.
    """
    
    def __init__(self):
        self.state = AudioState()
        self.music_library = {track.track_id: track for track in MUSIC_LIBRARY}
        self.soundscape_presets = SOUNDSCAPE_PRESETS
    
    def get_soundscape_for_zone(self, zone_type: str) -> Optional[SoundscapePreset]:
        """Get soundscape preset for a zone type."""
        try:
            zone_enum = ZoneType(zone_type.lower())
            return self.soundscape_presets.get(zone_enum)
        except (ValueError, KeyError):
            # Default to ship if unknown
            return self.soundscape_presets.get(ZoneType.SHIP)
    
    def select_music_for_state(
        self,
        tension: float,
        combat_active: bool = False,
        outcome: Optional[str] = None
    ) -> Optional[MusicTrack]:
        """
        Select appropriate music based on game state.
        
        Args:
            tension: Director tension level (0.0-1.0)
            combat_active: Whether combat is active
            outcome: Recent outcome ("victory", "defeat", None)
        
        Returns:
            MusicTrack or None
        """
        # Handle outcomes first (stings)
        if outcome == "victory":
            return self.music_library.get("victory")
        elif outcome == "defeat":
            return self.music_library.get("defeat")
        
        # Combat music
        if combat_active:
            if tension > 0.7:
                return self.music_library.get("combat_intense")
            else:
                return self.music_library.get("combat_light")
        
        # Tension-based exploration music
        if tension > 0.6:
            return self.music_library.get("tension_high")
        elif tension > 0.4:
            return self.music_library.get("tension_low")
        elif tension > 0.2:
            return self.music_library.get("explore_tense")
        else:
            return self.music_library.get("explore_calm")
    
    def update_for_location(self, location: str, location_type: str = "ship") -> dict:
        """
        Update audio state for a new location.
        
        Returns:
            Audio directives for frontend
        """
        preset = self.get_soundscape_for_zone(location_type)
        
        if preset:
            self.state.current_ambient = preset.zone_type.value
            
        return {
            "ambient": {
                "zone_type": self.state.current_ambient,
                "tracks": preset.ambient_tracks if preset else [],
                "volume": preset.volume if preset else 0.5
            }
        }
    
    def update_for_tension(
        self,
        tension: float,
        combat_active: bool = False,
        outcome: Optional[str] = None
    ) -> dict:
        """
        Update music based on tension/combat state.
        
        Returns:
            Audio directives for frontend
        """
        track = self.select_music_for_state(tension, combat_active, outcome)
        
        if track:
            self.state.current_music = track.track_id
            
        return {
            "music": {
                "track_id": track.track_id if track else None,
                "filename": track.filename if track else None,
                "mood": track.mood.value if track else None,
                "volume": self.state.music_volume
            }
        }
    
    def get_audio_directives(
        self,
        location: str,
        location_type: str,
        tension: float,
        combat_active: bool = False,
        outcome: Optional[str] = None
    ) -> dict:
        """
        Get complete audio directives for current game state.
        
        Returns:
            Complete audio state for frontend
        """
        ambient_directive = self.update_for_location(location, location_type)
        music_directive = self.update_for_tension(tension, combat_active, outcome)
        
        return {
            **ambient_directive,
            **music_directive,
            "volumes": {
                "ambient": self.state.ambient_volume,
                "music": self.state.music_volume,
                "voice": self.state.voice_volume,
                "master": self.state.master_volume
            },
            "muted": self.state.muted
        }
    
    def set_volume(self, channel: str, volume: float) -> None:
        """Set volume for a specific channel."""
        volume = max(0.0, min(1.0, volume))
        
        if channel == "ambient":
            self.state.ambient_volume = volume
        elif channel == "music":
            self.state.music_volume = volume
        elif channel == "voice":
            self.state.voice_volume = volume
        elif channel == "master":
            self.state.master_volume = volume
    
    def toggle_mute(self) -> bool:
        """Toggle mute state. Returns new mute state."""
        self.state.muted = not self.state.muted
        return self.state.muted
    
    def to_dict(self) -> dict:
        """Serialize state for persistence."""
        return {
            "current_ambient": self.state.current_ambient,
            "current_music": self.state.current_music,
            "ambient_volume": self.state.ambient_volume,
            "music_volume": self.state.music_volume,
            "voice_volume": self.state.voice_volume,
            "master_volume": self.state.master_volume,
            "muted": self.state.muted
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "AudioEngine":
        """Deserialize from saved state."""
        engine = cls()
        engine.state.current_ambient = data.get("current_ambient")
        engine.state.current_music = data.get("current_music")
        engine.state.ambient_volume = data.get("ambient_volume", 0.5)
        engine.state.music_volume = data.get("music_volume", 0.6)
        engine.state.voice_volume = data.get("voice_volume", 0.8)
        engine.state.master_volume = data.get("master_volume", 1.0)
        engine.state.muted = data.get("muted", False)
        return engine
