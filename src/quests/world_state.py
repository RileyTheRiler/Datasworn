"""
World State Management

Handles persistent world flags and quest consequence application.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional
import json
import yaml
from pathlib import Path


@dataclass
class WorldDelta:
    """Represents a localized world change triggered by a quest."""
    id: str
    trigger_flag: str
    changes: List[Dict[str, any]] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "trigger_flag": self.trigger_flag,
            "changes": self.changes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "WorldDelta":
        return cls(
            id=data["id"],
            trigger_flag=data.get("trigger_flag", ""),
            changes=data.get("changes", [])
        )


class WorldState:
    """
    Manages persistent world state flags and quest consequences.
    
    Tracks:
    - World flags (e.g., ruler_skellige, refugee_status_velem)
    - Applied world deltas
    - Ending conditions
    """
    
    def __init__(self):
        self.flags: Set[str] = set()
        self.applied_deltas: Set[str] = set()  # Delta IDs that have been applied
        self.metadata: Dict[str, any] = {}  # Additional state data
    
    def set_flag(self, flag: str):
        """Set a world state flag."""
        self.flags.add(flag)
    
    def unset_flag(self, flag: str):
        """Remove a world state flag."""
        self.flags.discard(flag)
    
    def has_flag(self, flag: str) -> bool:
        """Check if a flag is set."""
        return flag in self.flags
    
    def has_all_flags(self, flags: List[str]) -> bool:
        """Check if all specified flags are set."""
        return all(flag in self.flags for flag in flags)
    
    def has_any_flag(self, flags: List[str]) -> bool:
        """Check if any of the specified flags are set."""
        return any(flag in self.flags for flag in flags)
    
    def get_flags(self) -> List[str]:
        """Get all set flags."""
        return sorted(list(self.flags))
    
    def set_metadata(self, key: str, value: any):
        """Set metadata value."""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: any = None) -> any:
        """Get metadata value."""
        return self.metadata.get(key, default)
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "flags": list(self.flags),
            "applied_deltas": list(self.applied_deltas),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "WorldState":
        """Deserialize from dictionary."""
        state = cls()
        state.flags = set(data.get("flags", []))
        state.applied_deltas = set(data.get("applied_deltas", []))
        state.metadata = data.get("metadata", {})
        return state


class DeltaApplicator:
    """
    Applies world deltas when quest flags are set.
    
    Handles changes like:
    - Location descriptions
    - NPC availability
    - Shop inventories
    - Faction patrol routes
    """
    
    def __init__(self):
        self.deltas: Dict[str, WorldDelta] = {}
        self.world_state = WorldState()
    
    def load_deltas_from_yaml(self, delta_dir: str):
        """Load world deltas from YAML files."""
        delta_path = Path(delta_dir)
        if not delta_path.exists():
            return
        
        for yaml_file in delta_path.glob("*.yaml"):
            with open(yaml_file, 'r') as f:
                delta_data = yaml.safe_load(f)
                if delta_data:
                    delta = WorldDelta.from_dict(delta_data)
                    self.deltas[delta.id] = delta
    
    def add_delta(self, delta: WorldDelta):
        """Add a world delta."""
        self.deltas[delta.id] = delta
    
    def check_and_apply_deltas(self) -> List[WorldDelta]:
        """
        Check if any deltas should be applied based on current flags.
        
        Returns list of newly applied deltas.
        """
        newly_applied = []
        
        for delta_id, delta in self.deltas.items():
            # Skip if already applied
            if delta_id in self.world_state.applied_deltas:
                continue
            
            # Check if trigger flag is set
            if self.world_state.has_flag(delta.trigger_flag):
                self._apply_delta(delta)
                self.world_state.applied_deltas.add(delta_id)
                newly_applied.append(delta)
        
        return newly_applied
    
    def _apply_delta(self, delta: WorldDelta):
        """Apply a world delta's changes."""
        # This is where you would actually modify game state
        # For now, we just track that it was applied
        # In a full implementation, this would:
        # - Update location descriptions
        # - Change NPC availability
        # - Modify shop inventories
        # - Update faction patrol routes
        # etc.
        pass
    
    def get_delta_changes(self, delta_id: str) -> Optional[List[Dict[str, any]]]:
        """Get the changes associated with a delta."""
        if delta_id in self.deltas:
            return self.deltas[delta_id].changes
        return None
    
    def is_delta_applied(self, delta_id: str) -> bool:
        """Check if a delta has been applied."""
        return delta_id in self.world_state.applied_deltas
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "deltas": {did: delta.to_dict() for did, delta in self.deltas.items()},
            "world_state": self.world_state.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "DeltaApplicator":
        """Deserialize from dictionary."""
        applicator = cls()
        
        for did, delta_data in data.get("deltas", {}).items():
            applicator.deltas[did] = WorldDelta.from_dict(delta_data)
        
        if "world_state" in data:
            applicator.world_state = WorldState.from_dict(data["world_state"])
        
        return applicator


class EndingEvaluator:
    """
    Evaluates ending conditions based on world state flags.
    """
    
    def __init__(self):
        self.ending_conditions: Dict[str, Dict[str, any]] = {}
    
    def add_ending(self, ending_id: str, required_flags: List[str], 
                   forbidden_flags: List[str] = None, 
                   description: str = ""):
        """
        Add an ending condition.
        
        Args:
            ending_id: Unique ending identifier
            required_flags: Flags that must be set
            forbidden_flags: Flags that must NOT be set
            description: Ending description
        """
        self.ending_conditions[ending_id] = {
            "required_flags": required_flags,
            "forbidden_flags": forbidden_flags or [],
            "description": description
        }
    
    def evaluate_endings(self, world_state: WorldState) -> List[str]:
        """
        Evaluate which endings are possible given current world state.
        
        Returns list of ending IDs that match current flags.
        """
        possible_endings = []
        
        for ending_id, conditions in self.ending_conditions.items():
            # Check required flags
            if not world_state.has_all_flags(conditions["required_flags"]):
                continue
            
            # Check forbidden flags
            if world_state.has_any_flag(conditions["forbidden_flags"]):
                continue
            
            possible_endings.append(ending_id)
        
        return possible_endings
    
    def get_ending_description(self, ending_id: str) -> Optional[str]:
        """Get description for an ending."""
        if ending_id in self.ending_conditions:
            return self.ending_conditions[ending_id]["description"]
        return None
