"""
NPC Memory State System

Short-lived memory tokens for recent interactions with decay timers.
Feeds into dialogue selection and behavior modification.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime, timedelta


class MemoryTokenType(Enum):
    """Types of short-term memories"""
    GREETED_KINDLY = "greeted_kindly"
    THREATENED = "threatened"
    WITNESSED_CRIME = "witnessed_crime"
    WITNESSED_RESCUE = "witnessed_rescue"
    RESCUED_BY_PLAYER = "rescued_by_player"
    RECEIVED_BRIBE = "received_bribe"
    RECEIVED_GIFT = "received_gift"
    INSULTED = "insulted"
    COMPLIMENTED = "complimented"
    HELPED = "helped"
    ATTACKED = "attacked"
    TRADED_WITH = "traded_with"
    LIED_TO = "lied_to"
    TOLD_TRUTH = "told_truth"


@dataclass
class MemoryToken:
    """A single memory token with decay"""
    token_type: MemoryTokenType
    context: str
    created_at: datetime
    duration: int  # minutes until decay
    intensity: float = 1.0  # 0.0-1.0, affects dialogue weight
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self, current_time: datetime) -> bool:
        """Check if memory has decayed"""
        elapsed = (current_time - self.created_at).total_seconds() / 60
        return elapsed >= self.duration
    
    def get_age(self, current_time: datetime) -> float:
        """Get age of memory in minutes"""
        return (current_time - self.created_at).total_seconds() / 60
    
    def get_decay_factor(self, current_time: datetime) -> float:
        """Get decay factor (1.0 = fresh, 0.0 = expired)"""
        age = self.get_age(current_time)
        if age >= self.duration:
            return 0.0
        return 1.0 - (age / self.duration)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.token_type.value,
            "context": self.context,
            "age_minutes": (datetime.now() - self.created_at).total_seconds() / 60,
            "intensity": self.intensity,
            "metadata": self.metadata,
        }


@dataclass
class NPCMemoryState:
    """
    Collection of memory tokens for an NPC.
    
    Manages short-term interaction history with automatic decay.
    """
    npc_id: str
    tokens: List[MemoryToken] = field(default_factory=list)
    max_tokens: int = 20  # Maximum number of tokens to keep
    
    def add_memory(
        self,
        token_type: MemoryTokenType,
        context: str,
        duration: int = 60,  # Default 1 hour
        intensity: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
        current_time: Optional[datetime] = None
    ) -> MemoryToken:
        """
        Add a new memory token.
        
        Args:
            token_type: Type of memory
            context: Description of what happened
            duration: Duration in minutes before decay
            intensity: Strength of memory (0.0-1.0)
            metadata: Additional data
            current_time: Current game time
        
        Returns:
            The created MemoryToken
        """
        current_time = current_time or datetime.now()
        
        token = MemoryToken(
            token_type=token_type,
            context=context,
            created_at=current_time,
            duration=duration,
            intensity=intensity,
            metadata=metadata or {},
        )
        
        self.tokens.append(token)
        
        # Trim if over limit
        if len(self.tokens) > self.max_tokens:
            # Remove oldest tokens
            self.tokens = sorted(self.tokens, key=lambda t: t.created_at, reverse=True)
            self.tokens = self.tokens[:self.max_tokens]
        
        return token
    
    def has_memory(
        self,
        token_type: MemoryTokenType,
        current_time: Optional[datetime] = None,
        max_age: Optional[int] = None
    ) -> bool:
        """
        Check if NPC has a specific type of memory.
        
        Args:
            token_type: Type of memory to check for
            current_time: Current game time
            max_age: Maximum age in minutes (None = any age)
        
        Returns:
            True if memory exists and is not expired
        """
        current_time = current_time or datetime.now()
        
        for token in self.tokens:
            if token.token_type == token_type:
                if not token.is_expired(current_time):
                    if max_age is None or token.get_age(current_time) <= max_age:
                        return True
        
        return False
    
    def get_memories(
        self,
        token_type: Optional[MemoryTokenType] = None,
        current_time: Optional[datetime] = None,
        include_expired: bool = False
    ) -> List[MemoryToken]:
        """
        Get memories, optionally filtered by type.
        
        Args:
            token_type: Filter by type (None = all types)
            current_time: Current game time
            include_expired: Include expired memories
        
        Returns:
            List of matching memory tokens
        """
        current_time = current_time or datetime.now()
        
        results = []
        for token in self.tokens:
            # Type filter
            if token_type and token.token_type != token_type:
                continue
            
            # Expiration filter
            if not include_expired and token.is_expired(current_time):
                continue
            
            results.append(token)
        
        return results
    
    def get_most_recent(
        self,
        token_type: MemoryTokenType,
        current_time: Optional[datetime] = None
    ) -> Optional[MemoryToken]:
        """Get the most recent memory of a specific type"""
        memories = self.get_memories(token_type, current_time)
        if not memories:
            return None
        return max(memories, key=lambda t: t.created_at)
    
    def decay(
        self,
        time_delta: int,
        current_time: Optional[datetime] = None
    ) -> int:
        """
        Age and remove expired memories.
        
        Args:
            time_delta: Time passed in minutes
            current_time: Current game time
        
        Returns:
            Number of memories removed
        """
        current_time = current_time or datetime.now()
        
        initial_count = len(self.tokens)
        self.tokens = [
            token for token in self.tokens
            if not token.is_expired(current_time)
        ]
        
        return initial_count - len(self.tokens)
    
    def get_dialogue_modifiers(
        self,
        current_time: Optional[datetime] = None
    ) -> Dict[str, float]:
        """
        Get dialogue weight modifiers based on active memories.
        
        Returns:
            Dictionary of modifier keys and their weights
        """
        current_time = current_time or datetime.now()
        modifiers = {}
        
        # Check for each memory type and calculate weight
        for token in self.tokens:
            if token.is_expired(current_time):
                continue
            
            decay_factor = token.get_decay_factor(current_time)
            weight = token.intensity * decay_factor
            
            # Map token types to dialogue modifiers
            modifier_key = f"memory_{token.token_type.value}"
            modifiers[modifier_key] = max(modifiers.get(modifier_key, 0.0), weight)
        
        return modifiers
    
    def get_behavior_state(
        self,
        current_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get NPC behavioral state based on memories.
        
        Returns:
            Dictionary with behavioral flags and values
        """
        current_time = current_time or datetime.now()
        
        state = {
            "fearful": False,
            "hostile": False,
            "friendly": False,
            "grateful": False,
            "suspicious": False,
            "traumatized": False,
        }
        
        # Analyze memories to set behavioral flags
        for token in self.tokens:
            if token.is_expired(current_time):
                continue
            
            decay_factor = token.get_decay_factor(current_time)
            if decay_factor < 0.3:  # Too faded to affect behavior
                continue
            
            # Map memories to behaviors
            if token.token_type == MemoryTokenType.THREATENED:
                state["fearful"] = True
                state["hostile"] = True
            elif token.token_type == MemoryTokenType.WITNESSED_CRIME:
                state["fearful"] = True
                state["suspicious"] = True
                if token.metadata.get("crime_type") == "murder":
                    state["traumatized"] = True
            elif token.token_type == MemoryTokenType.RESCUED_BY_PLAYER:
                state["grateful"] = True
                state["friendly"] = True
            elif token.token_type == MemoryTokenType.GREETED_KINDLY:
                state["friendly"] = True
            elif token.token_type == MemoryTokenType.ATTACKED:
                state["hostile"] = True
                state["fearful"] = True
            elif token.token_type == MemoryTokenType.RECEIVED_BRIBE:
                state["suspicious"] = True
        
        return state
    
    def clear_type(
        self,
        token_type: MemoryTokenType
    ) -> int:
        """
        Clear all memories of a specific type.
        
        Args:
            token_type: Type to clear
        
        Returns:
            Number of memories removed
        """
        initial_count = len(self.tokens)
        self.tokens = [
            token for token in self.tokens
            if token.token_type != token_type
        ]
        return initial_count - len(self.tokens)
    
    def clear_all(self) -> int:
        """Clear all memories"""
        count = len(self.tokens)
        self.tokens = []
        return count
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "npc_id": self.npc_id,
            "token_count": len(self.tokens),
            "tokens": [token.to_dict() for token in self.tokens],
            "dialogue_modifiers": self.get_dialogue_modifiers(),
            "behavior_state": self.get_behavior_state(),
        }


