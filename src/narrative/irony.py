"""
Dramatic Irony System.

This module helps manage the gap between what the Player knows and what the
PC/NPCs know, creating tension through dramatic irony.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set

@dataclass
class KnowledgeGap:
    """A specific piece of information known by A but not B."""
    fact_id: str
    description: str
    known_by: Set[str] = field(default_factory=set) # Set of NPC IDs or "PLAYER"
    unknown_by: Set[str] = field(default_factory=set) # Set of NPC IDs or "PLAYER"
    
    # "PLAYER" in known_by and "PC" in unknown_by = Dramatic Irony (Audience Superior)
    # "PC" in known_by and "NPC" in unknown_by = Deception/Secret

@dataclass
class DramaticIronyTracker:
    """
    Manages knowledge states to suggest scenes built on tension.
    """
    active_gaps: Dict[str, KnowledgeGap] = field(default_factory=dict)
    
    def register_secret(self, fact_id: str, description: str, 
                        known_by: List[str], unknown_by: List[str]):
        """
        Register a new secret or hidden threat.
        """
        self.active_gaps[fact_id] = KnowledgeGap(
            fact_id=fact_id,
            description=description,
            known_by=set(known_by),
            unknown_by=set(unknown_by)
        )

    def reveal_secret(self, fact_id: str, to_whom: str) -> bool:
        """
        Mark a secret as revealed to a specific entity.
        Returns True if this closes the gap (everyone knows).
        """
        if fact_id not in self.active_gaps:
            return False
            
        gap = self.active_gaps[fact_id]
        gap.known_by.add(to_whom)
        if to_whom in gap.unknown_by:
            gap.unknown_by.remove(to_whom)
            
        # If no one is left who doesn't know,/or key targets know, gap might be closed
        # For simple logic: if unknown_by is empty, delete gap
        if not gap.unknown_by:
            del self.active_gaps[fact_id]
            return True
            
        return False

    def identify_irony_opportunities(self, current_scene_npcs: List[str]) -> List[str]:
        """
        Suggest ways to exploit irony in the current scene.
        """
        suggestions = []
        
        for gap in self.active_gaps.values():
            # Scenario 1: Player knows something the active NPC doesn't
            # (Audience Superior) - Create suspense
            if "PLAYER" in gap.known_by:
                for npc in current_scene_npcs:
                    if npc in gap.unknown_by:
                        suggestions.append(
                            f"SUSPENSE: You know '{gap.description}', but {npc} doesn't. "
                            f"Watch them walk into the trap."
                        )
            
            # Scenario 2: Active NPC knows something Player doesn't
            # (Mystery) 
            for npc in current_scene_npcs:
                if npc in gap.known_by and "PLAYER" in gap.unknown_by:
                     suggestions.append(
                        f"MYSTERY: {npc} knows '{gap.description}' but hides it. "
                        f"Look for their nervous ticks."
                     )
                     
        return suggestions

    def to_dict(self) -> dict:
        return {
            "active_gaps": {
                fid: {
                    "fact_id": g.fact_id,
                    "description": g.description,
                    "known_by": list(g.known_by),
                    "unknown_by": list(g.unknown_by)
                }
                for fid, g in self.active_gaps.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DramaticIronyTracker":
        system = cls()
        for fid, g_data in data.get("active_gaps", {}).items():
            system.active_gaps[fid] = KnowledgeGap(
                fact_id=g_data["fact_id"],
                description=g_data["description"],
                known_by=set(g_data["known_by"]),
                unknown_by=set(g_data["unknown_by"])
            )
        return system
