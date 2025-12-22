"""
Quest State Management

Tracks quest states and manages state transitions for the threaded quest system.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Optional, Set
import json


class QuestState(Enum):
    """Quest state machine states."""
    LOCKED = "locked"              # Prerequisites not met
    AVAILABLE = "available"        # Can be started
    IN_PROGRESS = "in_progress"    # Currently active
    PAUSED = "paused"              # Temporarily suspended
    COMPLETED = "completed"        # Successfully finished
    FAILED = "failed"              # Permanently failed
    ALTERNATE = "alternate"        # Completed via alternate path
    EXPIRED = "expired"            # Missed due to phase transition


@dataclass
class QuestStateEntry:
    """State information for a single quest."""
    quest_id: str
    state: QuestState
    started_scene: Optional[int] = None
    completed_scene: Optional[int] = None
    failure_reason: str = ""
    alternate_path: str = ""
    
    def to_dict(self) -> dict:
        return {
            "quest_id": self.quest_id,
            "state": self.state.value,
            "started_scene": self.started_scene,
            "completed_scene": self.completed_scene,
            "failure_reason": self.failure_reason,
            "alternate_path": self.alternate_path
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "QuestStateEntry":
        return cls(
            quest_id=data["quest_id"],
            state=QuestState(data["state"]),
            started_scene=data.get("started_scene"),
            completed_scene=data.get("completed_scene"),
            failure_reason=data.get("failure_reason", ""),
            alternate_path=data.get("alternate_path", "")
        )


class QuestStateManager:
    """
    Manages quest states and transitions.
    
    Validates state transitions and tracks quest lifecycle.
    """
    
    def __init__(self):
        self.states: Dict[str, QuestStateEntry] = {}
        self.current_scene: int = 0
        self.current_phase: int = 1
    
    def initialize_quest(self, quest_id: str, initial_state: QuestState = QuestState.LOCKED):
        """Initialize a quest with a starting state."""
        if quest_id not in self.states:
            self.states[quest_id] = QuestStateEntry(
                quest_id=quest_id,
                state=initial_state
            )
    
    def get_state(self, quest_id: str) -> Optional[QuestState]:
        """Get the current state of a quest."""
        if quest_id in self.states:
            return self.states[quest_id].state
        return None
    
    def can_transition(self, quest_id: str, new_state: QuestState) -> bool:
        """Check if a state transition is valid."""
        if quest_id not in self.states:
            return False
        
        current = self.states[quest_id].state
        
        # Define valid transitions
        valid_transitions = {
            QuestState.LOCKED: {QuestState.AVAILABLE, QuestState.EXPIRED},
            QuestState.AVAILABLE: {QuestState.IN_PROGRESS, QuestState.EXPIRED},
            QuestState.IN_PROGRESS: {QuestState.PAUSED, QuestState.COMPLETED, 
                                     QuestState.FAILED, QuestState.ALTERNATE},
            QuestState.PAUSED: {QuestState.IN_PROGRESS, QuestState.FAILED, QuestState.EXPIRED},
            QuestState.COMPLETED: set(),  # Terminal state
            QuestState.FAILED: set(),     # Terminal state
            QuestState.ALTERNATE: set(),  # Terminal state
            QuestState.EXPIRED: set()     # Terminal state
        }
        
        return new_state in valid_transitions.get(current, set())
    
    def transition(self, quest_id: str, new_state: QuestState, 
                   reason: str = "", alternate_path: str = "") -> bool:
        """Transition a quest to a new state."""
        if not self.can_transition(quest_id, new_state):
            return False
        
        entry = self.states[quest_id]
        entry.state = new_state
        
        # Track scene numbers for lifecycle events
        if new_state == QuestState.IN_PROGRESS and entry.started_scene is None:
            entry.started_scene = self.current_scene
        elif new_state in {QuestState.COMPLETED, QuestState.FAILED, 
                           QuestState.ALTERNATE, QuestState.EXPIRED}:
            entry.completed_scene = self.current_scene
        
        if new_state == QuestState.FAILED:
            entry.failure_reason = reason
        elif new_state == QuestState.ALTERNATE:
            entry.alternate_path = alternate_path
        
        return True
    
    def start_quest(self, quest_id: str) -> bool:
        """Start a quest (AVAILABLE → IN_PROGRESS)."""
        return self.transition(quest_id, QuestState.IN_PROGRESS)
    
    def complete_quest(self, quest_id: str, alternate: bool = False, 
                       alternate_path: str = "") -> bool:
        """Complete a quest."""
        if alternate:
            return self.transition(quest_id, QuestState.ALTERNATE, 
                                 alternate_path=alternate_path)
        return self.transition(quest_id, QuestState.COMPLETED)
    
    def fail_quest(self, quest_id: str, reason: str = "") -> bool:
        """Fail a quest."""
        return self.transition(quest_id, QuestState.FAILED, reason=reason)
    
    def unlock_quest(self, quest_id: str) -> bool:
        """Unlock a quest (LOCKED → AVAILABLE)."""
        return self.transition(quest_id, QuestState.AVAILABLE)
    
    def expire_quest(self, quest_id: str) -> bool:
        """Expire a quest due to phase transition."""
        return self.transition(quest_id, QuestState.EXPIRED)
    
    def get_quests_by_state(self, state: QuestState) -> Set[str]:
        """Get all quest IDs in a specific state."""
        return {qid for qid, entry in self.states.items() if entry.state == state}
    
    def get_active_quests(self) -> Set[str]:
        """Get all active (in-progress) quest IDs."""
        return self.get_quests_by_state(QuestState.IN_PROGRESS)
    
    def get_available_quests(self) -> Set[str]:
        """Get all available quest IDs."""
        return self.get_quests_by_state(QuestState.AVAILABLE)
    
    def get_completed_quests(self) -> Set[str]:
        """Get all completed quest IDs (including alternates)."""
        completed = self.get_quests_by_state(QuestState.COMPLETED)
        alternate = self.get_quests_by_state(QuestState.ALTERNATE)
        return completed | alternate
    
    def expire_phase_quests(self, quest_ids: Set[str]):
        """Expire quests that are no longer available in the current phase."""
        for qid in quest_ids:
            if qid in self.states:
                current_state = self.states[qid].state
                if current_state in {QuestState.AVAILABLE, QuestState.PAUSED}:
                    self.expire_quest(qid)
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "states": {qid: entry.to_dict() for qid, entry in self.states.items()},
            "current_scene": self.current_scene,
            "current_phase": self.current_phase
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "QuestStateManager":
        """Deserialize from dictionary."""
        manager = cls()
        manager.current_scene = data.get("current_scene", 0)
        manager.current_phase = data.get("current_phase", 1)
        
        for qid, entry_data in data.get("states", {}).items():
            manager.states[qid] = QuestStateEntry.from_dict(entry_data)
        
        return manager
    
    def save_to_file(self, filepath: str):
        """Save state to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load_from_file(cls, filepath: str) -> "QuestStateManager":
        """Load state from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)
