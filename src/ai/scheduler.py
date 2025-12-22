"""
NPC Scheduler System

Manages daily schedules for NPCs with task states, interruptions, and fallback behaviors.
Loads schedule templates from YAML and handles runtime execution.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
from pathlib import Path
import yaml
import random
from datetime import datetime, timedelta


class TaskState(Enum):
    """State of a scheduled task"""
    PLANNED = "planned"
    ACTIVE = "active"
    PAUSED = "paused"
    RESUMED = "resumed"
    COMPLETE = "complete"
    CANCELLED = "cancelled"


@dataclass
class ScheduleTask:
    """A single task in an NPC's schedule"""
    time: str  # "HH:MM" format
    duration: int  # minutes
    location: str
    behavior: str
    description: str
    animation: str = "idle"
    props_required: List[str] = field(default_factory=list)
    reservation: Optional[str] = None  # Prop/space to reserve
    cooldown: int = 0  # Cooldown in seconds before reusing reservation
    waypoints: List[str] = field(default_factory=list)
    priority: int = 5  # 1-10, higher = more important
    state: TaskState = TaskState.PLANNED
    start_time: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "time": self.time,
            "duration": self.duration,
            "location": self.location,
            "behavior": self.behavior,
            "description": self.description,
            "animation": self.animation,
            "state": self.state.value,
            "priority": self.priority,
        }


@dataclass
class Interruption:
    """An interruption that pauses current schedule"""
    reason: str
    priority: int
    behavior: str
    location: Optional[str] = None
    duration: int = 0  # minutes, 0 = indefinite
    resume_after: bool = True
    triggered_at: Optional[datetime] = None


@dataclass
class NPCSchedule:
    """Complete schedule for an NPC"""
    npc_id: str
    archetype: str
    tasks: List[ScheduleTask] = field(default_factory=list)
    current_task_index: int = 0
    active_interruption: Optional[Interruption] = None
    weather_override_active: bool = False
    rare_variant_active: Optional[str] = None
    
    def get_current_task(self) -> Optional[ScheduleTask]:
        """Get the currently active task"""
        if 0 <= self.current_task_index < len(self.tasks):
            return self.tasks[self.current_task_index]
        return None
    
    def get_next_task(self) -> Optional[ScheduleTask]:
        """Get the next scheduled task"""
        next_index = self.current_task_index + 1
        if next_index < len(self.tasks):
            return self.tasks[next_index]
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "npc_id": self.npc_id,
            "archetype": self.archetype,
            "current_task": self.get_current_task().to_dict() if self.get_current_task() else None,
            "next_task": self.get_next_task().to_dict() if self.get_next_task() else None,
            "active_interruption": self.active_interruption.reason if self.active_interruption else None,
            "tasks_completed": self.current_task_index,
            "total_tasks": len(self.tasks),
        }


