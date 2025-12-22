"""
Game State Schema for Starforged AI Game Master.
Uses Pydantic for validation and TypedDict for LangGraph state.
"""

from __future__ import annotations
from typing import Annotated, Any, Literal, TypedDict, Optional
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from src.npc.schemas import CognitiveState
import time


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


class ShipModule(BaseModel):
    """Component of a ship."""
    id: str
    name: str
    type: str  # bridge, engineering, cargo, quarters, medical
    integrity: int = 100
    max_integrity: int = 100
    status: str = "operational"
    description: str = ""


class ShipState(BaseModel):
    """Player ship state."""
    name: str = "The Exile's Gambit"
    class_type: str = "freighter"
    hull_integrity: int = 100
    max_hull: int = 100
    shield_integrity: int = 100
    max_shield: int = 100
    modules: list[ShipModule] = Field(default_factory=list)
    active_alerts: list[str] = Field(default_factory=list)
    
    def get_module(self, module_id: str) -> ShipModule | None:
        return next((m for m in self.modules if m.id == module_id), None)


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


class WorldState(BaseModel):
    """World information."""
    current_location: str = "Unknown Sector"
    location_type: str = "neutral"
    discovered_locations: list[str] = Field(default_factory=list)
    truths: dict[str, str] = Field(default_factory=dict)
    npcs: list[dict[str, Any]] = Field(default_factory=list)
    factions: list[dict[str, Any]] = Field(default_factory=list)
    ship: ShipState = Field(default_factory=lambda: ShipState())
    
    # Combat State
    combat_active: bool = False
    enemy_count: int = 0
    enemy_strength: float = 1.0
    threat_level: float = 0.0

    # Environmental State
    current_time: str = "Day"  # Day, Night, Twilight, Dawn
    current_weather: str = "Clear"  # Clear, Rain, Dust Storm, Fog, Snow, Storm
    location_visuals: dict[str, dict[str, str]] = Field(default_factory=dict)  # location -> {time, weather, image_url}


class AudioState(BaseModel):
    """Audio playback state."""
    current_ambient: Optional[str] = None  # Zone type
    current_tracks: list[str] = Field(default_factory=list) # Actual MP3 filenames (without .mp3)
    current_music: Optional[str] = None  # Track ID
    music_filename: Optional[str] = None # MP3 filename
    ambient_volume: float = 0.5
    music_volume: float = 0.6
    voice_volume: float = 0.8
    master_volume: float = 1.0
    muted: bool = False


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
    
    # World Simulation Integration
    # Crime & Reputation
    crimes_committed: list[dict[str, Any]] = Field(default_factory=list)
    reputation: dict[str, float] = Field(default_factory=dict)  # faction_id -> rep (-1.0 to 1.0)
    honor: float = Field(default=0.5, ge=0.0, le=1.0)
    
    # Posture & State
    current_posture: str = "normal"  # normal, sneaking, combat_ready
    weapon_readied: bool = False
    intoxication_level: float = Field(default=0.0, ge=0.0, le=1.0)
    disguise_active: Optional[str] = None  # disguise_id or None





class NarrativeState(BaseModel):
    """Narrative context."""
    current_scene: str = ""
    pending_narrative: str = ""
    campaign_summary: str = ""
    session_summary: str = ""
    
    # Interrogation Manager (stored loosely as it's not a Pydantic model yet)
    interrogation_manager: Optional[Any] = None
    
    # Ending System State
    ending_triggered: bool = False
    ending_choice: Optional[str] = None  # "accept" or "reject"
    ending_type: Optional[str] = None  # "hero" or "tragedy"
    ending_stage: str = "not_started"  # decision/test/resolution/wisdom/final_scene/complete
    
    # Investigation Flags (for Port Arrival docking scenarios)
    murder_reported: bool = False  # Did player report murder to authorities?
    yuki_past_revealed: bool = False  # Was Yuki's Helix Dynamics past exposed?
    kai_debts_unresolved: bool = True  # Are Kai's debts still outstanding?

 


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
# Psychological State (Updated)
# ============================================================================

from src.psych_profile import PsychologicalProfile

class PsycheState(BaseModel):
    """Psychological profile and inner voice state."""
    profile: PsychologicalProfile = Field(default_factory=PsychologicalProfile)
    # Map of Aspect Name -> Dominance (0.0-1.0)
    voice_dominance: dict[str, float] = Field(default_factory=dict)
    # List of unlocked memory IDs (linking to MemoryPalace)
    unlocked_memories: list[str] = Field(default_factory=list)
    # Current active hijack (if any)
    active_hijack: dict[str, str] | None = None
    # Track which stress/sanity events have already fired
    events_triggered: list[str] = Field(default_factory=list)
    
    # Archetype System Fields
    archetype_profile: Any = None  # ArchetypeProfile instance
    behavior_history: list[Any] = Field(default_factory=list)  # List of BehaviorInstance
    revelation_progress: Any = None  # RevelationProgress instance
    
    class Config:
        arbitrary_types_allowed = True  # Allow non-Pydantic types


class RelationshipState(BaseModel):
    """Crew relationship state."""
    crew: dict[str, dict[str, Any]] = Field(default_factory=dict)


