from __future__ import annotations
import yaml
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class FactionStanding(Enum):
    NEMESIS = -100
    HOSTILE = -50
    SUSPICIOUS = -10
    NEUTRAL = 0
    FRIENDLY = 20
    ALLIED = 50
    HONORED = 80

    @classmethod
    def from_score(cls, score: float) -> FactionStanding:
        """Determine standing from a raw reputation score."""
        # Check from highest to lowest
        for standing in reversed(cls):
            if score >= standing.value:
                return standing
        return cls.NEMESIS

@dataclass
class Faction:
    id: str
    name: str
    description: str
    type: str
    initial_standing: str
    territory_influence: List[str]
    color: str = "#ffffff"
    
    @property
    def default_reputation(self) -> float:
        try:
            return FactionStanding[self.initial_standing.upper()].value
        except (KeyError, AttributeError):
            return 0.0

class FactionManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FactionManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.factions: Dict[str, Faction] = {}
        self.reputation_cache: Dict[str, float] = {} # Run-time cache, but source of truth is GameState
        self._load_factions()
        self._initialized = True

    def _load_factions(self):
        """Load faction definitions from YAML."""
        try:
            data_path = Path("data/world/factions.yaml")
            if not data_path.exists():
                logger.warning(f"Faction data not found at {data_path}")
                return

            with open(data_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            for faction_data in data.get('factions', []):
                faction = Faction(**faction_data)
                self.factions[faction.id] = faction
                
            logger.info(f"Loaded {len(self.factions)} factions.")
            
        except Exception as e:
            logger.error(f"Failed to load factions: {e}")

    def get_faction(self, faction_id: str) -> Optional[Faction]:
        return self.factions.get(faction_id)

    def get_all_factions(self) -> List[Faction]:
        return list(self.factions.values())

    def get_standing(self, faction_id: str, current_reputation: float) -> FactionStanding:
        """Calculate standing based on reputation score."""
        return FactionStanding.from_score(current_reputation)

    def get_reputation_label(self, score: float) -> str:
        return self.get_standing("", score).name.title()

    def get_trade_modifier(self, score: float) -> float:
        """Return price multiplier based on standing."""
        standing = FactionStanding.from_score(score)
        
        modifiers = {
            FactionStanding.NEMESIS: 2.0,   # Won't trade or double price
            FactionStanding.HOSTILE: 1.5,
            FactionStanding.SUSPICIOUS: 1.2,
            FactionStanding.NEUTRAL: 1.0,
            FactionStanding.FRIENDLY: 0.9,
            FactionStanding.ALLIED: 0.8,
            FactionStanding.HONORED: 0.7
        }
        return modifiers.get(standing, 1.0)

    def get_narrator_context(self, character_reputation: Dict[str, float]) -> str:
        """Generate a context string for the narrator/LLM."""
        if not character_reputation:
            return ""
            
        context_lines = ["Faction Standings:"]
        relevant_relations = False
        
        for faction_id, score in character_reputation.items():
            faction = self.get_faction(faction_id)
            if not faction:
                continue
                
            standing = self.get_standing(faction_id, score)
            if standing != FactionStanding.NEUTRAL:
                relevant_relations = True
                context_lines.append(f"- {faction.name}: {standing.name} ({score})")
                
        if not relevant_relations:
            return ""
            
        return "\n".join(context_lines)

    def get_territory_status(self, location_name: str, character_reputation: Dict[str, float]) -> Optional[str]:
        """Determine if the current location is controlled by a faction and the player's status there."""
        # Simple string matching for now. Ideally this would be connected to region data.
        # This is a placeholder for a more complex territory system
        
        # Check against all factions to see if they influence this location type
        # In a real implementation, we'd check the Region object for a `controlled_by` field.
        # Here we'll just check if a faction name is in the location name for demo purposes, 
        # or rely on the `territory_influence` tags matching the location description (not passed here).
        
        # For now, let's just return None to be safe, as we don't have location metadata passed in fully yet.
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize manager state."""
        return {
            "reputation_cache": self.reputation_cache
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FactionManager:
        """Deserialize manager state."""
        instance = cls()
        instance.reputation_cache = data.get("reputation_cache", {})
        return instance
