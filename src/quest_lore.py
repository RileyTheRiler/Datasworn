"""
Quest, Lore, and Dynamic World Systems

This module provides systems for tracking objectives, generating lore,
managing NPC schedules, and creating dynamic environmental challenges.

Key Systems:
1. Quest/Objective Tracker - Track goals, sub-goals, and progress
2. Procedural Lore Generator - Deep worldbuilding on demand
3. NPC Schedule System - Where NPCs are and what they're doing
4. Environmental Hazard System - Dynamic environmental dangers
5. Rumor Network - Information spreading through the world
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, Any
import random
from collections import defaultdict


# =============================================================================
# QUEST/OBJECTIVE TRACKER
# =============================================================================

class QuestStatus(Enum):
    """Status of a quest."""
    UNKNOWN = "unknown"        # Not yet discovered
    AVAILABLE = "available"    # Can be started
    ACTIVE = "active"          # Currently pursuing
    COMPLETED = "completed"    # Successfully done
    FAILED = "failed"          # Permanently failed
    ABANDONED = "abandoned"    # Dropped by player


class QuestType(Enum):
    """Types of quests/objectives."""
    MAIN = "main"              # Central storyline
    SIDE = "side"              # Optional content
    PERSONAL = "personal"      # Character-driven
    FACTION = "faction"        # Group-related
    EXPLORATION = "exploration" # Discovery-driven
    URGENT = "urgent"          # Time-sensitive


@dataclass
class QuestObjective:
    """A single objective within a quest."""
    objective_id: str
    description: str
    is_completed: bool = False
    is_optional: bool = False
    completion_hint: str = ""
    discovered: bool = True


@dataclass
class Quest:
    """A quest or goal being tracked."""
    quest_id: str
    title: str
    description: str
    quest_type: QuestType
    status: QuestStatus
    objectives: List[QuestObjective] = field(default_factory=list)
    giver_npc: str = ""
    deadline_day: Optional[int] = None
    reward_hint: str = ""
    narrative_stakes: str = ""  # Why this matters to the story
    related_npcs: List[str] = field(default_factory=list)
    discovery_scene: int = 0
    
    def get_progress(self) -> float:
        """Get completion percentage."""
        if not self.objectives:
            return 0.0
        required = [o for o in self.objectives if not o.is_optional]
        if not required:
            return 1.0 if self.status == QuestStatus.COMPLETED else 0.0
        completed = sum(1 for o in required if o.is_completed)
        return completed / len(required)


@dataclass
@dataclass
class QuestTracker:
    """
    Tracks goals, sub-goals, and narrative progress.
    
    Provides quest reminders, tracks player commitments,
    and helps maintain narrative momentum.
    """
    
    quests: Dict[str, Quest] = field(default_factory=dict)
    current_scene: int = 0
    
    def add_quest(self, quest_id: str, title: str, description: str,
                   quest_type: QuestType, giver: str = "",
                   stakes: str = "", deadline: int = None) -> Quest:
        """Add a new quest."""
        quest = Quest(
            quest_id=quest_id,
            title=title,
            description=description,
            quest_type=quest_type,
            status=QuestStatus.ACTIVE,
            giver_npc=giver,
            deadline_day=deadline,
            narrative_stakes=stakes,
            discovery_scene=self.current_scene
        )
        self.quests[quest_id] = quest
        return quest
    
    def add_objective(self, quest_id: str, obj_id: str, description: str,
                       optional: bool = False, hint: str = ""):
        """Add objective to a quest."""
        if quest_id in self.quests:
            obj = QuestObjective(
                objective_id=obj_id,
                description=description,
                is_optional=optional,
                completion_hint=hint
            )
            self.quests[quest_id].objectives.append(obj)
    
    def complete_objective(self, quest_id: str, obj_id: str):
        """Mark an objective as completed."""
        if quest_id in self.quests:
            for obj in self.quests[quest_id].objectives:
                if obj.objective_id == obj_id:
                    obj.is_completed = True
                    break
            
            # Check if quest is now complete
            quest = self.quests[quest_id]
            if quest.get_progress() >= 1.0:
                quest.status = QuestStatus.COMPLETED
    
    def get_active_quests(self) -> List[Quest]:
        """Get all active quests."""
        return [q for q in self.quests.values() if q.status == QuestStatus.ACTIVE]
    
    def get_urgent_quests(self, current_day: int) -> List[Quest]:
        """Get quests with approaching deadlines."""
        urgent = []
        for q in self.get_active_quests():
            if q.deadline_day and q.deadline_day - current_day <= 3:
                urgent.append(q)
        return sorted(urgent, key=lambda x: x.deadline_day or 999)
    
    def get_quest_guidance(self, current_day: int = 1) -> str:
        """Generate quest tracking guidance for narrator."""
        active = self.get_active_quests()
        
        if not active:
            return """<quest_tracker>
