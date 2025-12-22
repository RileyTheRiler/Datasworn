"""
Cognitive Engine Schemas for Starforged AI Game Master.
Defines the core data structures for NPC memory, relationships, and cognitive state.
# Forced recompile
"""

from __future__ import annotations
from typing import List, Dict, Optional, Literal, Any, TypedDict
from pydantic import BaseModel, Field
import uuid
import json

# ============================================================================
# Memory System
# ============================================================================

class MemoryObject(BaseModel):
    """
    Represents a single unit of memory (observation, reflection, etc).
    Aligned with 'events' and 'npc_knowledge' tables.
    """
    memory_id: Optional[int] = None  # DB ID
    event_id: Optional[int] = None   # Source Event ID
    timestamp: str = "Unknown"
    content: str
    importance_score: int = 1        # 1-10
    type: str = "observation"        # observation, reflection, dialogue, action
    embedding: Optional[List[float]] = None
    keywords: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Helper for legacy or new code expecting 'related_memory_ids'
    related_memory_ids: List[str] = Field(default_factory=list)

    def to_text_context(self) -> str:
        """Format for LLM injection."""
        return f"[{self.timestamp}] ({self.type.upper()}) {self.content}"

# ============================================================================
# Planning System
# ============================================================================

class ScheduleEntry(BaseModel):
    time: str
    activity: str
    location: str
    status: str = "pending"  # pending, active, completed, cancelled, interrupted

class DailyPlan(BaseModel):
    date: str
    entries: List[ScheduleEntry]
    current_entry_index: int = 0
    goal: str = "Survive another day."

# ============================================================================
# Disposition & Profile
# ============================================================================

class PersonalityProfile(BaseModel):
    name: str
    role: str
    traits: List[str]
    current_mood: str = "Neutral"
    motivation: str = "Survival"
    fears: List[str] = Field(default_factory=list)
    narrative_seed: str = "" # Added to support Engine usage

class RelationshipState(BaseModel):
    target_id: str
    trust: float = 0.0          # -1.0 to 1.0
    intimacy: float = 0.0       # 0.0 to 1.0
    dynamic_label: str = "Stranger"
    last_interaction: str = "Never"
    
    def get_semantic_descriptor(self) -> str:
        """Translate valid metrics into naturally language."""
        if self.trust < 0.2: return "Hostile"
        if self.trust > 0.8: return "Ally"
        return "Neutral"

# ============================================================================
# Input / Output
# ============================================================================

class CognitiveState(BaseModel):
    """Runtime state bundle for the Engine."""
    npc_id: str
    profile: PersonalityProfile
    memories: List[MemoryObject] = Field(default_factory=list) # Working memory (retrieved)
    relationships: Dict[str, RelationshipState] = Field(default_factory=dict)
    current_plan: Optional[DailyPlan] = None
    last_reflection_time: str = ""
    
    # World Simulation Integration - Crime Memory
    witnessed_crimes: List[Dict[str, Any]] = Field(default_factory=list)
    disturbance_memory: List[Dict[str, Any]] = Field(default_factory=list)
    memory_decay_rate: float = 0.1  # per hour
    
    def decay_memories(self, time_passed: float):
        """Decay crime and disturbance memories over time."""
        # Decay witnessed crimes
        for crime in self.witnessed_crimes:
            crime['decay_progress'] = crime.get('decay_progress', 0.0) + (self.memory_decay_rate * time_passed)
        
        # Remove fully decayed crimes
        self.witnessed_crimes = [c for c in self.witnessed_crimes if c.get('decay_progress', 0.0) < 1.0]
        
        # Decay disturbances
        for disturbance in self.disturbance_memory:
            disturbance['decay_progress'] = disturbance.get('decay_progress', 0.0) + (self.memory_decay_rate * time_passed)
        
        # Remove fully decayed disturbances
        self.disturbance_memory = [d for d in self.disturbance_memory if d.get('decay_progress', 0.0) < 1.0]
    
    def clear_memories_by_disguise(self):
        """Clear memories when player uses disguise."""
        self.witnessed_crimes = []
        self.disturbance_memory = []
    
    def clear_memories_by_bribe(self, amount: float):
        """Clear memories based on bribe amount (0.0-1.0)."""
        # Higher bribe = more memories cleared
        clear_threshold = amount
        
        self.witnessed_crimes = [
            c for c in self.witnessed_crimes 
            if c.get('severity', 1) > (clear_threshold * 5)
        ]
        
        self.disturbance_memory = [
            d for d in self.disturbance_memory
            if d.get('severity', 1) > (clear_threshold * 5)
        ]

class NPCOutput(TypedDict):
    """Structured output from the engine."""
    narrative: str
    state_updates: Dict[str, Any]
