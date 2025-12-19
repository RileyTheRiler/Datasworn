"""
Game State Schema for Starforged AI Game Master.
Uses Pydantic for validation and TypedDict for LangGraph state.
"""

from __future__ import annotations
from typing import Annotated, Any, Literal, TypedDict
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages


# ============================================================================
# Pydantic Models for validation and serialization
# ============================================================================

class CharacterStats(BaseModel):
    """Core character stats (each 1-3)."""
    edge: int = Field(default=1, ge=1, le=3)
    heart: int = Field(default=1, ge=1, le=3)
    iron: int = Field(default=1, ge=1, le=3)
    shadow: int = Field(default=1, ge=1, le=3)
    wits: int = Field(default=1, ge=1, le=3)


class CharacterCondition(BaseModel):
    """Condition meters."""
    health: int = Field(default=5, ge=0, le=5)
    spirit: int = Field(default=5, ge=0, le=5)
    supply: int = Field(default=5, ge=0, le=5)


class MomentumState(BaseModel):
    """Momentum tracking."""
    value: int = Field(default=2, ge=-6, le=10)
    max_value: int = Field(default=10)
    reset_value: int = Field(default=2)


class AssetState(BaseModel):
    """Single equipped asset."""
    id: str
    name: str
    abilities_enabled: list[bool] = Field(default_factory=lambda: [True, False, False])


class VowState(BaseModel):
    """Active vow (progress track)."""
    name: str
    rank: Literal["troublesome", "dangerous", "formidable", "extreme", "epic"]
    ticks: int = Field(default=0, ge=0, le=40)
    completed: bool = False


class Character(BaseModel):
    """Complete character state."""
    name: str
    stats: CharacterStats = Field(default_factory=CharacterStats)
    condition: CharacterCondition = Field(default_factory=CharacterCondition)
    momentum: MomentumState = Field(default_factory=MomentumState)
    assets: list[AssetState] = Field(default_factory=list)
    vows: list[VowState] = Field(default_factory=list)
    experience: int = 0
    legacy_tracks: dict[str, int] = Field(default_factory=lambda: {
        "quests": 0,
        "bonds": 0,
        "discoveries": 0,
    })


class WorldState(BaseModel):
    """World information."""
    current_location: str = "Unknown Sector"
    location_type: str = "neutral"
    discovered_locations: list[str] = Field(default_factory=list)
    truths: dict[str, str] = Field(default_factory=dict)
    npcs: list[dict[str, Any]] = Field(default_factory=list)
    factions: list[dict[str, Any]] = Field(default_factory=list)
    
    # Combat State
    combat_active: bool = False
    enemy_count: int = 0
    enemy_strength: float = 1.0
    threat_level: float = 0.0


class NarrativeState(BaseModel):
    """Narrative context."""
    current_scene: str = ""
    pending_narrative: str = ""
    campaign_summary: str = ""
    session_summary: str = ""


class RollState(BaseModel):
    """Last roll result for approval flow."""
    roll_type: str = ""  # "action", "progress", "oracle"
    result_text: str = ""
    outcome: str = ""  # "strong_hit", "weak_hit", "miss"
    is_match: bool = False


class SessionState(BaseModel):
    """Session control state."""
    awaiting_approval: bool = False
    user_decision: str = ""  # "accept", "retry", "edit"
    edited_text: str = ""
    turn_count: int = 0


class DirectorStateModel(BaseModel):
    """Director's dramatic state tracking."""
    current_act: str = "act_1_setup"
    recent_pacing: list[str] = Field(default_factory=list)
    active_beats: list[str] = Field(default_factory=list)
    tension_level: float = 0.2
    scenes_since_breather: int = 0
    foreshadowing: list[str] = Field(default_factory=list)
    moral_patterns: list[str] = Field(default_factory=list)
    # Last Director plan for narrator reference
    last_pacing: str = "standard"
    last_tone: str = "mysterious"
    last_notes: str = ""