class MysteryState(BaseModel):
    """Procedural mystery state."""
    threat_id: str = ""
    threat_motive: str = ""
    clues: list[dict[str, Any]] = Field(default_factory=list)
    is_revealed: bool = False


class NarrativeOrchestratorState(BaseModel):
    """Narrative orchestrator state for all narrative systems."""
    orchestrator_data: dict[str, Any] = Field(default_factory=dict)
    
    # Phase 1: Foundational Systems Persistence
    payoff_tracker: dict[str, Any] = Field(default_factory=dict)
    npc_memories: dict[str, dict[str, Any]] = Field(default_factory=dict)  # npc_id -> memory_data
    consequence_manager: dict[str, Any] = Field(default_factory=dict)
    echo_system: dict[str, Any] = Field(default_factory=dict)
    
    # Phase 2: NPC Depth Persistence
    npc_emotions: dict[str, Any] = Field(default_factory=dict) # emotional_states
    reputation: dict[str, Any] = Field(default_factory=dict)
    irony_tracker: dict[str, Any] = Field(default_factory=dict)
    
    # Phase 3: Advanced Narrative Persistence
    story_beats: dict[str, Any] = Field(default_factory=dict)
    plot_manager: dict[str, Any] = Field(default_factory=dict)
    branching_system: dict[str, Any] = Field(default_factory=dict)
    npc_goals: dict[str, Any] = Field(default_factory=dict)
    
    # Phase 4: Polish Persistence
    ending_system: dict[str, Any] = Field(default_factory=dict)
    dilemma_generator: dict[str, Any] = Field(default_factory=dict)
    environmental_storyteller: dict[str, Any] = Field(default_factory=dict)
    flashback_system: dict[str, Any] = Field(default_factory=dict)
    
    # Phase 5: Experimental Persistence
    unreliable_system: dict[str, Any] = Field(default_factory=dict)
    meta_system: dict[str, Any] = Field(default_factory=dict)
    npc_skills: dict[str, Any] = Field(default_factory=dict)
    multiplayer_system: dict[str, Any] = Field(default_factory=dict)
    
    # Psychological Systems (Phase 1)
    dream_engine: dict[str, Any] = Field(default_factory=dict)
    phobia_system: dict[str, Any] = Field(default_factory=dict)
    
    # Psychological Systems (Phase 2)
    addiction_system: dict[str, Any] = Field(default_factory=dict)
    moral_injury_system: dict[str, Any] = Field(default_factory=dict)
    
    # Psychological Systems (Phase 3)
    attachment_system: dict[str, Any] = Field(default_factory=dict)
    trust_dynamics: dict[str, Any] = Field(default_factory=dict)


class StarmapState(BaseModel):
    """Starmap and exploration state."""
    current_sector: dict[str, Any] = Field(default_factory=dict)
    current_system_id: str = ""
    discovered_systems: list[str] = Field(default_factory=list)
    travel_history: list[str] = Field(default_factory=list)


class RumorState(BaseModel):
    """Rumor network state."""
    rumors: dict[str, dict[str, Any]] = Field(default_factory=dict)
    rumor_counter: int = 0


class WorldSimState(BaseModel):
    """State for the living world simulation."""
    events: list[dict[str, Any]] = Field(default_factory=list)
    event_counter: int = 0
    serialized_state: dict[str, Any] = Field(default_factory=dict)


class HazardState(BaseModel):
    """State for environmental hazards."""
    active_hazards: list[dict[str, Any]] = Field(default_factory=list)




class PhotoEntry(BaseModel):
    """A captured moment in the photo album."""
    id: str
    image_url: str
    caption: str
    timestamp: str  # In-game date/time or real time
    tags: list[str] = Field(default_factory=list)  # e.g., ["Boss", "Vow", "Betrayal"]
    scene_id: str = ""


class PhotoAlbumState(BaseModel):
    """Persistent state for the photo album."""
    photos: list[PhotoEntry] = Field(default_factory=list)



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

    # Psychological State
    psyche: PsycheState

    # Crew Relationships
    relationships: RelationshipState

    # Mystery Configuration
    mystery: MysteryState
    
    # Narrative Orchestrator (all narrative systems)
    narrative_orchestrator: NarrativeOrchestratorState

    # Photo Album
    album: PhotoAlbumState

    # Star Map (stored as dict)
    starmap: dict[str, Any] = Field(default_factory=dict)

    # Rumor Network (stored as dict)
    rumors: dict[str, Any] = Field(default_factory=dict)

    # World Simulation (stored as dict)
    world_sim: WorldSimState = Field(default_factory=WorldSimState)

    # Hazards (stored as dict)
    hazards: dict[str, Any] = Field(default_factory=dict)

    # Audio State
    audio: AudioState

    # Cognitive Engine (NPC Minds)
    cognitive_npc_state: dict[str, CognitiveState] = Field(default_factory=dict)

    # Routing decision
    route: str


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
        psyche=PsycheState(),
        relationships=RelationshipState(),
        mystery=MysteryState(),
        narrative_orchestrator=NarrativeOrchestratorState(),
        album=PhotoAlbumState(),
        starmap={},
        cognitive_npc_state={},
        rumors={},
        world_sim=WorldSimState(),
        hazards={},
        audio=AudioState(),
        route="",
    )

