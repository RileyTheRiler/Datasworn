"""
Event Dispatcher - Pub/sub system for world events.
Allows systems to publish events and subscribers to react to them.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Callable, Any, Optional
from enum import Enum
import time


class EventType(Enum):
    """Types of world events."""
    # Traffic events
    TRAFFIC_SPAWN = "traffic_spawn"
    TRAFFIC_CONGESTION = "traffic_congestion"
    PATROL_SPAWN = "patrol_spawn"
    PATROL_SCAN = "patrol_scan"
    
    # Law events
    CRIME_COMMITTED = "crime_committed"
    SUSPICION_CLEARED = "suspicion_cleared"
    INVESTIGATION_STARTED = "investigation_started"
    INVESTIGATION_CONCLUDED = "investigation_concluded"
    PURSUIT_INITIATED = "pursuit_initiated"
    PURSUIT_ABANDONED = "pursuit_abandoned"
    PURSUIT_ESCALATED = "pursuit_escalated"
    BLOCKADE_INITIATED = "blockade_initiated"
    BOUNTY_POSTED = "bounty_posted"
    BOUNTY_EXPIRED = "bounty_expired"
    
    # Wildlife events
    WILDLIFE_SPAWN = "wildlife_spawn"
    WILDLIFE_MIGRATION = "wildlife_migration"
    PREDATOR_STALKING = "predator_stalking"
    PREDATOR_KILL = "predator_kill"
    PREY_ESCAPE = "prey_escape"
    BEHAVIOR_CHANGE = "behavior_change"
    
    # Weather events
    WEATHER_CHANGE = "weather_change"
    WEATHER_HAZARD = "weather_hazard"
    HAZARD_ENDED = "hazard_ended"
    
    # Cross-system events
    DISTRESS_SIGNAL = "distress_signal"
    NPC_WITNESSED = "npc_witnessed"
    PLAYER_LOCATION = "player_location"
    
    # Faction events
    FACTION_UPDATE = "faction_update"
    FACTION_WAR = "faction_war"


@dataclass
class WorldEvent:
    """A world event that can be published and subscribed to."""
    event_type: EventType
    data: Dict[str, Any]
    timestamp: float
    event_id: str


class WorldEventDispatcher:
    """Central event dispatcher for world simulation."""
    
    def __init__(self, max_history: int = 100):
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[WorldEvent] = []
        self.max_history = max_history
        self._event_counter = 0
    
    def subscribe(self, event_type: EventType, callback: Callable[[WorldEvent], None]):
        """
        Subscribe to an event type.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Function to call when event is published
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """Unsubscribe from an event type."""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(callback)
    
    def publish(self, event_type: EventType, data: Dict[str, Any]) -> WorldEvent:
        """
        Publish an event to all subscribers.
        
        Args:
            event_type: Type of event
            data: Event data
            
        Returns:
            The published event
        """
        self._event_counter += 1
        
        event = WorldEvent(
            event_type=event_type,
            data=data,
            timestamp=time.time(),
            event_id=f"evt_{self._event_counter}"
        )
        
        # Add to history
        self.event_history.append(event)
        
        # Trim history if too long
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
        
        # Notify subscribers
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event subscriber: {e}")
        
        return event
    
    def publish_batch(self, events: List[Dict[str, Any]]) -> List[WorldEvent]:
        """
        Publish multiple events at once.
        
        Args:
            events: List of event dicts with 'type' and 'data' keys
            
        Returns:
            List of published events
        """
        published = []
        for event_data in events:
            event_type_str = event_data.get('type')
            if event_type_str:
                # Try to convert string to EventType
                try:
                    event_type = EventType(event_type_str)
                    event = self.publish(event_type, event_data)
                    published.append(event)
                except ValueError:
                    # Unknown event type, skip
                    pass
        return published
    
    def get_recent_events(self, count: int = 10, event_type: Optional[EventType] = None) -> List[WorldEvent]:
        """
        Get recent events.
        
        Args:
            count: Number of events to retrieve
            event_type: Optional filter by event type
            
        Returns:
            List of recent events
        """
        if event_type:
            filtered = [e for e in self.event_history if e.event_type == event_type]
            return filtered[-count:]
        return self.event_history[-count:]
    
    def clear_history(self):
        """Clear event history."""
        self.event_history = []
    
    def to_dict(self) -> Dict:
        """Serialize state."""
        return {
            "event_history": [
                {
                    "event_type": e.event_type.value,
                    "data": e.data,
                    "timestamp": e.timestamp,
                    "event_id": e.event_id
                }
                for e in self.event_history
            ],
            "event_counter": self._event_counter
        }
    
    @classmethod
    def from_dict(cls, data: Dict, max_history: int = 100) -> WorldEventDispatcher:
        """Deserialize state."""
        dispatcher = cls(max_history)
        dispatcher._event_counter = data.get("event_counter", 0)
        
        # Restore event history
        for event_data in data.get("event_history", []):
            event = WorldEvent(
                event_type=EventType(event_data["event_type"]),
                data=event_data["data"],
                timestamp=event_data["timestamp"],
                event_id=event_data["event_id"]
            )
            dispatcher.event_history.append(event)
        
        return dispatcher