# Preset durations for common memory types
DEFAULT_DURATIONS = {
    MemoryTokenType.GREETED_KINDLY: 30,  # 30 minutes
    MemoryTokenType.THREATENED: 120,  # 2 hours
    MemoryTokenType.WITNESSED_CRIME: 360,  # 6 hours
    MemoryTokenType.WITNESSED_RESCUE: 480,  # 8 hours
    MemoryTokenType.RESCUED_BY_PLAYER: 720,  # 12 hours
    MemoryTokenType.RECEIVED_BRIBE: 180,  # 3 hours
    MemoryTokenType.RECEIVED_GIFT: 240,  # 4 hours
    MemoryTokenType.INSULTED: 180,  # 3 hours
    MemoryTokenType.COMPLIMENTED: 120,  # 2 hours
    MemoryTokenType.HELPED: 240,  # 4 hours
    MemoryTokenType.ATTACKED: 360,  # 6 hours
    MemoryTokenType.TRADED_WITH: 60,  # 1 hour
    MemoryTokenType.LIED_TO: 240,  # 4 hours
    MemoryTokenType.TOLD_TRUTH: 180,  # 3 hours
}


def get_default_duration(token_type: MemoryTokenType) -> int:
    """Get the default duration for a memory type"""
    return DEFAULT_DURATIONS.get(token_type, 60)
