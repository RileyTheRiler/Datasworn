"""
Companion AI System ("Buddy AI").
Provides intelligent companion behavior without being annoying.

Based on Game AI Pro patterns for follower AI:
- Stay logically close to player
- Offer utility when needed (heal, warn, assist)
- Don't spam interventions
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable
import random


# ============================================================================
# Companion States
# ============================================================================

class CompanionState(Enum):
    """Current activity state of the companion."""
    FOLLOWING = "following"  # Default - staying with player
    ASSISTING = "assisting"  # Currently helping with task
    COMBAT = "combat"  # In combat alongside player
    HEALING = "healing"  # Administering aid to player
    SCOUTING = "scouting"  # Checking ahead
    WARNING = "warning"  # Alerting player to danger
    IDLE = "idle"  # Waiting at a location
    SEPARATED = "separated"  # Lost contact with player


class InterventionType(Enum):
    """Types of help the companion can offer."""
    HEAL = "heal"  # Medical assistance
    WARN_DANGER = "warn_danger"  # Alert about threat
    TACTICAL_ADVICE = "tactical_advice"  # Combat suggestions
    COMBAT_ASSIST = "combat_assist"  # Direct combat help
    COVER_FIRE = "cover_fire"  # Suppressing fire
    INFORMATION = "information"  # Lore/world knowledge
    EMOTIONAL_SUPPORT = "emotional_support"  # Encouragement
    ITEM_OFFER = "item_offer"  # Offer supplies


# ============================================================================
# Companion Profile
# ============================================================================

@dataclass
class CompanionProfile:
    """Defines a companion's personality and capabilities."""
    name: str
    
    # Capability levels (0-1)
    medical_skill: float = 0.5  # How good at healing
    combat_skill: float = 0.5  # How good in a fight
    perception_skill: float = 0.5  # How good at spotting threats
    knowledge_skill: float = 0.5  # How much lore they know
    
    # Personality traits
    chattiness: float = 0.5  # How often they speak (0=quiet, 1=chatty)
    boldness: float = 0.5  # How willing to act independently
    loyalty: float = 0.8  # How committed to helping player
    
    # Intervention thresholds (when they'll step in)
    heal_threshold: float = 0.4  # Player health below this triggers heal
    warn_threshold: float = 0.6  # Danger level above this triggers warning
    
    # Cooldowns (prevent spam)
    min_intervention_gap: int = 3  # Minimum scenes between interventions
    last_intervention_scene: int = 0
    
    # Voice and characterization
    speech_style: str = "supportive"  # How they talk
    signature_phrases: list[str] = field(default_factory=list)
    
    def can_intervene(self, current_scene: int) -> bool:
        """Check if enough time has passed for another intervention."""
        return (current_scene - self.last_intervention_scene) >= self.min_intervention_gap


# ============================================================================
# Pre-built Companion Archetypes
# ============================================================================

COMPANION_ARCHETYPES = {
    "medic": CompanionProfile(
        name="Medic",
        medical_skill=0.9,
        combat_skill=0.3,
        perception_skill=0.5,
        knowledge_skill=0.4,
        chattiness=0.4,
        boldness=0.3,
        loyalty=0.9,
        heal_threshold=0.5,
        speech_style="clinical, caring",
        signature_phrases=[
            "Let me take a look at that.",
            "Hold still, this might hurt.",
            "You're pushing yourself too hard.",
        ],
    ),
    "soldier": CompanionProfile(
        name="Soldier",
        medical_skill=0.3,
        combat_skill=0.9,
        perception_skill=0.7,
        knowledge_skill=0.3,
        chattiness=0.3,
        boldness=0.8,
        loyalty=0.7,
        warn_threshold=0.5,
        speech_style="tactical, clipped",
        signature_phrases=[
            "Contact ahead.",
            "I'll take point.",
            "On your six.",
        ],
    ),
    "scholar": CompanionProfile(
        name="Scholar",
        medical_skill=0.4,
        combat_skill=0.2,
        perception_skill=0.6,
        knowledge_skill=0.9,
        chattiness=0.7,
        boldness=0.2,
        loyalty=0.8,
        speech_style="curious, verbose",
        signature_phrases=[
            "According to my research...",
            "Interesting, I've read about this.",
            "Perhaps we should reconsider.",
        ],
    ),
    "scoundrel": CompanionProfile(
        name="Scoundrel",
        medical_skill=0.2,
        combat_skill=0.6,
        perception_skill=0.8,
        knowledge_skill=0.5,
        chattiness=0.6,
        boldness=0.9,
        loyalty=0.5,
        warn_threshold=0.4,
        speech_style="sarcastic, street-smart",
        signature_phrases=[
            "Bad idea. Let's do it.",
            "I know a guy.",
            "Trust me on this one.",
        ],
    ),
}


