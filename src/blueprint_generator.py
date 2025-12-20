"""
Tactical Blueprint Generator.

Generates AI prompts and tactical data for blueprint map generation.
Extracts zone layouts, cover spots, NPC positions, and entry points.
"""

from typing import Any
from src.smart_zones import ZoneType


# ============================================================================
# Zone Tactical Data
# ============================================================================

ZONE_COVER_SPOTS: dict[str, list[str]] = {
    ZoneType.BAR: [
        "Bar counter (full cover)",
        "Tables (half cover)", 
        "Support columns (full cover)",
        "Booths (3/4 cover)",
        "Bottle racks (concealment)"
    ],
    ZoneType.MARKET: [
        "Vendor stalls (half cover)",
        "Cargo crates (full cover)",
        "Awning supports (minimal cover)",
        "Crowds (concealment only)",
        "Parked vehicles (full cover)"
    ],
    ZoneType.RESIDENTIAL: [
        "Furniture (half cover)",
        "Doorways (3/4 cover)",
        "Beds and couches (half cover)",
        "Kitchen counters (full cover)"
    ],
    ZoneType.INDUSTRIAL: [
        "Machinery (full cover)",
        "Pipes and conduits (half cover)",
        "Storage containers (full cover)",
        "Catwalks (minimal cover)",
        "Control stations (3/4 cover)"
    ],
    ZoneType.MILITARY: [
        "Barricades (full cover)",
        "Equipment crates (full cover)",
        "Blast shields (full cover)",
        "Doorway bunkers (3/4 cover)",
        "Armored positions (full cover)"
    ],
    ZoneType.DERELICT: [
        "Debris piles (half cover)",
        "Collapsed walls (full cover)",
        "Wreckage (variable cover)",
        "Exposed beams (minimal cover)",
        "Rubble mounds (half cover)"
    ],
    ZoneType.WILDERNESS: [
        "Trees and rocks (full cover)",
        "Boulders (full cover)",
        "Dense vegetation (concealment)",
        "Terrain elevation (half cover)",
        "Natural formations (variable)"
    ]
}

ZONE_ENTRY_POINTS: dict[str, list[str]] = {
    ZoneType.BAR: ["Main entrance", "Back door", "Service entrance"],
    ZoneType.MARKET: ["Street access (multiple)", "Loading dock", "Alley exits"],
    ZoneType.RESIDENTIAL: ["Front door", "Back door", "Windows", "Fire escape"],
    ZoneType.INDUSTRIAL: ["Main bay doors", "Personnel entrance", "Maintenance tunnels"],
    ZoneType.MILITARY: ["Checkpoint entrance", "Emergency exits", "Ventilation shafts"],
    ZoneType.DERELICT: ["Multiple breaches", "Collapsed sections", "Original entrances"],
    ZoneType.WILDERNESS: ["Open terrain (all directions)", "Paths and trails"]
}

ZONE_LAYOUT_DESCRIPTIONS: dict[str, str] = {
    ZoneType.BAR: "Rectangular space with central bar counter, scattered tables, booths along walls, dim atmospheric lighting",
    ZoneType.MARKET: "Open bazaar layout with vendor stalls in rows, wide central aisle, cramped side passages, overhead awnings",
    ZoneType.RESIDENTIAL: "Apartment or hab-unit with rooms connected by hallways, furniture clusters, natural chokepoints at doorways",
    ZoneType.INDUSTRIAL: "Large warehouse or factory floor with machinery arrays, cargo storage, elevated catwalks, low lighting",
    ZoneType.MILITARY: "Fortified structure with defensive positions, clear sightlines, reinforced cover positions, controlled access",
    ZoneType.DERELICT: "Ruined structure with collapsed sections, debris fields, unstable terrain, shadows and blind spots",
    ZoneType.WILDERNESS: "Natural terrain with vegetation, rocks, elevation changes, limited artificial structures"
}


# ============================================================================
# Tactical Data Extraction
# ============================================================================

def _resolve_zone_type(zone_type: str | ZoneType) -> ZoneType | None:
    """Convert string zone type to ZoneType enum."""
    if isinstance(zone_type, ZoneType):
        return zone_type
    try:
        return ZoneType(zone_type.lower())
    except (ValueError, AttributeError):
        return None


def extract_cover_spots(zone_type: str | ZoneType) -> list[str]:
    """Get cover spots for a zone type."""
    resolved = _resolve_zone_type(zone_type)
    return ZONE_COVER_SPOTS.get(resolved, ["Scattered obstacles (half cover)"])


