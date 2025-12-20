"""
Trust & Betrayal Dynamics.

This module tracks deep trust relationships and the lasting impact of betrayals.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

class BetrayalSeverity(str, Enum):
    MINOR = "minor"         # Lie, omission
    MODERATE = "moderate"   # Broken promise, hidden agenda
    MAJOR = "major"         # Active sabotage, endangering life

@dataclass
class BetrayalEvent:
    betrayer_id: str
    description: str
    severity: BetrayalSeverity
    forgiven: bool = False

@dataclass
class TrustDynamicsSystem:
    """
    Tracks trust and betrayal history.
    """
    trust_scores: Dict[str, float] = field(default_factory=dict)  # npc_id -> trust
    betrayal_history: List[BetrayalEvent] = field(default_factory=list)
    
    def get_trust(self, npc_id: str) -> float:
        return self.trust_scores.get(npc_id, 0.5)
    
    def adjust_trust(self, npc_id: str, delta: float):
        current = self.get_trust(npc_id)
        self.trust_scores[npc_id] = max(0.0, min(1.0, current + delta))
    
    def record_betrayal(self, betrayer_id: str, description: str, severity: BetrayalSeverity):
        """Record a betrayal event."""
        event = BetrayalEvent(betrayer_id, description, severity)
        self.betrayal_history.append(event)
        
        # Massive trust collapse
        penalty = {
            BetrayalSeverity.MINOR: 0.2,
            BetrayalSeverity.MODERATE: 0.4,
            BetrayalSeverity.MAJOR: 0.8
        }[severity]
        self.adjust_trust(betrayer_id, -penalty)
    
    def forgive_betrayal(self, index: int) -> bool:
        """Attempt to forgive a betrayal."""
        if 0 <= index < len(self.betrayal_history):
            event = self.betrayal_history[index]
            if not event.forgiven:
                event.forgiven = True
                # Partial trust restoration
                self.adjust_trust(event.betrayer_id, 0.1)
                return True
        return False
    
    def get_trust_context(self, npc_id: str) -> Optional[str]:
        """Get narrator guidance for trust state."""
        trust = self.get_trust(npc_id)
        
        if trust < 0.2:
            return f"[TRUST: Broken. Character expects the worst from {npc_id}. Describe suspicion and guardedness.]"
        elif trust < 0.4:
            return f"[TRUST: Low. Character is wary of {npc_id}. Eye contact is brief, words are measured.]"
        elif trust > 0.8:
            return f"[TRUST: High. Character feels safe with {npc_id}. Describe vulnerability and openness.]"
        return None
    
    def get_unresolved_betrayals(self) -> List[BetrayalEvent]:
        """Get list of unforgiven betrayals."""
        return [b for b in self.betrayal_history if not b.forgiven]

    def to_dict(self) -> dict:
        return {
            "trust_scores": self.trust_scores,
            "betrayal_history": [
                {
                    "betrayer_id": b.betrayer_id,
                    "description": b.description,
                    "severity": b.severity.value,
                    "forgiven": b.forgiven
                }
                for b in self.betrayal_history
            ]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TrustDynamicsSystem":
        sys = cls()
        sys.trust_scores = data.get("trust_scores", {})
        for b in data.get("betrayal_history", []):
            sys.betrayal_history.append(BetrayalEvent(
                betrayer_id=b["betrayer_id"],
                description=b["description"],
                severity=BetrayalSeverity(b["severity"]),
                forgiven=b.get("forgiven", False)
            ))
        return sys