class MemoryStateModel(BaseModel):
    """Three-tier memory state for persistence."""
    # Active context
    current_scene: str = ""
    active_npcs: list[str] = Field(default_factory=list)
    current_vow: str = ""
    recent_exchanges: list[dict[str, str]] = Field(default_factory=list)
    
    # Session buffer
    scene_summaries: list[str] = Field(default_factory=list)
    decisions_made: list[str] = Field(default_factory=list)
    npcs_encountered: dict[str, str] = Field(default_factory=dict)
    
    # Campaign summary
    major_beats: list[str] = Field(default_factory=list)
    key_relationships: dict[str, str] = Field(default_factory=dict)
    world_changes: list[str] = Field(default_factory=list)


class VoiceManagerState(BaseModel):
    """Character voice profiles for persistence."""
    profiles: dict[str, dict[str, Any]] = Field(default_factory=dict)
    active_characters: list[str] = Field(default_factory=list)


class ConsequenceEngineState(BaseModel):
    """Consequence tracking for persistence."""
    delayed_beats: list[dict[str, Any]] = Field(default_factory=list)
    moral_patterns: list[str] = Field(default_factory=list)
    scene_count: int = 0


class VowManagerState(BaseModel):
    """Enhanced vow tracking for dramatic pacing."""
    vows: dict[str, dict[str, Any]] = Field(default_factory=dict)
    vow_counter: int = 0


class QuestLoreState(BaseModel):
    """Combined state for Quest, Lore, Schedules, and Rumors."""
    quests: dict[str, Any] = Field(default_factory=dict)
    lore: dict[str, Any] = Field(default_factory=dict)
    schedules: dict[str, Any] = Field(default_factory=dict)
    rumors: dict[str, Any] = Field(default_factory=dict)


class CompanionManagerState(BaseModel):
    """Companion AI persistence."""
    companions: dict[str, dict[str, Any]] = Field(default_factory=dict)
    active_companion: str = ""


class ThemeTrackerState(BaseModel):
    """Theme tracking persistence."""
    primary_theme: str = "love_vs_survival"
    theme_moments: list[str] = Field(default_factory=list)
    theme_reinforced_count: int = 0
    theme_subverted_count: int = 0


# ============================================================================
# LangGraph State TypedDict (uses Annotated for reducers)
# ============================================================================

class GameState(TypedDict):
    """LangGraph state schema."""
    # Messages with add_messages reducer (appends new messages)
    messages: Annotated[list[dict[str, Any]], add_messages]

    # Character data (replaced on update)
    character: Character

    # World state
    world: WorldState

    # Narrative context
    narrative: NarrativeState

    # Last roll for approval
    last_roll: RollState

    # Session control
    session: SessionState

    # Director's dramatic state
    director: DirectorStateModel
    
    # Memory system
    memory: MemoryStateModel
    
    # Character voice profiles
    voices: VoiceManagerState
    
    # Consequence tracking
    consequences: ConsequenceEngineState
    
    # Vow management
    vows: VowManagerState

    # Quest & Lore systems
    quest_lore: QuestLoreState

    # Companion AI
    companions: CompanionManagerState

    # Theme tracking
    theme_tracker: ThemeTrackerState

    # Routing decision
    route: str  # "move", "oracle", "narrative", "end_turn", "approval"


# ============================================================================
# Helper functions
# ============================================================================

def create_new_character(name: str) -> Character:
    """Create a new character with default stats."""
    return Character(
        name=name,
        vows=[
            VowState(
                name="Background Vow",
                rank="epic",
            )
        ],
    )


def create_initial_state(character_name: str) -> GameState:
    """Create initial game state for a new game."""
    character = create_new_character(character_name)
    return GameState(
        messages=[],
        character=character,
        world=WorldState(),
        narrative=NarrativeState(),
        last_roll=RollState(),
        session=SessionState(),
        director=DirectorStateModel(),
        memory=MemoryStateModel(),
        voices=VoiceManagerState(),
        consequences=ConsequenceEngineState(),
        vows=VowManagerState(),
        quest_lore=QuestLoreState(),
        companions=CompanionManagerState(),
        theme_tracker=ThemeTrackerState(),
        route="",
    )

