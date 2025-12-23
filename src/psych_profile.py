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

class NPCPsyche(BaseModel):
    """Simplified psychological profile for an NPC actor."""
    name: str
    dominant_trait: str
    current_emotion: EmotionalState = EmotionalState.NEUTRAL
    instability: float = 0.0  # 0-1, high = unpredictable behavior

class CopingMechanism(BaseModel):
    """A coping strategy the character can use to manage stress/trauma."""
    id: str
    name: str
    description: str
    stress_reduction: float  # Amount of stress reduced on success
    sanity_cost: float = 0.0  # Potential sanity cost
    side_effect: str = ""  # Description of potential side effect
    requires_npc: bool = False  # Requires interaction with NPC

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

        return f"""<psychological_profile>
CURRENT STATE:
  Emotion: {profile.current_emotion.value.upper()} | Stress: {profile.stress_level:.0%} | Sanity: {profile.sanity:.0%}

CORE DRIVERS:
  Values: {values_str}
  Traits: {traits_str}

BELIEFS:
  - {beliefs_str}

RELATIONSHIPS:
  {opinions_str}

INNER MONOLOGUE GUIDANCE:
  Filter all perceptions through this psychological state. 
  If Stress is high, focus on threats and failure.
  If Sanity is low, hallucinate or misinterpret details.
  If {profile.get_dominant_values()[0][0].value} is high, frame choices through that lens.
</psychological_profile>"""

    def evolve_from_event(self, profile: PsychologicalProfile, event_desc: str, outcome: str = ""):
        """
        Heuristic-based evolution. (can be enhanced with LLM later).
        Updates stats based on simple keyword matching or outcome.
        """
        # Simple heuristic examples
        
        # Stress/Sanity from outcome
        if outcome == "miss":
            self.update_stress(profile, 0.1)
            profile.current_emotion = EmotionalState.AFRAID
        elif outcome == "strong_hit":
            self.update_stress(profile, -0.1)
            profile.current_emotion = EmotionalState.CONFIDENT
        
        # Keyword matching
        lower_desc = event_desc.lower()
        
        if "betray" in lower_desc:
            self.update_stress(profile, 0.2)
            profile.traits["paranoia"] = min(1.0, profile.traits.get("paranoia", 0.0) + 0.1)
            profile.current_emotion = EmotionalState.SUSPICIOUS
            
        if "horror" in lower_desc or "terrifying" in lower_desc:
            self.update_sanity(profile, -0.1)
            self.update_stress(profile, 0.2)
            
        if "help" in lower_desc or "saved" in lower_desc:
            profile.values[ValueSystem.COMMUNITY] = min(1.0, profile.values.get(ValueSystem.COMMUNITY, 0.0) + 0.05)

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

    def generate_hallucination(
        self,
        profile: PsychologicalProfile,
        policy: "HallucinationPolicy | None" = None,
        hallucination_confidence: float = 1.0,
        hallucinations_this_scene: int = 0,
        director_approved: bool = False,
    ) -> str | None:
        """
        If sanity is critically low, generate a false detail to inject into the narrative.

        A HallucinationPolicy can be provided to enforce designer-tunable
        guardrails (scene limits, confidence gates, or director approval).
        """
        from src.ai_tuning import HallucinationPolicy

        if policy is None:
            if profile.sanity >= 0.3:
                return None
        elif isinstance(policy, HallucinationPolicy):
            if not policy.allows(
                sanity=profile.sanity,
                hallucinations_this_scene=hallucinations_this_scene,
                hallucination_confidence=hallucination_confidence,
                director_approved=director_approved,
            ):
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
