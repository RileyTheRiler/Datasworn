"""
Revelation Manager System
Handles triggering and tracking of character micro-revelations during gameplay.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from src.narrative.secondary_characters import (
    SECONDARY_CHARACTERS, 
    SecondaryCharacter, 
    MicroRevelation,
    check_micro_revelation
)

@dataclass
class RevelationState:
    """Tracks which revelations have been revealed for a character."""
    character_id: str
    revealed_ids: List[str] = field(default_factory=list)
    
    def is_revealed(self, revelation_id: str) -> bool:
        return revelation_id in self.revealed_ids
    
    def mark_revealed(self, revelation_id: str):
        if revelation_id not in self.revealed_ids:
            self.revealed_ids.append(revelation_id)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "revealed_ids": self.revealed_ids
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RevelationState":
        return cls(
            character_id=data["character_id"],
            revealed_ids=data.get("revealed_ids", [])
        )

class RevelationManager:
    """Manages character revelations across the game session."""
    
    def __init__(self):
        self.states: Dict[str, RevelationState] = {}
        self._initialize_states()
    
    def _initialize_states(self):
        """Initialize revelation states for all secondary characters."""
        for char_id in SECONDARY_CHARACTERS.keys():
            self.states[char_id] = RevelationState(character_id=char_id)
    
    def check_for_revelations(
        self, 
        npc_id: str, 
        context: Dict[str, Any]
    ) -> Optional[MicroRevelation]:
        """
        Check if any revelations should trigger for this NPC given the context.
        
        Args:
            npc_id: Character ID (e.g., "torres", "kai")
            context: Dict with keys like 'topic', 'trust_score', 'player_archetype'
        
        Returns:
            MicroRevelation if one should trigger, None otherwise
        """
        if npc_id not in self.states:
            return None
        
        # Check if a revelation should trigger
        revelation = check_micro_revelation(npc_id, context)
        
        if revelation and not self.is_revealed(npc_id, revelation.id):
            return revelation
        
        return None
    
    def trigger_revelation(
        self, 
        npc_id: str, 
        revelation_id: str
    ) -> bool:
        """
        Mark a revelation as revealed.
        
        Returns:
            True if successfully marked, False if already revealed or invalid
        """
        if npc_id not in self.states:
            return False
        
        if self.is_revealed(npc_id, revelation_id):
            return False
        
        self.states[npc_id].mark_revealed(revelation_id)
        return True
    
    def is_revealed(self, npc_id: str, revelation_id: str) -> bool:
        """Check if a specific revelation has been revealed."""
        if npc_id not in self.states:
            return False
        return self.states[npc_id].is_revealed(revelation_id)
    
    def get_unrevealed_count(self, npc_id: str) -> int:
        """Get the number of unrevealed revelations for a character."""
        char = SECONDARY_CHARACTERS.get(npc_id)
        if not char:
            return 0
        
        total = len(char.micro_revelations)
        revealed = len(self.states.get(npc_id, RevelationState(npc_id)).revealed_ids)
        return total - revealed
    
    def get_all_revelations(self, npc_id: str) -> List[Dict[str, Any]]:
        """Get all revelations for a character with their revealed status."""
        char = SECONDARY_CHARACTERS.get(npc_id)
        if not char:
            return []
        
        state = self.states.get(npc_id, RevelationState(npc_id))
        
        return [
            {
                "id": rev.id,
                "text": rev.revelation_text,
                "trigger": rev.trigger_condition,
                "is_revealed": state.is_revealed(rev.id)
            }
            for rev in char.micro_revelations
        ]
    
    def get_revealed_revelations(self, npc_id: str) -> List[Dict[str, Any]]:
        """Get only the revelations that have been revealed."""
        all_revs = self.get_all_revelations(npc_id)
        return [r for r in all_revs if r["is_revealed"]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for game state storage."""
        return {
            "states": {
                char_id: state.to_dict() 
                for char_id, state in self.states.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RevelationManager":
        """Deserialize from game state."""
        manager = cls()
        manager.states = {
            char_id: RevelationState.from_dict(state_data)
            for char_id, state_data in data.get("states", {}).items()
        }
        return manager
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of revelation progress across all characters."""
        summary = {}
        for char_id in SECONDARY_CHARACTERS.keys():
            char = SECONDARY_CHARACTERS[char_id]
            state = self.states.get(char_id, RevelationState(char_id))
            
            summary[char_id] = {
                "name": char.name,
                "total_revelations": len(char.micro_revelations),
                "revealed_count": len(state.revealed_ids),
                "unrevealed_count": len(char.micro_revelations) - len(state.revealed_ids)
            }
        
        return summary
