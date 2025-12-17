"""
AI Difficulty Tuning System.
Implements "AI Dumbing Down" for fair, cinematic combat.

Based on Game AI Pro patterns for dynamic difficulty adjustment,
telegraphing, near-misses, and reaction delays.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import random


# ============================================================================
# Difficulty Levels
# ============================================================================

class DifficultyLevel(Enum):
    """Difficulty presets."""
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"
    NIGHTMARE = "nightmare"
    CINEMATIC = "cinematic"  # Dramatic, not punishing


@dataclass
class DifficultySettings:
    """
    Settings that control AI behavior for difficulty.
    """
    level: DifficultyLevel = DifficultyLevel.NORMAL
    
    # Reaction delays (in narrative beats)
    min_reaction_delay: float = 0.0  # Instant
    max_reaction_delay: float = 1.0  # 1 beat delay
    
    # Accuracy modifiers
    base_accuracy: float = 0.7  # 0-1
    accuracy_after_hit: float = 0.5  # Reduce accuracy after landing a hit
    
    # Telegraphing (0 = no warning, 1 = obvious warning)
    attack_telegraph_strength: float = 0.5
    
    # Near-miss chance (dramatic misses instead of clean hits)
    near_miss_chance: float = 0.3
    
    # Mercy mechanics
    mercy_health_threshold: float = 0.2  # Below this, AI gets "worse"
    mercy_accuracy_penalty: float = 0.3  # Reduce accuracy when player is low
    
    # Aggression (0 = passive, 1 = relentless)
    aggression: float = 0.5
    
    # Hesitation (chance to pause before attacking)
    hesitation_chance: float = 0.2


# Preset configurations
DIFFICULTY_PRESETS = {
    DifficultyLevel.EASY: DifficultySettings(
        level=DifficultyLevel.EASY,
        min_reaction_delay=0.5,
        max_reaction_delay=2.0,
        base_accuracy=0.4,
        accuracy_after_hit=0.2,
        attack_telegraph_strength=0.9,
        near_miss_chance=0.5,
        mercy_health_threshold=0.3,
        mercy_accuracy_penalty=0.5,
        aggression=0.3,
        hesitation_chance=0.4,
    ),
    DifficultyLevel.NORMAL: DifficultySettings(
        level=DifficultyLevel.NORMAL,
        min_reaction_delay=0.2,
        max_reaction_delay=1.0,
        base_accuracy=0.6,
        accuracy_after_hit=0.4,
        attack_telegraph_strength=0.6,
        near_miss_chance=0.35,
        mercy_health_threshold=0.2,
        mercy_accuracy_penalty=0.3,
        aggression=0.5,
        hesitation_chance=0.25,
    ),
    DifficultyLevel.HARD: DifficultySettings(
        level=DifficultyLevel.HARD,
        min_reaction_delay=0.0,
        max_reaction_delay=0.5,
        base_accuracy=0.75,
        accuracy_after_hit=0.6,
        attack_telegraph_strength=0.3,
        near_miss_chance=0.15,
        mercy_health_threshold=0.1,
        mercy_accuracy_penalty=0.1,
        aggression=0.7,
        hesitation_chance=0.1,
    ),
    DifficultyLevel.NIGHTMARE: DifficultySettings(
        level=DifficultyLevel.NIGHTMARE,
        min_reaction_delay=0.0,
        max_reaction_delay=0.2,
        base_accuracy=0.9,
        accuracy_after_hit=0.8,
        attack_telegraph_strength=0.1,
        near_miss_chance=0.05,
        mercy_health_threshold=0.0,
        mercy_accuracy_penalty=0.0,
        aggression=0.9,
        hesitation_chance=0.0,
    ),
    DifficultyLevel.CINEMATIC: DifficultySettings(
        level=DifficultyLevel.CINEMATIC,
        min_reaction_delay=0.3,
        max_reaction_delay=1.5,
        base_accuracy=0.5,  # Fair, not punishing
        accuracy_after_hit=0.3,  # Give player breathing room
        attack_telegraph_strength=0.7,
        near_miss_chance=0.4,  # Lots of dramatic near-misses
        mercy_health_threshold=0.25,
        mercy_accuracy_penalty=0.4,
        aggression=0.4,  # Enemies feel dangerous but beatable
        hesitation_chance=0.3,  # Dramatic pauses
    ),
}


# ============================================================================
# Combat Modifiers
# ============================================================================

@dataclass
class TelegraphedAttack:
    """An attack with a dramatic warning."""
    attack_name: str
    telegraph_description: str  # What the player notices
    delay_beats: float  # How long before it lands
    can_dodge: bool = True
    can_interrupt: bool = False


# Pre-built telegraphed attacks
TELEGRAPHED_ATTACKS = {
    "heavy_swing": TelegraphedAttack(
        attack_name="Heavy Swing",
        telegraph_description="pulls back for a devastating blow",
        delay_beats=1.0,
        can_dodge=True,
        can_interrupt=True,
    ),
    "aimed_shot": TelegraphedAttack(
        attack_name="Aimed Shot",
        telegraph_description="takes careful aim, red targeting laser visible",
        delay_beats=0.5,
        can_dodge=True,
        can_interrupt=True,
    ),
    "rush_attack": TelegraphedAttack(
        attack_name="Rush Attack",
        telegraph_description="lowers into a charging stance",
        delay_beats=0.75,
        can_dodge=True,
        can_interrupt=False,
    ),
    "grenade_throw": TelegraphedAttack(
        attack_name="Grenade",
        telegraph_description="pulls a grenade, arm cocked back",
        delay_beats=1.5,
        can_dodge=True,
        can_interrupt=True,
    ),
}


@dataclass
class NearMissResult:
    """Result of a near-miss instead of a clean hit."""
    original_attack: str
    miss_description: str
    dramatic_tension: str
    close_call_rating: float  # 0-1 how close it was


# Near-miss description templates
NEAR_MISS_TEMPLATES = [
    "The shot sparks off the bulkhead inches from your head",
    "You feel the wind of the blade as it whistles past",
    "Their fist grazes your cheek, a warning of what's to come",
    "A round punches through your coat, missing flesh by millimeters",
    "The blow lands where you stood a heartbeat ago",
    "You dive aside as energy scorches the deck plates",
    "The strike clips your shoulder, more bruise than wound",
    "Their attack tears through the space you just vacated",
]


# ============================================================================
# Difficulty Controller
# ============================================================================

class DifficultyController:
    """
    Controls AI behavior based on difficulty settings.
    Provides methods for combat narration that respect difficulty.
    """
    
    def __init__(self, level: DifficultyLevel = DifficultyLevel.NORMAL):
        self.settings = DIFFICULTY_PRESETS.get(level, DIFFICULTY_PRESETS[DifficultyLevel.NORMAL])
        self.last_hit_player = False  # Track if AI just landed a hit
    
    def set_difficulty(self, level: DifficultyLevel) -> None:
        """Change difficulty level."""
        self.settings = DIFFICULTY_PRESETS.get(level, self.settings)
    
    def should_hesitate(self) -> bool:
        """Check if AI should pause before attacking."""
        return random.random() < self.settings.hesitation_chance
    
    def get_reaction_delay(self) -> float:
        """Get a random reaction delay based on settings."""
        return random.uniform(
            self.settings.min_reaction_delay,
            self.settings.max_reaction_delay
        )
    
    def calculate_accuracy(self, player_health: float) -> float:
        """
        Calculate current AI accuracy considering all factors.
        
        Args:
            player_health: 0-1 player health ratio
            
        Returns:
            0-1 accuracy value
        """
        accuracy = self.settings.base_accuracy
        
        # Reduce accuracy if AI just hit the player (give breathing room)
        if self.last_hit_player:
            accuracy *= self.settings.accuracy_after_hit
        
        # Mercy mechanics - reduce accuracy when player is hurting
        if player_health < self.settings.mercy_health_threshold:
            accuracy -= self.settings.mercy_accuracy_penalty
        
        return max(0.1, min(1.0, accuracy))  # Clamp to 0.1-1.0
    
    def roll_attack(self, player_health: float) -> dict:
        """
        Roll an AI attack with difficulty modifiers.
        
        Returns:
            Dict with hit/miss/near_miss and descriptions
        """
        accuracy = self.calculate_accuracy(player_health)
        roll = random.random()
        
        if roll < accuracy:
            # Hit - but check for near-miss conversion
            if random.random() < self.settings.near_miss_chance:
                # Convert to dramatic near-miss
                self.last_hit_player = False
                return self._generate_near_miss()
            else:
                self.last_hit_player = True
                return {
                    "result": "hit",
                    "description": "The attack lands",
                    "damage_modifier": 1.0,
                }
        else:
            # Clean miss
            self.last_hit_player = False
            return {
                "result": "miss",
                "description": "The attack goes wide",
                "damage_modifier": 0.0,
            }
    
    def _generate_near_miss(self) -> dict:
        """Generate a dramatic near-miss result."""
        template = random.choice(NEAR_MISS_TEMPLATES)
        close_call = random.uniform(0.7, 0.95)
        
        return {
            "result": "near_miss",
            "description": template,
            "close_call_rating": close_call,
            "damage_modifier": 0.0,
            "dramatic_tension": f"({int(close_call * 100)}% close call)",
        }
    
    def get_telegraph(self, attack_type: str = "") -> TelegraphedAttack | None:
        """
        Get a telegraphed version of an attack based on difficulty.
        
        Args:
            attack_type: Specific attack type, or empty for random
            
        Returns:
            TelegraphedAttack if should telegraph, None otherwise
        """
        # Check if we should telegraph based on settings
        if random.random() > self.settings.attack_telegraph_strength:
            return None  # No telegraph, attack comes faster
        
        if attack_type and attack_type in TELEGRAPHED_ATTACKS:
            return TELEGRAPHED_ATTACKS[attack_type]
        
        # Return random telegraphed attack
        return random.choice(list(TELEGRAPHED_ATTACKS.values()))
    
    def get_aggression_modifier(self) -> str:
        """Get narrative description of AI aggression."""
        if self.settings.aggression > 0.7:
            return "presses the attack relentlessly"
        elif self.settings.aggression > 0.4:
            return "maintains steady pressure"
        else:
            return "moves cautiously, looking for an opening"
    
    def get_combat_context(self, player_health: float) -> str:
        """
        Generate combat context for narrator based on difficulty.
        
        Args:
            player_health: 0-1 player health
            
        Returns:
            Context string for narrator prompt
        """
        lines = ["[COMBAT DIFFICULTY CONTEXT]"]
        
        # Accuracy info
        accuracy = self.calculate_accuracy(player_health)
        if accuracy < 0.4:
            lines.append("Enemies are missing frequently, giving you openings")
        elif accuracy > 0.7:
            lines.append("Enemies are dangerously accurate")
        
        # Mercy mechanics
        if player_health < self.settings.mercy_health_threshold:
            lines.append("You're wounded - enemies seem to be overconfident, making mistakes")
        
        # Aggression
        lines.append(f"Enemy tactics: {self.get_aggression_modifier()}")
        
        # Hesitation
        if self.should_hesitate():
            lines.append("There's a momentary pause in the assault")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        """Serialize for storage."""
        return {
            "level": self.settings.level.value,
            "last_hit_player": self.last_hit_player,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "DifficultyController":
        """Deserialize from storage."""
        level = DifficultyLevel(data.get("level", "normal"))
        controller = cls(level)
        controller.last_hit_player = data.get("last_hit_player", False)
        return controller


# ============================================================================
# Convenience Functions
# ============================================================================

def create_difficulty_controller(level: str = "normal") -> DifficultyController:
    """Create a difficulty controller from string level name."""
    try:
        difficulty_level = DifficultyLevel(level.lower())
    except ValueError:
        difficulty_level = DifficultyLevel.NORMAL
    return DifficultyController(difficulty_level)


def evaluate_combat_action(
    player_health: float,
    difficulty: str = "normal",
    attack_type: str = "",
) -> dict:
    """
    Convenience function to evaluate a single combat action.
    
    Args:
        player_health: 0-1 player health
        difficulty: Difficulty level string
        attack_type: Specific attack type for telegraphing
        
    Returns:
        Dict with full combat evaluation
    """
    controller = create_difficulty_controller(difficulty)
    
    result = {
        "hesitate": controller.should_hesitate(),
        "reaction_delay": controller.get_reaction_delay(),
        "telegraph": None,
        "attack_result": None,
        "combat_context": controller.get_combat_context(player_health),
    }
    
    # Check for telegraph
    telegraph = controller.get_telegraph(attack_type)
    if telegraph:
        result["telegraph"] = {
            "name": telegraph.attack_name,
            "description": telegraph.telegraph_description,
            "delay": telegraph.delay_beats,
            "can_dodge": telegraph.can_dodge,
            "can_interrupt": telegraph.can_interrupt,
        }
    
    # Roll the attack
    result["attack_result"] = controller.roll_attack(player_health)
    
    return result
