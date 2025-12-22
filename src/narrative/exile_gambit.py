"""
The Exile Gambit Data Module.
Defines the ship as a character, including its zones, environmental storytelling,
and dynamic responses to game state.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple

@dataclass
class EnvironmentalDetail:
    """A specific clickable or observable element in a zone."""
    id: str
    name: str # The visible object
    story_text: str # What it tells (the lore/meaning)
    is_discovered: bool = False

@dataclass
class ArchetypeSeed:
    """A narrative seed that only appears for specific archetypes."""
    archetype_role: str # e.g. "Controller", "Ghost", "Judge"
    description: str

@dataclass
class ShipZone:
    """A distinct area of the ship with specific atmosphere and storytelling."""
    id: str
    name: str
    function: str
    keeper: str # Character who "keeps" this zone
    atmosphere: str
    environmental_details: List[EnvironmentalDetail]
    archetype_seeds: List[ArchetypeSeed] = field(default_factory=list)
    current_status: str = "normal" # normal, damaged, sealed, etc.

@dataclass
class ShipIdentity:
    name: str
    class_type: str
    age: str
    tenure: str
    status: str
    metaphor_themes: Dict[str, str]

# ============================================================================
# DATA POPULATION
# ============================================================================

SHIP_IDENTITY = ShipIdentity(
    name="Exile Gambit",
    class_type="Wanderer-class Freighter",
    age="22 years",
    tenure="12 years",
    status="Functional but worn; held together by Kai's genius and hope",
    metaphor_themes={
        "Second Chances": "Old, discarded ship given new purpose; like its crew",
        "Hidden Damage": "Patched exterior hiding deeper structural issues; like its people",
        "Fragile Connection": "Systems interdependent; one failure cascades; like relationships",
        "Trapped Together": "Confined space, can't escape each other; pressure cooker for truth",
        "Journey Without Destination": "Always moving, never arriving; fugitive existence"
    }
)

# 1. THE BRIDGE
THE_BRIDGE = ShipZone(
    id="bridge",
    name="The Bridge",
    function="Navigation and control center",
    keeper="Torres (primary)",
    atmosphere="Clean, professional, controlled",
    environmental_details=[
        EnvironmentalDetail("bridge_chair", "Captain's chair", "Empty now. No one sits in it. The crew navigates around it like a grave."),
        EnvironmentalDetail("bridge_charts", "Navigation charts", "Reyes's obsessive annotations visible. Routes planned, contingencies mapped."),
        EnvironmentalDetail("bridge_torres_notes", "Torres's additions", "Newer annotations in different handwriting. She's taking over, reluctantly."),
        EnvironmentalDetail("bridge_screens", "View screens", "Stars, void, distance. The nothing Ember contemplates."),
        EnvironmentalDetail("bridge_console", "Manual override console", "Worn from use. Someone liked to control things directly.")
    ],
    archetype_seeds=[
        ArchetypeSeed("Controller", "The override console. Player notices it's worn smooth. 'Someone needed to control everything manually.'"),
        ArchetypeSeed("Controller", "A navigation log: 'Adjusted course by 0.003 degrees. Unnecessary but it felt right.'"),
        ArchetypeSeed("Ghost", "The empty chair. The absence at the center."),
        ArchetypeSeed("Ghost", "Torres's log: 'The captain spent hours here. Just watching the stars. I never understood what he was looking for.'")
    ]
)

# 2. CAPTAIN'S QUARTERS
CAPTAINS_QUARTERS = ShipZone(
    id="quarters_captain",
    name="Captain's Quarters",
    function="Private living space / office",
    keeper="Sealed (Investigation)",
    atmosphere="A life interrupted. Sealed since death.",
    environmental_details=[
        EnvironmentalDetail("cap_bed", "Unmade bed", "He died in the night. The sheets are still rumpled."),
        EnvironmentalDetail("cap_journal", "Journal on desk", "His private thoughts. Fragmentary. Revealing."),
        EnvironmentalDetail("cap_photo", "Photo on wall", "Reyes with someone in prison uniform. Both smiling. He forgave someone once."),
        EnvironmentalDetail("cap_maria", "Maria's effects", "A scarf. A wedding band. A faded photo. She's been dead for years, but he kept her close."),
        EnvironmentalDetail("cap_meds", "Medical supplies", "Hidden in a drawer. His secret illness. Self-treatment he didn't tell anyone about."),
        EnvironmentalDetail("cap_controls", "Environmental controls", "A panel by the bed. This is how Yuki killed him.")
    ],
    archetype_seeds=[
        ArchetypeSeed("Controller", "His journal shows obsessive planning. Contingencies for everything. It wasn't enough."),
        ArchetypeSeed("Judge", "The photo of the person he forgave. 'What did they do? Why forgive them?'"),
        ArchetypeSeed("Fugitive", "Travel documents. Old identities. Reyes had a past too."),
        ArchetypeSeed("Savior", "A list of crew members with notes: 'Torres - trust issues, work on.' 'Kai - addiction, intervention needed.' He was managing everyone.")
    ]
)

# 3. ENGINEERING
ENGINEERING = ShipZone(
    id="engineering",
    name="Engineering",
    function="Power, life support, propulsion",
    keeper="Kai",
    atmosphere="Chaos contained. Barely.",
    environmental_details=[
        EnvironmentalDetail("eng_rigged", "Jury-rigged systems", "Nothing is factory standard. Everything has been modified, patched, reimagined. Genius at work."),
        EnvironmentalDetail("eng_stash", "Hidden stash", "Kai's substances. Hidden in a panel. Not hidden well enough."),
        EnvironmentalDetail("eng_logs", "The logs", "System records. Somewhere in here is the evidence of sabotage."),
        EnvironmentalDetail("eng_fuel", "Fuel readings", "Off. Someone's been skimming."),
        EnvironmentalDetail("eng_cot", "A cot", "Kai sleeps here sometimes. More often lately."),
        EnvironmentalDetail("eng_drawings", "Drawings", "Kai doodles when he's thinking. Complex, beautiful patterns. A mind that never rests.")
    ],
    archetype_seeds=[
        ArchetypeSeed("Controller", "A system labeled 'REDUNDANCY OVERRIDE - TRUST THE AUTOMATION.' Kai's note: 'No. Check manually.'"),
        ArchetypeSeed("Hedonist", "The stash. The cot. The signs of someone living half-asleep."),
        ArchetypeSeed("Fugitive", "The stash. The cot. The signs of someone living half-asleep."), # Shared seed
        ArchetypeSeed("Perfectionist", "A component labeled '98.6% efficient.' A note in different handwriting (Kai's): 'Good enough. Ship still flies.'")
    ]
)

# 4. MED BAY
MED_BAY = ShipZone(
    id="med_bay",
    name="Med Bay",
    function="Medical treatment and examination",
    keeper="Dr. Okonkwo",
    atmosphere="Clinical but warm. Professional distance with hidden humanity.",
    environmental_details=[
        EnvironmentalDetail("med_table", "Autopsy table", "Recently used. The captain's body was here."),
        EnvironmentalDetail("med_notes", "Okonkwo's notes", "Clinical. Detached. But between the lines—grief."),
        EnvironmentalDetail("med_cabinet", "Treatment cabinet", "Organized precisely. One section locked: the captain's private medications."),
        EnvironmentalDetail("med_equip", "Old equipment", "Not cutting-edge, but well-maintained. She makes do."),
        EnvironmentalDetail("med_plant", "A plant", "Something alive in this room of dealing with death. She tends it carefully."),
        EnvironmentalDetail("med_photo", "Photo hidden in desk", "Okonkwo younger. Medical coat. A different hospital. Her past life.")
    ],
    archetype_seeds=[
        ArchetypeSeed("Ghost", "The plant. Life maintained at a distance. Cared for without intimacy."),
        ArchetypeSeed("Martyr", "A log: 'The crew doesn't need to know how much I worry. It would burden them.'"),
        ArchetypeSeed("Judge", "The autopsy notes. The precision of diagnosis. The attempt to categorize even death.")
    ]
)

# 5. CARGO BAY
CARGO_BAY = ShipZone(
    id="cargo_bay",
    name="Cargo Bay",
    function="Storage, inventory, shipping",
    keeper="Vasquez",
    atmosphere="Organized chaos. Things hiding in plain sight.",
    environmental_details=[
        EnvironmentalDetail("cargo_crate", "The sealed crate", "Vasquez's secret cargo. Medical supplies. The connection to everything."),
        EnvironmentalDetail("cargo_manifest", "Manifest discrepancies", "Weight doesn't match inventory. Someone's hiding something."),
        EnvironmentalDetail("cargo_org", "Vasquez's organization", "Impeccable on the surface. Convenient gaps if you know where to look."),
        EnvironmentalDetail("cargo_emerg", "Emergency supplies", "Survival gear. Escape pods accessed from here. Exit strategy."),
        EnvironmentalDetail("cargo_marks", "Old cargo marks", "Previous shipments. The ship has carried many things."),
        EnvironmentalDetail("cargo_corner", "A hidden corner", "Ember's hiding place when she was a stowaway. She still goes there sometimes.")
    ],
    archetype_seeds=[
        ArchetypeSeed("Manipulator", "Double manifests. Official and actual. 'Flexibility in accounting.'"),
        ArchetypeSeed("Fugitive", "The emergency supplies. The escape pod access. Always ready to run."),
        ArchetypeSeed("Impostor", "Cargo labeled one thing, containing another. Surface vs. truth.")
    ]
)

# 6. CREW QUARTERS
# Consolidating individual quarters into a single zone for simplicity,
# but allowing drill-down via details.
CREW_QUARTERS = ShipZone(
    id="quarters_crew",
    name="Crew Quarters",
    function="Living spaces for crew",
    keeper="Individual",
    atmosphere="Private spaces. Each reflects its owner.",
    environmental_details=[
        EnvironmentalDetail("q_torres", "Torres's Quarters", "Military precision. A single item: brother's insignia. Locked drawer."),
        EnvironmentalDetail("q_kai", "Kai's Quarters", "Chaos. Papers, parts. Drug paraphernalia. Complex drawings."),
        EnvironmentalDetail("q_okonkwo", "Okonkwo's Quarters", "Sparse. Hidden photo of the child she saved. Marked medical texts."),
        EnvironmentalDetail("q_vasquez", "Vasquez's Quarters", "Comfortable, staged. Hidden false documents."),
        EnvironmentalDetail("q_ember", "Ember's Quarters", "Almost nothing. A collection of small objects. A journal."),
        EnvironmentalDetail("q_yuki", "Yuki's Quarters", "Bare, impersonal. Hidden corporate ID and go-bag.")
    ],
    archetype_seeds=[] # Individual quarters carry their own implied seeds
)

# 7. COMMON AREA / MESS HALL
COMMON_AREA = ShipZone(
    id="common_area",
    name="Common Area",
    function="Eating, gathering, community",
    keeper="Shared",
    atmosphere="The heart of the ship. Where community exists or fails.",
    environmental_details=[
        EnvironmentalDetail("mess_table", "The table", "Big enough for everyone. Signs of use—scratches, stains, history."),
        EnvironmentalDetail("mess_seat", "Captain's seat", "Empty since his death. No one takes it."),
        EnvironmentalDetail("mess_food", "Food stores", "Getting low. Tension about rationing."),
        EnvironmentalDetail("mess_games", "Board games", "Played, well-worn. Torres vs. Kai chess matches."),
        EnvironmentalDetail("mess_board", "Bulletin board", "Notices, jokes, complaints. The texture of community."),
        EnvironmentalDetail("mess_burn", "Burn marks", "From a 'Team Building Day' that went badly. Someone doesn't believe in trust exercises.")
    ],
    archetype_seeds=[
        ArchetypeSeed("Ghost", "An empty seat. Not the captain's—another one. Someone who left before."),
        ArchetypeSeed("Cynic", "The burned trust exercise poster. 'TEAM BUILDING' with scorch marks."),
        ArchetypeSeed("Connection", "The worn board games. People spent time together here. It mattered.")
    ]
)

# 8. OBSERVATION DECK
OBSERVATION_DECK = ShipZone(
    id="observation_deck",
    name="Observation Deck",
    function="Recreation, contemplation",
    keeper="Ember (unofficially)",
    atmosphere="Quiet. Sacred. The place for truth.",
    environmental_details=[
        EnvironmentalDetail("obs_window", "The window", "The void. Stars. The nothing and the everything."),
        EnvironmentalDetail("obs_corner", "Ember's corner", "A blanket. A pillow. She comes here to think."),
        EnvironmentalDetail("obs_marks", "Marks on the glass", "Someone traced constellations. Teaching someone else?"),
        EnvironmentalDetail("obs_chair", "A single chair", "Facing the window. The captain used to sit here."),
        EnvironmentalDetail("obs_writing", "Writing on the wall", "Half-erased. 'We are all—' The rest illegible."),
        EnvironmentalDetail("obs_silence", "The silence", "The ship hums elsewhere. Here, it's almost quiet.")
    ],
    archetype_seeds=[] # This zone is for major revelations
)

SHIP_ZONES = {
    "bridge": THE_BRIDGE,
    "quarters_captain": CAPTAINS_QUARTERS,
    "engineering": ENGINEERING,
    "med_bay": MED_BAY,
    "cargo_bay": CARGO_BAY,
    "quarters_crew": CREW_QUARTERS,
    "common_area": COMMON_AREA,
    "observation_deck": OBSERVATION_DECK
}

# ============================================================================
# DYNAMIC FUNCTIONS
# ============================================================================

def get_ship_data() -> Dict[str, Any]:
    """Return static ship identity and metadata."""
    return {
        "name": SHIP_IDENTITY.name,
        "class": SHIP_IDENTITY.class_type,
        "age": SHIP_IDENTITY.age,
        "tenure": SHIP_IDENTITY.tenure,
        "status": SHIP_IDENTITY.status,
        "themes": SHIP_IDENTITY.metaphor_themes
    }

def get_all_zones() -> List[Dict[str, Any]]:
    """Return summary list of all zones."""
    return [
        {
            "id": z.id,
            "name": z.name,
            "keeper": z.keeper,
            "atmosphere": z.atmosphere
        }
        for z in SHIP_ZONES.values()
    ]

def get_zone_details(zone_id: str, player_archetype: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Return full details for a zone, including archetype-specific seeds
    if an archetype is provided.
    """
    zone = SHIP_ZONES.get(zone_id)
    if not zone:
        return None

    # Filter seeds
    relevant_seeds = []
    if player_archetype:
        # Match archetype roughly (contains check or exact)
        seeds = [
            s.description 
            for s in zone.archetype_seeds 
            if s.archetype_role.lower() in player_archetype.lower() or player_archetype.lower() in s.archetype_role.lower()
        ]
        if seeds:
            relevant_seeds = seeds
    
    return {
        "id": zone.id,
        "name": zone.name,
        "function": zone.function,
        "keeper": zone.keeper,
        "atmosphere": zone.atmosphere,
        "status": zone.current_status,
        "details": [
            {"id": d.id, "name": d.name, "story": d.story_text}
            for d in zone.environmental_details
        ],
        "archetype_seeds": relevant_seeds
    }
