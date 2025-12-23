"""Shared audio-related enumerations and constants."""

from enum import Enum


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
