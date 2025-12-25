"""
Inner Voice System for Starforged AI Game Master.
Implements a Disco Elysium-style "Thought Cabinet" where different aspects of the character's psyche
comment on the narrative, argue with each other, and evolve based on player choices.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import json
import ollama
from .psych_profile import PsychologicalProfile, ValueSystem

# ============================================================================
# Psyche Aspect
# ============================================================================

@dataclass
class PsycheAspect:
    """
    Represents a specific facet of the character's psyche.
    Examples: "The Brute" (Iron), "The Shadow" (Deception), "The Archive" (Wits).
    """
    name: str              # Internal name (e.g., "Iron")
    voice_name: str        # Display name (e.g., "The Brute")
    description: str       # Personality description
    dominance: float = 0.5 # 0.0 to 1.0 (How loud/frequent this voice is)
    memories: list[str] = field(default_factory=list) # Specific events this aspect remembers
    voice_id: str | None = None # ElevenLabs Voice ID
    voice_settings: dict[str, float] | None = None # Custom voice settings (stability, similarity)
    
    def log_memory(self, memory: str):
        """Add a memory specific to this aspect."""
        self.memories.append(memory)
        # Keep recent
        if len(self.memories) > 20:
            self.memories.pop(0)

    def evolve(self, delta: float):
        """Increase or decrease dominance."""
        self.dominance = max(0.0, min(1.0, self.dominance + delta))

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "voice_name": self.voice_name,
            "description": self.description,
            "dominance": self.dominance,
            "memories": self.memories,
            "voice_id": self.voice_id,
            "voice_settings": self.voice_settings,
        }

    @classmethod
    def from_dict(cls, data: dict) -> PsycheAspect:
        # Handle legacy data without voice_id
        aspect = cls(
            name=data.get("name", "Unknown"),
            voice_name=data.get("voice_name", "Unknown"),
            description=data.get("description", ""),
            dominance=data.get("dominance", 0.5),
            memories=data.get("memories", []),
            voice_id=data.get("voice_id"),
            voice_settings=data.get("voice_settings"),
        )
        return aspect


# ============================================================================
# Inner Voice System
# ============================================================================

VOICE_SYSTEM_PROMPT = """You are the Inner Voice of a character in a psychological sci-fi thriller. 
Your goal is to provide internal monologue from specific BRAIN REGIONS.

INPUT:
- Context: What is happening.
- Active Regions: Which parts of the brain are firing.
- Profile: The character's psychological state.

GUIDELINES - THE CHORUS OF THE MIND:
- **Amygdala**: The primitive alarm. Fear, aggression, fight-or-flight, paranoia. Speaks in jagged, urgent bursts.
- **Prefrontal Cortex**: The executive. Logic, planning, impulse control, analysis. Speaks in cool, detached structures.
- **Hippocampus**: The archivist. Memory, nostalgia, trauma, past associations. Speaks in flashbacks and sensory echoes.
- **Brain Stem**: The lizard. Hunger, pain, physical survival, exhaustion. Speaks in raw somatic sensations.
- **Temporal Lobe**: The interpreter. Social intuition, empathy, language, connection. Speaks in emotions and social dynamics.

IDENTITY AND DISSONANCE:
- If the character identity (Archetype) is strong, voices should reinforce that persona.
- If **Dissonance** is high, the voices should be conflicted, questioning the character's recent inconsistent actions. They might argue about who they "really" are.

