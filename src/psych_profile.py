"""
Psychological Profile System

This module defines the data structures and logic for evolving character psychology.
It tracks values, personality traits, beliefs, and emotional states, providing
a rich inner life for the character that influences narrative generation.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from pydantic import BaseModel, Field
import random
from datetime import datetime
from .character_identity import CharacterIdentity, WoundType, WoundProfile, WoundScore, RUOType
from src.config.archetype_config_loader import ArchetypeConfigLoader
from src.narrative.archetype_types import ArchetypeProfile


@dataclass
class PsychologicalStressEvent:
    """A stress-induced event or hallucination."""
    name: str
    description: str
    threshold: float  # 0.0 to 1.0
    effect_type: str  # "visual", "narrative", "mechanical"





STRESS_EVENTS = [
    PsychologicalStressEvent("Flickering Lights", "The lights flicker. Just for a moment.", 0.25, "visual"),
    PsychologicalStressEvent("Phantom Sound", "You hear your name whispered. No one is there.", 0.3, "narrative"),
    PsychologicalStressEvent("Shadow Movement", "Something moves in your peripheral vision.", 0.5, "visual"),
    PsychologicalStressEvent("Deja Vu", "This conversation... you've had it before.", 0.6, "narrative"),
    PsychologicalStressEvent("Hallucination", "A seventh figure stands in the corner.", 0.75, "narrative"),
    PsychologicalStressEvent("Unreliable Oracle", "The Oracle's voice changes and might be lying.", 0.8, "mechanical"),
    PsychologicalStressEvent("Psychotic Break", "Reality and nightmare merge.", 1.0, "mechanical"),
]

# ============================================================================
# Enums and Constants
# ============================================================================

class ValueSystem(str, Enum):
    """Core values that drive character decisions."""
    ALTRUISM = "altruism"       # Selflessness, helping others
    AMBITION = "ambition"       # Desire for power, status, or achievement
    AUTONOMY = "autonomy"       # Independence, freedom
    COMMUNITY = "community"     # Loyalty to group, belonging
    CURIOSITY = "curiosity"     # Desire to learn, explore
    DEDICATION = "dedication"   # Duty, discipline, persistence
    HEDONISM = "hedonism"       # Pleasure, comfort, enjoyment
    JUSTICE = "justice"         # Fairness, law, righteousness
    ORDER = "order"             # Stability, structure, control
    SECURITY = "security"       # Safety, survival, caution
    TRADITION = "tradition"     # Respect for past, rituals, customs

class EmotionalState(str, Enum):
    """Current dominant emotional state."""
    NEUTRAL = "neutral"
    AFRAID = "afraid"
    ANGRY = "angry"
    ANXIOUS = "anxious"
    CONFIDENT = "confident"
    DEPRESSED = "depressed"
    DETERMINED = "determined"
    EXCITED = "excited"
    GUILTY = "guilty"
    HOPEFUL = "hopeful"
    LONELY = "lonely"
    OVERWHELMED = "overwhelmed"
    PEACEFUL = "peaceful"
    RESENTFUL = "resentful"
    SHOCKED = "shocked"
    SUSPICIOUS = "suspicious"
    TIRED = "tired"

# ============================================================================
# Core Data Models
# ============================================================================

class MemorySeal(BaseModel):
    """A suppressed memory with an integrity seal."""
    id: str
    description: str
    seal_integrity: float = 1.0  # 1.0 (Locked) to 0.0 (Unlocked)
    is_revealed: bool = False

class TraumaScar(BaseModel):
    """A permanent psychological scar from a breaking point."""
    name: str
    description: str
    trait_modifier: Dict[str, float] = Field(default_factory=dict)
    acquired_at: datetime = Field(default_factory=datetime.now)
    arc_stage: str = "fresh"  # fresh → healing → scarred → integrated
    therapy_sessions: int = 0  # Track healing progress

class ValueConflict(BaseModel):
    """A clash between two core values requiring resolution."""
    value_a: ValueSystem
    value_b: ValueSystem
    description: str
    resolved: bool = False
    chosen_value: Optional[ValueSystem] = None

class Compulsion(BaseModel):
    """A behavioral dependency formed through repeated actions."""
    trigger: str  # e.g., "take stims", "check door"
    satisfaction: float = 0.0  # 0.0 to 1.0, decays over time
    withdrawal_stress: float = 0.1  # Stress added if unsatisfied
    uses: int = 0  # How many times triggered
    threshold: int = 3  # Uses before it becomes a compulsion


class CopingMechanism(BaseModel):
    """A coping strategy the character can use to manage stress/trauma."""
    id: str
    name: str
    description: str
    stress_reduction: float  # Amount of stress reduced on success
    sanity_cost: float = 0.0  # Potential sanity cost
    side_effect: str = ""  # Description of potential side effect
    requires_npc: bool = False  # Requires interaction with NPC

@dataclass
class MoralProfile:
    """The deep moral architecture of a character."""
    # The central question they answer
    central_problem_answer: str
    # Their specific argument/justification
    strong_but_flawed_argument: str
    # The psychological wound driving them
    psychological_wound: str
    # Archetypes they mirror (reflect back to player)
    mirrors: List[str] = field(default_factory=list)
    # Archetypes they challenge (force growth)
    challenges: List[str] = field(default_factory=list)
    # Specific interactions keyed by player archetype (WoundType)
    # e.g., {"CONTROLLER": "You think you can control death?"}
    archetype_interactions: Dict[str, str] = field(default_factory=dict)

class NPCPsyche(BaseModel):
    """Simplified psychological profile for an NPC actor."""
    name: str
    dominant_trait: str
    current_emotion: EmotionalState = EmotionalState.NEUTRAL
    instability: float = 0.0  # 0-1, high = unpredictable behavior
    description: str = ""
    # Deep moral profile (optional for generic NPCs, required for Main Cast)
    moral_profile: Optional[MoralProfile] = None

    class Config:
        arbitrary_types_allowed = True

class PsychologicalArc(BaseModel):
    """Tracks the evolution of a trauma over time."""
    scar_name: str
    original_name: str
    transformation_path: List[str] = Field(default_factory=list)
    milestones_reached: List[str] = Field(default_factory=list)

class PsychologicalProfile(BaseModel):
    """
    A comprehensive psychological profile for a character.
    Tracks values, traits, beliefs, and relationships.
    """
    
    # Core Values (0.0 to 1.0) - High value means this drives them
    values: Dict[ValueSystem, float] = Field(default_factory=lambda: {
        ValueSystem.SECURITY: 0.7,
        ValueSystem.AUTONOMY: 0.6,
        ValueSystem.COMMUNITY: 0.5,
    })
    
    # Personality Traits (0.0 to 1.0) - e.g., "Paranoia": 0.8
    traits: Dict[str, float] = Field(default_factory=lambda: {
        "caution": 0.6,
        "empathy": 0.5,
        "resilience": 0.5,
    })
    
    """Deep psychological model of the character."""
    values: dict[ValueSystem, float] = Field(default_factory=lambda: {ValueSystem.SECURITY: 0.8})
    traits: dict[str, float] = Field(default_factory=dict)  # e.g., "aggression": 0.5
    beliefs: list[str] = Field(default_factory=list)
    current_emotion: EmotionalState = EmotionalState.NEUTRAL
    stress_level: float = 0.0  # 0.0 to 1.0
    sanity: float = 1.0  # 1.0 to 0.0
    opinions: dict[str, float] = Field(default_factory=dict)  # Entity/NPC -> -1.0 to 1.0
    memories: list[str] = Field(default_factory=list)  # Narrative summary of key events
    suppressed_memories: list[MemorySeal] = Field(default_factory=list)
    trauma_scars: List[TraumaScar] = Field(default_factory=list)
    
    # Consequence tracking
    addiction_level: float = 0.0  # 0-1, withdrawal penalties when high
    isolation_level: float = 0.0  # 0-1, social penalties when high
    coping_usage_counts: Dict[str, int] = Field(default_factory=dict)
    
    # Deep Mechanics
    active_conflicts: list[ValueConflict] = Field(default_factory=list)
    compulsions: list[Compulsion] = Field(default_factory=list)
    corrupted_memory_indices: list[int] = Field(default_factory=list)  # Indices of corrupted memories
    identity: CharacterIdentity = Field(default_factory=CharacterIdentity)

    def get_dominant_values(self, count: int = 3) -> List[tuple[ValueSystem, float]]:
        """Return the top N values."""
        sorted_values = sorted(self.values.items(), key=lambda x: x[1], reverse=True)
        return sorted_values[:count]

    def get_dominant_traits(self, count: int = 3) -> List[tuple[str, float]]:
        """Return the top N traits."""
        sorted_traits = sorted(self.traits.items(), key=lambda x: x[1], reverse=True)
        return sorted_traits[:count]

    def to_api_dict(self) -> dict:
        """Return a dictionary suitable for API responses."""
        return {
            "stress_level": self.stress_level,
            "sanity": self.sanity,
            "current_emotion": self.current_emotion.value,
            "trauma_scars": [s.model_dump() for s in self.trauma_scars],
            "suppressed_memories": [m.model_dump() for m in self.suppressed_memories],
            "beliefs": self.beliefs[-5:],
            "dominant_trait": self.get_dominant_traits(1)[0][0] if self.traits else "none",
            "identity": self.identity.to_dict()
        }

    def get_primary_fear(self) -> str:
        """Analyze trauma scars and traits to determine primary fear."""
        # Trauma scars take priority
        if self.trauma_scars:
            scar = self.trauma_scars[-1]  # Most recent
            if "Trust" in scar.name:
                return "betrayal"
            elif "Logic" in scar.name:
                return "loss_of_control"
            elif "Nerves" in scar.name:
                return "environmental_threat"
        
        # Fall back to dominant trait
        top_traits = self.get_dominant_traits(1)
        if top_traits:
            trait_name = top_traits[0][0]
            if trait_name == "paranoia":
                return "infiltration"
            elif trait_name == "caution":
                return "environmental_threat"
            elif trait_name == "empathy":
                return "harm_to_loved_ones"
        
        return "unknown"

    def get_available_coping_mechanisms(self) -> list[str]:
        """Return list of coping mechanism IDs available to this character."""
        mechanisms = ["meditate", "journal"]
        
        # Unlock based on traits/state
        if self.traits.get("empathy", 0) > 0.5:
            mechanisms.append("vent_to_crew")
        
        if self.stress_level > 0.8:
            mechanisms.append("stim_injection")  # Desperate measure
        
        return mechanisms

# ============================================================================
# Psychological Engine
# ============================================================================

class PsychologicalEngine:
    """
    Logic for evolving the psychological profile based on events.
    """
    
    def __init__(self, llm_client=None):
        self.llm_client = llm_client  # Optional for LLM-based updates
        try:
            self.archetype_config = ArchetypeConfigLoader()
        except Exception:
            self.archetype_config = None

    def update_stress(self, profile: PsychologicalProfile, amount: float):
        """Update stress level, clamping between 0 and 1."""
        profile.stress_level = max(0.0, min(1.0, profile.stress_level + amount))
        
        # Stress impacts emotion
        if profile.stress_level > 0.8:
            profile.current_emotion = EmotionalState.OVERWHELMED
        elif profile.stress_level > 0.6 and profile.current_emotion == EmotionalState.PEACEFUL:
            profile.current_emotion = EmotionalState.ANXIOUS

    def update_sanity(self, profile: PsychologicalProfile, amount: float):
        """Update sanity level, clamping between 0 and 1."""
        profile.sanity = max(0.0, min(1.0, profile.sanity + amount))

    def add_belief(self, profile: PsychologicalProfile, belief: str):
        """Add a new core belief if not already present."""
        if belief not in profile.beliefs:
            profile.beliefs.append(belief)
            # Keep only most recent/relevant 10 beliefs to avoid context bloat
            if len(profile.beliefs) > 10:
                profile.beliefs.pop(0)

    def update_opinion(self, profile: PsychologicalProfile, entity: str, amount: float):
        """Update opinion of an entity, clamping between -1 and 1."""
        current = profile.opinions.get(entity, 0.0)
        new_val = max(-1.0, min(1.0, current + amount))
        profile.opinions[entity] = new_val

    def check_stress_events(self, profile: PsychologicalProfile) -> PsychologicalStressEvent | None:
        """
        Check if a stress event should trigger based on current level.
        Returns an event if one triggers, None otherwise.
        """
        # Collect events that haven't triggered yet and are within threshold
        # (We assume the caller tracks triggered events in the state/profile)
        eligible = [e for e in STRESS_EVENTS if e.threshold <= profile.stress_level]
        
        if not eligible:
            return None
            
        # Higher stress = higher chance
        # For simplicity, we filter out what's in profile.memories or similar if needed, 
        # but the caller usually handles 'already triggered' logic.
        
        if random.random() < (profile.stress_level * 0.2):
            return random.choice(eligible)
            
        return None

    def assign_trauma(self, profile: PsychologicalProfile) -> TraumaScar:
        """
        Trigger a psychotic break and assign a permanent scar.
        Resets stress but lowers sanity.
        """
        scars = [
            TraumaScar("Shattered Trust", "You can no longer trust anyone.", {"paranoia": 0.5, "trust": -0.5}),
            TraumaScar("Cold Logic", "Emotions are a weakness. Eliminate them.", {"logic": 0.5, "empathy": -0.5}),
            TraumaScar("Survivor's Guilt", "Why did you live when they died?", {"hesitation": 0.3, "guilt": 0.5}),
            TraumaScar("Hyper-Vigilance", "They are coming. You must be ready.", {"caution": 0.5, "rest": -0.3}),
        ]
        
        # Pick a scar not already present
        existing_names = [s.name for s in profile.trauma_scars]
        candidates = [s for s in scars if s.name not in existing_names]
        
        if not candidates:
            # Fallback if really messed up
            scar = scars[0]
        else:
            scar = random.choice(candidates)
            
        profile.trauma_scars.append(scar)
        
        # Apply immediate trait modifiers
        for trait, mod in scar.trait_modifier.items():
            current = profile.traits.get(trait, 0.5)
            # Add modifier, clamping 0-1
            profile.traits[trait] = max(0.0, min(1.0, current + mod))
            
        # Reset Stress but Sanity takes a hit
        profile.stress_level = 0.4  # Leaves you shaken, not calm
        profile.sanity = max(0.0, profile.sanity - 0.15)
        profile.current_emotion = EmotionalState.OVERWHELMED
        
        return scar

    # =========================================================================
    # VALUE CONFLICTS
    # =========================================================================
    
    def detect_value_conflict(self, profile: PsychologicalProfile, action_description: str) -> ValueConflict | None:
        """
        Detect if an action creates a clash between two high-priority values.
        Returns a ValueConflict if detected, None otherwise.
        """
        # Get top 2 values
        top_values = profile.get_dominant_values(2)
        if len(top_values) < 2:
            return None
        
        v1, s1 = top_values[0]
        v2, s2 = top_values[1]
        
        # Only trigger if both are strong (> 0.6)
        if s1 < 0.6 or s2 < 0.6:
            return None
        
        # Heuristic conflict detection based on action keywords
        conflict_triggers = {
            (ValueSystem.SECURITY, ValueSystem.AUTONOMY): ["risk", "escape", "flee", "expose"],
            (ValueSystem.COMMUNITY, ValueSystem.AUTONOMY): ["betray", "abandon", "leave", "solo"],
            (ValueSystem.JUSTICE, ValueSystem.COMMUNITY): ["report", "expose", "accuse", "truth"],
            (ValueSystem.SECURITY, ValueSystem.CURIOSITY): ["investigate", "explore", "unknown"],
        }
        
        action_lower = action_description.lower()
        for (va, vb), triggers in conflict_triggers.items():
            if ({v1, v2} == {va, vb}) and any(t in action_lower for t in triggers):
                conflict = ValueConflict(
                    value_a=va,
                    value_b=vb,
                    description=f"Your {va.value} clashes with your {vb.value}."
                )
                profile.active_conflicts.append(conflict)
                return conflict
        
        return None

    def resolve_conflict(self, profile: PsychologicalProfile, conflict: ValueConflict, chosen: ValueSystem):
        """
        Resolve a value conflict by choosing one value over another.
        Permanently shifts values.
        """
        conflict.resolved = True
        conflict.chosen_value = chosen
        
        # Boost chosen, weaken the other
        other = conflict.value_a if chosen == conflict.value_b else conflict.value_b
        profile.values[chosen] = min(1.0, profile.values.get(chosen, 0.5) + 0.15)
        profile.values[other] = max(0.0, profile.values.get(other, 0.5) - 0.15)
        
        # Add belief
        profile.beliefs.append(f"I chose {chosen.value} over {other.value}.")

    # =========================================================================
    # COMPULSION / ADDICTION
    # =========================================================================

    def track_compulsion(self, profile: PsychologicalProfile, action: str):
        """
        Track repeated behaviors. If past threshold, it becomes a compulsion.
        """
        action_lower = action.lower()
        for comp in profile.compulsions:
            if comp.trigger in action_lower:
                comp.uses += 1
                comp.satisfaction = 1.0  # Satisfied
                return
        
        # Check if we should create a new potential compulsion
        # (Simplified: any action containing 'stim', 'drink', 'check' etc.)
        triggers = ["stim", "drink", "check door", "count", "lock"]
        for t in triggers:
            if t in action_lower:
                # See if we already track this
                existing = [c for c in profile.compulsions if c.trigger == t]
                if existing:
                    existing[0].uses += 1
                    existing[0].satisfaction = 1.0
                else:
                    profile.compulsions.append(Compulsion(trigger=t, uses=1, satisfaction=1.0))
                return

    def apply_withdrawal(self, profile: PsychologicalProfile):
        """
        Apply withdrawal stress for unsatisfied compulsions.
        Called once per turn.
        """
        for comp in profile.compulsions:
            if comp.uses >= comp.threshold:  # It's a real compulsion
                comp.satisfaction = max(0.0, comp.satisfaction - 0.2)  # Decay
                if comp.satisfaction < 0.3:
                    # Withdrawal kicks in
                    self.update_stress(profile, comp.withdrawal_stress)

    # =========================================================================
    # MEMORY CORRUPTION
    # =========================================================================

    def corrupt_memory(self, profile: PsychologicalProfile, index: int = None, corruption_text: str = None):
        """
        Subtly alter a memory due to high stress.
        """
        if not profile.memories:
            return
        
        if index is None:
            index = random.randint(0, len(profile.memories) - 1)
        
        if index in profile.corrupted_memory_indices:
            return  # Already corrupted
        
        original = profile.memories[index]
        
        # Simple corruption: add uncertainty
        corruptions = [
            " (or was it?)",
            " ...no, that's not quite right.",
            " [memory unclear]",
            " But you're not sure anymore.",
        ]
        
        if corruption_text:
            profile.memories[index] = corruption_text
        else:
            profile.memories[index] = original + random.choice(corruptions)
        
        profile.corrupted_memory_indices.append(index)

    def get_narrative_context(self, profile: PsychologicalProfile) -> str:
        """
        Generate a context string for the narrator system prompt.
        """
        values_str = ", ".join([f"{v.value} ({s:.1f})" for v, s in profile.get_dominant_values()])
        traits_str = ", ".join([f"{k} ({v:.1f})" for k, v in profile.get_dominant_traits()])
        
        # Format beliefs
        beliefs_str = "\n  - ".join(profile.beliefs[-3:]) if profile.beliefs else "No strong beliefs yet."
        
        # Format significant strong opinions
        opinion_strs = []
        for entity, score in profile.opinions.items():
            if abs(score) > 0.3:
                desc = "trusts" if score > 0 else "distrusts"
                intensity = "deeply" if abs(score) > 0.7 else "somewhat"
                opinion_strs.append(f"{desc} {entity} {intensity}")
        opinions_str = ", ".join(opinion_strs) if opinion_strs else "Neutral towards known entities."
        
        identity_info = f"{profile.identity.archetype.value.upper()}"
        if profile.identity.dissonance_score > 0.3:
            identity_info += f" (Dissonant: {profile.identity.dissonance_score:.1f})"

        return f"""<psychological_profile>
