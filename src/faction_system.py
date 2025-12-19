"""
Dynamic Faction System

Tracks player reputation with various factions and generates
faction-influenced encounters, opportunities, and complications.

Reputation affects:
- NPC attitudes and availability
- Quest/opportunity access
- Trade prices
- Combat difficulty
- Safe havens and hostile territory
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum


class FactionStanding(Enum):
    """Reputation levels with a faction."""
    REVILED = "reviled"        # -100 to -75: Kill on sight
    HOSTILE = "hostile"        # -75 to -50: Aggressive
    UNFRIENDLY = "unfriendly"  # -50 to -25: Suspicious, unhelpful
    NEUTRAL = "neutral"        # -25 to 25: No strong opinion
    FRIENDLY = "friendly"      # 25 to 50: Welcoming
    ALLIED = "allied"          # 50 to 75: Strong support
    REVERED = "revered"        # 75 to 100: Legendary status


class FactionType(Enum):
    """Types of factions."""
    GUILD = "guild"
    MILITARY = "military"
    CRIMINAL = "criminal"
    POLITICAL = "political"
    RELIGIOUS = "religious"
    CORPORATE = "corporate"
    REBEL = "rebel"
    INDEPENDENT = "independent"


@dataclass
class FactionRelation:
    """Relationship between two factions."""
    faction_id: str
    target_faction: str
    relation: str  # "allied", "friendly", "neutral", "hostile", "war"
    strength: float = 0.5  # How strong the relation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "faction_id": self.faction_id,
            "target_faction": self.target_faction,
            "relation": self.relation,
            "strength": self.strength,
        }


@dataclass
class Faction:
    """A faction in the game world."""
    id: str
    name: str
    faction_type: FactionType
    description: str
    home_territory: List[str] = field(default_factory=list)
    allies: List[str] = field(default_factory=list)
    enemies: List[str] = field(default_factory=list)
    notable_npcs: List[str] = field(default_factory=list)
    values: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "faction_type": self.faction_type.value,
            "description": self.description,
            "home_territory": self.home_territory,
            "allies": self.allies,
            "enemies": self.enemies,
            "notable_npcs": self.notable_npcs,
            "values": self.values,
            "resources": self.resources,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Faction":
        return cls(
            id=data["id"],
            name=data["name"],
            faction_type=FactionType(data.get("faction_type", "independent")),
            description=data.get("description", ""),
            home_territory=data.get("home_territory", []),
            allies=data.get("allies", []),
            enemies=data.get("enemies", []),
            notable_npcs=data.get("notable_npcs", []),
            values=data.get("values", []),
            resources=data.get("resources", []),
        )


@dataclass
class ReputationChange:
    """Record of a reputation change."""
    faction_id: str
    old_value: int
    new_value: int
    reason: str
    scene_number: int = 0
    cascade_effects: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "faction_id": self.faction_id,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "reason": self.reason,
            "scene_number": self.scene_number,
            "cascade_effects": self.cascade_effects,
        }


# Default Starforged-style factions
DEFAULT_FACTIONS: List[Faction] = [
    Faction(
        id="iron_syndicate",
        name="Iron Syndicate",
        faction_type=FactionType.CRIMINAL,
        description="A widespread criminal network dealing in smuggling, information, and violence",
        values=["profit", "loyalty", "discretion"],
        resources=["black market goods", "informants", "safe houses"],
    ),
    Faction(
        id="stellar_navy",
        name="Stellar Navy",
        faction_type=FactionType.MILITARY,
        description="The formal military force maintaining order in settled space",
        values=["order", "duty", "protection"],
        resources=["warships", "military bases", "trained soldiers"],
    ),
    Faction(
        id="free_traders",
        name="Free Traders Guild",
        faction_type=FactionType.GUILD,
        description="Independent merchants and haulers who value freedom and fair dealing",
        values=["freedom", "fair trade", "solidarity"],
        resources=["trade routes", "cargo holds", "market access"],
    ),
    Faction(
        id="seekers",
        name="Seekers of the Forgotten",
        faction_type=FactionType.RELIGIOUS,
        description="Mystics and scholars searching for ancient truths",
        values=["knowledge", "preservation", "mystery"],
        resources=["ancient texts", "hidden archives", "occult knowledge"],
    ),
    Faction(
        id="reclamation",
        name="Reclamation Corps",
        faction_type=FactionType.CORPORATE,
        description="Salvagers and reclaimers of derelict technology",
        values=["efficiency", "recovery", "profit"],
        resources=["salvage equipment", "derelict maps", "recycling facilities"],
    ),
    Faction(
        id="sovereign",
        name="Sovereign Pact",
        faction_type=FactionType.POLITICAL,
        description="Coalition of settlements seeking independence from central authority",
        values=["autonomy", "democracy", "resistance"],
        resources=["hidden bases", "popular support", "guerrilla fighters"],
    ),
]


class FactionSystem:
    """
    Engine for tracking faction reputations and their effects.

    Features:
    - Reputation tracking with 7 standing levels
    - Cascade effects (helping allies, hurting enemies)
    - Standing-based encounter modifiers
    - Territory-based complications
    - Trade price modifiers
    """

    STANDING_THRESHOLDS = [
        (FactionStanding.REVILED, -75),
        (FactionStanding.HOSTILE, -50),
        (FactionStanding.UNFRIENDLY, -25),
        (FactionStanding.NEUTRAL, 25),
        (FactionStanding.FRIENDLY, 50),
        (FactionStanding.ALLIED, 75),
        (FactionStanding.REVERED, 100),
    ]

    def __init__(self):
        self._factions: Dict[str, Faction] = {}
        self._reputations: Dict[str, int] = {}  # faction_id -> reputation (-100 to 100)
        self._relations: Dict[str, Dict[str, FactionRelation]] = {}  # faction_id -> {target -> relation}
        self._history: List[ReputationChange] = []
        self._current_scene: int = 0

        # Initialize with default factions
        for faction in DEFAULT_FACTIONS:
            self.add_faction(faction)

        # Set up default relations
        self._setup_default_relations()

    def _setup_default_relations(self):
        """Set up default faction relationships."""
        # Iron Syndicate enemies
        self.set_faction_relation("iron_syndicate", "stellar_navy", "hostile", 0.8)
        self.set_faction_relation("stellar_navy", "iron_syndicate", "hostile", 0.8)

        # Free Traders tensions
        self.set_faction_relation("free_traders", "iron_syndicate", "unfriendly", 0.5)
        self.set_faction_relation("free_traders", "sovereign", "friendly", 0.6)

        # Sovereign vs Navy
        self.set_faction_relation("sovereign", "stellar_navy", "hostile", 0.9)
        self.set_faction_relation("stellar_navy", "sovereign", "hostile", 0.7)

    def add_faction(self, faction: Faction):
        """Add a faction to the system."""
        self._factions[faction.id] = faction
        if faction.id not in self._reputations:
            self._reputations[faction.id] = 0  # Start neutral

    def set_faction_relation(
        self,
        faction_id: str,
        target_id: str,
        relation: str,
        strength: float = 0.5
    ):
        """Set relationship between two factions."""
        if faction_id not in self._relations:
            self._relations[faction_id] = {}

        self._relations[faction_id][target_id] = FactionRelation(
            faction_id=faction_id,
            target_faction=target_id,
            relation=relation,
            strength=strength,
        )

    def get_standing(self, faction_id: str) -> FactionStanding:
        """Get current standing with a faction."""
        rep = self._reputations.get(faction_id, 0)

        for standing, threshold in self.STANDING_THRESHOLDS:
            if rep < threshold:
                return standing

        return FactionStanding.REVERED

    def get_reputation(self, faction_id: str) -> int:
        """Get raw reputation value (-100 to 100)."""
        return self._reputations.get(faction_id, 0)

    def modify_reputation(
        self,
        faction_id: str,
        change: int,
        reason: str,
        cascade: bool = True
    ) -> ReputationChange:
        """
        Modify reputation with a faction.

        Args:
            faction_id: Faction to modify
            change: Amount to change (-100 to 100)
            reason: Why the change occurred
            cascade: Whether to affect allied/enemy factions

        Returns:
            ReputationChange record
        """
        old_value = self._reputations.get(faction_id, 0)
        new_value = max(-100, min(100, old_value + change))
        self._reputations[faction_id] = new_value

        cascade_effects = []

        # Apply cascade effects
        if cascade and faction_id in self._relations:
            for target_id, relation in self._relations[faction_id].items():
                if relation.relation in ["allied", "friendly"]:
                    # Allies share reputation changes (reduced)
                    cascade_change = int(change * relation.strength * 0.5)
                    if cascade_change != 0:
                        self._reputations[target_id] = max(-100, min(100,
                            self._reputations.get(target_id, 0) + cascade_change
                        ))
                        cascade_effects.append(
                            f"{self._factions.get(target_id, target_id).name}: {cascade_change:+d}"
                        )
                elif relation.relation in ["hostile", "war"]:
                    # Enemies get opposite effect (reduced)
                    cascade_change = int(-change * relation.strength * 0.3)
                    if cascade_change != 0:
                        self._reputations[target_id] = max(-100, min(100,
                            self._reputations.get(target_id, 0) + cascade_change
                        ))
                        cascade_effects.append(
                            f"{self._factions.get(target_id, target_id).name}: {cascade_change:+d}"
                        )

        record = ReputationChange(
            faction_id=faction_id,
            old_value=old_value,
            new_value=new_value,
            reason=reason,
            scene_number=self._current_scene,
            cascade_effects=cascade_effects,
        )
        self._history.append(record)

        return record

    def get_npc_attitude(
        self,
        faction_id: str,
        base_disposition: str = "neutral"
    ) -> Tuple[str, str]:
        """
        Get NPC attitude modifier based on faction standing.

        Returns:
            Tuple of (attitude_modifier, behavior_hint)
        """
        standing = self.get_standing(faction_id)

        modifiers = {
            FactionStanding.REVILED: ("hostile", "May attack on sight, refuses all cooperation"),
            FactionStanding.HOSTILE: ("aggressive", "Openly antagonistic, threatens/intimidates"),
            FactionStanding.UNFRIENDLY: ("suspicious", "Terse, unhelpful, inflated prices"),
            FactionStanding.NEUTRAL: (base_disposition, "Standard NPC behavior"),
            FactionStanding.FRIENDLY: ("welcoming", "Helpful, fair prices, shares information"),
            FactionStanding.ALLIED: ("supportive", "Goes out of way to help, discounts, warnings"),
            FactionStanding.REVERED: ("reverent", "Treats as hero/legend, offers best resources"),
        }

        return modifiers.get(standing, ("neutral", "Standard behavior"))

    def get_trade_modifier(self, faction_id: str) -> float:
        """
        Get trade price modifier based on standing.

        Returns multiplier (0.75 = 25% discount, 1.5 = 50% markup)
        """
        standing = self.get_standing(faction_id)

        modifiers = {
            FactionStanding.REVILED: 2.0,      # +100%
            FactionStanding.HOSTILE: 1.5,      # +50%
            FactionStanding.UNFRIENDLY: 1.25,  # +25%
            FactionStanding.NEUTRAL: 1.0,      # Normal
            FactionStanding.FRIENDLY: 0.9,     # -10%
            FactionStanding.ALLIED: 0.8,       # -20%
            FactionStanding.REVERED: 0.7,      # -30%
        }

        return modifiers.get(standing, 1.0)

    def get_territory_status(
        self,
        location: str
    ) -> List[Tuple[str, FactionStanding, str]]:
        """
        Check faction presence at a location.

        Returns list of (faction_name, standing, implication)
        """
        results = []

        for faction in self._factions.values():
            if location.lower() in [t.lower() for t in faction.home_territory]:
                standing = self.get_standing(faction.id)

                if standing in [FactionStanding.REVILED, FactionStanding.HOSTILE]:
                    implication = f"DANGER: {faction.name} territory - hunted"
                elif standing == FactionStanding.UNFRIENDLY:
                    implication = f"CAUTION: {faction.name} territory - unwelcome"
                elif standing in [FactionStanding.ALLIED, FactionStanding.REVERED]:
                    implication = f"SAFE HAVEN: {faction.name} territory - protected"
                else:
                    implication = f"{faction.name} territory - tolerated"

                results.append((faction.name, standing, implication))

        return results

    def get_possible_allies(self) -> List[Tuple[str, FactionStanding]]:
        """Get factions that could provide support."""
        allies = []
        for faction_id, faction in self._factions.items():
            standing = self.get_standing(faction_id)
            if standing in [FactionStanding.FRIENDLY, FactionStanding.ALLIED, FactionStanding.REVERED]:
                allies.append((faction.name, standing))
        return allies

    def get_threats(self) -> List[Tuple[str, FactionStanding]]:
        """Get factions that pose a threat."""
        threats = []
        for faction_id, faction in self._factions.items():
            standing = self.get_standing(faction_id)
            if standing in [FactionStanding.REVILED, FactionStanding.HOSTILE, FactionStanding.UNFRIENDLY]:
                threats.append((faction.name, standing))
        return threats

    def get_narrator_context(self) -> str:
        """Generate faction context for narrator."""
        lines = ["[FACTION STATUS]"]

        # Key standings
        allied = self.get_possible_allies()
        threats = self.get_threats()

        if allied:
            lines.append("ALLIED FACTIONS: " + ", ".join([f"{n} ({s.value})" for n, s in allied]))

        if threats:
            lines.append("HOSTILE FACTIONS: " + ", ".join([f"{n} ({s.value})" for n, s in threats]))

        return "\n".join(lines)

    def get_encounter_modifier(self, faction_id: str) -> Dict[str, Any]:
        """Get modifiers for encounters with faction members."""
        standing = self.get_standing(faction_id)

        modifiers = {
            FactionStanding.REVILED: {
                "initial_attitude": "combat_ready",
                "negotiation_penalty": -3,
                "can_flee": False,
                "reinforcements_likely": True,
            },
            FactionStanding.HOSTILE: {
                "initial_attitude": "aggressive",
                "negotiation_penalty": -2,
                "can_flee": True,
                "reinforcements_likely": True,
            },
            FactionStanding.UNFRIENDLY: {
                "initial_attitude": "suspicious",
                "negotiation_penalty": -1,
                "can_flee": True,
                "reinforcements_likely": False,
            },
            FactionStanding.NEUTRAL: {
                "initial_attitude": "neutral",
                "negotiation_penalty": 0,
                "can_flee": True,
                "reinforcements_likely": False,
            },
            FactionStanding.FRIENDLY: {
                "initial_attitude": "welcoming",
                "negotiation_penalty": 1,
                "can_flee": True,
                "reinforcements_likely": False,
            },
            FactionStanding.ALLIED: {
                "initial_attitude": "supportive",
                "negotiation_penalty": 2,
                "offers_help": True,
            },
            FactionStanding.REVERED: {
                "initial_attitude": "awed",
                "negotiation_penalty": 3,
                "offers_help": True,
                "offers_best": True,
            },
        }

        return modifiers.get(standing, {"initial_attitude": "neutral"})

    def set_scene(self, scene_number: int):
        """Set current scene number."""
        self._current_scene = scene_number

    def to_dict(self) -> Dict[str, Any]:
        """Serialize faction system state."""
        return {
            "factions": {k: v.to_dict() for k, v in self._factions.items()},
            "reputations": self._reputations,
            "relations": {
                k: {t: r.to_dict() for t, r in v.items()}
                for k, v in self._relations.items()
            },
            "history": [h.to_dict() for h in self._history[-50:]],  # Keep last 50
            "current_scene": self._current_scene,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FactionSystem":
        """Deserialize faction system state."""
        system = cls()

        # Load custom factions
        for faction_id, faction_data in data.get("factions", {}).items():
            system._factions[faction_id] = Faction.from_dict(faction_data)

        system._reputations = data.get("reputations", {})
        system._current_scene = data.get("current_scene", 0)

        return system


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("FACTION SYSTEM TEST")
    print("=" * 60)

    system = FactionSystem()

    # Test reputation changes
    print("\n--- Reputation Changes ---")

    change = system.modify_reputation(
        "iron_syndicate",
        change=30,
        reason="Completed a smuggling run",
        cascade=True
    )
    print(f"Iron Syndicate: {change.old_value} -> {change.new_value}")
    print(f"  Reason: {change.reason}")
    if change.cascade_effects:
        print(f"  Cascade: {change.cascade_effects}")

    change = system.modify_reputation(
        "stellar_navy",
        change=-40,
        reason="Resisted arrest",
        cascade=True
    )
    print(f"Stellar Navy: {change.old_value} -> {change.new_value}")
    print(f"  Reason: {change.reason}")
    if change.cascade_effects:
        print(f"  Cascade: {change.cascade_effects}")

    # Test standings
    print("\n--- Current Standings ---")
    for faction_id in system._factions:
        standing = system.get_standing(faction_id)
        rep = system.get_reputation(faction_id)
        print(f"{system._factions[faction_id].name}: {standing.value} ({rep})")

    # Test NPC attitudes
    print("\n--- NPC Attitudes ---")
    for faction_id in ["iron_syndicate", "stellar_navy", "free_traders"]:
        attitude, hint = system.get_npc_attitude(faction_id)
        faction_name = system._factions[faction_id].name
        print(f"{faction_name} NPC: {attitude}")
        print(f"  Behavior: {hint}")

    # Test trade modifiers
    print("\n--- Trade Modifiers ---")
    for faction_id in system._factions:
        modifier = system.get_trade_modifier(faction_id)
        faction_name = system._factions[faction_id].name
        print(f"{faction_name}: {modifier:.0%}")

    # Test narrator context
    print("\n--- Narrator Context ---")
    print(system.get_narrator_context())
