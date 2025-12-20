"""
NPC Emotional State Machine.

This module provides dynamic emotional states for NPCs, allowing them to
react emotionally to events and have those emotions influence their dialogue.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Tuple, Optional

class EmotionType(Enum):
    CALM = "CALM"
    ANXIOUS = "ANXIOUS"
    ANGRY = "ANGRY"
    FEARFUL = "FEARFUL"
    JOYFUL = "JOYFUL"
    GRIEVING = "GRIEVING"

@dataclass
class EmotionData:
    """Current emotional state."""
    current_state: EmotionType = EmotionType.CALM
    intensity: float = 0.0  # 0.0 to 1.0
    duration: int = 0  # Scenes in this state

@dataclass
class NPCEmotionalStateMachine:
    """
    Manages emotional state transitions and dialogue coloration.
    """
    states: Dict[str, EmotionData] = field(default_factory=dict) # npc_id -> state
    
    # Event -> (OldState, NewState, Intensity)
    # This is a simplified transition table.
    TRIGGERS = {
        "BETRAYED": (EmotionType.ANGRY, 0.8),
        "THREATENED": (EmotionType.FEARFUL, 0.7),
        "LOSS": (EmotionType.GRIEVING, 0.9),
        "SUCCESS": (EmotionType.JOYFUL, 0.5),
        "REASSURED": (EmotionType.CALM, 0.2)
    }

    def get_state(self, npc_id: str) -> EmotionData:
        if npc_id not in self.states:
            self.states[npc_id] = EmotionData()
        return self.states[npc_id]

    def process_event(self, npc_id: str, event_type: str):
        """
        Trigger an emotional reaction.
        """
        state = self.get_state(npc_id)
        
        # Simple transition logic
        if event_type in self.TRIGGERS:
            new_type, intensity = self.TRIGGERS[event_type]
            
            # Don't override high intensity with low intensity of same type immediately
            if state.current_state == new_type and state.intensity > intensity:
                return

            state.current_state = new_type
            state.intensity = intensity
            state.duration = 0

    def decay_emotion(self, npc_id: str):
        """
        Fade emotions over time toward CALM.
        """
        if npc_id not in self.states:
            return
            
        state = self.states[npc_id]
        state.duration += 1
        
        # Decay intensity
        state.intensity *= 0.9
        
        if state.intensity < 0.2:
            state.current_state = EmotionType.CALM
            state.intensity = 0.0

    def modify_dialogue(self, npc_id: str, base_dialogue: str) -> str:
        """
        Color dialogue based on emotion.
        """
        state = self.get_state(npc_id)
        
        if state.intensity < 0.3:
            return base_dialogue
            
        if state.current_state == EmotionType.ANGRY:
            return f"{base_dialogue.upper()}!"
        elif state.current_state == EmotionType.FEARFUL:
            return f"{base_dialogue}... please."
        elif state.current_state == EmotionType.GRIEVING:
            return f"...{base_dialogue.lower()}..."
            
        return base_dialogue

    def to_dict(self) -> dict:
        return {
            "states": {
                nid: {
                    "current_state": s.current_state.value,
                    "intensity": s.intensity,
                    "duration": s.duration
                }
                for nid, s in self.states.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NPCEmotionalStateMachine":
        system = cls()
        for nid, s_data in data.get("states", {}).items():
            system.states[nid] = EmotionData(
                current_state=EmotionType(s_data["current_state"]),
                intensity=s_data["intensity"],
                duration=s_data["duration"]
            )
        return system