No active quests tracked.

Consider introducing:
  - A main objective to drive narrative
  - Side objectives that reveal character/world
  - Urgent time-sensitive goals for tension
</quest_tracker>"""
        
        # Sort by type priority
        main = [q for q in active if q.quest_type == QuestType.MAIN]
        urgent = [q for q in active if q.quest_type == QuestType.URGENT or 
                  (q.deadline_day and q.deadline_day - current_day <= 3)]
        side = [q for q in active if q.quest_type in [QuestType.SIDE, QuestType.PERSONAL]]
        
        sections = []
        
        if main:
            main_text = []
            for q in main[:2]:
                progress = f"{q.get_progress():.0%}"
                objs = [o for o in q.objectives if not o.is_completed][:2]
                obj_text = "\n".join([f"      □ {o.description}" for o in objs])
                main_text.append(f"  📍 {q.title} ({progress})\n{obj_text}")
            sections.append(f"MAIN OBJECTIVES:\n{chr(10).join(main_text)}")
        
        if urgent:
            urgent_text = []
            for q in urgent[:2]:
                days_left = q.deadline_day - current_day if q.deadline_day else "?"
                urgent_text.append(f"  ⏰ {q.title} ({days_left} days left)")
            sections.append(f"URGENT:\n{chr(10).join(urgent_text)}")
        
        if side:
            side_text = [f"  ○ {q.title} ({q.get_progress():.0%})" for q in side[:3]]
            sections.append(f"SIDE QUESTS:\n{chr(10).join(side_text)}")
        
        return f"""<quest_tracker>
ACTIVE OBJECTIVES ({len(active)} total):

{chr(10).join(sections)}

NARRATIVE MOMENTUM:
  - Reference active goals in character thoughts/dialogue
  - Obstacles should connect to objectives when possible
  - Progress should feel earned, not given
  - Stakes should be clear and escalating
