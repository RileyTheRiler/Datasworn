"""
Dream System for Starforged AI Game Master.
Generates surreal, fragmented narrative interludes when sanity is low.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List
import random
from src.psych_profile import PsychologicalProfile, EmotionalState


@dataclass
class DreamFragment:
    """A potential dream or flashback sequence."""
    id: str
    trigger_condition: str  # e.g., "sanity < 0.5", "hippocampus > 0.8"
    narrative_seed: str  # Starting point for the dream
    memory_link: Optional[str] = None  # Links to a memory index if relevant
    intensity: float = 0.5  # 0.0 to 1.0


# Pre-defined dream fragments
DREAM_FRAGMENTS = [
    DreamFragment(
        id="childhood_door",
        trigger_condition="sanity < 0.6",
        narrative_seed="You're standing in front of a door you haven't seen since childhood. The paint is peeling. Someone is crying on the other side.",
        intensity=0.4,
    ),
    DreamFragment(
        id="endless_corridor",
        trigger_condition="sanity < 0.5",
        narrative_seed="The ship's corridor stretches impossibly long. Your footsteps echo, but you haven't moved. The walls are breathing.",
        intensity=0.6,
    ),
    DreamFragment(
        id="mirror_self",
        trigger_condition="sanity < 0.4",
        narrative_seed="In the viewport's reflection, you see yourself. But you're mouthing words you aren't saying. You're smiling.",
        intensity=0.7,
    ),
    DreamFragment(
        id="dead_crew",
        trigger_condition="sanity < 0.3",
        narrative_seed="The mess hall is full. Every seat taken. But they're all staring at you. And they're all dead. They've been dead for weeks.",
        intensity=0.9,
    ),
    DreamFragment(
        id="time_loop",
        trigger_condition="stress > 0.8",
        narrative_seed="This moment. You've lived it before. The same words, the same gestures. How many times have you been here?",
        intensity=0.5,
    ),
    DreamFragment(
        id="voice_of_void",
        trigger_condition="hippocampus > 0.8",
        narrative_seed="Something is whispering from the black between stars. It knows your name. It knows what you did.",
        memory_link="0",  # Links to first memory
        intensity=0.8,
    ),
]


class DreamEngine:
    """
    Generates surreal narrative interludes based on psychological state.
    """

    def check_trigger(self, profile: PsychologicalProfile) -> DreamFragment | None:
        """
        Check if a dream should trigger based on current psychological state.
        Returns a DreamFragment if triggered, None otherwise.
        """
        eligible = []
        
        for fragment in DREAM_FRAGMENTS:
            cond = fragment.trigger_condition.lower()
            
            # Parse simple conditions
            if "sanity <" in cond:
                threshold = float(cond.split("<")[1].strip())
                if profile.sanity < threshold:
                    eligible.append(fragment)
            elif "stress >" in cond:
                threshold = float(cond.split(">")[1].strip())
                if profile.stress_level > threshold:
                    eligible.append(fragment)
            elif "hippocampus >" in cond:
                # This would need inner voice dominance, but we can check traits
                if profile.traits.get("introspection", 0.0) > 0.7:
                    eligible.append(fragment)
        
        if not eligible:
            return None
        
        # Probability based on intensity and sanity
        for fragment in sorted(eligible, key=lambda x: x.intensity, reverse=True):
            trigger_chance = (1.0 - profile.sanity) * fragment.intensity
            if random.random() < trigger_chance:
                return fragment
        
        return None

    def generate_dream(
        self, 
        profile: PsychologicalProfile, 
        context: str = "",
        fragment: DreamFragment | None = None
    ) -> str:
        """
        Generate a dream/flashback narrative sequence.
        """
        if not fragment:
            fragment = self.check_trigger(profile)
        
        if not fragment:
            return ""
        
        lines = ["[DREAM SEQUENCE]"]
        lines.append("")
        lines.append("*The world shifts. Reality bends.*")
        lines.append("")
        lines.append(fragment.narrative_seed)
        
        # Add memory corruption if linked
        if fragment.memory_link and profile.memories:
            try:
                idx = int(fragment.memory_link)
                if idx < len(profile.memories):
                    lines.append("")
                    lines.append(f"*You remember: {profile.memories[idx]}*")
                    lines.append("*(But was that how it happened?)*")
            except (ValueError, IndexError):
                pass
        
        # Add emotional coloring
        if profile.current_emotion == EmotionalState.AFRAID:
            lines.append("")
            lines.append("*Your heart pounds. This isn't real. It can't be real.*")
        elif profile.current_emotion == EmotionalState.GUILTY:
            lines.append("")
            lines.append("*You deserve this. You know you do.*")
        
        lines.append("")
        lines.append("*...and then you're back. The moment passes.*")
        lines.append("[END DREAM]")
        
        return "\n".join(lines)

    def get_narrator_injection(self, profile: PsychologicalProfile) -> str:
        """
        Get a subtle narrative hint if the player is close to dreaming.
        Used to build atmosphere before a full dream triggers.
        """
        if profile.sanity < 0.4:
            hints = [
                "[Hint: Reality feels thin. Include brief sensory glitches.]",
                "[Hint: Time is uncertain. Describe moments of deja vu.]",
                "[Hint: The player catches glimpses of things that aren't there.]",
            ]
            return random.choice(hints)
        elif profile.sanity < 0.6:
            hints = [
                "[Hint: The player feels watched. Include uneasy atmosphere.]",
                "[Hint: Sounds seem slightly off. Echoes where there shouldn't be.]",
            ]
            return random.choice(hints)
        
        return ""
