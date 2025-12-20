"""
The Memory Palace.
A system for tracking suppressed memories, unlocking them via secrets/stats,
and allowing the player to piece together their past.
"""

from __future__ import annotations
from dataclasses import dataclass, field
import json

@dataclass
class MemoryFragment:
    """A single piece of a suppressed memory."""
    id: str                # Unique ID (e.g., "incident_01")
    title: str             # "The Red Door"
    content: str           # The actual text of the memory
    unlock_condition: str  # Description of how to unlock (e.g. "High Amygdala")
    is_locked: bool = True
    is_corrupted: bool = False
    original_content: str | None = None  # To revert if needed
    
    def to_dict(self) -> dict:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryFragment":
        return cls(**data)


@dataclass
class MemoryPalace:
    """
    Manages the collection of memories.
    """
    fragments: dict[str, MemoryFragment] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.fragments:
            self._initialize_defaults()
            
    def _initialize_defaults(self):
        """Initialize the core mystery fragments."""
        defaults = [
            MemoryFragment("mem_001", "The Launch", "You remember the champagne bottle shattering. Not on the hull, but on the Captain's head.", "Amygdala > 0.7"),
            MemoryFragment("mem_002", "The Code", "Protocol 99-Delta. It wasn't a rescue mission. It was a containment protocol.", "Cortex > 0.7"),
            MemoryFragment("mem_003", "The Passenger", "There were seven cryo-pods listed on the manifest. But you only counted six crew members at breakfast.", "Hippocampus > 0.7"),
            MemoryFragment("mem_004", "The Pain", "A phantom searing in your left arm. But your left arm is fine. It's the cybernetic one that hurts.", "BrainStem > 0.7"),
            MemoryFragment("mem_005", "The Lie", "She told you she loved you before the airlock closed. You know that was a manipulation.", "Temporal > 0.7"),
        ]
        for f in defaults:
            self.fragments[f.id] = f

    def check_unlocks(self, profile: dict) -> list[MemoryFragment]:
        """
        Check if any locked memories should be unlocked based on current profile/voice state.
        Returns list of newly unlocked fragments.
        """
        unlocked = []
        
        # Mapping voice dominance to condition keys
        # This is a simple implementation. A real one would use a proper condition parser.
        # Here we just parse "Region > X.X" strings manually for the defaults.
        
        region_map = {
            "Amygdala": profile.get("amygdala_dominance", 0.0),
            "Cortex": profile.get("cortex_dominance", 0.0),
            "Hippocampus": profile.get("hippocampus_dominance", 0.0),
            "BrainStem": profile.get("brain_stem_dominance", 0.0),
            "Temporal": profile.get("temporal_dominance", 0.0),
        }

        for frag in self.fragments.values():
            if frag.is_locked:
                # Parse condition "Region > Value"
                try:
                    parts = frag.unlock_condition.split(">")
                    if len(parts) == 2:
                        region = parts[0].strip()
                        val = float(parts[1].strip())
                        
                        if region_map.get(region, 0.0) >= val:
                            frag.is_locked = False
                            unlocked.append(frag)
                except:
                    continue
                    
        return unlocked

    def inject_false_memory(self, title: str, content: str) -> MemoryFragment:
        """Inject a completely false memory into the palace."""
        frag = MemoryFragment(
            id=f"false_{len(self.fragments)}",
            title=title,
            content=content,
            unlock_condition="None (Injected)",
            is_locked=False,
            is_corrupted=True,
            original_content="[FALSE MEMORY - NO ORIGIN]"
        )
        self.fragments[frag.id] = frag
        return frag

    def to_dict(self) -> dict:
        return {"fragments": {k: v.to_dict() for k, v in self.fragments.items()}}

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryPalace":
        palace = cls(fragments={})
        for k, v in data.get("fragments", {}).items():
            palace.fragments[k] = MemoryFragment.from_dict(v)
        return palace