</quest_tracker>"""
    
    def to_dict(self) -> dict:
        return {
            "quests": {
                qid: {
                    "quest_id": q.quest_id,
                    "title": q.title,
                    "description": q.description,
                    "quest_type": q.quest_type.value,
                    "status": q.status.value,
                    "objectives": [
                        {"objective_id": o.objective_id, "description": o.description,
                         "is_completed": o.is_completed, "is_optional": o.is_optional}
                        for o in q.objectives
                    ],
                    "giver_npc": q.giver_npc,
                    "deadline_day": q.deadline_day,
                    "narrative_stakes": q.narrative_stakes,
                    "related_npcs": q.related_npcs
                } for qid, q in self.quests.items()
            },
            "current_scene": self.current_scene
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "QuestTracker":
        tracker = cls()
        tracker.current_scene = data.get("current_scene", 0)
        
        for qid, q in data.get("quests", {}).items():
            quest = Quest(
                quest_id=q["quest_id"],
                title=q["title"],
                description=q["description"],
                quest_type=QuestType(q["quest_type"]),
                status=QuestStatus(q["status"]),
                giver_npc=q.get("giver_npc", ""),
                deadline_day=q.get("deadline_day"),
                narrative_stakes=q.get("narrative_stakes", ""),
                related_npcs=q.get("related_npcs", [])
            )
            for o in q.get("objectives", []):
                quest.objectives.append(QuestObjective(
                    objective_id=o["objective_id"],
                    description=o["description"],
                    is_completed=o.get("is_completed", False),
                    is_optional=o.get("is_optional", False)
                ))
            tracker.quests[qid] = quest
        return tracker


# =============================================================================
# PROCEDURAL LORE GENERATOR
# =============================================================================

class LoreCategory(Enum):
    """Categories of lore."""
    HISTORY = "history"          # Past events
    CULTURE = "culture"          # Traditions, beliefs
    TECHNOLOGY = "technology"    # Tech level, innovations
    POLITICS = "politics"        # Power structures
    MYTHOLOGY = "mythology"      # Legends, religions
    GEOGRAPHY = "geography"      # Places, features
    BIOLOGY = "biology"          # Species, creatures
    ECONOMICS = "economics"      # Trade, resources


@dataclass
class LoreEntry:
    """A piece of world lore."""
    lore_id: str
    category: LoreCategory
    title: str
    content: str
    is_common_knowledge: bool = True
    related_entries: List[str] = field(default_factory=list)
    discovered_by_player: bool = False


@dataclass
class ProceduralLoreGenerator:
    """
    Generates and tracks deep worldbuilding on demand.
    
    Creates consistent lore, tracks what's been established,
    and prevents contradictions.
    """
    
    lore_entries: Dict[str, LoreEntry] = field(default_factory=dict)
    established_facts: Dict[str, str] = field(default_factory=dict)  # Quick lookup
    
    # Lore templates by category
    LORE_TEMPLATES: Dict[LoreCategory, List[Dict[str, str]]] = field(default_factory=lambda: {
        LoreCategory.HISTORY: [
            {"pattern": "The {adjective} {event} of {number} years ago",
             "elements": ["Great Collapse", "Iron Migration", "Silent War", "Founding"]},
            {"pattern": "Before the {era}, the {group} controlled {thing}",
             "elements": ["Expansion", "Darkness", "First Charter", "Sundering"]}
        ],
        LoreCategory.CULTURE: [
            {"pattern": "The {group} believe that {belief}",
             "elements": ["stars guide the worthy", "the void remembers", "machines have souls"]},
            {"pattern": "It is {custom} to {action} when {occasion}",
             "elements": ["customary", "forbidden", "sacred", "expected"]}
        ],
        LoreCategory.TECHNOLOGY: [
            {"pattern": "The {tech} was developed by {group} during {era}",
             "elements": ["drift drives", "neural links", "fabricators", "void shields"]},
            {"pattern": "{tech} works by {mechanism}, though few understand it",
             "elements": ["quantum entanglement", "dark energy manipulation", "precursor algorithms"]}
        ],
        LoreCategory.MYTHOLOGY: [
            {"pattern": "Legend speaks of {figure} who {deed}",
             "elements": ["the First Navigator", "the Iron Saint", "the Void Walker"]},
            {"pattern": "The {people} tell of {place} where {phenomenon}",
             "elements": ["Outer Rim", "Deep Black", "the Shattered Worlds"]}
        ]
    })
    
    def establish_fact(self, category: str, key: str, value: str):
        """Establish a fact about the world."""
        full_key = f"{category}:{key}"
        self.established_facts[full_key] = value
    
    def get_fact(self, category: str, key: str) -> Optional[str]:
        """Get an established fact."""
        return self.established_facts.get(f"{category}:{key}")
    
    def add_lore_entry(self, lore_id: str, category: LoreCategory,
                        title: str, content: str,
                        common: bool = True) -> LoreEntry:
        """Add a lore entry."""
        entry = LoreEntry(
            lore_id=lore_id,
            category=category,
            title=title,
            content=content,
            is_common_knowledge=common
        )
        self.lore_entries[lore_id] = entry
        return entry
    
    def get_relevant_lore(self, keywords: List[str], 
                           limit: int = 3) -> List[LoreEntry]:
        """Get lore entries relevant to keywords."""
        relevant = []
        for entry in self.lore_entries.values():
            for kw in keywords:
                if kw.lower() in entry.title.lower() or kw.lower() in entry.content.lower():
                    relevant.append(entry)
                    break
        return relevant[:limit]
    
    def get_lore_guidance(self, location: str = "", 
                           topic_hints: List[str] = None) -> str:
        """Generate lore guidance for narrator."""
        
        relevant = []
        if topic_hints:
            relevant = self.get_relevant_lore(topic_hints)
        
        established_text = ""
        if self.established_facts:
            facts = list(self.established_facts.items())[-5:]
            fact_lines = [f"  {k}: {v}" for k, v in facts]
            established_text = f"""
