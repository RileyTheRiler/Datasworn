"""
World Memory System

Area-level rumor cache for witnessed events (crimes, heroics).
Manages decay and cleanup with chapter/time-skip resets.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from enum import Enum


class EventType(Enum):
    """Types of events tracked in world memory"""
    CRIME_MURDER = "crime_murder"
    CRIME_THEFT = "crime_theft"
    CRIME_ASSAULT = "crime_assault"
    HEROIC_RESCUE = "heroic_rescue"
    HEROIC_DEFENSE = "heroic_defense"
    FACTION_CONFLICT = "faction_conflict"
    SUPERNATURAL_SIGHTING = "supernatural_sighting"
    DISASTER = "disaster"


@dataclass
class WorldEvent:
    """A single event in world memory"""
    event_id: str
    event_type: EventType
    area_id: str
    description: str
    actor: Optional[str] = None  # Who did it (player, NPC, etc.)
    witnesses: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    severity: float = 0.5  # 0.0-1.0
    decay_rate: float = 0.1  # How fast this fades
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_age(self, current_time: datetime) -> float:
        """Get age of event in minutes"""
        return (current_time - self.timestamp).total_seconds() / 60
    
    def get_decay_factor(self, current_time: datetime) -> float:
        """Get decay factor (1.0 = fresh, 0.0 = forgotten)"""
        age_hours = self.get_age(current_time) / 60
        decay = age_hours * self.decay_rate
        return max(0.0, 1.0 - decay)
    
    def is_forgotten(self, current_time: datetime, threshold: float = 0.1) -> bool:
        """Check if event has decayed below threshold"""
        return self.get_decay_factor(current_time) < threshold
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "area_id": self.area_id,
            "description": self.description,
            "actor": self.actor,
            "witnesses": self.witnesses,
            "age_minutes": (datetime.now() - self.timestamp).total_seconds() / 60,
            "severity": self.severity,
            "decay_factor": self.get_decay_factor(datetime.now()),
        }


@dataclass
class AreaMemory:
    """Memory for a specific area"""
    area_id: str
    events: List[WorldEvent] = field(default_factory=list)
    max_events: int = 50
    
    def add_event(self, event: WorldEvent) -> None:
        """Add an event to this area's memory"""
        self.events.append(event)
        
        # Trim if over limit (keep most recent)
        if len(self.events) > self.max_events:
            self.events = sorted(self.events, key=lambda e: e.timestamp, reverse=True)
            self.events = self.events[:self.max_events]
    
    def get_recent_events(
        self,
        event_type: Optional[EventType] = None,
        max_age_minutes: Optional[int] = None,
        current_time: Optional[datetime] = None
    ) -> List[WorldEvent]:
        """Get recent events, optionally filtered"""
        current_time = current_time or datetime.now()
        results = []
        
        for event in self.events:
            # Type filter
            if event_type and event.event_type != event_type:
                continue
            
            # Age filter
            if max_age_minutes and event.get_age(current_time) > max_age_minutes:
                continue
            
            # Decay filter (not forgotten)
            if event.is_forgotten(current_time):
                continue
            
            results.append(event)
        
        return sorted(results, key=lambda e: e.timestamp, reverse=True)
    
    def get_rumors(
        self,
        current_time: Optional[datetime] = None,
        limit: int = 5
    ) -> List[str]:
        """Get rumor text for recent events"""
        current_time = current_time or datetime.now()
        recent = self.get_recent_events(current_time=current_time)
        
        rumors = []
        for event in recent[:limit]:
            decay = event.get_decay_factor(current_time)
            if decay > 0.7:
                rumors.append(f"Just heard: {event.description}")
            elif decay > 0.4:
                rumors.append(f"Word is: {event.description}")
            else:
                rumors.append(f"Some say: {event.description}")
        
        return rumors
    
    def decay(
        self,
        time_delta_minutes: int,
        current_time: Optional[datetime] = None
    ) -> int:
        """Remove forgotten events"""
        current_time = current_time or datetime.now()
        initial_count = len(self.events)
        
        self.events = [
            event for event in self.events
            if not event.is_forgotten(current_time)
        ]
        
        return initial_count - len(self.events)
    
    def clear(self) -> int:
        """Clear all events"""
        count = len(self.events)
        self.events = []
        return count