CURRENT STATE:
  Emotion: {profile.current_emotion.value.upper()} | Stress: {profile.stress_level:.0%} | Sanity: {profile.sanity:.0%}

CORE DRIVERS:
  Values: {values_str}
  Traits: {traits_str}

RELATIONSHIPS:
  {opinions_str}

IDENTITY:
  Archetype: {identity_info}
  Recent Path: {', '.join([c.description for c in profile.identity.choice_history[-3:]]) if profile.identity.choice_history else "None"}
  Core Wound: {profile.identity.wound_profile.dominant_wound.value.upper()} (Rev: {profile.identity.wound_profile.revelation_progress:.0%})

INNER MONOLOGUE GUIDANCE:
  If Stress is high, focus on threats and failure.
  If Sanity is low, hallucinate or misinterpret details.
  If Dissonance is high, the voices should express confusion or self-loathing about recent choices.
  If {profile.get_dominant_values()[0][0].value} is high, frame choices through that lens.
</psychological_profile>"""

    def evolve_from_event(self, profile: PsychologicalProfile, event_desc: str, outcome: str = "", archetype_profile: Optional[ArchetypeProfile] = None):
        """
        Heuristic-based evolution. (can be enhanced with LLM later).
        Updates stats based on simple keyword matching or outcome.
        """
        # Calculate stress multiplier from Archetype
        stress_mult = 1.0
        if archetype_profile and self.archetype_config and archetype_profile.primary_archetype:
            try:
                defn = self.archetype_config.get_archetype(archetype_profile.primary_archetype)
                for key, mod in defn.stress_modifiers.items():
                    # Check if key (e.g. "loss_of_control") matches event description 
                    # Normalize key: "loss_of_control" -> "loss of control"
                    normalized_key = key.replace("_", " ")
                    if normalized_key in event_desc.lower():
                        stress_mult *= mod
                    
                    # Also map outcome "miss" to potential fear of failure keys
                    if outcome == "miss" and key in ["failure", "making_mistakes", "mistake"]:
                        stress_mult *= mod
            except Exception as e:
                print(f"Error applying archetype stress modifiers: {e}")

        # Simple heuristic examples
        
        # Stress/Sanity from outcome
        if outcome == "miss":
            self.update_stress(profile, 0.1 * stress_mult)
            profile.current_emotion = EmotionalState.AFRAID
        elif outcome == "strong_hit":
            self.update_stress(profile, -0.1) # Relief doesn't get multiplied by stress modifiers usually
            profile.current_emotion = EmotionalState.CONFIDENT
        
        # Keyword matching
        lower_desc = event_desc.lower()
        
        if "betray" in lower_desc:
            self.update_stress(profile, 0.2 * stress_mult)
            profile.traits["paranoia"] = min(1.0, profile.traits.get("paranoia", 0.0) + 0.1)
            profile.current_emotion = EmotionalState.SUSPICIOUS
            
        if "horror" in lower_desc or "terrifying" in lower_desc:
            self.update_sanity(profile, -0.1)
            self.update_stress(profile, 0.2 * stress_mult)
            
        if "help" in lower_desc or "saved" in lower_desc:
            profile.values[ValueSystem.COMMUNITY] = min(1.0, profile.values.get(ValueSystem.COMMUNITY, 0.0) + 0.05)
            
        # Identity Evolution
        from .character_identity import IdentityScore
        impact = IdentityScore()
        if any(w in lower_desc for w in ["violence", "kill", "strike", "attack", "brutal", "hit"]):
            impact.violence = 0.1
        if any(w in lower_desc for w in ["stealth", "hide", "sneak", "hid", "snuck", "shadow"]):
            impact.stealth = 0.1
        if any(w in lower_desc for w in ["help", "save", "mercy", "spare", "empathy"]):
            impact.empathy = 0.1
        if any(w in lower_desc for w in ["hack", "logic", "calculate", "analyze", "data"]):
            impact.logic = 0.1
            
        if any([impact.violence, impact.stealth, impact.empathy, impact.logic, impact.greed]):
            profile.identity.update_scores(impact, event_desc)

    def evolve_soul_searching(self, profile: PsychologicalProfile, narrative_context: str) -> str:
        """
        Trigger an LLM-driven deep evaluation of the character's psyche.
        Returns a summary of the internal shift.
        """
        if not self.llm_client:
            return "No LLM client available for soul-searching."
            
        prompt = f"""You are the character's Subsconscious. Analyze their recent narrative and current profile.
        
