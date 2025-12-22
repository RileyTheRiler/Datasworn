"""
Camp Layout System.

Defines the physical structure of the camp/hub with zones, interaction spots,
and acoustic groups to prevent dialogue overlaps.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SpotType(Enum):
    """Types of interaction spots in camp."""
    SEAT = "seat"
    CHORE = "chore"
    LOOKOUT = "lookout"
    CRAFTING = "crafting"
    FIREPIT = "firepit"
    SLEEPING = "sleeping"
    STORAGE = "storage"


@dataclass
class InteractionSpot:
    """A specific spot where NPCs can be and players can interact."""
    spot_id: str
    name: str
    spot_type: SpotType
    max_occupancy: int = 1
    acoustic_group: int = 0  # Spots in same group can hear each other
    description: str = ""
    
    def to_dict(self) -> dict:
        return {
            "spot_id": self.spot_id,
            "name": self.name,
            "spot_type": self.spot_type.value,
            "max_occupancy": self.max_occupancy,
            "acoustic_group": self.acoustic_group,
            "description": self.description,
        }


@dataclass
class CampZone:
    """A zone within the camp."""
    zone_id: str
    name: str
    description: str
    interaction_spots: list[InteractionSpot] = field(default_factory=list)
    atmosphere: str = ""
    
    def get_spot(self, spot_id: str) -> Optional[InteractionSpot]:
        """Get a specific interaction spot by ID."""
        for spot in self.interaction_spots:
            if spot.spot_id == spot_id:
                return spot
        return None
    
    def get_spots_by_type(self, spot_type: SpotType) -> list[InteractionSpot]:
        """Get all spots of a specific type."""
        return [s for s in self.interaction_spots if s.spot_type == spot_type]
    
    def to_dict(self) -> dict:
        return {
            "zone_id": self.zone_id,
            "name": self.name,
            "description": self.description,
            "atmosphere": self.atmosphere,
            "interaction_spots": [s.to_dict() for s in self.interaction_spots],
        }


# =============================================================================
# CAMP LAYOUT DEFINITION
# =============================================================================

CAMP_LAYOUT = {
    "common_area": CampZone(
        zone_id="common_area",
        name="Common Area",
        description="The heart of camp. A cleared space with seating around a central firepit.",
        atmosphere="Warm, social, the smell of cooking food and coffee",
        interaction_spots=[
            InteractionSpot(
                spot_id="firepit_center",
                name="Central Firepit",
                spot_type=SpotType.FIREPIT,
                max_occupancy=6,
                acoustic_group=1,
                description="The main gathering spot. Warmth and light draw people here."
            ),
            InteractionSpot(
                spot_id="bench_north",
                name="North Bench",
                spot_type=SpotType.SEAT,
                max_occupancy=2,
                acoustic_group=1,
                description="A worn bench facing the fire."
            ),
            InteractionSpot(
                spot_id="bench_south",
                name="South Bench",
                spot_type=SpotType.SEAT,
                max_occupancy=2,
                acoustic_group=1,
                description="Another bench, slightly apart from the main group."
            ),
            InteractionSpot(
                spot_id="cooking_station",
                name="Cooking Station",
                spot_type=SpotType.CHORE,
                max_occupancy=2,
                acoustic_group=1,
                description="A makeshift kitchen area. Someone's always preparing something."
            ),
        ]
    ),
    
    "workshop": CampZone(
        zone_id="workshop",
        name="Workshop",
        description="A covered area with workbenches and tools. The sound of repairs and tinkering.",
        atmosphere="Busy, mechanical, the smell of oil and metal",
        interaction_spots=[
            InteractionSpot(
                spot_id="main_workbench",
                name="Main Workbench",
                spot_type=SpotType.CRAFTING,
                max_occupancy=2,
                acoustic_group=2,
                description="The primary repair station. Always cluttered with projects."
            ),
            InteractionSpot(
                spot_id="tool_storage",
                name="Tool Storage",
                spot_type=SpotType.STORAGE,
                max_occupancy=1,
                acoustic_group=2,
                description="Organized chaos. Tools hang on pegboards."
            ),
            InteractionSpot(
                spot_id="parts_table",
                name="Parts Table",
                spot_type=SpotType.CRAFTING,
                max_occupancy=1,
                acoustic_group=2,
                description="Salvaged components sorted into bins."
            ),
        ]
    ),
    
    "lookout_point": CampZone(
        zone_id="lookout_point",
        name="Lookout Point",
        description="A raised position overlooking the surrounding area. Good for watching and thinking.",
        atmosphere="Quiet, exposed, wind carries distant sounds",
        interaction_spots=[
            InteractionSpot(
                spot_id="observation_post",
                name="Observation Post",
                spot_type=SpotType.LOOKOUT,
                max_occupancy=2,
                acoustic_group=3,
                description="A clear view in all directions. Binoculars rest on a ledge."
            ),
            InteractionSpot(
                spot_id="quiet_corner",
                name="Quiet Corner",
                spot_type=SpotType.SEAT,
                max_occupancy=1,
                acoustic_group=3,
                description="A spot away from the main post. For those who want solitude."
            ),
        ]
    ),
    
    "sleeping_quarters": CampZone(
        zone_id="sleeping_quarters",
        name="Sleeping Quarters",
        description="Individual sleeping spaces. Privacy is respected here.",
        atmosphere="Dim, quiet, personal items make each space unique",
        interaction_spots=[
            InteractionSpot(
                spot_id="yuki_bunk",
                name="Yuki's Bunk",
                spot_type=SpotType.SLEEPING,
                max_occupancy=1,
                acoustic_group=4,
                description="Spartan and organized. A single photo tucked into the frame."
            ),
            InteractionSpot(
                spot_id="torres_bunk",
                name="Torres's Bunk",
                spot_type=SpotType.SLEEPING,
                max_occupancy=1,
                acoustic_group=4,
                description="Navigation charts pinned to the wall. A well-worn flight jacket."
            ),
            InteractionSpot(
                spot_id="kai_bunk",
                name="Kai's Bunk",
                spot_type=SpotType.SLEEPING,
                max_occupancy=1,
                acoustic_group=4,
                description="Technical manuals stacked neatly. A small plant in a recycled container."
            ),
            InteractionSpot(
                spot_id="okonkwo_bunk",
                name="Dr. Okonkwo's Bunk",
                spot_type=SpotType.SLEEPING,
                max_occupancy=1,
                acoustic_group=4,
                description="Medical texts and a journal. Everything has its place."
            ),
            InteractionSpot(
                spot_id="vasquez_bunk",
                name="Vasquez's Bunk",
                spot_type=SpotType.SLEEPING,
                max_occupancy=1,
                acoustic_group=4,
                description="Cargo manifests and a collection of small trinkets from various ports."
            ),
            InteractionSpot(
                spot_id="ember_bunk",
                name="Ember's Bunk",
                spot_type=SpotType.SLEEPING,
                max_occupancy=1,
                acoustic_group=4,
                description="Drawings and sketches. A makeshift dreamcatcher hangs above."
            ),
        ]
    ),
    
    "supply_area": CampZone(
        zone_id="supply_area",
        name="Supply Area",
        description="Where equipment and provisions are stored and maintained.",
        atmosphere="Organized, practical, the smell of canvas and preservatives",
        interaction_spots=[
            InteractionSpot(
                spot_id="inventory_station",
                name="Inventory Station",
                spot_type=SpotType.CHORE,
                max_occupancy=2,
                acoustic_group=5,
                description="Clipboard and manifests. Someone's always counting something."
            ),
            InteractionSpot(
                spot_id="equipment_rack",
                name="Equipment Rack",
                spot_type=SpotType.STORAGE,
                max_occupancy=1,
                acoustic_group=5,
                description="Gear hangs ready for deployment. Everything has a designated spot."
            ),
            InteractionSpot(
                spot_id="maintenance_corner",
                name="Maintenance Corner",
                spot_type=SpotType.CHORE,
                max_occupancy=1,
                acoustic_group=5,
                description="A small area for cleaning and repairing equipment."
            ),
        ]
    ),
    
    "meditation_spot": CampZone(
        zone_id="meditation_spot",
        name="Meditation Spot",
        description="A secluded area away from the main camp. For reflection and peace.",
        atmosphere="Serene, isolated, the sound of wind through trees",
        interaction_spots=[
            InteractionSpot(
                spot_id="reflection_seat",
                name="Reflection Seat",
                spot_type=SpotType.SEAT,
                max_occupancy=1,
                acoustic_group=6,
                description="A simple seat facing away from camp. For those who need distance."
            ),
        ]
    ),
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_zone(zone_id: str) -> Optional[CampZone]:
    """Get a camp zone by ID."""
    return CAMP_LAYOUT.get(zone_id)


def get_all_zones() -> list[CampZone]:
    """Get all camp zones."""
    return list(CAMP_LAYOUT.values())


def get_spot(zone_id: str, spot_id: str) -> Optional[InteractionSpot]:
    """Get a specific interaction spot."""
    zone = get_zone(zone_id)
    if zone:
        return zone.get_spot(spot_id)
    return None


def get_spots_in_acoustic_group(acoustic_group: int) -> list[InteractionSpot]:
    """Get all spots that can hear each other (same acoustic group)."""
    spots = []
    for zone in CAMP_LAYOUT.values():
        for spot in zone.interaction_spots:
            if spot.acoustic_group == acoustic_group:
                spots.append(spot)
    return spots


def get_available_spots(spot_type: Optional[SpotType] = None) -> list[InteractionSpot]:
    """Get all available interaction spots, optionally filtered by type."""
    spots = []
    for zone in CAMP_LAYOUT.values():
        if spot_type:
            spots.extend(zone.get_spots_by_type(spot_type))
        else:
            spots.extend(zone.interaction_spots)
    return spots


def get_camp_layout_dict() -> dict:
    """Get the entire camp layout as a dictionary for API responses."""
    return {
        zone_id: zone.to_dict()
        for zone_id, zone in CAMP_LAYOUT.items()
    }
