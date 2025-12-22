"""
Data models for tracking Revelation Ladder progress.
"""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class BehaviorInstance:
    """A specific instance of player behavior that triggered/influenced this stage."""
    description: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class RevelationStage:
    """Tracks the delivery and outcome of a specific revelation stage."""
    stage: str  # "mirror_moment", "cost_revealed", "origin_glimpsed", "choice_crystallized"
    delivered: bool
    scene_id: str
    player_response: str  # "engaged", "deflected", "attacked", "accepted"
    archetype_at_delivery: str
    timestamp: datetime = field(default_factory=datetime.now)
    follow_up_behavior: List[BehaviorInstance] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "stage": self.stage,
            "delivered": self.delivered,
            "scene_id": self.scene_id,
            "player_response": self.player_response,
            "archetype_at_delivery": self.archetype_at_delivery,
            "timestamp": self.timestamp.isoformat(),
            "follow_up_behavior": [
                {"description": b.description, "timestamp": b.timestamp.isoformat()}
                for b in self.follow_up_behavior
            ]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RevelationStage":
        return cls(
            stage=data["stage"],
            delivered=data["delivered"],
            scene_id=data["scene_id"],
            player_response=data["player_response"],
            archetype_at_delivery=data["archetype_at_delivery"],
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.now(),
            follow_up_behavior=[
                BehaviorInstance(
                    description=b["description"],
                    timestamp=datetime.fromisoformat(b["timestamp"])
                ) for b in data.get("follow_up_behavior", [])
            ]
        )
