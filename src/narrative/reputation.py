"""
Moral Reputation System.

This module tracks the moral alignment of the player based on their choices,
allowing the world to react to their reputation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class ReputationScore:
    """Score on a specific moral axis (-100 to 100)."""
    value: int = 0
    
    # Axis definitions
    # Merciful (+) | Ruthless (-)
    # Honest (+)   | Deceptive (-)
    # Selfless (+) | Selfish (-)

    def adjust(self, amount: int):
        self.value = max(-100, min(100, self.value + amount))

    @property
    def label(self) -> str:
        if self.value > 50: return "HIGH_POSITIVE"
        if self.value < -50: return "HIGH_NEGATIVE"
        if self.value > 10: return "LEANING_POSITIVE"
        if self.value < -10: return "LEANING_NEGATIVE"
        return "NEUTRAL"

@dataclass
class MoralReputationSystem:
    """
    Tracks player reputation across different axes.
    """
    mercy_ruthless: ReputationScore = field(default_factory=ReputationScore)
    honest_deceptive: ReputationScore = field(default_factory=ReputationScore)
    selfless_selfish: ReputationScore = field(default_factory=ReputationScore)
    
    history: List[str] = field(default_factory=list) # Log of moral choices
    
    def record_choice(self, description: str, 
                     mercy_delta: int = 0, 
                     honest_delta: int = 0, 
                     selfless_delta: int = 0):
        """
        Record a choice that impacts reputation.
        """
        self.mercy_ruthless.adjust(mercy_delta)
        self.honest_deceptive.adjust(honest_delta)
        self.selfless_selfish.adjust(selfless_delta)
        
        self.history.append(description)

    def get_reputation_summary(self) -> str:
        """
        Get a description of how the world sees the player.
        """
        traits = []
        
        if self.mercy_ruthless.value > 50: traits.append("Known as a merciful protector.")
        elif self.mercy_ruthless.value < -50: traits.append("Feared as a ruthless executioner.")
        
        if self.honest_deceptive.value > 50: traits.append("Trusted to keep their word.")
        elif self.honest_deceptive.value < -50: traits.append("Suspected of being a liar.")
        
        if self.selfless_selfish.value > 50: traits.append("Praised for their generosity.")
        elif self.selfless_selfish.value < -50: traits.append("Despised for their greed.")
        
        if not traits:
            return "An unknown wanderer with no reputation yet."
            
        return " ".join(traits)

    def to_dict(self) -> dict:
        return {
            "mercy_ruthless": self.mercy_ruthless.value,
            "honest_deceptive": self.honest_deceptive.value,
            "selfless_selfish": self.selfless_selfish.value,
            "history": self.history
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MoralReputationSystem":
        system = cls()
        system.mercy_ruthless.value = data.get("mercy_ruthless", 0)
        system.honest_deceptive.value = data.get("honest_deceptive", 0)
        system.selfless_selfish.value = data.get("selfless_selfish", 0)
        system.history = data.get("history", [])
        return system


# =============================================================================
# Social Reputation Vectors
# =============================================================================

@dataclass
class RelationshipVector:
    """Quantify player reputation with an NPC or faction."""

    trust: int = 0       # -100 to 100
    fear: int = 0        # -100 to 100 (positive = they fear you)
    debt: int = 0        # favors owed (+ means you owe them)

    def adjust(self, trust_delta: int = 0, fear_delta: int = 0, debt_delta: int = 0):
        self.trust = max(-100, min(100, self.trust + trust_delta))
        self.fear = max(-100, min(100, self.fear + fear_delta))
        self.debt = max(-100, min(100, self.debt + debt_delta))

    def stance(self) -> str:
        if self.trust > 50:
            return "ALLY"
        if self.trust < -50 or self.fear > 50:
            return "HOSTILE"
        if self.trust < -10:
            return "WARY"
        return "NEUTRAL"

    def dialogue_modifier(self) -> int:
        return 2 if self.trust > 50 else (-2 if self.trust < -50 else 0)

    def price_modifier(self) -> float:
        if self.trust > 50:
            return 0.85
        if self.trust < -50:
            return 1.25
        return 1.0

    def combat_posture(self) -> str:
        if self.fear > 50:
            return "AVOID"
        if self.trust < -50:
            return "ESCALATE"
        return "NEGOTIATE"

    def to_dict(self) -> dict:
        return {"trust": self.trust, "fear": self.fear, "debt": self.debt}

    @classmethod
    def from_dict(cls, data: dict) -> "RelationshipVector":
        return cls(
            trust=data.get("trust", 0),
            fear=data.get("fear", 0),
            debt=data.get("debt", 0),
        )


@dataclass
class ReputationLedger:
    """Track per-faction and per-NPC reputation vectors."""

    factions: Dict[str, RelationshipVector] = field(default_factory=dict)
    npcs: Dict[str, RelationshipVector] = field(default_factory=dict)

    def _get_vector(self, table: Dict[str, RelationshipVector], key: str) -> RelationshipVector:
        if key not in table:
            table[key] = RelationshipVector()
        return table[key]

    def adjust_faction(self, faction: str, trust_delta: int = 0, fear_delta: int = 0, debt_delta: int = 0):
        self._get_vector(self.factions, faction).adjust(trust_delta, fear_delta, debt_delta)

    def adjust_npc(self, npc: str, trust_delta: int = 0, fear_delta: int = 0, debt_delta: int = 0):
        self._get_vector(self.npcs, npc).adjust(trust_delta, fear_delta, debt_delta)

    def get_dialogue_bonus(self, npc: str, faction: str | None = None) -> int:
        bonuses = []
        if faction and faction in self.factions:
            bonuses.append(self.factions[faction].dialogue_modifier())
        if npc in self.npcs:
            bonuses.append(self.npcs[npc].dialogue_modifier())
        return max(bonuses) if bonuses else 0

    def get_price_modifier(self, npc: str, faction: str | None = None) -> float:
        modifiers = []
        if faction and faction in self.factions:
            modifiers.append(self.factions[faction].price_modifier())
        if npc in self.npcs:
            modifiers.append(self.npcs[npc].price_modifier())
        return min(modifiers) if modifiers else 1.0

    def get_combat_posture(self, npc: str, faction: str | None = None) -> str:
        # Prefer explicit NPC stance, fall back to faction
        if npc in self.npcs:
            return self.npcs[npc].combat_posture()
        if faction and faction in self.factions:
            return self.factions[faction].combat_posture()
        return "NEGOTIATE"

    def qualifies_for(self, npc: str, required_trust: int, faction: str | None = None) -> bool:
        vector = None
        if npc in self.npcs:
            vector = self.npcs[npc]
        elif faction and faction in self.factions:
            vector = self.factions[faction]
        if not vector:
            return required_trust <= 0
        return vector.trust >= required_trust

    def to_dict(self) -> dict:
        return {
            "factions": {k: v.to_dict() for k, v in self.factions.items()},
            "npcs": {k: v.to_dict() for k, v in self.npcs.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ReputationLedger":
        ledger = cls()
        ledger.factions = {k: RelationshipVector.from_dict(v) for k, v in data.get("factions", {}).items()}
        ledger.npcs = {k: RelationshipVector.from_dict(v) for k, v in data.get("npcs", {}).items()}
        return ledger