def extract_entry_points(zone_type: str | ZoneType) -> list[str]:
    """Get entry/exit points for a zone type."""
    resolved = _resolve_zone_type(zone_type)
    return ZONE_ENTRY_POINTS.get(resolved, ["Single entrance/exit"])


def get_zone_layout_description(zone_type: str | ZoneType) -> str:
    """Get base layout description for a zone type."""
    resolved = _resolve_zone_type(zone_type)
    return ZONE_LAYOUT_DESCRIPTIONS.get(resolved, "Generic interior space")


def get_npc_disposition_color(npc: dict[str, Any]) -> str:
    """Determine NPC color based on disposition."""
    disposition = npc.get("disposition", "neutral")
    role = npc.get("role", "").lower()
    
    # Check for hostility indicators
    if disposition in ["hostile", "enemy", "aggressive"]:
        return "red"
    elif disposition in ["ally", "friendly", "companion"]:
        return "green"
    elif "guard" in role or "security" in role or "enforcer" in role:
        return "orange"  # Potentially hostile
    else:
        return "yellow"  # Neutral


def calculate_npc_grid_position(
    npc_index: int, 
    total_npcs: int, 
    image_width: int, 
    image_height: int
) -> tuple[int, int]:
    """Calculate grid position for an NPC marker."""
    # Distribute NPCs in a semicircle in upper half of image
    import math
    
    margin = 80
    usable_width = image_width - 2 * margin
    usable_height = (image_height // 2) - margin
    
    if total_npcs == 1:
        return (image_width // 2, image_height // 3)
    
    # Arc from left to right
    angle = math.pi * (npc_index + 1) / (total_npcs + 1)
    x = margin + int(usable_width * (1 - math.cos(angle)) / 2)
    y = margin + int(usable_height * (1 - math.sin(angle)))
    
    return (x, y)


def calculate_movement_range(character_speed: int = 30, grid_size: int = 40) -> int:
    """
    Calculate movement range in pixels.
    
    Args:
        character_speed: Character movement speed in feet (default 30ft)
        grid_size: Size of one grid square in pixels (default 40px = 5ft)
        
    Returns:
        Movement range radius in pixels
    """
    # Assume 5ft per grid square
    feet_per_square = 5
    squares = character_speed // feet_per_square
    return squares * grid_size


def calculate_vision_cone(
    npc_position: tuple[int, int],
    facing_angle: float = 0.0,
    fov_degrees: float = 90.0,
    max_range: int = 200
) -> list[tuple[int, int]]:
    """
    Calculate vision cone polygon points for an NPC.
    
    Args:
        npc_position: (x, y) position of NPC
        facing_angle: Direction NPC is facing in degrees (0 = right, 90 = down)
        fov_degrees: Field of view angle in degrees
        max_range: Maximum vision range in pixels
        
    Returns:
        List of (x, y) points forming the vision cone polygon
    """
    import math
    
    x, y = npc_position
    
    # Convert to radians
    facing_rad = math.radians(facing_angle)
    half_fov = math.radians(fov_degrees / 2)
    
    # Start at NPC position
    points = [(x, y)]
    
    # Generate arc points
    num_arc_points = 20
    for i in range(num_arc_points + 1):
        angle = facing_rad - half_fov + (2 * half_fov * i / num_arc_points)
        px = x + max_range * math.cos(angle)
        py = y + max_range * math.sin(angle)
        points.append((int(px), int(py)))
    
    # Close the polygon
    points.append((x, y))
    
    return points


# ============================================================================
# Prompt Generation
# ============================================================================

def generate_tactical_prompt(game_state: dict[str, Any]) -> str:
    """
    Generate a detailed prompt for AI tactical map generation.
    
    Args:
        game_state: Full game state dictionary
        
    Returns:
        Detailed prompt string for image generation
    """
    world = game_state.get("world", {})
    memory = game_state.get("memory", {})
    combat = game_state.get("combat_state", {})
    
    # Get zone info
    location = world.get("current_location", "Unknown Location")
    zone_type = world.get("location_type", "residential")
    
    # Get NPCs
    npcs = world.get("npcs", [])
    npc_descriptions = []
    for npc in npcs[:6]:  # Limit to 6 NPCs for clarity
        name = npc.get("name", "Unknown")
        role = npc.get("role", "bystander")
        color = get_npc_disposition_color(npc)
        npc_descriptions.append(f"- {name} ({role}): marked with {color} circle")
    
    # Get tactical elements
    cover_spots = extract_cover_spots(zone_type)
    entry_points = extract_entry_points(zone_type)
    layout = get_zone_layout_description(zone_type)
    
    # Build prompt
    prompt_parts = [
        "Create a top-down tactical blueprint/battle map in the style of a D&D encounter map.",
        "",
        f"SETTING: {location}",
        f"ZONE TYPE: {zone_type.upper()}",
        f"LAYOUT: {layout}",
        "",
        "VISUAL REQUIREMENTS:",
        "- Top-down view with slight isometric angle",
        "- Grid overlay (5ft/1.5m squares)",
        "- Clean, readable tactical style",
        "- Muted color palette (grays, browns, dark blues)",
        "- Clear walls and structural boundaries",
        "",
        "COVER POSITIONS:",
    ]
    
    for cover in cover_spots[:4]:
        prompt_parts.append(f"  • {cover}")
    
    prompt_parts.extend([
        "",
        "ENTRY/EXIT POINTS:",
    ])
    
    for entry in entry_points[:3]:
        prompt_parts.append(f"  • {entry}")
    
    if npc_descriptions:
        prompt_parts.extend([
            "",
            "CHARACTER MARKERS (colored circles):",
            "- Player: BLUE circle at bottom center",
        ])
        prompt_parts.extend(npc_descriptions)
    
    # Add combat context if active
    if combat.get("in_combat") or world.get("combat_active"):
        prompt_parts.extend([
            "",
            "COMBAT ACTIVE:",
            "- Show line-of-sight cones",
            "- Highlight cover quality",
            "- Mark danger zones in red tint"
        ])
    
    # Add scene context
    scene = memory.get("current_scene", "")
    if scene:
        prompt_parts.extend([
            "",
            f"SCENE CONTEXT: {scene[:200]}..."
        ])
    
    return "\n".join(prompt_parts)


def extract_tactical_metadata(game_state: dict[str, Any]) -> dict[str, Any]:
    """
    Extract tactical metadata for overlay and UI display.
    
    Args:
        game_state: Full game state dictionary
        
    Returns:
        Dictionary with cover spots, entry points, NPC positions, etc.
    """
    world = game_state.get("world", {})
    zone_type = world.get("location_type", "residential")
    npcs = world.get("npcs", [])
    
    # Process NPCs with positions and colors
    npc_data = []
    for i, npc in enumerate(npcs[:6]):
        npc_data.append({
            "name": npc.get("name", "Unknown"),
            "role": npc.get("role", "bystander"),
            "disposition": npc.get("disposition", "neutral"),
            "color": get_npc_disposition_color(npc),
            "index": i
        })
    
    return {
        "location": world.get("current_location", "Unknown"),
        "zone_type": zone_type,
        "cover_spots": extract_cover_spots(zone_type),
        "entry_points": extract_entry_points(zone_type),
        "layout": get_zone_layout_description(zone_type),
        "npcs": npc_data,
        "in_combat": world.get("combat_active", False)
    }


def generate_cache_key(game_state: dict[str, Any]) -> str:
    """Generate a cache key based on relevant game state."""
    import hashlib
    
    world = game_state.get("world", {})
    npcs = world.get("npcs", [])
    
    key_parts = [
        world.get("current_location", ""),
        world.get("location_type", ""),
        str(len(npcs)),
        str(world.get("combat_active", False))
    ]
    
    # Include NPC names for cache invalidation on NPC changes
    for npc in npcs[:6]:
        key_parts.append(npc.get("name", ""))
    
    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()[:16]


# ============================================================================
# Ship Blueprints
# ============================================================================

SHIP_LAYOUTS = {
    "freighter": {
        "hull_shape": "freighter",
        "dimensions": (500, 700),
        "rooms": {
            "bridge": {"pos": (250, 80), "size": (80, 60), "name": "Bridge"},
            "engineering": {"pos": (250, 600), "size": (120, 100), "name": "Engineering"},
            "cargo_bay": {"pos": (250, 350), "size": (180, 200), "name": "Main Cargo"},
            "crew_quarters": {"pos": (120, 250), "size": (60, 120), "name": "Quarters"},
            "medical_bay": {"pos": (380, 250), "size": (60, 80), "name": "Med Bay"},
            "mess_hall": {"pos": (380, 150), "size": (60, 60), "name": "Mess Hall"},
            "airlock": {"pos": (450, 350), "size": (40, 40), "name": "Airlock"},
        }
    },
    "fighter": {
        "hull_shape": "fighter",
        "dimensions": (400, 500),
        "rooms": {
            "bridge": {"pos": (200, 150), "size": (60, 80), "name": "Cockpit"},
            "engineering": {"pos": (200, 400), "size": (80, 80), "name": "Engine Core"},
            "weapons": {"pos": (100, 250), "size": (40, 60), "name": "Weapon Bay"},
            "systems": {"pos": (300, 250), "size": (40, 60), "name": "Systems"}
        }
    },
    "explorer": {
        "hull_shape": "explorer",
        "dimensions": (450, 650),
        "rooms": {
            "bridge": {"pos": (225, 70), "size": (70, 70), "name": "Bridge"},
            "engineering": {"pos": (225, 550), "size": (100, 80), "name": "Engineering"},
            "lab": {"pos": (150, 300), "size": (60, 100), "name": "Science Lab"},
            "sensors": {"pos": (300, 300), "size": (60, 100), "name": "Sensor Array"},
            "cargo": {"pos": (225, 450), "size": (100, 80), "name": "Stores"}
        }
    }
}

def extract_ship_metadata(game_state: dict[str, Any]) -> dict[str, Any]:
    """
    Extract ship configuration and status for blueprint generation.
    """
    world_state = game_state.get("world", {})
    if not isinstance(world_state, dict) and hasattr(world_state, "dict"):
        world_state = world_state.dict()
        
    ship_data = world_state.get("ship", {})
    if not isinstance(ship_data, dict) and hasattr(ship_data, "dict"):
        ship_data = ship_data.dict()
        
    class_type = ship_data.get("class_type", "freighter")
    layout = SHIP_LAYOUTS.get(class_type, SHIP_LAYOUTS["freighter"])
    
    # Map modules to layout rooms if possible, or use default layout
    modules = ship_data.get("modules", [])
    
    # Calculate damage overlays
    hull_percent = ship_data.get("hull_integrity", 100) / max(1, ship_data.get("max_hull", 100))
    damage_intensity = 1.0 - hull_percent
    
    # Calculate crew positions
    crew = []
    npcs = world_state.get("npcs", [])
    for npc in npcs:
        # Check if they are on the ship (or if they are crew)
        role = npc.get("role", "").lower()
        is_crew = "crew" in role or npc.get("on_ship", False)
        
        if is_crew:
            # Simple heuristic for room assignment
            room_assignment = "crew_quarters"
            if any(k in role for k in ["pilot", "captain", "bridge", "navigator"]):
                room_assignment = "bridge"
            elif any(k in role for k in ["engineer", "mechanic", "technician"]):
                room_assignment = "engineering"
            elif any(k in role for k in ["medic", "doctor", "scientist"]):
                room_assignment = "medical_bay" if "medical_bay" in layout["rooms"] else "lab" if "lab" in layout["rooms"] else "crew_quarters"
            elif any(k in role for k in ["cook", "chef"]):
                room_assignment = "mess_hall" if "mess_hall" in layout["rooms"] else "crew_quarters"
            elif "cargo" in role:
                room_assignment = "cargo_bay" if "cargo_bay" in layout["rooms"] else "cargo" if "cargo" in layout["rooms"] else "crew_quarters"

            crew.append({
                "name": npc.get("name"),
                "role": role,
                "room": room_assignment,
                "color": npc.get("color", "yellow") 
            })

    return {
        "name": ship_data.get("name", "Unknown Ship"),
        "class_type": class_type,
        "layout": layout,
        "integrity": {
            "hull": ship_data.get("hull_integrity", 100),
            "max": ship_data.get("max_hull", 100),
            "percent": int(hull_percent * 100)
        },
        "damage_level": "critical" if damage_intensity > 0.7 else "heavy" if damage_intensity > 0.4 else "moderate" if damage_intensity > 0.1 else "none",
        "alerts": ship_data.get("active_alerts", []),
        "crew": crew
    }


def calculate_movement_range(character_speed: int = 30) -> int:
    """
    Calculate movement range in pixels for tactical display.
    
    Args:
        character_speed: Character movement speed in feet (default 30ft)
    
    Returns:
        Movement range radius in pixels
    """
    # Convert feet to grid squares (5ft per square)
    squares = character_speed // 5
    
    # Convert squares to pixels (40px per square)
    pixels = squares * 40
    
    return pixels


def generate_cache_key(game_state: dict[str, Any]) -> str:
    """
    Generate a unique cache key for the current tactical situation.
    """
    world_state = game_state.get("world", {})
    if not isinstance(world_state, dict) and hasattr(world_state, "dict"):
        world_state = world_state.dict()
        
    location = world_state.get("current_location", "unknown")
    npcs = world_state.get("npcs", [])
    
    # Hash of location and NPC dispositions
    npc_fingerprint = "|".join([f"{n.get('name')}:{n.get('disposition')}" for n in npcs])
    
    import hashlib
    combined = f"{location}_{npc_fingerprint}"
    return f"tactical_{hashlib.md5(combined.encode()).hexdigest()}"