class Scheduler:
    """
    Runtime scheduler engine for managing NPC schedules.
    
    Features:
    - Load schedules from YAML templates
    - Tick tasks based on game time
    - Handle interruptions with priority
    - Apply weather overrides
    - Trigger rare variants
    - Manage fallback behaviors
    """
    
    def __init__(self, schedule_dir: str = "data/npc_schedules"):
        self.schedule_dir = Path(schedule_dir)
        self.templates: Dict[str, Dict] = {}  # archetype -> template data
        self.active_schedules: Dict[str, NPCSchedule] = {}  # npc_id -> schedule
        self.load_templates()
    
    def load_templates(self) -> None:
        """Load all schedule templates from YAML files"""
        if not self.schedule_dir.exists():
            print(f"Warning: Schedule directory not found: {self.schedule_dir}")
            return
        
        for yaml_file in self.schedule_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                    archetype = data.get('archetype')
                    if archetype:
                        self.templates[archetype] = data
                        print(f"Loaded schedule template: {archetype}")
            except Exception as e:
                print(f"Error loading {yaml_file}: {e}")
    
    def assign_schedule(
        self,
        npc_id: str,
        archetype: str,
        region: str = "default",
        current_time: Optional[datetime] = None
    ) -> Optional[NPCSchedule]:
        """
        Assign a schedule to an NPC from a template.
        
        Args:
            npc_id: Unique NPC identifier
            archetype: Schedule archetype (farmer, guard, merchant, etc.)
            region: Regional variant (default, arid, etc.)
            current_time: Current game time
        
        Returns:
            NPCSchedule instance or None if template not found
        """
        if archetype not in self.templates:
            print(f"Warning: No template found for archetype '{archetype}'")
            return None
        
        template = self.templates[archetype]
        region_data = template.get('regions', {}).get(region, template.get('regions', {}).get('default', {}))
        
        # Check for rare variants
        rare_variant = None
        if 'rare_variants' in template:
            for variant in template['rare_variants']:
                if random.random() < variant.get('probability', 0):
                    rare_variant = variant
                    break
        
        # Build task list
        tasks = []
        if rare_variant and 'override_tasks' in rare_variant:
            # Use rare variant tasks
            task_data_list = rare_variant['override_tasks']
        else:
            # Use normal tasks
            task_data_list = region_data.get('tasks', [])
        
        for task_data in task_data_list:
            task = ScheduleTask(
                time=task_data.get('time', '00:00'),
                duration=task_data.get('duration', 60),
                location=task_data.get('location', 'unknown'),
                behavior=task_data.get('behavior', 'idle'),
                description=task_data.get('description', ''),
                animation=task_data.get('animation', 'idle'),
                props_required=task_data.get('props_required', []),
                reservation=task_data.get('reservation'),
                cooldown=task_data.get('cooldown', 0),
                waypoints=task_data.get('waypoints', []),
                priority=task_data.get('priority', 5),
            )
            tasks.append(task)
        
        schedule = NPCSchedule(
            npc_id=npc_id,
            archetype=archetype,
            tasks=tasks,
            rare_variant_active=rare_variant['name'] if rare_variant else None,
        )
        
        self.active_schedules[npc_id] = schedule
        return schedule
    
    def tick(
        self,
        current_time: datetime,
        world_state: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Update all active schedules based on current time and world state.
        
        Args:
            current_time: Current game time
            world_state: Dictionary with weather, events, etc.
        
        Returns:
            Dictionary of events: {"task_started": [...], "task_completed": [...]}
        """
        events = {
            "task_started": [],
            "task_completed": [],
            "task_interrupted": [],
            "task_resumed": [],
        }
        
        for npc_id, schedule in self.active_schedules.items():
            # Handle active interruption
            if schedule.active_interruption:
                interruption = schedule.active_interruption
                if interruption.duration > 0:
                    elapsed = (current_time - interruption.triggered_at).total_seconds() / 60
                    if elapsed >= interruption.duration:
                        # Interruption complete
                        if interruption.resume_after:
                            current_task = schedule.get_current_task()
                            if current_task and current_task.state == TaskState.PAUSED:
                                current_task.state = TaskState.RESUMED
                                events["task_resumed"].append(npc_id)
                        schedule.active_interruption = None
                continue  # Skip normal task processing during interruption
            
            # Get current task
            current_task = schedule.get_current_task()
            if not current_task:
                continue
            
            # Check if task should start
            if current_task.state == TaskState.PLANNED:
                task_hour, task_minute = map(int, current_task.time.split(':'))
                if current_time.hour == task_hour and current_time.minute >= task_minute:
                    current_task.state = TaskState.ACTIVE
                    current_task.start_time = current_time
                    events["task_started"].append(f"{npc_id}:{current_task.behavior}")
            
            # Check if task should complete
            elif current_task.state == TaskState.ACTIVE or current_task.state == TaskState.RESUMED:
                if current_task.start_time:
                    elapsed = (current_time - current_task.start_time).total_seconds() / 60
                    if elapsed >= current_task.duration:
                        current_task.state = TaskState.COMPLETE
                        schedule.current_task_index += 1
                        events["task_completed"].append(f"{npc_id}:{current_task.behavior}")
        
        return events
    
    def interrupt(
        self,
        npc_id: str,
        reason: str,
        priority: int,
        behavior: str,
        location: Optional[str] = None,
        duration: int = 0,
        resume_after: bool = True,
        current_time: Optional[datetime] = None
    ) -> bool:
        """
        Interrupt an NPC's current schedule.
        
        Args:
            npc_id: NPC to interrupt
            reason: Reason for interruption (crime_alarm, player_proximity, etc.)
            priority: Interruption priority (1-10)
            behavior: Behavior during interruption
            location: Location to move to (optional)
            duration: Duration in minutes (0 = indefinite)
            resume_after: Whether to resume task after interruption
            current_time: Current game time
        
        Returns:
            True if interruption was applied, False otherwise
        """
        if npc_id not in self.active_schedules:
            return False
        
        schedule = self.active_schedules[npc_id]
        current_task = schedule.get_current_task()
        
        if not current_task:
            return False
        
        # Check if interruption priority is high enough
        if priority < current_task.priority:
            return False  # Current task is more important
        
        # Pause current task
        if current_task.state == TaskState.ACTIVE:
            current_task.state = TaskState.PAUSED
            current_task.paused_at = current_time or datetime.now()
        
        # Create interruption
        interruption = Interruption(
            reason=reason,
            priority=priority,
            behavior=behavior,
            location=location,
            duration=duration,
            resume_after=resume_after,
            triggered_at=current_time or datetime.now(),
        )
        
        schedule.active_interruption = interruption
        return True
    
    def resume(self, npc_id: str) -> bool:
        """
        Manually resume an NPC's paused task.
        
        Args:
            npc_id: NPC to resume
        
        Returns:
            True if resumed, False otherwise
        """
        if npc_id not in self.active_schedules:
            return False
        
        schedule = self.active_schedules[npc_id]
        schedule.active_interruption = None
        
        current_task = schedule.get_current_task()
        if current_task and current_task.state == TaskState.PAUSED:
            current_task.state = TaskState.RESUMED
            return True
        
        return False
    
    def get_active_task(self, npc_id: str) -> Optional[ScheduleTask]:
        """Get the current active task for an NPC"""
        if npc_id in self.active_schedules:
            return self.active_schedules[npc_id].get_current_task()
        return None
    
    def get_schedule(self, npc_id: str) -> Optional[NPCSchedule]:
        """Get the full schedule for an NPC"""
        return self.active_schedules.get(npc_id)
    
    def get_all_active_schedules(self) -> Dict[str, NPCSchedule]:
        """Get all active schedules"""
        return self.active_schedules.copy()
