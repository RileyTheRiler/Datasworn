"""
Encounter Spawner System (AI Director).
Dynamically spawns enemies based on location, difficulty, and player state.

Based on Game AI Pro patterns for spawn management.
Prevents "pop-in" by checking visibility and narrative context.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import random


# ============================================================================
# Spawn Triggers
# ============================================================================

class SpawnTrigger(Enum):
    """What causes enemies to spawn."""
    LOCATION_ENTRY = "location_entry"  # Player enters new area
    THREAT_THRESHOLD = "threat_threshold"  # Threat level exceeds threshold
    TIMED = "timed"  # Scheduled encounter
    ACTION_BASED = "action_based"  # Player does something (loud noise, etc.)
    STORY_BEAT = "story_beat"  # Director-triggered for story
    PATROL = "patrol"  # Regular patrol patterns


class SpawnType(Enum):
    """Types of encounter spawns."""
    AMBUSH = "ambush"  # Surprise attack
    PATROL = "patrol"  # Wandering enemies
    GUARD = "guard"  # Stationary defenders
    BOSS = "boss"  # Major encounter
    REINFORCEMENT = "reinforcement"  # Called during combat
    ENVIRONMENTAL = "environmental"  # Hazard creatures


# ============================================================================
# Spawn Templates
# ============================================================================

@dataclass
class EnemyTemplate:
    """Template for an enemy type."""
    name: str
    threat_value: float = 1.0  # How dangerous (1 = average)
    preferred_spawn: SpawnType = SpawnType.PATROL
    group_size_min: int = 1
    group_size_max: int = 3
    description: str = ""
    behaviors: list[str] = field(default_factory=list)


# Pre-built enemy templates for Starforged
ENEMY_TEMPLATES = {
    "raider": EnemyTemplate(
        name="Raiders",
        threat_value=0.8,
        preferred_spawn=SpawnType.AMBUSH,
        group_size_min=2,
        group_size_max=4,
        description="Desperate scavengers looking for easy prey",
        behaviors=["aggressive", "flanking"],
    ),
    "pirate": EnemyTemplate(
        name="Pirates",
        threat_value=1.2,
        preferred_spawn=SpawnType.PATROL,
        group_size_min=3,
        group_size_max=5,
        description="Organized criminals with better gear",
        behaviors=["tactical", "cover_user"],
    ),
    "security": EnemyTemplate(
        name="Security Forces",
        threat_value=1.0,
        preferred_spawn=SpawnType.GUARD,
        group_size_min=2,
        group_size_max=3,
        description="Professional guards protecting something",
        behaviors=["defensive", "call_backup"],
    ),
    "creature": EnemyTemplate(
        name="Hostile Creature",
        threat_value=1.5,
        preferred_spawn=SpawnType.ENVIRONMENTAL,
        group_size_min=1,
        group_size_max=2,
        description="Alien predator hunting in its territory",
        behaviors=["stalking", "territorial"],
    ),
    "machine": EnemyTemplate(
        name="Rogue Machine",
        threat_value=1.3,
        preferred_spawn=SpawnType.PATROL,
        group_size_min=1,
        group_size_max=3,
        description="Malfunctioning or reprogrammed automaton",
        behaviors=["relentless", "armored"],
    ),
    "boss": EnemyTemplate(
        name="Nemesis",
        threat_value=3.0,
        preferred_spawn=SpawnType.BOSS,
        group_size_min=1,
        group_size_max=1,
        description="A powerful adversary with a grudge",
        behaviors=["elite", "tactical_mastermind"],
    ),
}


# ============================================================================
# Spawn Context
# ============================================================================

@dataclass
class SpawnContext:
    """Context for spawn decisions."""
    location: str = ""
    location_type: str = "neutral"  # ship, station, planet, derelict
    threat_level: float = 0.0  # 0-1
    player_health: float = 1.0  # 0-1
    player_visible: bool = True  # Is player in an observable area
    recent_combat: bool = False  # Was there combat recently
    story_beat: str = ""  # Any active story beat requiring encounter
    current_scene: int = 0
    difficulty: str = "normal"


# ============================================================================
# Encounter Director
# ============================================================================

@dataclass
class SpawnDecision:
    """Result of a spawn decision."""
    should_spawn: bool = False
    template: EnemyTemplate | None = None
    count: int = 0
    spawn_type: SpawnType = SpawnType.PATROL
    narrative_intro: str = ""
    delay_scenes: int = 0  # Delay before spawn activates


class EncounterDirector:
    """
    AI Director for encounter spawning.
    Manages when and how enemies appear based on game state.
    """
    
    def __init__(self, difficulty: str = "normal"):
        self.difficulty = difficulty
        self.spawn_history: list[dict] = []
        self.scenes_since_combat: int = 5
        self.tension_buildup: float = 0.0
        self.active_encounters: list[dict] = []
        
        # Difficulty modifiers
        self.difficulty_modifiers = {
            "easy": {"spawn_chance": 0.6, "group_size": 0.7, "threat_mult": 0.8},
            "normal": {"spawn_chance": 1.0, "group_size": 1.0, "threat_mult": 1.0},
            "hard": {"spawn_chance": 1.2, "group_size": 1.2, "threat_mult": 1.2},
            "nightmare": {"spawn_chance": 1.5, "group_size": 1.5, "threat_mult": 1.5},
        }
    
    def evaluate(self, context: SpawnContext) -> SpawnDecision:
        """
        Evaluate whether to spawn an encounter.
        
        Args:
            context: Current game context
            
        Returns:
            SpawnDecision with spawn details
        """
        decision = SpawnDecision()
        
        # Get difficulty modifier
        mod = self.difficulty_modifiers.get(context.difficulty, self.difficulty_modifiers["normal"])
        
        # Build up tension over non-combat scenes
        self.scenes_since_combat += 1
        self.tension_buildup = min(1.0, self.scenes_since_combat * 0.1)
        
        # Don't spawn if player just fought
        if context.recent_combat:
            self.scenes_since_combat = 0
            self.tension_buildup = 0.0
            return decision
        
        # Check for story-mandated encounter
        if context.story_beat:
            return self._spawn_story_encounter(context, mod)
        
        # Calculate spawn probability
        base_chance = 0.15 * mod["spawn_chance"]
        
        # Increase chance with tension buildup
        spawn_chance = base_chance + (self.tension_buildup * 0.3)
        
        # Reduce chance if player is hurt (mercy mechanic)
        if context.player_health < 0.4:
            spawn_chance *= 0.5
        
        # Increase chance in high-threat areas
        spawn_chance += context.threat_level * 0.2
        
        # Roll for spawn
        if random.random() > spawn_chance:
            return decision  # No spawn
        
        # Select appropriate enemy template
        template = self._select_template(context)
        if not template:
            return decision
        
        # Calculate group size
        base_size = random.randint(template.group_size_min, template.group_size_max)
        group_size = max(1, int(base_size * mod["group_size"]))
        
        # Determine spawn type
        spawn_type = self._determine_spawn_type(context, template)
        
        # Generate narrative introduction
        narrative = self._generate_narrative_intro(template, spawn_type, group_size, context)
        
        # Update state
        self.scenes_since_combat = 0
        self.tension_buildup = 0.0
        
        decision.should_spawn = True
        decision.template = template
        decision.count = group_size
        decision.spawn_type = spawn_type
        decision.narrative_intro = narrative
        
        # Record spawn
        self.spawn_history.append({
            "template": template.name,
            "count": group_size,
            "scene": context.current_scene,
            "location": context.location,
        })
        
        return decision
    
    def _spawn_story_encounter(self, context: SpawnContext, mod: dict) -> SpawnDecision:
        """Spawn a story-mandated encounter."""
        decision = SpawnDecision()
        
        # Story beats get boss-level treatment
        template = ENEMY_TEMPLATES.get("boss", ENEMY_TEMPLATES["pirate"])
        
        decision.should_spawn = True
        decision.template = template
        decision.count = 1
        decision.spawn_type = SpawnType.BOSS
        decision.narrative_intro = f"The moment you've been dreading arrives. {template.description}."
        
        return decision
    
    def _select_template(self, context: SpawnContext) -> EnemyTemplate | None:
        """Select appropriate enemy template based on context."""
        # Filter by location type
        location_preferences = {
            "ship": ["pirate", "raider"],
            "station": ["security", "raider", "machine"],
            "planet": ["creature", "raider"],
            "derelict": ["machine", "creature", "raider"],
        }
        
        preferred = location_preferences.get(context.location_type, ["raider", "pirate"])
        
        # Weight by threat level
        if context.threat_level > 0.7:
            preferred = ["pirate", "security", "boss"]
        
        # Select from preferred templates
        available = [ENEMY_TEMPLATES[k] for k in preferred if k in ENEMY_TEMPLATES]
        
        if not available:
            return ENEMY_TEMPLATES.get("raider")
        
        return random.choice(available)
    
    def _determine_spawn_type(self, context: SpawnContext, template: EnemyTemplate) -> SpawnType:
        """Determine how enemies will appear."""
        # Use template preference as default
        spawn_type = template.preferred_spawn
        
        # Override based on context
        if not context.player_visible:
            spawn_type = SpawnType.AMBUSH
        
        if context.threat_level > 0.8:
            spawn_type = random.choice([SpawnType.AMBUSH, SpawnType.GUARD])
        
        return spawn_type
    
    def _generate_narrative_intro(
        self,
        template: EnemyTemplate,
        spawn_type: SpawnType,
        count: int,
        context: SpawnContext,
    ) -> str:
        """Generate narrative introduction for the encounter."""
        intros = {
            SpawnType.AMBUSH: [
                f"Movement in the shadows. {template.description} emerge from hiding.",
                f"You walked right into it. {count} hostiles surround you.",
                f"The trap springs. {template.name} reveal themselves.",
            ],
            SpawnType.PATROL: [
                f"Voices ahead. A patrol of {template.name.lower()} rounds the corner.",
                f"You spot them before they spot you. {count} contacts.",
                f"A routine patrol—{template.name.lower()}—blocks your path.",
            ],
            SpawnType.GUARD: [
                f"{template.name} stand watch ahead. They haven't seen you yet.",
                f"Guards. {count} of them. {template.description}.",
                f"The checkpoint ahead is manned. {template.name.lower()}.",
            ],
            SpawnType.BOSS: [
                f"They've found you. {template.description}.",
                f"No more running. Your nemesis has arrived.",
                f"The confrontation you knew was coming is here.",
            ],
            SpawnType.REINFORCEMENT: [
                f"More of them. {count} reinforcements arriving.",
                f"Backup has arrived for your enemies.",
                f"The fight just got harder. More {template.name.lower()} pour in.",
            ],
            SpawnType.ENVIRONMENTAL: [
                f"Something moves in the dark. {template.description}.",
                f"You're not alone. {template.name} hunts here.",
                f"The local fauna takes interest in you. Hostile.",
            ],
        }
        
        templates = intros.get(spawn_type, intros[SpawnType.PATROL])
        return random.choice(templates)
    
    def get_encounter_context(self) -> str:
        """Generate context for narrator about current encounter state."""
        if not self.active_encounters:
            if self.tension_buildup > 0.5:
                return "[ENCOUNTER: Tension building. Something may happen soon.]"
            return ""
        
        enc = self.active_encounters[0]
        return f"[ACTIVE ENCOUNTER: {enc.get('template', 'Unknown')} x{enc.get('count', 1)}]"
    
    def to_dict(self) -> dict:
        return {
            "difficulty": self.difficulty,
            "spawn_history": self.spawn_history[-10:],
            "scenes_since_combat": self.scenes_since_combat,
            "tension_buildup": self.tension_buildup,
            "active_encounters": self.active_encounters,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "EncounterDirector":
        director = cls(difficulty=data.get("difficulty", "normal"))
        director.spawn_history = data.get("spawn_history", [])
        director.scenes_since_combat = data.get("scenes_since_combat", 5)
        director.tension_buildup = data.get("tension_buildup", 0.0)
        director.active_encounters = data.get("active_encounters", [])
        return director


# ============================================================================
# Convenience Functions
# ============================================================================

def create_encounter_director(difficulty: str = "normal") -> EncounterDirector:
    """Create a new encounter director."""
    return EncounterDirector(difficulty=difficulty)


def evaluate_spawn(
    location: str,
    threat_level: float,
    player_health: float,
    difficulty: str = "normal",
) -> dict | None:
    """
    Quick evaluation for spawning.
    
    Returns:
        Spawn info dict or None if no spawn
    """
    director = create_encounter_director(difficulty)
    
    context = SpawnContext(
        location=location,
        threat_level=threat_level,
        player_health=player_health,
        difficulty=difficulty,
    )
    
    decision = director.evaluate(context)
    
    if not decision.should_spawn:
        return None
    
    return {
        "enemy": decision.template.name if decision.template else "Unknown",
        "count": decision.count,
        "type": decision.spawn_type.value,
        "narrative": decision.narrative_intro,
    }