ESTABLISHED FACTS (do not contradict):
{chr(10).join(fact_lines)}"""
        
        relevant_text = ""
        if relevant:
            rel_lines = [f"  - {e.title}: {e.content[:60]}..." for e in relevant]
            relevant_text = f"""
RELEVANT LORE:
{chr(10).join(rel_lines)}"""
        
        # Suggest a lore type to introduce
        category = random.choice(list(LoreCategory))
        templates = self.LORE_TEMPLATES.get(category, [])
        template = random.choice(templates) if templates else {"pattern": "Unknown lore pattern"}
        
        return f"""<lore_generator>
{established_text}{relevant_text}

LORE OPPORTUNITY ({category.value}):
  Pattern: "{template.get('pattern', 'Create relevant lore')}"
  
WORLDBUILDING PRINCIPLES:
  - Consistency > novelty (don't contradict established facts)
  - Imply more than you explain (the iceberg)
  - Lore should feel lived-in, not encyclopedic
  - Connect lore to character experience when possible
  
DELIVERY METHODS:
  - NPCs mention it casually (established knowledge)
  - Environmental storytelling (inscriptions, artifacts)
  - Character memories/associations
  - Contrast with outsider ignorance
</lore_generator>"""
    
    def to_dict(self) -> dict:
        return {
            "lore_entries": {
                lid: {
                    "lore_id": e.lore_id,
                    "category": e.category.value,
                    "title": e.title,
                    "content": e.content,
                    "is_common_knowledge": e.is_common_knowledge,
                    "discovered_by_player": e.discovered_by_player
                } for lid, e in self.lore_entries.items()
            },
            "established_facts": self.established_facts
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ProceduralLoreGenerator":
        gen = cls()
        gen.established_facts = data.get("established_facts", {})
        
        for lid, e in data.get("lore_entries", {}).items():
            gen.lore_entries[lid] = LoreEntry(
                lore_id=e["lore_id"],
                category=LoreCategory(e["category"]),
                title=e["title"],
                content=e["content"],
                is_common_knowledge=e.get("is_common_knowledge", True),
                discovered_by_player=e.get("discovered_by_player", False)
            )
        return gen


# =============================================================================
# NPC SCHEDULE SYSTEM
# =============================================================================

class ActivityType(Enum):
    """Types of NPC activities."""
    WORK = "work"
    REST = "rest"
    SOCIAL = "social"
    TRAVEL = "travel"
    EATING = "eating"
    RECREATION = "recreation"
    DUTY = "duty"
    SECRET = "secret"


@dataclass 
class ScheduleBlock:
    """A scheduled activity for an NPC."""
    time_start: str  # e.g., "morning", "night"
    time_end: str
    location: str
    activity: ActivityType
    interruptible: bool = True
    secret: bool = False
    with_npcs: List[str] = field(default_factory=list)


@dataclass
class NPCSchedule:
    """A complete schedule for an NPC."""
    npc_name: str
    schedule: List[ScheduleBlock] = field(default_factory=list)
    deviation_reason: str = ""  # Why they're off-schedule
    is_deviating: bool = False


@dataclass
class NPCScheduleSystem:
    """
    Tracks where NPCs are and what they're doing.
    
    Creates a sense of a living world where NPCs
    have their own lives and routines.
    """
    
    schedules: Dict[str, NPCSchedule] = field(default_factory=dict)
    current_time: str = "morning"
    
    TIME_ORDER = ["dawn", "morning", "midday", "afternoon", "dusk", "evening", "night", "late_night"]
    
    def create_schedule(self, npc_name: str) -> NPCSchedule:
        """Create a schedule for an NPC."""
        schedule = NPCSchedule(npc_name=npc_name)
        self.schedules[npc_name] = schedule
        return schedule
    
    def add_activity(self, npc_name: str, time_start: str, time_end: str,
                      location: str, activity: ActivityType,
                      interruptible: bool = True, secret: bool = False):
        """Add an activity to NPC's schedule."""
        if npc_name not in self.schedules:
            self.create_schedule(npc_name)
        
        block = ScheduleBlock(
            time_start=time_start,
            time_end=time_end,
            location=location,
            activity=activity,
            interruptible=interruptible,
            secret=secret
        )
        self.schedules[npc_name].schedule.append(block)
    
    def get_npc_location(self, npc_name: str, time: str = None) -> Optional[Tuple[str, ActivityType]]:
        """Get NPC's current location and activity."""
        time = time or self.current_time
        
        if npc_name not in self.schedules:
            return None
        
        schedule = self.schedules[npc_name]
        
        # Check for deviation
        if schedule.is_deviating:
            return None  # Location unknown due to deviation
        
        # Find current activity
        for block in schedule.schedule:
            start_idx = self.TIME_ORDER.index(block.time_start) if block.time_start in self.TIME_ORDER else 0
            end_idx = self.TIME_ORDER.index(block.time_end) if block.time_end in self.TIME_ORDER else len(self.TIME_ORDER)
            current_idx = self.TIME_ORDER.index(time) if time in self.TIME_ORDER else 0
            
            if start_idx <= current_idx <= end_idx:
                return (block.location, block.activity)
        
        return None
    
    def get_npcs_at_location(self, location: str, time: str = None) -> List[str]:
        """Get all NPCs at a location."""
        time = time or self.current_time
        npcs = []
        
        for npc_name in self.schedules:
            loc_info = self.get_npc_location(npc_name, time)
            if loc_info and loc_info[0] == location:
                npcs.append(npc_name)
        
        return npcs
    
    def set_deviation(self, npc_name: str, reason: str):
        """Mark NPC as deviating from schedule."""
        if npc_name in self.schedules:
            self.schedules[npc_name].is_deviating = True
            self.schedules[npc_name].deviation_reason = reason
    
    def get_schedule_guidance(self, current_location: str = "") -> str:
        """Generate schedule guidance for narrator."""
        
        # Who's at current location?
        at_location = []
        if current_location:
            at_location = self.get_npcs_at_location(current_location)
        
        at_loc_text = ""
        if at_location:
            details = []
            for npc in at_location:
                loc_info = self.get_npc_location(npc)
                if loc_info:
                    details.append(f"  - {npc}: {loc_info[1].value}")
            at_loc_text = f"""
NPCS AT {current_location.upper()}:
{chr(10).join(details)}"""
        
        # Any deviations?
        deviations = [s for s in self.schedules.values() if s.is_deviating]
        dev_text = ""
        if deviations:
            dev_lines = [f"  - {s.npc_name}: {s.deviation_reason}" for s in deviations]
            dev_text = f"""
OFF-SCHEDULE (suspicious/notable):
{chr(10).join(dev_lines)}"""
        
        return f"""<npc_schedules>
CURRENT TIME: {self.current_time}
{at_loc_text}{dev_text}

LIVING WORLD PRINCIPLES:
  - NPCs have lives when player isn't looking
  - "Where is X?" should have an answer
  - Deviations from routine are suspicious/significant
  - Finding someone requires knowing their schedule (or following them)
  
SCHEDULE USES:
  - Player can stake out locations
  - NPCs have alibis (or don't)
  - Miss the window, miss the opportunity
  - "They're usually here by now..." tension
</npc_schedules>"""
    
    def to_dict(self) -> dict:
        return {
            "schedules": {
                name: {
                    "npc_name": s.npc_name,
                    "schedule": [
                        {"time_start": b.time_start, "time_end": b.time_end,
                         "location": b.location, "activity": b.activity.value,
                         "interruptible": b.interruptible, "secret": b.secret}
                        for b in s.schedule
                    ],
                    "is_deviating": s.is_deviating,
                    "deviation_reason": s.deviation_reason
                } for name, s in self.schedules.items()
            },
            "current_time": self.current_time
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "NPCScheduleSystem":
        system = cls()
        system.current_time = data.get("current_time", "morning")
        
        for name, s in data.get("schedules", {}).items():
            schedule = NPCSchedule(
                npc_name=s["npc_name"],
                is_deviating=s.get("is_deviating", False),
                deviation_reason=s.get("deviation_reason", "")
            )
            for b in s.get("schedule", []):
                schedule.schedule.append(ScheduleBlock(
                    time_start=b["time_start"],
                    time_end=b["time_end"],
                    location=b["location"],
                    activity=ActivityType(b["activity"]),
                    interruptible=b.get("interruptible", True),
                    secret=b.get("secret", False)
                ))
            system.schedules[name] = schedule
        return system


# =============================================================================
# RUMOR NETWORK SYSTEM
# =============================================================================

class RumorType(Enum):
    """Types of rumors."""
    TRUE = "true"              # Actually happened
    DISTORTED = "distorted"    # Based on truth but wrong
    FALSE = "false"            # Completely made up
    PROPHETIC = "prophetic"    # Will become true
    PLANTED = "planted"        # Deliberately spread


@dataclass
class Rumor:
    """A piece of spreading information."""
    rumor_id: str
    content: str
    rumor_type: RumorType
    source_npc: str
    origin_scene: int
    spread_count: int = 0
    known_by: Set[str] = field(default_factory=set)
    distortion_level: float = 0.0  # How distorted from original


@dataclass
class RumorNetwork:
    """
    Tracks how information spreads through the world.
    
    Creates a sense of a reactive world where news travels
    and player actions become known.
    """
    
    rumors: Dict[str, Rumor] = field(default_factory=dict)
    npc_connections: Dict[str, List[str]] = field(default_factory=dict)  # Social network
    current_scene: int = 0
    
    def create_rumor(self, rumor_id: str, content: str, rumor_type: RumorType,
                      source: str) -> Rumor:
        """Create a new rumor."""
        rumor = Rumor(
            rumor_id=rumor_id,
            content=content,
            rumor_type=rumor_type,
            source_npc=source,
            origin_scene=self.current_scene,
            known_by={source}
        )
        self.rumors[rumor_id] = rumor
        return rumor
    
    def spread_rumor(self, rumor_id: str, to_npc: str, distortion: float = 0.0):
        """Spread a rumor to another NPC."""
        if rumor_id in self.rumors:
            rumor = self.rumors[rumor_id]
            rumor.known_by.add(to_npc)
            rumor.spread_count += 1
            rumor.distortion_level = min(1.0, rumor.distortion_level + distortion)
    
    def get_npc_rumors(self, npc_name: str) -> List[Rumor]:
        """Get rumors an NPC knows."""
        return [r for r in self.rumors.values() if npc_name in r.known_by]
    
    def add_connection(self, npc1: str, npc2: str):
        """Add a social connection between NPCs."""
        if npc1 not in self.npc_connections:
            self.npc_connections[npc1] = []
        if npc2 not in self.npc_connections:
            self.npc_connections[npc2] = []
        
        if npc2 not in self.npc_connections[npc1]:
            self.npc_connections[npc1].append(npc2)
        if npc1 not in self.npc_connections[npc2]:
            self.npc_connections[npc2].append(npc1)
    
    def simulate_spread(self, scenes_passed: int = 1):
        """Simulate rumor spreading over time."""
        for rumor in self.rumors.values():
            if rumor.spread_count >= 10:  # Already well-known
                continue
            
            # Each NPC who knows might tell their connections
            new_knowers = set()
            for knower in rumor.known_by:
                connections = self.npc_connections.get(knower, [])
                for conn in connections:
                    if conn not in rumor.known_by and random.random() < 0.3:
                        new_knowers.add(conn)
            
            for npc in new_knowers:
                self.spread_rumor(rumor.rumor_id, npc, distortion=0.1)
    
    def get_rumor_guidance(self, active_npcs: List[str]) -> str:
        """Generate rumor network guidance."""
        
        # What do active NPCs know?
        npc_rumors = []
        for npc in active_npcs:
            rumors = self.get_npc_rumors(npc)
            if rumors:
                recent = rumors[-2:]
                for r in recent:
                    distort_note = f" (distorted {r.distortion_level:.0%})" if r.distortion_level > 0.2 else ""
                    npc_rumors.append(f"  {npc} heard: \"{r.content[:50]}...\"{distort_note}")
        
        rumors_text = "\n".join(npc_rumors) if npc_rumors else "  No rumors among present NPCs"
        
        return f"""<rumor_network>
WHAT PRESENT NPCS HAVE HEARD:
{rumors_text}

RUMOR MECHANICS:
  - Information travels through social connections
  - Each retelling adds potential distortion
  - "Where did you hear that?" traces the chain
  - False rumors can be just as dangerous as true ones
  
USES:
  - Player actions become known (consequences)
  - NPCs have opinions based on what they've heard
  - Misinformation can be weaponized
  - Reputation is built by rumor as much as deed
</rumor_network>"""
    
    def to_dict(self) -> dict:
        return {
            "rumors": {
                rid: {
                    "rumor_id": r.rumor_id,
                    "content": r.content,
                    "rumor_type": r.rumor_type.value,
                    "source_npc": r.source_npc,
                    "origin_scene": r.origin_scene,
                    "spread_count": r.spread_count,
                    "known_by": list(r.known_by),
                    "distortion_level": r.distortion_level
                } for rid, r in self.rumors.items()
            },
            "npc_connections": self.npc_connections,
            "current_scene": self.current_scene
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "RumorNetwork":
        network = cls()
        network.current_scene = data.get("current_scene", 0)
        network.npc_connections = data.get("npc_connections", {})
        
        for rid, r in data.get("rumors", {}).items():
            network.rumors[rid] = Rumor(
                rumor_id=r["rumor_id"],
                content=r["content"],
                rumor_type=RumorType(r["rumor_type"]),
                source_npc=r["source_npc"],
                origin_scene=r["origin_scene"],
                spread_count=r.get("spread_count", 0),
                known_by=set(r.get("known_by", [])),
                distortion_level=r.get("distortion_level", 0.0)
            )
        return network


# =============================================================================
# MASTER QUEST AND LORE ENGINE
# =============================================================================

@dataclass
class QuestLoreEngine:
    """Master engine coordinating quest, lore, and dynamic world systems."""
    
    quests: QuestTracker = field(default_factory=QuestTracker)
    lore: ProceduralLoreGenerator = field(default_factory=ProceduralLoreGenerator)
    schedules: NPCScheduleSystem = field(default_factory=NPCScheduleSystem)
    rumors: RumorNetwork = field(default_factory=RumorNetwork)
    
    def get_comprehensive_guidance(
        self,
        current_location: str = "",
        active_npcs: List[str] = None,
        current_day: int = 1,
        topic_hints: List[str] = None
    ) -> str:
        """Generate comprehensive quest and lore guidance."""
        
        sections = []
        
        # Quest tracking
        quest_guidance = self.quests.get_quest_guidance(current_day)
        if quest_guidance:
            sections.append(quest_guidance)
        
        # Lore
        lore_guidance = self.lore.get_lore_guidance(current_location, topic_hints or [])
        if lore_guidance:
            sections.append(lore_guidance)
        
        # Schedules
        schedule_guidance = self.schedules.get_schedule_guidance(current_location)
        if schedule_guidance:
            sections.append(schedule_guidance)
        
        # Rumors
        if active_npcs:
            rumor_guidance = self.rumors.get_rumor_guidance(active_npcs)
            if rumor_guidance:
                sections.append(rumor_guidance)
        
        if not sections:
            return ""
        
        return f"""
<quest_lore_systems>
=== QUEST, LORE & WORLD SYSTEMS ===
{chr(10).join(sections)}
</quest_lore_systems>
"""
    
    def to_dict(self) -> dict:
        return {
            "quests": self.quests.to_dict(),
            "lore": self.lore.to_dict(),
            "schedules": self.schedules.to_dict(),
            "rumors": self.rumors.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "QuestLoreEngine":
        engine = cls()
        if "quests" in data:
            engine.quests = QuestTracker.from_dict(data["quests"])
        if "lore" in data:
            engine.lore = ProceduralLoreGenerator.from_dict(data["lore"])
        if "schedules" in data:
            engine.schedules = NPCScheduleSystem.from_dict(data["schedules"])
        if "rumors" in data:
            engine.rumors = RumorNetwork.from_dict(data["rumors"])
        return engine


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("QUEST & LORE ENGINE - TEST")
    print("=" * 60)
    
    engine = QuestLoreEngine()
    
    # Add a quest
    engine.quests.add_quest(
        "find_brother",
        "Find Marcus",
        "Locate your missing brother who was last seen on Station Omega",
        QuestType.MAIN,
        stakes="Family is all you have left"
    )
    engine.quests.add_objective("find_brother", "obj1", "Reach Station Omega")
    engine.quests.add_objective("find_brother", "obj2", "Find someone who saw Marcus")
    engine.quests.add_objective("find_brother", "obj3", "Discover what happened", optional=True)
    
    # Add lore
    engine.lore.establish_fact("history", "Great_Collapse", "occurred 200 years ago")
    engine.lore.add_lore_entry(
        "collapse",
        LoreCategory.HISTORY,
        "The Great Collapse",
        "When the old gates failed, thousands of worlds were cut off forever."
    )
    
    # Add schedule
    engine.schedules.create_schedule("Torres")
    engine.schedules.add_activity("Torres", "morning", "afternoon", "Bridge", ActivityType.DUTY)
    engine.schedules.add_activity("Torres", "evening", "night", "Officers' Mess", ActivityType.SOCIAL)
    
    # Add rumor
    engine.rumors.create_rumor(
        "marcus_rumor",
        "Someone matching his description was seen near the lower docks",
        RumorType.TRUE,
        "Dockworker"
    )
    engine.rumors.spread_rumor("marcus_rumor", "Torres")
    
    print("\n--- COMPREHENSIVE GUIDANCE ---")
    guidance = engine.get_comprehensive_guidance(
        current_location="Bridge",
        active_npcs=["Torres"],
        current_day=3
    )
    print(guidance[:3000] + "..." if len(guidance) > 3000 else guidance)