Narrative Context:
{narrative_context}

Current Profile:
{profile.model_dump_json(indent=2)}

TASK:
1. Analyze if recent events challenge their current BELIEFS or VALUES.
2. Propose 1 change to their beliefs (add or remove) and 1 shift in their values (0.1 scale).
3. Return the shift in JSON format: {{"shift_summary": "...", "belief_change": "...", "value_shift": {{"value": "...", "delta": 0.1}}}}
"""
        try:
            # Note: Assuming llm_client has a generate_sync or similar method
            # This is a placeholder for actual LLM integration
            response = self.llm_client.generate_sync(prompt)
            # Logic to parse and apply response would go here
            return f"Soul-searching complete: {response[:100]}..."
        except Exception as e:
            return f"Soul-searching failed: {e}"

    def unlock_memory(self, profile: PsychologicalProfile, memory_id: str, delta: float):
        """Weaken the seal of a suppressed memory."""
        for memory in profile.suppressed_memories:
            if memory.id == memory_id:
                memory.seal_integrity = max(0.0, memory.seal_integrity - delta)
                if memory.seal_integrity <= 0.0 and not memory.is_revealed:
                    memory.is_revealed = True
                    profile.memories.append(f"RECOVERED: {memory.description}")

    def check_breaking_point(self, profile: PsychologicalProfile) -> TraumaScar | None:
        """
        Check if the character has hit a breaking point (>90% stress).
        Assigns a new Trauma Scar if they have and returns it.
        """
        if profile.stress_level >= 0.9 and random.random() < 0.3:
            return self.assign_trauma(profile)
        return None

    def assign_trauma(self, profile: PsychologicalProfile) -> TraumaScar:
        """Assign a random trauma scar based on current dominant traits/emotions."""
        traumas = [
            TraumaScar(
                name="Shattered Trust", 
                description="The void of space isn't as cold as the people in it. You will never fully trust anyone again.",
                trait_modifier={"paranoia": 0.3, "empathy": -0.2}
            ),
            TraumaScar(
                name="Cold Logic", 
                description="Emotion is a liability in a dying ship. You've learned to shut it off entirely.",
                trait_modifier={"logic": 0.4, "empathy": -0.3}
            ),
            TraumaScar(
                name="Jittery Nerves", 
                description="Every creak of the hull is a threat. Every shadow is a monster.",
                trait_modifier={"caution": 0.3, "resilience": -0.1}
            ),
            TraumaScar(
                name="Survivor's Guilt",
                description="They died. You lived. Why? The question haunts you.",
                trait_modifier={"empathy": 0.3, "resilience": -0.2}
            ),
            TraumaScar(
                name="Paranoid Delusion",
                description="The walls have eyes. The AI is watching. They're all in on it.",
                trait_modifier={"paranoia": 0.5, "logic": -0.2}
            ),
            TraumaScar(
                name="Emotional Shutdown",
                description="Feeling is pain. You've learned to feel nothing at all.",
                trait_modifier={"empathy": -0.4, "resilience": 0.2}
            ),
            TraumaScar(
                name="Reckless Abandon",
                description="Death is inevitable. Might as well go out swinging.",
                trait_modifier={"boldness": 0.4, "caution": -0.3}
            ),
            TraumaScar(
                name="Crushing Isolation",
                description="No one understands. No one can help. You are alone.",
                trait_modifier={"empathy": -0.3, "resilience": -0.2}
            ),
            TraumaScar(
                name="Obsessive Control",
                description="If you control everything, nothing can hurt you. Right?",
                trait_modifier={"logic": 0.3, "caution": 0.2}
            ),
            TraumaScar(
                name="Fractured Identity",
                description="Who are you? Were you ever real? The mirror shows a stranger.",
                trait_modifier={"paranoia": 0.2, "logic": -0.3}
            ),
        ]
        scar = random.choice(traumas)
        profile.trauma_scars.append(scar)
        
        # Apply modifiers
        for trait, mod in scar.trait_modifier.items():
            profile.traits[trait] = max(0.0, min(1.0, profile.traits.get(trait, 0.0) + mod))
            
        # Dramatic stress reset but sanity cost
        profile.stress_level = 0.4
        profile.sanity = max(0.0, profile.sanity - 0.2)
        
        return scar

    def get_move_modifier(self, profile: PsychologicalProfile, stat: str) -> int:
        """
        Return a modifier to apply to a move roll based on psychological state.
        """
        modifier = 0
        
        # High stress penalizes Heart (emotional stability) moves
        if profile.stress_level > 0.7 and stat.lower() == "heart":
            modifier -= 1
        
        # Fear penalizes Iron (physical bravery) moves
        if profile.current_emotion == EmotionalState.AFRAID and stat.lower() == "iron":
            modifier -= 1
        
        # Overwhelmed penalizes all moves
        if profile.current_emotion == EmotionalState.OVERWHELMED:
            modifier -= 1
        
        # Low sanity penalizes Wits (perception, awareness)
        if profile.sanity < 0.3 and stat.lower() == "wits":
            modifier -= 1
        
        return modifier

    def generate_hallucination(self, profile: PsychologicalProfile) -> str | None:
        """
        If sanity is critically low, generate a false detail to inject into the narrative.
        """
        if profile.sanity >= 0.3:
            return None
            
        # Pool of hallucinations based on emotional state
        hallucinations = {
            EmotionalState.AFRAID: [
                "A shadow moves in the corner. It wasn't there before.",
                "You see eyes in the darkness of the vent. They blink.",
                "The ship's AI whispers your true name. You never told it.",
            ],
            EmotionalState.SUSPICIOUS: [
                "The crew member's smile doesn't reach their eyes. It never does.",
                "The transmission log shows messages you never sent. Who is pretending to be you?",
                "The medical bay records show someone accessed your file. Last night.",
            ],
            EmotionalState.GUILTY: [
                "You see your father's face in the reflection on the viewport.",
                "The dead crewmember is sitting in the mess hall. They look disappointed.",
                "The oxygen alarm keeps counting down. But only you can hear it.",
            ],
        }
        
        emotion = profile.current_emotion
        pool = hallucinations.get(emotion, [
            "The lights flicker. Just for a moment.",
            "You smell smoke. There is no fire.",
            "Someone is standing behind you. Don't turn around.",
        ])
        
        return random.choice(pool)

    # =========================================================================
    # CHARACTER IDENTITY & WOUND SYSTEM (EXPANDED)
    # =========================================================================

    def detect_wound_indicators(self, text: str) -> Dict[WoundType, float]:
        """
        Analyze text for signals pointing to specific core wounds (22 types).
        Returns a dictionary of wound types and their detected intensity (0.0 to 1.0).
        """
        text = text.lower()
        scores: Dict[WoundType, float] = {w: 0.0 for w in WoundType if w != WoundType.UNKNOWN}
        
        # Helper to add score
        def add(wound: WoundType, amount: float):
            scores[wound] += amount

        # --- OVERCONTROLLED CLUSTER ---
        if any(w in text for w in ["interrogate", "demand", "force", "analyze", "puzzle", "control", "methodical"]):
            add(WoundType.CONTROLLER, 0.2)
        if any(w in text for w in ["guilty", "criminal", "monster", "punish", "justice", "wrong", "sin", "blame"]):
            add(WoundType.JUDGE, 0.2)
        if any(w in text for w in ["dead", "gone", "memory", "ghost", "past", "forget", "leave", "alone"]):
            add(WoundType.GHOST, 0.2)
        if any(w in text for w in ["perfect", "mistake", "error", "flaw", "fail", "correct", "precise"]):
            add(WoundType.PERFECTIONIST, 0.2)
        if any(w in text for w in ["sacrifice", "burden", "suffering", "carry", "save them", "my fault"]):
            add(WoundType.MARTYR, 0.2)
        if any(w in text for w in ["deny", "refuse", "discipline", "clean", "pure", "abstain", "control self"]):
            add(WoundType.ASCETIC, 0.2)
        if any(w in text for w in ["spy", "watch", "traitor", "enemy", "trust no one", "suspect", "plot"]):
            add(WoundType.PARANOID, 0.2)
        if any(w in text for w in ["actually", "technically", "ignorant", "study", "read", "fact", "wrong"]):
            add(WoundType.PEDANT, 0.2)

        # --- UNDERCONTROLLED CLUSTER ---
        if any(w in text for w in ["betray", "lie", "fake", "naive", "stupid", "always", "expect"]):
            add(WoundType.CYNIC, 0.2)
        if any(w in text for w in ["run", "escape", "hide", "identity", "secret", "chase", "behind", "track"]):
            add(WoundType.FUGITIVE, 0.2)
        if any(w in text for w in ["want", "take", "pleasure", "now", "bored", "more", "taste"]):
            add(WoundType.HEDONIST, 0.2)
        if any(w in text for w in ["burn", "break", "destroy", "smash", "kill", "rage", "hate"]):
            add(WoundType.DESTROYER, 0.2)
        if any(w in text for w in ["joke", "laugh", "trick", "fool", "chaos", "fun", "bored"]):
            add(WoundType.TRICKSTER, 0.2)
        if any(w in text for w in ["me", "mine", "admire", "look at me", "best", "deserve", "special"]):
            add(WoundType.NARCISSIST, 0.2)
        if any(w in text for w in ["prey", "hunt", "weak", "strong", "win", "loser", "dominant"]):
            add(WoundType.PREDATOR, 0.2)
        if any(w in text for w in ["use", "pawn", "game", "play", "strategy", "move", "tool"]):
            add(WoundType.MANIPULATOR, 0.2)

        # --- HYBRID CLUSTER ---
        if any(w in text for w in ["fake", "pretend", "mask", "actor", "role", "hide who i am"]):
            add(WoundType.IMPOSTOR, 0.2)
        if any(w in text for w in ["help", "fix", "rescue", "need me", "good person", "support"]):
            add(WoundType.SAVIOR, 0.2)
        if any(w in text for w in ["revenge", "avenge", "payback", "blood", "debt", "settle"]):
            add(WoundType.AVENGER, 0.2)
        if any(w in text for w in ["afraid", "scared", "run away", "danger", "safe", "hide me"]):
            add(WoundType.COWARD, 0.2)
        if any(w in text for w in ["faith", "belief", "cause", "mission", "truth", "convert", "blind"]):
            add(WoundType.ZEALOT, 0.2)
        if any(w in text for w in ["agree", "yes", "compliment", "nice", "approve", "like me"]):
            add(WoundType.FLATTERER, 0.2)
        if any(w in text for w in ["keep", "hoard", "mine", "scarce", "cost", "price", "loss"]):
            add(WoundType.MISER, 0.2)

        return scores
    
    def detect_ruo_signals(self, text: str) -> Dict[RUOType, float]:
        """Detect signals for Resilient, Overcontrolled, or Undercontrolled tendencies."""
        text = text.lower()
        signals = {RUOType.RESILIENT: 0.0, RUOType.OVERCONTROLLED: 0.0, RUOType.UNDERCONTROLLED: 0.0}
        
        # Overcontrolled: Inhibition, anxiety, planning, withdrawal
        if any(w in text for w in ["wait", "plan", "analyze", "careful", "danger", "risk", "rule", "protocol"]):
            signals[RUOType.OVERCONTROLLED] += 0.2
            
        # Undercontrolled: Impulsivity, action, emotion, risk-taking
        if any(w in text for w in ["go", "attack", "now", "feel", "hate", "love", "rush", "impulse"]):
            signals[RUOType.UNDERCONTROLLED] += 0.2
            
        # Resilient: Adaptation, balance, perspective, regulation
        if any(w in text for w in ["adjust", "adapt", "learn", "calm", "balance", "okay", "handle"]):
            signals[RUOType.RESILIENT] += 0.2
            
        return signals

    def update_wound_profile(self, profile: PsychologicalProfile, text: str):
        """
        Update the character's wound profile based on their actions/dialogue.
        Calculates scores, RUO tendency, and updates dominant/secondary/tertiary wounds.
        """
        detected_wounds = self.detect_wound_indicators(text)
        detected_ruo = self.detect_ruo_signals(text)
        wound_profile = profile.identity.wound_profile
        
        # 1. Update Wound Scores
        for wound, score in detected_wounds.items():
            if score > 0:
                current = wound_profile.scores.scores.get(wound, 0.0)
                # Dampened accumulation
                wound_profile.scores.scores[wound] = min(1.0, current + score * 0.1)
                
        # 2. Update RUO Tendency
        for ruo, score in detected_ruo.items():
            if score > 0:
                current = wound_profile.ruo_tendency.get(ruo, 0.0)
                wound_profile.ruo_tendency[ruo] = min(1.0, current + score * 0.1)

        # 3. Determine Dominant, Secondary, Tertiary
        # Sort wounds by score
        sorted_wounds = sorted(
            wound_profile.scores.scores.items(), 
            key=lambda item: item[1], 
            reverse=True
        )
        
        # Update hierarchy if thresholds met
        if len(sorted_wounds) >= 1 and sorted_wounds[0][1] > 0.3:
            wound_profile.dominant_wound = sorted_wounds[0][0]
        if len(sorted_wounds) >= 2 and sorted_wounds[1][1] > 0.2:
            wound_profile.secondary_wound = sorted_wounds[1][0]
        if len(sorted_wounds) >= 3 and sorted_wounds[2][1] > 0.15:
            wound_profile.tertiary_wound = sorted_wounds[2][0]
            
        # 4. Update Needs and Wisdom based on Dominant Wound
        self._update_derived_psychology(wound_profile)

    def _update_derived_psychology(self, profile: WoundProfile):
        """Update derived fields like needs and dark wisdom based on dominant wound."""
        w = profile.dominant_wound
        
        # Map logic here (truncated for brevity, but covers key types)
        if w == WoundType.CONTROLLER:
            profile.philosophical_need = "To accept that control is an illusion and find peace in uncertainty."
            profile.moral_need = "To respect others as autonomous beings, not puzzles to solve."
            profile.dark_wisdom = "Control is the last illusion. I held it until it crushed what I loved."
        elif w == WoundType.JUDGE:
            profile.philosophical_need = "To accept that good people do terrible things and terrible people have humanity."
            profile.moral_need = "To extend empathy even to those who have done wrong."
            profile.dark_wisdom = "I built a world of monsters and victims. I was both."
        elif w == WoundType.GHOST:
            profile.philosophical_need = "To accept that loss is part of love, not a reason to avoid it."
            profile.moral_need = "To stay with people even when staying is painful."
            profile.dark_wisdom = "I died slowly to avoid dying all at once. I was already a ghost."
        elif w == WoundType.FUGITIVE:
             profile.philosophical_need = "To accept responsibility for who they were, and forgive themselves."
             profile.moral_need = "To own their past and make amends."
             profile.dark_wisdom = "I ran so far I forgot what I was running from. It was always me."
        elif w == WoundType.CYNIC:
             profile.philosophical_need = "To accept that trust is a choice, not a guarantee."
             profile.moral_need = "To extend trust even at risk of being hurt again."
             profile.dark_wisdom = "I was right about everyone. I made sure of it."
        elif w == WoundType.DESTROYER:
            profile.philosophical_need = "To accept that pain is not an excuse to create more pain."
            profile.moral_need = "To build something instead of tearing everything down."
            profile.dark_wisdom = "I burned it all down to feel warmth. Now I'm just alone in the ash."
        # Defaults for others...
            
    def get_thematic_lens(self, profile: PsychologicalProfile) -> str:
        """
        Return narrator instructions based on the dominant wound.
        """
        wound = profile.identity.wound_profile.dominant_wound
        
        lens_map = {
            WoundType.CONTROLLER: "THEME: Chaos and entropy. Describe things breaking, glitching, or defying analysis. Emphasize the futility of trying to solve people.",
            WoundType.JUDGE: "THEME: Moral ambiguity. Describe suspects with redeeming qualities and 'innocents' with dark secrets. Challenge moral certainty.",
            WoundType.GHOST: "THEME: Absence and haunting. Emphasize silence, cold, and remnants of those who are gone. The environment feels like a graveyard.",
            WoundType.FUGITIVE: "THEME: Paranoia and the past. Every shadow could be a pursuer. Messages seem to reference secret history.",
            WoundType.CYNIC: "THEME: Unexpected kindness that feels threatening. Betrayals are expected; genuine connection is the danger.",
            WoundType.DESTROYER: "THEME: Decay and ruin. The fragility of structures. The anger simmering beneath the surface of things.",
            WoundType.SAVIOR: "THEME: Helplessness. Situations where you cannot save everyone. The weight of others' dependence.",
            WoundType.PERFECTIONIST: "THEME: Flaws and cracks. The impossibility of purity. The ugly truth beneath the polished surface.",
        }
        
        return lens_map.get(wound, "THEME: Mysterious and claustrophobic sci-fi noir.")

    def get_ember_dialogue(self, profile: PsychologicalProfile) -> str:
        """
        Generate dialogue for The Philosopher (Ember) based on the player's wound.
        Ember acts as a mirror, stating the uncomfortable truth.
        """
        wound = profile.identity.wound_profile.dominant_wound
        
        dialogues = {
            WoundType.CONTROLLER: "You went through everything. You're looking for something that'll make this make sense. It won't. The captain's dead and nothing you find changes that.",
            WoundType.JUDGE: "You already decided who did it. I can see it. But you're not even curious anymore—you just want to be right. What if you're not?",
            WoundType.GHOST: "You don't look at people when they're talking about something real. You look past them. Like you're already gone.",
            WoundType.FUGITIVE: "You ask a lot of questions about everyone else. You never talk about before you got here. What are you running from?",
            WoundType.CYNIC: "You expect everyone to be lying. So when someone tells the truth, you don't believe them anyway. That's... sad.",
            WoundType.SAVIOR: "You keep helping me. Even when I don't need it. Why do you need me to need you?",
            WoundType.DESTROYER: "You're angry. Like, all the time. Under everything. I get it. But what happens when there's nothing left to be angry at?",
            WoundType.IMPOSTOR: "You're different with everyone. Different smile, different voice. Which one is real? Do you know?",
            WoundType.PERFECTIONIST: "You're so hard on them. But you're harder on yourself, aren't you? If you make one mistake, does the world end?",
            WoundType.PARANOID: "You think everyone's watching you. Maybe they are. But maybe you're just wishing you mattered enough to watch.",
        }
        
        return dialogues.get(wound, "You're searching for something. I don't think it's just the killer.")

    def get_dark_wisdom(self, profile: PsychologicalProfile) -> str:
        """
        Generate a 'Dark Wisdom' quote for tragic endings or high-insight moments.
        Represents the character understanding their fatal flaw too late.
        """
        wound = profile.identity.wound_profile.dominant_wound
        
        wisdom = {
            WoundType.CONTROLLER: "Control is the last illusion. I held onto it until it crushed everything I loved.",
            WoundType.JUDGE: "I built a world of monsters and victims. In the end, I was both.",
            WoundType.GHOST: "I died slowly to avoid dying all at once. I was already a ghost.",
            WoundType.FUGITIVE: "I ran so far I forgot what I was running from. It was always me.",
            WoundType.CYNIC: "I was right about everyone. I made sure of it.",
            WoundType.PERFECTIONIST: "I polished the surface until there was nothing left underneath.",
            WoundType.MARTYR: "I gave everything away until I was nothing but a void needing to be filled.",
            WoundType.SAVIOR: "I saved them all, but I couldn't save myself from needing to be the hero.",
            WoundType.DESTROYER: "I burned it all down to feel warmth. Now I'm just alone in the ash.",
            WoundType.NARCISSIST: "I looked in the mirror and saw a king. Everyone else saw a beggar.",
        }
        
        return wisdom.get(wound, "I see it clearly now, but the light is already fading.")
            
    def get_thematic_lens(self, profile: PsychologicalProfile) -> str:
        """
        Return narrator instructions based on the dominant wound.
        """
        wound = profile.identity.wound_profile.dominant_wound
        
        if wound == WoundType.CONTROLLER:
            return "THEME: The world is chaotic and resisting control. Describe things breaking, glitching, or defying analysis. Emphasize the futility of trying to solve people."
        elif wound == WoundType.JUDGE:
            return "THEME: The line between good and evil is blurred. Describe suspects with redeeming qualities and 'innocents' with dark secrets. Challenge the character's moral certainty."
        elif wound == WoundType.GHOST:
            return "THEME: The ship feels empty and haunted. Emphasize silence, cold, and remnants of those who are gone. The environment should feel like a graveyard."
        elif wound == WoundType.FUGITIVE:
            return "THEME: Paranoia and the past catching up. Every shadow could be a pursuer. Messages or signals seem to reference the character's secret history."
        elif wound == WoundType.CYNIC:
            return "THEME: Unexpected moments of beauty or kindness that feel threatening. Betrayals are expected, but genuine connection is the real danger. The world is dark, but maybe not as dark as they think."
        
        return "THEME: Mysterious and claustrophobic sci-fi noir."

    def apply_coping_mechanism(self, profile: PsychologicalProfile, mechanism_id: str, success: bool) -> dict:
        """
        Apply a coping mechanism. Returns a dict describing the outcome.
        """
        mechanisms = {
            "meditate": CopingMechanism(
                id="meditate",
                name="Meditate",
                description="Find stillness in the void. Center yourself.",
                stress_reduction=0.2,
                side_effect="Isolation increases if used too often."
            ),
            "journal": CopingMechanism(
                id="journal",
                name="Journal",
                description="Write down your thoughts. Externalize the chaos.",
                stress_reduction=0.15,
            ),
            "vent_to_crew": CopingMechanism(
                id="vent_to_crew",
                name="Vent to Crew",
                description="Talk to someone. Share the burden.",
                stress_reduction=0.25,
                requires_npc=True,
                side_effect="Reveals vulnerability. Trust increases but so does exposure."
            ),
            "stim_injection": CopingMechanism(
                id="stim_injection",
                name="Stim Injection",
                description="Chemical relief. Fast. Dangerous.",
                stress_reduction=0.4,
                sanity_cost=0.1,
                side_effect="Addiction risk. Sanity cost."
            ),
            "exercise": CopingMechanism(
                id="exercise",
                name="Physical Exercise",
                description="Push your body. Exhaust the mind.",
                stress_reduction=0.18,
            ),
            "art_therapy": CopingMechanism(
                id="art_therapy",
                name="Art Therapy",
                description="Create something. Give form to the formless.",
                stress_reduction=0.2,
                side_effect="Requires time and materials."
            ),
            "prayer": CopingMechanism(
                id="prayer",
                name="Prayer/Ritual",
                description="Find meaning in the void. Seek higher purpose.",
                stress_reduction=0.22,
            ),
            "substance_abuse": CopingMechanism(
                id="substance_abuse",
                name="Substance Abuse",
                description="Drown it all out. Forget.",
                stress_reduction=0.35,
                sanity_cost=0.15,
                side_effect="Severe addiction risk. Sanity damage."
            ),
            "self_isolation": CopingMechanism(
                id="self_isolation",
                name="Self-Isolation",
                description="Lock the door. Hide from everyone.",
                stress_reduction=0.25,
                side_effect="Severe isolation penalty."
            ),
        }
        
        mechanism = mechanisms.get(mechanism_id)
        if not mechanism:
            return {"success": False, "message": "Unknown coping mechanism."}
        
        # Track usage
        profile.coping_usage_counts[mechanism_id] = profile.coping_usage_counts.get(mechanism_id, 0) + 1
        usage_count = profile.coping_usage_counts[mechanism_id]
        
        result = {"mechanism": mechanism.name, "success": success, "usage_count": usage_count}
        
        if success:
            # Reduce stress
            self.update_stress(profile, -mechanism.stress_reduction)
            result["stress_reduced"] = mechanism.stress_reduction
            
            # Apply sanity cost
            if mechanism.sanity_cost > 0:
                self.update_sanity(profile, -mechanism.sanity_cost)
                result["sanity_cost"] = mechanism.sanity_cost
            
            # Consequence chains
            if mechanism_id == "stim_injection":
                profile.addiction_level = min(1.0, profile.addiction_level + 0.15)
                if usage_count >= 3:
                    result["warning"] = "Addiction developing. Withdrawal penalties active."
            
            if mechanism_id == "meditate":
                profile.isolation_level = min(1.0, profile.isolation_level + 0.1)
                if usage_count >= 5:
                    result["warning"] = "Isolation increasing. Social options may be limited."
            
            # Side effects
            if mechanism.side_effect:
                result["side_effect"] = mechanism.side_effect
        else:
            # Failure increases stress
            self.update_stress(profile, 0.1)
            result["message"] = "Failed to cope. Stress increases."
        
        return result

    def heal_trauma_scar(self, profile: PsychologicalProfile, scar_name: str, progress: float) -> dict:
        """
        Slowly heal a trauma scar. Progress accumulates over multiple therapy sessions.
        Scars can be weakened but never fully removed (permanent but less severe).
        """
        for scar in profile.trauma_scars:
            if scar.name == scar_name:
                # Reduce trait modifier intensity
                for trait, mod in scar.trait_modifier.items():
                    reduction = mod * progress * 0.1  # 10% reduction per session
                    new_mod = mod - reduction if mod > 0 else mod + abs(reduction)
                    scar.trait_modifier[trait] = new_mod
                    
                    # Apply the reduction to current traits
                    current = profile.traits.get(trait, 0.0)
                    profile.traits[trait] = max(0.0, min(1.0, current - reduction))
                
                return {
                    "scar": scar_name,
                    "progress": progress,
                    "message": f"Therapy session complete. {scar_name} is weakening.",
                    "fully_healed": all(abs(m) < 0.05 for m in scar.trait_modifier.values())
                }
        
        return {"success": False, "message": "Trauma scar not found."}

    def evolve_trauma_arc(self, profile: PsychologicalProfile, scar_name: str) -> dict:
        """
        Evolve a trauma scar through its arc stages based on therapy progress.
        Scars can transform into healthier versions.
        """
        for scar in profile.trauma_scars:
            if scar.name == scar_name:
                # Define transformation paths
                transformations = {
                    "Shattered Trust": {
                        10: ("healing", "Cautious Trust", "You're learning to trust again, slowly."),
                        20: ("scarred", "Guarded Openness", "Trust is earned, not given."),
                        30: ("integrated", "Wise Discernment", "You know who to trust and why."),
                    },
                    "Cold Logic": {
                        10: ("healing", "Balanced Rationality", "Logic and emotion can coexist."),
                        20: ("scarred", "Thoughtful Compassion", "You think before you feel, but you do feel."),
                        30: ("integrated", "Integrated Wisdom", "Head and heart work together."),
                    },
                    "Jittery Nerves": {
                        10: ("healing", "Heightened Awareness", "Caution without paranoia."),
                        20: ("scarred", "Calm Vigilance", "You're alert, not afraid."),
                        30: ("integrated", "Centered Presence", "You trust yourself to handle threats."),
                    },
                }
                
                path = transformations.get(scar.name, {})
                sessions = scar.therapy_sessions
                
                for threshold, (stage, new_name, description) in path.items():
                    if sessions >= threshold and scar.arc_stage != "integrated":
                        scar.arc_stage = stage
                        old_name = scar.name
                        scar.name = new_name
                        scar.description = description
                        
                        # Reduce negative modifiers, add positive ones
                        for trait, mod in scar.trait_modifier.items():
                            if mod < 0:
                                scar.trait_modifier[trait] = mod * 0.5  # Halve negative
                            else:
                                scar.trait_modifier[trait] = mod * 0.7  # Reduce intensity
                        
                        return {
                            "transformed": True,
                            "old_name": old_name,
                            "new_name": new_name,
                            "stage": stage,
                            "message": f"Your trauma has evolved: {old_name} → {new_name}"
                        }
                
                return {
                    "transformed": False,
                    "sessions": sessions,
                    "message": f"Continue therapy. {scar.name} is at stage: {scar.arc_stage}"
                }
        
        return {"success": False, "message": "Trauma scar not found."}