# ============================================================================
# Companion AI Controller
# ============================================================================

@dataclass
class CompanionContext:
    """Current context for companion decision-making."""
    player_health: float = 1.0
    player_in_combat: bool = False
    threat_level: float = 0.0
    current_scene: int = 0
    player_action: str = ""
    location: str = ""
    nearby_hazards: list[str] = field(default_factory=list)
    nearby_npcs: list[str] = field(default_factory=list)


class CompanionAI:
    """
    Controls companion behavior using utility-based decision making.
    Prevents annoying interventions through cooldowns and thresholds.
    """
    
    def __init__(self, profile: CompanionProfile):
        self.profile = profile
        self.state = CompanionState.FOLLOWING
        self.intervention_history: list[tuple[int, InterventionType]] = []
        self.suppressed_count: int = 0  # Track how many times we stayed quiet
    
    def update(self, context: CompanionContext) -> dict | None:
        """
        Update companion state and potentially trigger an intervention.
        
        Returns:
            Dict with intervention details, or None if no action
        """
        # Check if we can intervene at all
        if not self.profile.can_intervene(context.current_scene):
            return None
        
        # Score each possible intervention
        scores = self._score_interventions(context)
        
        # Filter out low-scoring interventions
        viable = [(itype, score) for itype, score in scores.items() if score > 0.5]
        
        if not viable:
            return None
        
        # Pick the best intervention
        viable.sort(key=lambda x: x[1], reverse=True)
        best_type, best_score = viable[0]
        
        # Apply chattiness filter - quiet companions skip more often
        if random.random() > self.profile.chattiness + 0.3:
            self.suppressed_count += 1
            return None
        
        # Record and execute intervention
        self.profile.last_intervention_scene = context.current_scene
        self.intervention_history.append((context.current_scene, best_type))
        self.suppressed_count = 0
        
        return self._generate_intervention(best_type, context)
    
    def _score_interventions(self, context: CompanionContext) -> dict[InterventionType, float]:
        """Score each intervention type based on context."""
        scores = {}
        
        # Heal intervention
        if context.player_health < self.profile.heal_threshold:
            heal_urgency = (self.profile.heal_threshold - context.player_health) * 2
            scores[InterventionType.HEAL] = heal_urgency * self.profile.medical_skill * self.profile.loyalty
        
        # Warning intervention
        if context.threat_level > self.profile.warn_threshold:
            warn_urgency = (context.threat_level - self.profile.warn_threshold) * 1.5
            scores[InterventionType.WARN_DANGER] = warn_urgency * self.profile.perception_skill
        
        # Combat assist
        if context.player_in_combat:
            combat_value = context.threat_level * self.profile.combat_skill * self.profile.boldness
            scores[InterventionType.COMBAT_ASSIST] = combat_value
            
            # Cover fire if player is hurt
            if context.player_health < 0.6:
                scores[InterventionType.COVER_FIRE] = combat_value * 1.2
        
        # Tactical advice in combat
        if context.player_in_combat and context.threat_level > 0.5:
            scores[InterventionType.TACTICAL_ADVICE] = (
                self.profile.combat_skill * self.profile.knowledge_skill * 0.8
            )
        
        # Information sharing (only if not in immediate danger)
        if not context.player_in_combat and context.threat_level < 0.3:
            # Trigger info share if there are NPCs or interesting location
            if context.nearby_npcs or context.location:
                scores[InterventionType.INFORMATION] = (
                    self.profile.knowledge_skill * self.profile.chattiness
                )
        
        # Emotional support if player has been struggling
        if self.suppressed_count >= 3 and context.player_health < 0.7:
            scores[InterventionType.EMOTIONAL_SUPPORT] = (
                self.profile.loyalty * 0.7
            )
        
        return scores
    
    def _generate_intervention(
        self, 
        itype: InterventionType, 
        context: CompanionContext,
    ) -> dict:
        """Generate the intervention details for the narrator."""
        phrase = random.choice(self.profile.signature_phrases) if self.profile.signature_phrases else ""
        
        templates = {
            InterventionType.HEAL: {
                "action": "approaches to tend your wounds",
                "dialogue_intent": "concerned about player's injuries",
                "effect": "healing",
            },
            InterventionType.WARN_DANGER: {
                "action": "signals danger ahead",
                "dialogue_intent": "urgent warning about threat",
                "effect": "awareness",
            },
            InterventionType.TACTICAL_ADVICE: {
                "action": "offers tactical observation",
                "dialogue_intent": "pointing out combat opportunity",
                "effect": "tactical_hint",
            },
            InterventionType.COMBAT_ASSIST: {
                "action": "moves to engage alongside you",
                "dialogue_intent": "ready for combat",
                "effect": "damage_support",
            },
            InterventionType.COVER_FIRE: {
                "action": "lays down suppressing fire",
                "dialogue_intent": "creating space for you",
                "effect": "suppression",
            },
            InterventionType.INFORMATION: {
                "action": "shares relevant knowledge",
                "dialogue_intent": "recalling useful information",
                "effect": "lore",
            },
            InterventionType.EMOTIONAL_SUPPORT: {
                "action": "offers words of encouragement",
                "dialogue_intent": "reassuring, supportive",
                "effect": "morale",
            },
            InterventionType.ITEM_OFFER: {
                "action": "offers supplies from their pack",
                "dialogue_intent": "practical, helpful",
                "effect": "item",
            },
        }
        
        template = templates.get(itype, {"action": "acts", "dialogue_intent": "helpful", "effect": "none"})
        
        return {
            "companion_name": self.profile.name,
            "intervention_type": itype.value,
            "action": template["action"],
            "dialogue_intent": template["dialogue_intent"],
            "effect": template["effect"],
            "signature_phrase": phrase,
            "speech_style": self.profile.speech_style,
        }
    
    def get_narrator_context(self, context: CompanionContext) -> str:
        """Generate companion context for the narrator."""
        lines = [f"[COMPANION: {self.profile.name}]"]
        lines.append(f"State: {self.state.value}")
        lines.append(f"Style: {self.profile.speech_style}")
        
        # Add any pending intervention hint
        scores = self._score_interventions(context)
        if scores:
            best_type = max(scores, key=lambda k: scores[k])
            if scores[best_type] > 0.6:
                lines.append(f"Ready to: {best_type.value}")
        
        return "\n".join(lines)
    
    def set_state(self, state: CompanionState) -> None:
        """Manually set companion state."""
        self.state = state


