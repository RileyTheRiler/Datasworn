"""
Attachment Style System.

This module models how the character forms and maintains relationships,
based on psychological attachment theory (Secure, Anxious, Avoidant, Disorganized).
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from enum import Enum

class AttachmentStyle(str, Enum):
    SECURE = "secure"           # Comfortable with intimacy and independence
    ANXIOUS = "anxious"         # Fearful of abandonment, seeks reassurance
    AVOIDANT = "avoidant"       # Distrusts intimacy, values independence
    DISORGANIZED = "disorganized"  # Conflicted, unpredictable in relationships

@dataclass
class RelationshipState:
    npc_id: str
    trust: float = 0.5          # 0.0 to 1.0
    closeness: float = 0.5      # 0.0 to 1.0
    conflict_count: int = 0
    positive_interactions: int = 0

@dataclass
class AttachmentSystem:
    """
    Manages attachment style and its effects on relationships.
    """
    style: AttachmentStyle = AttachmentStyle.SECURE
    relationships: Dict[str, RelationshipState] = field(default_factory=dict)
    
    def get_or_create_relationship(self, npc_id: str) -> RelationshipState:
        if npc_id not in self.relationships:
            self.relationships[npc_id] = RelationshipState(npc_id)
        return self.relationships[npc_id]
    
    def process_positive_interaction(self, npc_id: str):
        """Handle a positive interaction."""
        rel = self.get_or_create_relationship(npc_id)
        rel.positive_interactions += 1
        
        # Trust/Closeness increase depends on style
        if self.style == AttachmentStyle.SECURE:
            rel.trust = min(1.0, rel.trust + 0.1)
            rel.closeness = min(1.0, rel.closeness + 0.1)
        elif self.style == AttachmentStyle.ANXIOUS:
            rel.closeness = min(1.0, rel.closeness + 0.15)  # Clings faster
            rel.trust = min(1.0, rel.trust + 0.05)          # But trust is slower
        elif self.style == AttachmentStyle.AVOIDANT:
            rel.closeness = min(1.0, rel.closeness + 0.05)  # Slow to warm up
            rel.trust = min(1.0, rel.trust + 0.08)
        else:  # Disorganized
            rel.closeness = min(1.0, rel.closeness + 0.1)
            # Trust fluctuates unpredictably
            import random
            rel.trust = max(0.0, min(1.0, rel.trust + random.uniform(-0.1, 0.1)))
    
    def process_conflict(self, npc_id: str):
        """Handle a conflict."""
        rel = self.get_or_create_relationship(npc_id)
        rel.conflict_count += 1
        
        if self.style == AttachmentStyle.SECURE:
            rel.trust = max(0.0, rel.trust - 0.05)  # Resilient
        elif self.style == AttachmentStyle.ANXIOUS:
            rel.trust = max(0.0, rel.trust - 0.15)
            rel.closeness = max(0.0, rel.closeness - 0.1)  # Feels abandoned
        elif self.style == AttachmentStyle.AVOIDANT:
            rel.closeness = max(0.0, rel.closeness - 0.2)  # Pulls away
        else:  # Disorganized
            rel.trust = max(0.0, rel.trust - 0.2)
            rel.closeness = max(0.0, rel.closeness - 0.15)
    
    def get_relationship_guidance(self, npc_id: str) -> Optional[str]:
        """Get narrator guidance for this relationship."""
        rel = self.relationships.get(npc_id)
        if not rel:
            return None
            
        if self.style == AttachmentStyle.ANXIOUS and rel.closeness < 0.3:
            return f"[ATTACHMENT: Anxious. Character fears losing {npc_id}. Describe clinginess or desperate need for approval.]"
        elif self.style == AttachmentStyle.AVOIDANT and rel.closeness > 0.7:
            return f"[ATTACHMENT: Avoidant. Character feels smothered by {npc_id}. Describe emotional withdrawal.]"
        elif self.style == AttachmentStyle.DISORGANIZED:
            return f"[ATTACHMENT: Disorganized. Character's feelings toward {npc_id} are conflicted and unpredictable.]"
        return None

    def to_dict(self) -> dict:
        return {
            "style": self.style.value,
            "relationships": {
                k: {
                    "npc_id": v.npc_id,
                    "trust": v.trust,
                    "closeness": v.closeness,
                    "conflict_count": v.conflict_count,
                    "positive_interactions": v.positive_interactions
                }
                for k, v in self.relationships.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AttachmentSystem":
        sys = cls()
        sys.style = AttachmentStyle(data.get("style", "secure"))
        for k, v in data.get("relationships", {}).items():
            sys.relationships[k] = RelationshipState(
                npc_id=v["npc_id"],
                trust=v["trust"],
                closeness=v["closeness"],
                conflict_count=v.get("conflict_count", 0),
                positive_interactions=v.get("positive_interactions", 0)
            )
        return sys
