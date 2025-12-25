"""
Story Beat Generator.

This module actively suggests the type of narrative beat for the next scene
to ensure variety and proper pacing (e.g., following action with respite).
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
import random

class BeatType(Enum):
    ACTION = "ACTION"
    REVELATION = "REVELATION"
    RESPITE = "RESPITE"
    SOCIAL = "SOCIAL"
    MYSTERY = "MYSTERY"
    SUSPENSE = "SUSPENSE"
    TRANSITION = "TRANSITION"

@dataclass
class StoryBeatGenerator:
    """
    Suggests the next narrative beat type.
    """
    recent_beats: List[BeatType] = field(default_factory=list)
    
    # Simple adjacency rules: What shouldn't follow what?
    # e.g. Don't do 3 ACTIONS in a row.
    
    def suggest_next_beat(self, tension: float) -> BeatType:
        """
        Suggest a beat based on current tension and history.
        """
        options = list(BeatType)
        
        # Rule 1: No more than 2 of the same type in a row
        if len(self.recent_beats) >= 2:
            if self.recent_beats[-1] == self.recent_beats[-2]:
                last = self.recent_beats[-1]
                options = [o for o in options if o != last]
                
        # Rule 2: High tension demands eventual release (Respite)
        # But if we just had action, maybe we want more action OR suspense?
        if tension > 0.8 and self.recent_beats and self.recent_beats[-1] == BeatType.ACTION:
            # 50% chance of continued action, 50% chance of sudden respite/fallout
            if random.random() < 0.5:
                return BeatType.RESPITE
                
        # Rule 3: Low tension needs spark
        if tension < 0.3:
            # Prefer Action, Mystery, or Revelation to spike interest
            weights = {
                BeatType.ACTION: 0.3,
                BeatType.MYSTERY: 0.3,
                BeatType.REVELATION: 0.2,
                BeatType.SOCIAL: 0.1,
                BeatType.RESPITE: 0.05,
                BeatType.SUSPENSE: 0.05,
                BeatType.TRANSITION: 0.0
            }
            return self._weighted_choice(weights)
            
        return random.choice(options)

    def record_beat(self, beat: BeatType):
        self.recent_beats.append(beat)
        if len(self.recent_beats) > 5:
            self.recent_beats.pop(0)

    def _weighted_choice(self, weights: dict) -> BeatType:
        # Simple weighted random
        total = sum(weights.values())
        r = random.uniform(0, total)
        upto = 0
        for beat, w in weights.items():
            if upto + w > r:
                return beat
            upto += w
        return BeatType.ACTION

    def to_dict(self) -> dict:
        return {
            "recent_beats": [b.value for b in self.recent_beats]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StoryBeatGenerator":
        gen = cls()
        gen.recent_beats = [BeatType(b) for b in data.get("recent_beats", [])]
        return gen