# ============================================================================
# Convenience Functions
# ============================================================================

def create_companion(archetype: str, name: str | None = None) -> CompanionAI:
    """Create a companion from an archetype."""
    template = COMPANION_ARCHETYPES.get(archetype)
    if not template:
        template = COMPANION_ARCHETYPES["soldier"]
    
    # Create a copy of the profile with optional custom name
    profile = CompanionProfile(
        name=name or template.name,
        medical_skill=template.medical_skill,
        combat_skill=template.combat_skill,
        perception_skill=template.perception_skill,
        knowledge_skill=template.knowledge_skill,
        chattiness=template.chattiness,
        boldness=template.boldness,
        loyalty=template.loyalty,
        heal_threshold=template.heal_threshold,
        warn_threshold=template.warn_threshold,
        min_intervention_gap=template.min_intervention_gap,
        speech_style=template.speech_style,
        signature_phrases=template.signature_phrases.copy(),
    )
    
    return CompanionAI(profile)


def evaluate_companion_action(
    companion_archetype: str,
    player_health: float,
    threat_level: float,
    in_combat: bool,
    current_scene: int,
) -> dict | None:
    """
    Quick evaluation of what a companion would do.
    
    Returns:
        Intervention dict or None
    """
    companion = create_companion(companion_archetype)
    
    context = CompanionContext(
        player_health=player_health,
        player_in_combat=in_combat,
        threat_level=threat_level,
        current_scene=current_scene,
    )
    
    return companion.update(context)
