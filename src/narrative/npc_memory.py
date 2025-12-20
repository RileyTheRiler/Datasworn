"""
NPC Memory & Continuity System.

This module provides persistent memory for NPCs, allowing them to:
1. Recall past interactions with the player.
2. Avoid repeating themselves or contradicting past statements.
3. Make natural callbacks to previous events.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import random

@dataclass
class EpisodicMemory:
    """A single memory of an event or interaction."""
    scene: int
    topic: str
    content: str
    emotion: str  # e.g., "HIGH", "NEUTRAL", "CRITICAL"
    participants: List[str] = field(default_factory=lambda: ["player"])
    
@dataclass
class NPCMemoryBank:
    """
    Persistent memory store for a specific NPC.
    """
    npc_id: str
    episodic_memory: List[EpisodicMemory] = field(default_factory=list)
    conversation_history: Dict[str, List[int]] = field(default_factory=dict) # topic -> [scene_nums]
    promises_made: List[str] = field(default_factory=list)
    lies_told: List[str] = field(default_factory=list)
    secrets_revealed: List[str] = field(default_factory=list)
    
    def record_interaction(self, scene_num: int, topic: str, content: str, emotion: str = "NEUTRAL"):
        """
        Store what happened in this conversation.
        """
        memory = EpisodicMemory(
            scene=scene_num,
            topic=topic,
            content=content,
            emotion=emotion
        )
        self.episodic_memory.append(memory)

        if topic not in self.conversation_history:
            self.conversation_history[topic] = []
        self.conversation_history[topic].append(scene_num)

    def has_discussed(self, topic: str) -> bool:
        """Check if a topic has been discussed before."""
        return topic in self.conversation_history

    def get_last_discussion(self, topic: str) -> Optional[int]:
        """Get scene number of last discussion on this topic."""
        if topic in self.conversation_history:
            return self.conversation_history[topic][-1]
        return None

    def check_consistency(self, proposed_dialogue: str) -> List[str]:
        """
        Ensure NPC doesn't contradict past statements.
        Returns a list of potential contradiction warnings.
        (This is a placeholder for more advanced semantic checking)
        """
        # In a full ML implementation, this would semantically compare 
        # proposed_dialogue against self.episodic_memory content.
        # For now, we return empty list as we can't easily do semantic analysis here yet.
        return []

    def generate_callback(self, current_scene: int) -> Optional[str]:
        """
        Generate a dialogue line referencing a past meaningful interaction.
        """
        # Filter for memories that are:
        # 1. Emotional (HIGH/CRITICAL)
        # 2. Not from the very recent past (give it some time to breathe, e.g. > 1 scene ago)
        significant_memories = [
            m for m in self.episodic_memory 
            if m.emotion in ["HIGH", "CRITICAL"] and (current_scene - m.scene) > 1
        ]
        
        if significant_memories:
            memory = random.choice(significant_memories)
            # Simple template for now, could be expanded
            return f"I haven't forgotten about {memory.topic} back when we were at scene {memory.scene}."
            
        return None

    def to_dict(self) -> dict:
        """Serialize state."""
        return {
            "npc_id": self.npc_id,
            "episodic_memory": [
                {
                    "scene": m.scene,
                    "topic": m.topic,
                    "content": m.content,
                    "emotion": m.emotion,
                    "participants": m.participants
                }
                for m in self.episodic_memory
            ],
            "conversation_history": self.conversation_history,
            "promises_made": self.promises_made,
            "lies_told": self.lies_told,
            "secrets_revealed": self.secrets_revealed
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NPCMemoryBank":
        """Deserialize state."""
        bank = cls(npc_id=data.get("npc_id", "unknown"))
        
        for m_data in data.get("episodic_memory", []):
            bank.episodic_memory.append(EpisodicMemory(
                scene=m_data["scene"],
                topic=m_data["topic"],
                content=m_data["content"],
                emotion=m_data.get("emotion", "NEUTRAL"),
                participants=m_data.get("participants", ["player"])
            ))
            
        bank.conversation_history = data.get("conversation_history", {})
        bank.promises_made = data.get("promises_made", [])
        bank.lies_told = data.get("lies_told", [])
        bank.secrets_revealed = data.get("secrets_revealed", [])
        
        return bank
