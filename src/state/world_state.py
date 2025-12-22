"""
World State Management System

Manages consequence flags with scoped storage (global, region, faction, character),
supports typed values (bool, enum, numeric, timestamps), and handles long-tail triggers
for delayed narrative events.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from enum import Enum
import time


class FlagScope(Enum):
    """Scope levels for consequence flags."""
    GLOBAL = "global"
    REGION = "region"
    FACTION = "faction"
    CHARACTER = "character"


@dataclass
class ConsequenceFlag:
    """A single consequence flag with typed value."""
    scope: str  # e.g., "global", "region.forge", "faction.helix", "character.torres"
    key: str
    value: Any
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> dict:
        return {
            "scope": self.scope,
            "key": self.key,
            "value": self.value,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ConsequenceFlag":
        return cls(
            scope=data["scope"],
            key=data["key"],
            value=data["value"],
            timestamp=data.get("timestamp", time.time())
        )


@dataclass
class ScheduledTrigger:
    """A delayed event triggered when conditions are met."""
    trigger_id: str
    flag_condition: str  # e.g., "global.investigation_started == True"
    delay_scenes: int
    scheduled_scene: int  # When it should trigger
    event_data: dict
    triggered: bool = False
    
    def to_dict(self) -> dict:
        return {
            "trigger_id": self.trigger_id,
            "flag_condition": self.flag_condition,
            "delay_scenes": self.delay_scenes,
            "scheduled_scene": self.scheduled_scene,
            "event_data": self.event_data,
            "triggered": self.triggered
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ScheduledTrigger":
        return cls(
            trigger_id=data["trigger_id"],
            flag_condition=data["flag_condition"],
            delay_scenes=data["delay_scenes"],
            scheduled_scene=data["scheduled_scene"],
            event_data=data["event_data"],
            triggered=data.get("triggered", False)
        )


class WorldState:
    """
    Manages world state with scoped consequence flags and long-tail triggers.
    
    Scopes:
    - global: Affects entire game world
    - region.<name>: Affects specific region
    - faction.<name>: Affects specific faction
    - character.<id>: Affects specific character
    """
    
    def __init__(self):
        self.flags: Dict[str, ConsequenceFlag] = {}
        self.triggers: Dict[str, ScheduledTrigger] = {}
        self.current_scene: int = 0
        self.change_log: List[dict] = []  # Recent changes for UI updates
    
    def _make_flag_key(self, scope: str, key: str) -> str:
        """Create full flag key from scope and key."""
        return f"{scope}.{key}"
    
    def set_flag(self, scope: str, key: str, value: Any, log: bool = True) -> None:
        """
        Set a consequence flag.
        
        Args:
            scope: Scope string (e.g., "global", "region.forge", "character.torres")
            key: Flag key
            value: Flag value (bool, str, int, float)
            log: Whether to add to change log
        """
        flag_key = self._make_flag_key(scope, key)
        
        # Handle numeric modifiers (e.g., "+0.2", "-1")
        if isinstance(value, str) and value.startswith(('+', '-')):
            old_value = self.get_flag(scope, key, default=0)
            if isinstance(old_value, (int, float)):
                value = old_value + float(value)
        
        flag = ConsequenceFlag(scope=scope, key=key, value=value)
        self.flags[flag_key] = flag
        
        if log:
            self.change_log.append({
                "scene": self.current_scene,
                "scope": scope,
                "key": key,
                "value": value,
                "timestamp": flag.timestamp
            })
            # Keep only last 50 changes
            if len(self.change_log) > 50:
                self.change_log = self.change_log[-50:]
    
    def get_flag(self, scope: str, key: str, default: Any = None) -> Any:
        """Get a consequence flag value."""
        flag_key = self._make_flag_key(scope, key)
        flag = self.flags.get(flag_key)
        return flag.value if flag else default
    
    def has_flag(self, scope: str, key: str) -> bool:
        """Check if a flag exists."""
        flag_key = self._make_flag_key(scope, key)
        return flag_key in self.flags
    
    def get_flags_by_scope(self, scope_prefix: str) -> Dict[str, Any]:
        """Get all flags matching a scope prefix."""
        result = {}
        for flag_key, flag in self.flags.items():
            if flag.scope.startswith(scope_prefix):
                result[flag.key] = flag.value
        return result
    
    def schedule_trigger(self, trigger_id: str, flag_condition: str, 
                        delay_scenes: int, event_data: dict) -> None:
        """
        Schedule a delayed event trigger.
        
        Args:
            trigger_id: Unique trigger identifier
            flag_condition: Condition to check (e.g., "global.rescued_villager == True")
            delay_scenes: Number of scenes to delay
            event_data: Event data to return when triggered
        """
        trigger = ScheduledTrigger(
            trigger_id=trigger_id,
            flag_condition=flag_condition,
            delay_scenes=delay_scenes,
            scheduled_scene=self.current_scene + delay_scenes,
            event_data=event_data
        )
        self.triggers[trigger_id] = trigger
    
    def check_triggers(self, current_scene: int) -> List[dict]:
        """
        Check for triggers that should fire this scene.
        
        Returns:
            List of event_data dicts for triggered events
        """
        self.current_scene = current_scene
        triggered_events = []
        
        for trigger in self.triggers.values():
            if trigger.triggered:
                continue
            
            # Check if scene has arrived
            if current_scene < trigger.scheduled_scene:
                continue
            
            # Evaluate condition
            if self._evaluate_condition(trigger.flag_condition):
                trigger.triggered = True
                triggered_events.append(trigger.event_data)
        
        return triggered_events
    
    def _evaluate_condition(self, condition: str) -> bool:
        """
        Evaluate a flag condition.
        
        Simple evaluation supporting:
        - "scope.key == value"
        - "scope.key != value"
        - "scope.key > value"
        - "scope.key < value"
        """
        try:
            # Parse condition
            for op in ['==', '!=', '>=', '<=', '>', '<']:
                if op in condition:
                    left, right = condition.split(op, 1)
                    left = left.strip()
                    right = right.strip()
                    
                    # Parse left side (scope.key)
                    if '.' in left:
                        scope, key = left.rsplit('.', 1)
                        flag_value = self.get_flag(scope, key)
                    else:
                        return False
                    
                    # Parse right side (value)
                    if right.lower() == 'true':
                        right_value = True
                    elif right.lower() == 'false':
                        right_value = False
                    elif right.lower() == 'none':
                        right_value = None
                    else:
                        try:
                            right_value = float(right) if '.' in right else int(right)
                        except ValueError:
                            right_value = right.strip('"\'')
                    
                    # Evaluate
                    if op == '==':
                        return flag_value == right_value
                    elif op == '!=':
                        return flag_value != right_value
                    elif op == '>':
                        return flag_value > right_value
                    elif op == '<':
                        return flag_value < right_value
                    elif op == '>=':
                        return flag_value >= right_value
                    elif op == '<=':
                        return flag_value <= right_value
            
            return False
        except Exception:
            return False
    
    def snapshot(self) -> dict:
        """
        Create a snapshot of current world state.
        
        Returns:
            Dict with flags, triggers, and recent changes
        """
        return {
            "current_scene": self.current_scene,
            "flags": {k: v.to_dict() for k, v in self.flags.items()},
            "triggers": {k: v.to_dict() for k, v in self.triggers.items()},
            "recent_changes": self.change_log[-10:]  # Last 10 changes
        }
    
    def to_dict(self) -> dict:
        """Serialize to dict for persistence."""
        return {
            "current_scene": self.current_scene,
            "flags": {k: v.to_dict() for k, v in self.flags.items()},
            "triggers": {k: v.to_dict() for k, v in self.triggers.items()},
            "change_log": self.change_log
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "WorldState":
        """Deserialize from dict."""
        state = cls()
        state.current_scene = data.get("current_scene", 0)
        state.change_log = data.get("change_log", [])
        
        for k, v in data.get("flags", {}).items():
            state.flags[k] = ConsequenceFlag.from_dict(v)
        
        for k, v in data.get("triggers", {}).items():
            state.triggers[k] = ScheduledTrigger.from_dict(v)
        
        return state