class WorldMemoryManager:
    """
    Manages area-level memory across the game world.
    
    Features:
    - Track events per area
    - Decay over time
    - Rumor generation
    - Chapter/time-skip resets
    - Event propagation between areas
    """
    
    def __init__(self):
        self.areas: Dict[str, AreaMemory] = {}
        self.global_events: List[WorldEvent] = []  # World-wide events
        self.event_counter: int = 0
    
    def get_area(self, area_id: str) -> AreaMemory:
        """Get or create area memory"""
        if area_id not in self.areas:
            self.areas[area_id] = AreaMemory(area_id=area_id)
        return self.areas[area_id]
    
    def record_event(
        self,
        area_id: str,
        event_type: EventType,
        description: str,
        actor: Optional[str] = None,
        witnesses: Optional[List[str]] = None,
        severity: float = 0.5,
        decay_rate: float = 0.1,
        metadata: Optional[Dict[str, Any]] = None,
        current_time: Optional[datetime] = None
    ) -> WorldEvent:
        """
        Record a new event in an area.
        
        Args:
            area_id: Area where event occurred
            event_type: Type of event
            description: Human-readable description
            actor: Who caused the event
            witnesses: List of witness IDs
            severity: Event severity (0.0-1.0)
            decay_rate: How fast it fades
            metadata: Additional data
            current_time: Current game time
        
        Returns:
            The created WorldEvent
        """
        current_time = current_time or datetime.now()
        self.event_counter += 1
        
        event = WorldEvent(
            event_id=f"event_{self.event_counter}",
            event_type=event_type,
            area_id=area_id,
            description=description,
            actor=actor,
            witnesses=witnesses or [],
            timestamp=current_time,
            severity=severity,
            decay_rate=decay_rate,
            metadata=metadata or {},
        )
        
        # Add to area memory
        area = self.get_area(area_id)
        area.add_event(event)
        
        # Add to global if high severity
        if severity >= 0.8:
            self.global_events.append(event)
        
        return event
    
    def get_rumors(
        self,
        area_id: str,
        current_time: Optional[datetime] = None,
        limit: int = 5
    ) -> List[str]:
        """Get rumors for an area"""
        area = self.get_area(area_id)
        return area.get_rumors(current_time, limit)
    
    def get_events(
        self,
        area_id: str,
        event_type: Optional[EventType] = None,
        max_age_minutes: Optional[int] = None,
        current_time: Optional[datetime] = None
    ) -> List[WorldEvent]:
        """Get events for an area"""
        area = self.get_area(area_id)
        return area.get_recent_events(event_type, max_age_minutes, current_time)
    
    def decay_all(
        self,
        time_delta_minutes: int,
        current_time: Optional[datetime] = None
    ) -> int:
        """Decay all area memories"""
        current_time = current_time or datetime.now()
        total_removed = 0
        
        for area in self.areas.values():
            removed = area.decay(time_delta_minutes, current_time)
            total_removed += removed
        
        # Decay global events
        initial_count = len(self.global_events)
        self.global_events = [
            event for event in self.global_events
            if not event.is_forgotten(current_time)
        ]
        total_removed += initial_count - len(self.global_events)
        
        return total_removed
    
    def clear_area(self, area_id: str) -> int:
        """Clear all events in an area"""
        if area_id in self.areas:
            return self.areas[area_id].clear()
        return 0
    
    def clear_all(self) -> int:
        """Clear all events (chapter reset)"""
        total = 0
        for area in self.areas.values():
            total += area.clear()
        
        global_count = len(self.global_events)
        self.global_events = []
        total += global_count
        
        return total
    
    def clear_on_chapter(self) -> int:
        """Clear memories on chapter transition"""
        return self.clear_all()
    
    def propagate_event(
        self,
        event: WorldEvent,
        target_areas: List[str],
        decay_multiplier: float = 1.5
    ) -> None:
        """
        Propagate an event to nearby areas (rumor spreading).
        
        Args:
            event: Event to propagate
            target_areas: Areas to propagate to
            decay_multiplier: Increase decay rate for propagated events
        """
        for area_id in target_areas:
            # Create a copy with increased decay
            propagated = WorldEvent(
                event_id=f"{event.event_id}_prop_{area_id}",
                event_type=event.event_type,
                area_id=area_id,
                description=f"Heard from {event.area_id}: {event.description}",
                actor=event.actor,
                witnesses=[],  # No direct witnesses in propagated areas
                timestamp=event.timestamp,
                severity=event.severity * 0.7,  # Reduced severity
                decay_rate=event.decay_rate * decay_multiplier,
                metadata={**event.metadata, "propagated_from": event.area_id},
            )
            
            area = self.get_area(area_id)
            area.add_event(propagated)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of world memory"""
        return {
            "total_areas": len(self.areas),
            "total_events": sum(len(area.events) for area in self.areas.values()),
            "global_events": len(self.global_events),
            "areas": {
                area_id: {
                    "event_count": len(area.events),
                    "recent_rumors": area.get_rumors(limit=3),
                }
                for area_id, area in self.areas.items()
            },
        }
