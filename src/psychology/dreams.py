"""
Dream Sequence Engine.

This module generates surreal narrative experiences for the character during sleep,
drawing from their psychological state, repressed memories, and recent events.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
import random

# We will need to import the profile types for type hinting
# from src.psych_profile import PsychologicalProfile (circular import avoidance might be needed, using strings or TYPE_CHECKING)

@dataclass
class DreamElement:
    source_type: str  # "memory", "fear", "desire", "random"
    description: str
    distortion_level: float # 0.0 to 1.0

@dataclass
class DreamSequenceEngine:
    """
    Constructs dream narratives.
    """
    
    def generate_dream(self, 
                      recent_memories: List[str], 
                      suppressed_memories: List[str],
                      dominant_emotion: str,
                      stress_level: float) -> str:
        """
        Create a dream sequence.
        """
        # Determine Dream Tone
        is_nightmare = False
        if stress_level > 0.7 or dominant_emotion in ["afraid", "overwhelmed", "guilty"]:
            is_nightmare = True
            
        # Collect Elements
        elements = []
        
        # 1. Recent Residue (Something mundane made weird)
        if recent_memories:
            mem = random.choice(recent_memories)
            elements.append(DreamElement("memory", mem, 0.3))
            
        # 2. The Core Conflict (Fear or Desire)
        if is_nightmare:
            elements.append(DreamElement("fear", "Something is chasing you, but you cannot move.", 0.8))
        else:
            elements.append(DreamElement("desire", "You are flying, weightless and free.", 0.1))
            
        # 3. Suppressed Trauma (The intrusion)
        if suppressed_memories and random.random() < 0.4:
            trauma = random.choice(suppressed_memories)
            elements.append(DreamElement("trauma", f"A door opens. Inside, {trauma}", 0.5))
            
        # Synthesize Narrative (Template based for now, LLM in future)
        narrative = self._synthesize_dream_text(elements, is_nightmare)
        
        return narrative

    def _synthesize_dream_text(self, elements: List[DreamElement], is_nightmare: bool) -> str:
        """
        Combine elements into a surreal prose block.
        """
        lines = []
        
        # Opening
        if is_nightmare:
            lines.append("The air is thick, like breathing water.")
        else:
            lines.append("The light here is wrong, too bright, but cold.")
            
        # Middle
        for el in elements:
            if el.source_type == "memory":
                lines.append(f"You remember {el.description}, but it's melting.")
            elif el.source_type == "fear":
                lines.append(f"Suddenly, {el.description}")
            elif el.source_type == "trauma":
                lines.append(f"You try to look away, but {el.description}")
            else:
                lines.append(el.description)
                
        # Closing
        lines.append("You wake with a gasp.")
        
        return " ".join(lines)

    def to_dict(self) -> dict:
        return {} # Stateless

    @classmethod
    def from_dict(cls, data: dict) -> "DreamSequenceEngine":
        return cls()
