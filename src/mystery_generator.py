"""
Procedural Mystery Generator for Starforged AI Game Master.
Randomly assigns "The Threat" and generates clues pointing to them.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.psych_profile import PsychologicalProfile


@dataclass
class ClueFragment:
    """A clue pointing toward the threat."""
    id: str
    text: str
    implicates: str  # Crew member ID
    strength: float  # 0.0 (vague) to 1.0 (damning)
    discovered: bool = False


@dataclass
class MysteryConfig:
    """Configuration for the procedurally generated mystery."""
    threat_id: str = ""
    threat_motive: str = ""
    clues: list[ClueFragment] = field(default_factory=list)
    is_revealed: bool = False
    
    def __post_init__(self):
        if not self.threat_id:
            self._generate_mystery()
            
    def _generate_mystery(self):
        """Randomly assign the threat and generate clues."""
        crew_ids = ["captain", "engineer", "medic", "scientist", "security", "pilot"]
        self.threat_id = random.choice(crew_ids)
        
        motives = {
            "captain": "Covering up a mission failure that got their previous crew killed.",
            "engineer": "Sabotaging the ship to claim insurance on a fabricated accident.",
            "medic": "Testing an experimental drug on the crew without consent.",
            "scientist": "The 'research' is actually harvesting something from the crew.",
            "security": "Under orders from a shadow organization to eliminate witnesses.",
            "pilot": "Is not who they claim to be. An imposter with a hidden agenda.",
        }
        self.threat_motive = motives.get(self.threat_id, "Unknown motive.")
        
        # Generate clues that point to the threat
        self._generate_clues()
        
    def _generate_clues(self):
        """Generate a set of clues, some pointing to the threat, some red herrings."""
        threat = self.threat_id
        all_ids = ["captain", "engineer", "medic", "scientist", "security", "pilot"]
        
        # Strong clues pointing to the threat
        strong_clues = [
            ClueFragment(f"clue_strong_1", f"You find a data chip in {threat}'s quarters. The encryption is military grade.", threat, 0.8),
            ClueFragment(f"clue_strong_2", f"A crew member saw {threat} near the airlock at 0300. No one should have been awake.", threat, 0.7),
        ]
        
        # Moderate clues
        moderate_clues = [
            ClueFragment(f"clue_mod_1", f"{threat.capitalize()}'s bio file has a 3-year gap. What were they doing?", threat, 0.5),
        ]
        
        # Red herrings (point to innocents)
        innocents = [i for i in all_ids if i != threat]
        red_herrings = [
            ClueFragment(f"clue_red_1", f"{random.choice(innocents).capitalize()} has been acting strange. But they're hiding something personal, not dangerous.", random.choice(innocents), 0.3),
            ClueFragment(f"clue_red_2", f"You overhear a whispered argument. It's about supplies, not murder.", random.choice(innocents), 0.2),
        ]
        
        self.clues = strong_clues + moderate_clues + red_herrings
        random.shuffle(self.clues)

    def get_undiscovered_clue(self) -> ClueFragment | None:
        """Get a random undiscovered clue."""
        undiscovered = [c for c in self.clues if not c.discovered]
        return random.choice(undiscovered) if undiscovered else None
        
    def reveal_clue(self, clue_id: str):
        """Mark a clue as discovered."""
        for clue in self.clues:
            if clue.id == clue_id:
                clue.discovered = True
                break

    def calculate_accusation_confidence(self, accused_id: str) -> float:
        """Calculate how confident an accusation against this person would be."""
        discovered = [c for c in self.clues if c.discovered and c.implicates == accused_id]
        if not discovered:
            return 0.0
        return min(1.0, sum(c.strength for c in discovered))

    def to_dict(self) -> dict:
        return {
            "threat_id": self.threat_id,
            "threat_motive": self.threat_motive,
            "clues": [{"id": c.id, "text": c.text, "implicates": c.implicates, "strength": c.strength, "discovered": c.discovered} for c in self.clues],
            "is_revealed": self.is_revealed
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MysteryConfig":
        config = cls(
            threat_id=data.get("threat_id", ""),
            threat_motive=data.get("threat_motive", ""),
            is_revealed=data.get("is_revealed", False)
        )
        config.clues = [ClueFragment(**c) for c in data.get("clues", [])]
        return config

    def generate_personalized_mystery(self, psych_profile: "PsychologicalProfile"):
        """Generate a mystery tailored to the character's psychological fears."""
        fear = psych_profile.get_primary_fear()
        crew_ids = ["captain", "engineer", "medic", "scientist", "security", "pilot"]
        
        # Select threat and motive based on fear
        fear_mappings = {
            "betrayal": {
                "threat": "medic",  # Someone you trust
                "motive": "The medic has been your confidant. But they've been reporting everything to corporate.",
                "clue_theme": "trust_violation"
            },
            "infiltration": {
                "threat": "pilot",
                "motive": "The pilot is not who they claim. Facial recognition shows a 40% mismatch.",
                "clue_theme": "identity_theft"
            },
            "environmental_threat": {
                "threat": "engineer",
                "motive": "The engineer has been sabotaging life support. Slowly. Methodically.",
                "clue_theme": "sabotage"
            },
            "loss_of_control": {
                "threat": "scientist",
                "motive": "The scientist's 'research' involves mind control. You might already be compromised.",
                "clue_theme": "manipulation"
            },
            "harm_to_loved_ones": {
                "threat": "captain",
                "motive": "The captain knows about your family. And they're holding that knowledge over you.",
                "clue_theme": "blackmail"
            },
        }
        
        config = fear_mappings.get(fear, fear_mappings["infiltration"])
        self.threat_id = config["threat"]
        self.threat_motive = config["motive"]
        
        # Generate themed clues
        self._generate_themed_clues(config["clue_theme"])

    def _generate_themed_clues(self, theme: str):
        """Generate clues based on psychological theme."""
        threat = self.threat_id
        all_ids = ["captain", "engineer", "medic", "scientist", "security", "pilot"]
        
        theme_clues = {
            "trust_violation": [
                ClueFragment("clue_1", f"You find encrypted messages from {threat} to an unknown recipient. The subject line: 'Subject Update'.", threat, 0.8),
                ClueFragment("clue_2", f"{threat.capitalize()} has been accessing your personal logs. Why?", threat, 0.6),
            ],
            "identity_theft": [
                ClueFragment("clue_1", f"The ship's AI flags {threat}'s biometrics as 'anomalous'. Retinal scan mismatch.", threat, 0.9),
                ClueFragment("clue_2", f"You find two different ID badges in {threat}'s locker. Same face. Different names.", threat, 0.7),
            ],
            "sabotage": [
                ClueFragment("clue_1", f"Oxygen levels drop 2% every night. {threat.capitalize()} is always near the vents.", threat, 0.8),
                ClueFragment("clue_2", f"You find a maintenance log. {threat.capitalize()}'s handwriting. 'Phase 2: Complete.'", threat, 0.7),
            ],
            "manipulation": [
                ClueFragment("clue_1", f"You wake up with no memory of the last 3 hours. {threat.capitalize()} was the last person you saw.", threat, 0.8),
                ClueFragment("clue_2", f"The crew reports hearing you say things you don't remember. {threat.capitalize()} smiles when you ask.", threat, 0.6),
            ],
            "blackmail": [
                ClueFragment("clue_1", f"{threat.capitalize()} mentions your sister's name. You never told them you had a sister.", threat, 0.9),
                ClueFragment("clue_2", f"You find a dossier on your family in {threat}'s quarters. Photos. Addresses. Schedules.", threat, 0.8),
            ],
        }
        
        clues = theme_clues.get(theme, theme_clues["identity_theft"])
        
        # Add red herrings
        innocents = [i for i in all_ids if i != threat]
        red_herrings = [
            ClueFragment("red_1", f"{random.choice(innocents).capitalize()} has been acting strange. But it's just personal stress.", random.choice(innocents), 0.2),
        ]
        
        self.clues = clues + red_herrings
        random.shuffle(self.clues)