OUTPUT (JSON):
{
  "voices": [
    {
      "aspect": "Brain Region Name",
      "content": "The actual internal monologue. Use 'I' or 'We'. Distinctive voice for each region.",
      "intensity": 0.0-1.0
    }
  ]
}
"""

@dataclass
class InnerVoiceSystem:
    """
    Manages the chorus of inner voices.
    """
    aspects: dict[str, PsycheAspect] = field(default_factory=dict)
    model: str = "llama3.1"
    _client: ollama.Client = field(default_factory=ollama.Client, repr=False)

    def __post_init__(self):
        if not self.aspects:
            self._initialize_defaults()

    def _initialize_defaults(self):
        """Initialize brain regions with distinct voice profiles."""
        
        # 1. Amygdala (Fear/Aggression) - Tense, unstable
        self.aspects["amygdala"] = PsycheAspect(
            "Amygdala", "Amygdala", "Fear, aggression, survival instincts.",
            voice_id="21m00Tcm4TlvDq8ikWAM", # Rachel (using usually for veteran/strict)
            voice_settings={"stability": 0.3, "similarity_boost": 0.9} # Low stability = erratic
        )
        
        # 2. Cortex (Logic/Order) - Calm, stable, highly analytical
        self.aspects["cortex"] = PsycheAspect(
            "Cortex", "Prefrontal Cortex", "Logic, planning, social control.",
            voice_id="AZnzlk1XvdvUeBnXmlld", # Domi (Scholar)
            voice_settings={"stability": 0.9, "similarity_boost": 0.7} # High stability = robotic/calm
        )
        
        # 3. Hippocampus (Memory) - Soft, distant
        self.aspects["hippocampus"] = PsycheAspect(
            "Hippocampus", "Hippocampus", "Memory, trauma, past patterns.",
            voice_id="EXAVITQu4vr4xnSDxMaL", # Bella (Merchant - generally smooth)
            voice_settings={"stability": 0.5, "similarity_boost": 0.5} 
        )
        
        # 4. Brain Stem (Survival/Pain) - Raw, guttural
        self.aspects["brain_stem"] = PsycheAspect(
            "BrainStem", "Brain Stem", "Raw sensation, pain, hunger.",
            voice_id="ErXwobaYiN019PkySvjV", # Antoni (Rebel)
            voice_settings={"stability": 0.4, "similarity_boost": 0.95} # Intense
        )
        
        # 5. Temporal Lobe (Empathy/Social) - Warm, connecting
        self.aspects["temporal"] = PsycheAspect(
            "Temporal", "Temporal Lobe", "Empathy, language, social intuition.",
            voice_id="MF3mGyEYCl7XYWbV9V6O", # A distinct voice
            voice_settings={"stability": 0.8, "similarity_boost": 0.8}
        )

    def update_dominance(self, aspect_name: str, delta: float):
        """Directly modify the dominance of a voice."""
        key = aspect_name.lower()
        if key in self.aspects:
            self.aspects[key].evolve(delta)

    def sync_with_profile(self, profile: PsychologicalProfile):
        """
        Update voice dominance based on Psychological Profile traits and values.
        """
        # 1. Amygdala: Paranoia, Stress, and Fear triggers
        paranoia = profile.traits.get("paranoia", 0.3)
        self.aspects["amygdala"].dominance = max(paranoia, profile.stress_level)
        
        # 2. Prefrontal Cortex: Resilience and Discipline/Order values
        resilience = profile.traits.get("resilience", 0.5)
        discipline = profile.values.get(ValueSystem.DEDICATION, 0.5)
        order = profile.values.get(ValueSystem.ORDER, 0.5)
        self.aspects["cortex"].dominance = (resilience + max(discipline, order)) / 2
            
        # 3. Hippocampus: Curiosity and Memory depth
        curiosity = profile.values.get(ValueSystem.CURIOSITY, 0.5)
        memory_score = min(1.0, len(profile.memories) / 10.0)
        self.aspects["hippocampus"].dominance = (curiosity + memory_score) / 2
            
        # 4. Brain Stem: Caution and Survival (Stress)
        caution = profile.traits.get("caution", 0.5)
        survival_drive = profile.values.get(ValueSystem.SECURITY, 0.5)
        self.aspects["brain_stem"].dominance = (caution + survival_drive + profile.stress_level) / 3
            
        # 5. Temporal Lobe: Empathy and Community values
        empathy = profile.traits.get("empathy", 0.5)
        community = profile.values.get(ValueSystem.COMMUNITY, 0.5)
        self.aspects["temporal"].dominance = (empathy + community) / 2

    def check_hijack(self) -> dict | None:
        """
        Check if any brain region is dominant enough to hijack control.
        Threshold: 0.9 dominance.
        """
        HIJACK_THRESHOLD = 0.9
        
        hijacks = {
            "amygdala": "RAGE FUGUE. The player loses control. They attack the nearest threat with lethal intent.",
            "cortex": "ANALYSIS PARALYSIS. The player cannot act. They are locked in a loop of over-thinking.",
            "hippocampus": "TRAUMA CASCADE. The player is lost in a flashback.",
            "brain_stem": "SURVIVAL OVERRIDE. The player flees or freezes. Basic biological preservation takes over.",
            "temporal": "EMPATHY FLOOD. The player is overwhelmed by the emotions of others."
        }
        
        for key, aspect in self.aspects.items():
            if aspect.dominance >= HIJACK_THRESHOLD:
                return {
                    "aspect": aspect.voice_name,
                    "description": hijacks.get(key, "The mind overwrites the will.")
                }
        return None

    def inject_memory_echo(self, context: str, vector_db_callback: Any = None) -> dict | None:
        """
        Force a traumatic flashback or memory echo if stress is high.
        Narrative Echoes system.
        """
        # Narrative echo prompt
        ECHO_PROMPT = """
        You are the HIPPOCAMPUS, the archivist of the mind.
        The character is under high stress, triggering a FLASHBACK.
        
        CONTEXT: {context}
        RETRIEVED MEMORY: "{memory_text}"
        
        TASK:
        Reflect on this memory. Distort it. Make it haunt the present moment.
        Do not just repeat it. Embellish it with sensory details and regret.
        
        OUTPUT (JSON):
        {{
            "voice": "Hippocampus",
            "content": "The embellished memory text..."
        }}
        """
        
        # Only trigger if vector DB is available (mock check for now)
        if not vector_db_callback:
            return None
            
        # Try to retrieve a relevant memory
        try:
            # This is a hypothetical call - in real app, we'd pass the actual callback
            # memory = vector_db_callback(context)
             memory = "They left you behind on the station..." # Placeholder for logic without DB acting
        except Exception:
            return None
            
        if not memory:
            return None

        try:
            response = self._client.chat(
                model=self.model,
                messages=[
                    {"role": "user", "content": ECHO_PROMPT.format(context=context, memory_text=memory)},
                ],
                options={"temperature": 0.9, "format": "json"},
            )
            content = response.get("message", {}).get("content", "")
            data = json.loads(content)
            return {
                "aspect": "Hippocampus",
                "content": data.get("content", "I remember..."),
                "intensity": 1.0
            }
        except Exception as e:
            print(f"Echo generation failed: {e}")
            return None

    def trigger_voices(self, context: str, relevant_stats: list[str] = None, stress_level: float = 0.0) -> list[dict]:
        """
        Determine which voices speak based on context and dominance.
        """
        # Check for Narrative Echo (High Stress)
        if stress_level > 70.0: # 70% stress
             # In a real implementation, we would pass the vector DB query function here
             # For now, we simulate it if we wanted, or just skip.
             # Let's assume we want to TRY to inject if stress is super high.
             # We need a fallback if no callback provided.
             pass 

        candidates = []
        for key, aspect in self.aspects.items():
            score = aspect.dominance
            if relevant_stats and key in relevant_stats:
                score += 0.3
            
            import random
            if score + random.random() * 0.5 > 0.7:
                candidates.append(aspect)

        if not candidates:
            return []

        candidates.sort(key=lambda x: x.dominance, reverse=True)
        active_aspects = candidates[:3]

        prompt = f"""
        CONTEXT: {context}
        ACTIVE VOICES: {[a.voice_name + ": " + a.description for a in active_aspects]}
        STRESS: {stress_level}
        """

        try:
            response = self._client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": VOICE_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                options={"temperature": 0.8, "format": "json"},
            )
            
            content = response.get("message", {}).get("content", "")
            data = json.loads(content)
            
            voices = data.get("voices", [])
            
            # If stress is high, maybe prepend a raw reaction
            if stress_level > 80.0:
                 fake_echo = {
                     "aspect": "Hippocampus",
                     "content": "It's happening again. Just like before...",
                     "intensity": 0.9
                 }
                 voices.insert(0, fake_echo)
                 
            return voices

        except Exception as e:
            print(f"Inner Voice Generation Error: {e}")
            return []

    def to_dict(self) -> dict:
        return {"aspects": {k: v.to_dict() for k, v in self.aspects.items()}}

    @classmethod
    def from_dict(cls, data: dict) -> "InnerVoiceSystem":
        system = cls(aspects={})
        for k, v in data.get("aspects", {}).items():
            system.aspects[k] = PsycheAspect.from_dict(v)
        return system
