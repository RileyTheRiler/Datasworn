"""
Smart Zones & Perception System.
Implements "living scenes" and believable NPC perception.

Smart Zones pre-compute NPC roles and timelines for ambient life.
Perception uses distance-inverse FOV for believable stealth.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import random
import math
import time


# ============================================================================
# Smart Zone System (Living Scenes)
# ============================================================================

class ZoneType(Enum):
    """Types of zones with different ambient behaviors."""
    BAR = "bar"
    MARKET = "market"
    RESIDENTIAL = "residential"
    INDUSTRIAL = "industrial"
    MILITARY = "military"
    DERELICT = "derelict"
    WILDERNESS = "wilderness"


@dataclass
class NPCRole:
    """A role an NPC can fill in a scene."""
    role_name: str
    behaviors: list[str]
    dialogue_topics: list[str]
    personality_hints: str


@dataclass
class PerceptionWorldObject:
    """Simple representation of an object in the scene graph."""

    object_id: str
    position: tuple[float, float, float]
    affordance_tags: set[str] = field(default_factory=set)

    def add_tags(self, *tags: str) -> None:
        for tag in tags:
            self.affordance_tags.add(tag.lower())


@dataclass
class TriggerVolume:
    """Simplified trigger volume used for auditory cues."""

    name: str
    center: tuple[float, float, float]
    radius: float
    loudness: float = 1.0

    def contains(self, point: tuple[float, float, float]) -> bool:
        px, py, pz = point
        cx, cy, cz = self.center
        distance_sq = (px - cx) ** 2 + (py - cy) ** 2 + (pz - cz) ** 2
        return distance_sq <= self.radius**2


@dataclass
class PerceptionEnvironment:
    """Contextual modifiers based on weather and time of day."""

    time_of_day: str = "day"  # dawn, day, dusk, night
    weather: str = "clear"  # clear, rain, fog, storm, snow
    visibility_modifier: float = 1.0
    hearing_modifier: float = 1.0

    def compute_modifiers(self) -> None:
        """Update perception multipliers based on conditions."""
        time_modifiers = {
            "dawn": 0.9,
            "day": 1.0,
            "dusk": 0.8,
            "night": 0.6,
        }
        weather_visibility = {
            "clear": 1.0,
            "rain": 0.85,
            "fog": 0.6,
            "storm": 0.5,
            "snow": 0.75,
        }
        weather_hearing = {
            "clear": 1.0,
            "rain": 0.9,
            "fog": 1.05,
            "storm": 0.75,
            "snow": 0.95,
        }

        self.visibility_modifier = time_modifiers.get(self.time_of_day, 1.0)
        self.visibility_modifier *= weather_visibility.get(self.weather, 1.0)
        self.hearing_modifier = weather_hearing.get(self.weather, 1.0)


@dataclass
class PerceptionSnapshot:
    """Debug-friendly snapshot of the perception system."""

    timestamp: float
    detection_states: dict[str, float]
    detection_labels: dict[str, str]
    world_objects: dict[str, set[str]]
    environment: PerceptionEnvironment
    active_triggers: list[str]
    navmesh_nodes: int
    scene_nodes: int

    def as_text(self) -> str:
        lines = ["[PERCEPTION SNAPSHOT]"]
        lines.append(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.timestamp)))
        lines.append(f"Visibility modifier: {self.environment.visibility_modifier:.2f}")
        lines.append(f"Hearing modifier: {self.environment.hearing_modifier:.2f}")
        lines.append("\nDetections:")
        if not self.detection_states:
            lines.append("  (none)")
        for npc_id, awareness in self.detection_states.items():
            label = self.detection_labels.get(npc_id, "UNKNOWN")
            lines.append(f"  - {npc_id}: {label} ({awareness:.2f})")

        lines.append("\nWorld objects & affordances:")
        if not self.world_objects:
            lines.append("  (none tracked)")
        for obj_id, tags in self.world_objects.items():
            tag_list = ", ".join(sorted(tags)) if tags else "(no tags)"
            lines.append(f"  - {obj_id}: {tag_list}")

        if self.active_triggers:
            lines.append("\nActive triggers: " + ", ".join(self.active_triggers))
        else:
            lines.append("\nActive triggers: (none)")

        lines.append(f"Scene nodes tracked: {self.scene_nodes}")
        lines.append(f"Navmesh nodes tracked: {self.navmesh_nodes}")
        return "\n".join(lines)


# Pre-defined roles for different zone types
ZONE_ROLES = {
    ZoneType.BAR: [
        NPCRole("bartender", ["wipe glasses", "serve drinks", "lean on counter"],
                ["local gossip", "travelers warnings", "prices"], "gruff but observant"),
        NPCRole("drunk", ["sway", "mumble", "stare into drink"],
                ["regrets", "old stories", "conspiracy theories"], "melancholic"),
        NPCRole("smuggler", ["glance around nervously", "tap fingers", "check datapad"],
                ["job offers", "dangerous cargo", "avoiding authorities"], "paranoid"),
        NPCRole("regular", ["chat quietly", "laugh", "eat/drink"],
                ["daily life", "complaints", "local news"], "friendly but cautious"),
    ],
    ZoneType.MARKET: [
        NPCRole("vendor", ["arrange goods", "call out prices", "haggle"],
                ["deals", "quality", "competition"], "persuasive"),
        NPCRole("customer", ["browse", "compare items", "negotiate"],
                ["what they're looking for", "budget concerns"], "distracted"),
        NPCRole("pickpocket", ["blend in", "watch crowds", "move carefully"],
                ["nothing—they avoid conversation"], "invisible"),
        NPCRole("guard", ["patrol", "watch crowds", "stand at attention"],
                ["rules", "warnings", "suspicions"], "authoritative"),
    ],
    ZoneType.MILITARY: [
        NPCRole("officer", ["review reports", "give orders", "inspect"],
                ["mission status", "personnel", "threats"], "commanding"),
        NPCRole("soldier", ["patrol", "maintain equipment", "guard post"],
                ["orders", "rumors", "complaints"], "disciplined but bored"),
        NPCRole("tech", ["work on console", "troubleshoot", "take notes"],
                ["technical problems", "need resources"], "focused"),
    ],
    ZoneType.DERELICT: [
        NPCRole("scavenger", ["search debris", "collect parts", "hide"],
                ["finds", "dangers", "territory"], "wary"),
        NPCRole("survivor", ["huddle", "ration supplies", "keep watch"],
                ["how they got here", "what they've lost", "escape plans"], "haunted"),
    ],
}


@dataclass
class ScheduledAction:
    """An action scheduled for a specific time."""
    time_slot: int  # Hour of day (0-23)
    action: str
    location: str


@dataclass
class SmartZone:
    """
    A zone with pre-computed NPC assignments and ambient life.
    """
    zone_id: str
    zone_type: ZoneType
    name: str
    atmosphere: str = ""  # Overall mood
    
    # NPC assignments
    assigned_roles: dict[str, NPCRole] = field(default_factory=dict)  # npc_name -> role
    npc_schedules: dict[str, list[ScheduledAction]] = field(default_factory=dict)
    
    # Current state
    current_hour: int = 12
    active_interactions: list[str] = field(default_factory=list)
    
    def assign_npcs(self, npc_names: list[str]) -> None:
        """Assign roles to NPCs in this zone."""
        available_roles = ZONE_ROLES.get(self.zone_type, [])
        if not available_roles:
            return
        
        for name in npc_names:
            role = random.choice(available_roles)
            self.assigned_roles[name] = role
    
    def generate_atmosphere(self) -> str:
        """Generate ambient description of the zone."""
        atmospheres = {
            ZoneType.BAR: [
                "dim lighting, the clink of glasses, murmured conversations",
                "stale air thick with smoke, a jukebox playing something forgotten",
                "shadowy booths, suspicious glances, the smell of cheap synth-alcohol",
            ],
            ZoneType.MARKET: [
                "a cacophony of voices, exotic smells, crowds pushing past",
                "colorful stalls, haggling voices, the clink of credits changing hands",
                "vendors calling out deals, customers clutching purchases, guards watching",
            ],
            ZoneType.MILITARY: [
                "crisp uniforms, the hum of electronics, orders barked in the distance",
                "sterile corridors, the click of boots, tension in the air",
                "weapon racks gleaming, personnel moving with purpose",
            ],
            ZoneType.DERELICT: [
                "dust motes in failing lights, the creak of settling metal",
                "shadows that move wrong, the smell of rust and decay",
                "echoes of footsteps (yours?), something dripping somewhere",
            ],
            ZoneType.WILDERNESS: [
                "alien wind, strange calls in the distance, unfamiliar stars",
                "the crunch of unknown ground, bioluminescent something in the dark",
                "vast emptiness, a horizon that feels too close or too far",
            ],
        }
        
        options = atmospheres.get(self.zone_type, ["unremarkable surroundings"])
        self.atmosphere = random.choice(options)
        return self.atmosphere
    
    def get_scene_description(self) -> str:
        """Generate a living scene description."""
        lines = [f"[SMART ZONE: {self.name}]"]
        lines.append(f"Type: {self.zone_type.value}")
        
        if self.atmosphere:
            lines.append(f"Atmosphere: {self.atmosphere}")
        
        if self.assigned_roles:
            lines.append("\nNPCs in scene:")
            for npc_name, role in list(self.assigned_roles.items())[:4]:
                behavior = random.choice(role.behaviors)
                lines.append(f"  • {npc_name} ({role.role_name}): {behavior}")
        
        return "\n".join(lines)
    
    def get_narrator_context(self) -> str:
        """Generate context for narrator about this zone."""
        lines = [f"[LIVING SCENE: {self.name}]"]
        lines.append(f"Atmosphere: {self.atmosphere}")
        lines.append("\nScene direction:")
        lines.append("- NPCs should be IN MOTION when player enters")
        lines.append("- Describe ambient actions happening around the player")
        lines.append("- The world exists before the player looks at it")
        
        if self.assigned_roles:
            lines.append("\nCast:")
            for npc_name, role in list(self.assigned_roles.items())[:3]:
                lines.append(f"  {npc_name}: {role.personality_hints}")
                lines.append(f"    Topics: {', '.join(role.dialogue_topics[:2])}")
        
        return "\n".join(lines)


# ============================================================================
# Perception System
# ============================================================================

@dataclass
class PerceptionCone:
    """
    Distance-inverse field of view for believable perception.
    Close = wide peripheral vision, Far = narrow focus.
    """
    max_range: float = 20.0  # Maximum detection range
    near_angle: float = 180.0  # FOV at close range (degrees)
    far_angle: float = 30.0  # FOV at max range (degrees)
    
    def get_fov_at_distance(self, distance: float) -> float:
        """Calculate FOV at a given distance (inverse relationship)."""
        if distance <= 0:
            return self.near_angle
        if distance >= self.max_range:
            return self.far_angle
        
        # Linear interpolation (could be made non-linear for more realism)
        t = distance / self.max_range
        return self.near_angle + (self.far_angle - self.near_angle) * t
    
    def can_see(
        self,
        distance: float,
        angle_from_forward: float,  # Degrees from forward facing
        in_cover: bool = False,
        is_moving: bool = False,
    ) -> tuple[bool, float]:
        """
        Check if a target can be seen.
        
        Returns:
            (can_see, awareness_level)
            awareness_level: 0.0 (unaware) to 1.0 (full detection)
        """
        # Out of range
        if distance > self.max_range:
            return False, 0.0
        
        # Check angle
        fov = self.get_fov_at_distance(distance)
        half_fov = fov / 2
        
        if abs(angle_from_forward) > half_fov:
            return False, 0.0
        
        # Calculate base awareness
        distance_factor = 1.0 - (distance / self.max_range)
        angle_factor = 1.0 - (abs(angle_from_forward) / half_fov)
        awareness = distance_factor * angle_factor
        
        # Modifiers
        if in_cover:
            awareness *= 0.3  # Hard to spot in cover
        if is_moving:
            awareness *= 1.5  # Movement catches eye
        
        awareness = min(1.0, max(0.0, awareness))
        
        # Threshold for detection
        detected = awareness > 0.3
        
        return detected, awareness


class PerceptionManager:
    """Manages perception for multiple NPCs."""

    def __init__(self):
        self.npc_perceptions: dict[str, PerceptionCone] = {}
        self.detection_states: dict[str, float] = {}  # npc_id -> awareness of player
        self.detection_labels: dict[str, str] = {}
        self.scene_nodes: dict[str, tuple[float, float, float]] = {}
        self.navmesh: dict[str, set[str]] = {}
        self.world_objects: dict[str, PerceptionWorldObject] = {}
        self.trigger_volumes: list[TriggerVolume] = []
        self.environment: PerceptionEnvironment = PerceptionEnvironment()

    def register_npc(
        self,
        npc_id: str,
        max_range: float = 20.0,
        alertness: float = 1.0,  # Multiplier for perception quality
    ) -> None:
        """Register an NPC with perception."""
        cone = PerceptionCone(
            max_range=max_range * alertness,
            near_angle=180.0 * alertness,
            far_angle=30.0 * alertness,
        )
        self.npc_perceptions[npc_id] = cone
        self.detection_states[npc_id] = 0.0
        self.detection_labels[npc_id] = "UNAWARE"

    # ------------------------------------------------------------------
    # Scene graph / navigation helpers
    # ------------------------------------------------------------------
    def register_scene_node(self, node_id: str, position: tuple[float, float, float]) -> None:
        """Register a node in the simplified scene graph."""
        self.scene_nodes[node_id] = position

    def connect_navmesh(self, node_a: str, node_b: str) -> None:
        """Connect two navmesh nodes to indicate reachability."""
        self.navmesh.setdefault(node_a, set()).add(node_b)
        self.navmesh.setdefault(node_b, set()).add(node_a)

    def query_navmesh(self, start: str, goal: str) -> tuple[bool, int]:
        """Breadth-first reachability query on the simplified navmesh."""
        if start not in self.navmesh or goal not in self.navmesh:
            return False, 0

        visited = {start}
        frontier = [(start, 0)]

        while frontier:
            node, depth = frontier.pop(0)
            if node == goal:
                return True, depth
            for neighbor in self.navmesh.get(node, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    frontier.append((neighbor, depth + 1))

        return False, 0

    def perform_raycast(self, source: str, target: str) -> tuple[bool, float]:
        """Simulate a raycast for line-of-sight and return confidence."""
        if source not in self.scene_nodes or target not in self.scene_nodes:
            return False, 0.0

        sx, sy, sz = self.scene_nodes[source]
        tx, ty, tz = self.scene_nodes[target]
        distance = math.sqrt((sx - tx) ** 2 + (sy - ty) ** 2 + (sz - tz) ** 2)

        # Check for occluders tagged as cover near the midpoint
        mid_point = ((sx + tx) / 2, (sy + ty) / 2, (sz + tz) / 2)
        occlusion_penalty = 0.0
        for obj in self.world_objects.values():
            if "cover" in obj.affordance_tags:
                ox, oy, oz = obj.position
                if math.dist(mid_point, (ox, oy, oz)) < 2.5:
                    occlusion_penalty += 0.25

        visibility = max(0.0, 1.0 - (distance / 50.0) - occlusion_penalty)
        visibility *= self.environment.visibility_modifier

        return visibility > 0.15, min(1.0, visibility)

    # ------------------------------------------------------------------
    # World object tagging / trigger volumes
    # ------------------------------------------------------------------
    def register_world_object(
        self, object_id: str, position: tuple[float, float, float], tags: list[str] | None = None
    ) -> None:
        """Register an object with affordance tags for perception world state."""
        obj = PerceptionWorldObject(object_id, position, set())
        if tags:
            obj.add_tags(*tags)
        self.world_objects[object_id] = obj

    def tag_object(self, object_id: str, *tags: str) -> None:
        """Add affordance tags to an existing object."""
        if object_id not in self.world_objects:
            return
        self.world_objects[object_id].add_tags(*tags)

    def add_trigger_volume(self, name: str, center: tuple[float, float, float], radius: float, loudness: float = 1.0) -> None:
        self.trigger_volumes.append(TriggerVolume(name, center, radius, loudness))

    def check_trigger_volumes(self, position: tuple[float, float, float], sound_level: float = 1.0) -> list[str]:
        """Return list of trigger names that fired based on listener position and loudness."""
        activated = []
        for trigger in self.trigger_volumes:
            if trigger.contains(position):
                effective_loudness = sound_level * trigger.loudness * self.environment.hearing_modifier
                if effective_loudness > 0.25:
                    activated.append(trigger.name)
        return activated

    # ------------------------------------------------------------------
    # Environment and saliency
    # ------------------------------------------------------------------
    def set_environment(self, time_of_day: str | None = None, weather: str | None = None) -> None:
        if time_of_day:
            self.environment.time_of_day = time_of_day
        if weather:
            self.environment.weather = weather
        self.environment.compute_modifiers()

    def compute_saliency(
        self,
        is_moving: bool,
        sound_level: float,
        is_quest_target: bool = False,
        is_clutter: bool = False,
    ) -> float:
        """Calculate attention priority score."""
        saliency = 0.0
        if is_moving:
            saliency += 0.35
        if sound_level > 0.1:
            saliency += min(0.4, sound_level)
        if is_quest_target:
            saliency += 0.4
        if is_clutter:
            saliency -= 0.25

        return max(0.0, min(1.0, saliency))

    def update_detection(
        self,
        npc_id: str,
        player_distance: float,
        player_angle: float,
        player_in_cover: bool = False,
        player_moving: bool = False,
        player_position: tuple[float, float, float] | None = None,
        player_node: str | None = None,
        listener_node: str | None = None,
        sound_level: float = 0.0,
        is_quest_target: bool = False,
        is_background_clutter: bool = False,
    ) -> dict:
        """
        Update detection state for an NPC.
        
        Returns detection info.
        """
        if npc_id not in self.npc_perceptions:
            return {"detected": False, "awareness": 0.0}

        cone = self.npc_perceptions[npc_id]
        detected, awareness = cone.can_see(
            player_distance, player_angle, player_in_cover, player_moving
        )

        # Scene graph line-of-sight check supplements cone detection
        los_confidence = 1.0
        if player_node and listener_node:
            los_detected, los_confidence = self.perform_raycast(listener_node, player_node)
            detected = detected and los_detected
            awareness *= los_confidence

        # Navmesh reachability can nudge confidence
        navmesh_reachable = True
        if listener_node and player_node:
            navmesh_reachable, hops = self.query_navmesh(listener_node, player_node)
            if not navmesh_reachable:
                awareness *= 0.8
            else:
                awareness *= max(0.6, 1.0 - (hops * 0.05))

        # Sound cues from trigger volumes
        active_triggers = []
        if player_position:
            active_triggers = self.check_trigger_volumes(player_position, sound_level)
            if active_triggers:
                awareness += 0.15 * len(active_triggers)

        # Environment modifiers (weather/time-of-day)
        awareness *= self.environment.visibility_modifier

        # Attention saliency
        saliency = self.compute_saliency(
            is_moving=player_moving,
            sound_level=sound_level * self.environment.hearing_modifier,
            is_quest_target=is_quest_target,
            is_clutter=is_background_clutter,
        )
        awareness = min(1.0, awareness + saliency * 0.4)
        
        # Smooth awareness transitions
        current = self.detection_states.get(npc_id, 0.0)
        if awareness > current:
            # Awareness increases quickly
            new_awareness = min(1.0, current + (awareness - current) * 0.3)
        else:
            # Awareness decreases slowly
            new_awareness = max(0.0, current - 0.05)
        
        self.detection_states[npc_id] = new_awareness
        
        # Detection states
        if new_awareness > 0.9:
            state = "ALERT"
        elif new_awareness > 0.6:
            state = "SUSPICIOUS"
        elif new_awareness > 0.3:
            state = "CURIOUS"
        else:
            state = "UNAWARE"

        self.detection_labels[npc_id] = state

        return {
            "detected": detected,
            "awareness": new_awareness,
            "state": state,
            "saliency": saliency,
            "triggers": active_triggers,
            "navmesh_reachable": navmesh_reachable,
        }

    # ------------------------------------------------------------------
    # Debugging and snapshots
    # ------------------------------------------------------------------
    def snapshot(self) -> PerceptionSnapshot:
        return PerceptionSnapshot(
            timestamp=time.time(),
            detection_states=dict(self.detection_states),
            detection_labels=dict(self.detection_labels),
            world_objects={obj_id: set(obj.affordance_tags) for obj_id, obj in self.world_objects.items()},
            environment=self.environment,
            active_triggers=[t.name for t in self.trigger_volumes],
            navmesh_nodes=len(self.navmesh),
            scene_nodes=len(self.scene_nodes),
        )

    def get_stealth_context(self) -> str:
        """Generate stealth context for narrator."""
        if not self.detection_states:
            return ""
        
        lines = ["[STEALTH STATUS]"]
        
        for npc_id, awareness in self.detection_states.items():
            if awareness > 0.3:
                if awareness > 0.9:
                    lines.append(f"• {npc_id}: FULLY ALERT - knows player location")
                elif awareness > 0.6:
                    lines.append(f"• {npc_id}: SUSPICIOUS - actively searching")
                else:
                    lines.append(f"• {npc_id}: CURIOUS - heard/saw something")
        
        if len(lines) == 1:
            lines.append("All clear - no NPCs aware of player")
        
        return "\n".join(lines)


# ============================================================================
# Smart Zone Manager
# ============================================================================

class SmartZoneManager:
    """Manages all smart zones in the game world."""
    
    def __init__(self):
        self.zones: dict[str, SmartZone] = {}
        self.current_zone: str | None = None
        self.perception: PerceptionManager = PerceptionManager()
    
    def create_zone(
        self,
        zone_id: str,
        zone_type: ZoneType,
        name: str,
        npc_names: list[str] = None,
    ) -> SmartZone:
        """Create and populate a smart zone."""
        zone = SmartZone(
            zone_id=zone_id,
            zone_type=zone_type,
            name=name,
        )
        
        zone.generate_atmosphere()
        
        if npc_names:
            zone.assign_npcs(npc_names)
        
        self.zones[zone_id] = zone
        return zone
    
    def enter_zone(self, zone_id: str) -> str:
        """Enter a zone and get its living scene description."""
        if zone_id not in self.zones:
            return "[Unknown zone]"
        
        self.current_zone = zone_id
        zone = self.zones[zone_id]
        
        return zone.get_scene_description()
    
    def get_current_zone_context(self) -> str:
        """Get narrator context for current zone."""
        if not self.current_zone or self.current_zone not in self.zones:
            return ""
        
        zone = self.zones[self.current_zone]
        return zone.get_narrator_context()
    
    def to_dict(self) -> dict:
        return {
            "zones": {
                zid: {
                    "zone_type": z.zone_type.value,
                    "name": z.name,
                    "atmosphere": z.atmosphere,
                    "assigned_roles": {
                        npc: role.role_name
                        for npc, role in z.assigned_roles.items()
                    },
                }
                for zid, z in self.zones.items()
            },
            "current_zone": self.current_zone,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SmartZoneManager":
        manager = cls()
        
        for zid, zdata in data.get("zones", {}).items():
            zone_type = ZoneType(zdata.get("zone_type", "bar"))
            zone = SmartZone(
                zone_id=zid,
                zone_type=zone_type,
                name=zdata.get("name", "Unknown"),
                atmosphere=zdata.get("atmosphere", ""),
            )
            manager.zones[zid] = zone
        
        manager.current_zone = data.get("current_zone")
        return manager


# ============================================================================
# Convenience Functions
# ============================================================================

def create_living_scene(
    zone_type: str,
    name: str,
    npc_names: list[str] = None,
) -> str:
    """Quick creation of a living scene."""
    try:
        zt = ZoneType(zone_type)
    except ValueError:
        zt = ZoneType.BAR
    
    manager = SmartZoneManager()
    zone = manager.create_zone("temp", zt, name, npc_names or [])
    return zone.get_scene_description()


def check_perception(
    distance: float,
    angle: float,
    in_cover: bool = False,
) -> dict:
    """Quick perception check."""
    cone = PerceptionCone()
    detected, awareness = cone.can_see(distance, angle, in_cover)
    return {"detected": detected, "awareness": awareness}


def debug_perception_snapshot(manager: PerceptionManager) -> str:
    """Return a formatted perception snapshot for console overlays."""
    return manager.snapshot().as_text()
