"""
Revelation Orchestrator.
Coordinates the delivery of the Revelation Ladder stages based on story progress.
"""

from typing import Dict, Optional, List
from src.character_identity import WoundType, WoundProfile
from src.narrative.mirror_moment import MirrorMomentSystem
from src.narrative.cost_revealed import CostRevealedSystem
from src.narrative.origin_glimpsed import OriginGlimpsedSystem
from src.narrative.choice_crystallized import ChoiceCrystallizedSystem

class RevelationOrchestrator:
    @staticmethod
    def get_pending_revelation(profile: WoundProfile, story_progress: float) -> Optional[Dict]:
        """
        Determines if a revelation stage should be triggered based on progress
        and what has already been delivered.
        """
        # Thresholds
        # Stage 1: 0.25 (Mirror)
        # Stage 2: 0.40 (Cost)
        # Stage 3: 0.55 (Origin)
        # Stage 4: 0.70 (Choice)
        
        delivered_stages = [r.stage for r in profile.revelation_history]
        wound = profile.dominant_wound
        
        # Priority check from highest progress down
        
        # Stage 5 (Murder Mirror) - 90%
        if story_progress >= 0.90 and "murder_mirror" not in delivered_stages:
            from src.narrative.murder_mirror import MirrorSystem
            return MirrorSystem.generate_revelation(wound)
            
        # Stage 4 (Choice) - 70%
        if story_progress >= 0.70 and "choice_crystallized" not in delivered_stages:
            return ChoiceCrystallizedSystem.get_scene(wound)
            
        # Stage 3 (Origin) - 55%
        if story_progress >= 0.55 and "origin_glimpsed" not in delivered_stages:
            return OriginGlimpsedSystem.get_origin_scene(wound, story_progress)
            
        # Stage 2 (Cost) - 40%
        if story_progress >= 0.40 and "cost_revealed" not in delivered_stages:
            return CostRevealedSystem.get_cost_scene(wound, story_progress)
            
        # Stage 1 (Mirror) - 25%
        if story_progress >= 0.25 and "mirror_moment" not in delivered_stages:
            return MirrorMomentSystem.get_mirror_scene(wound, story_progress)
            
        return None

    @staticmethod
    def get_status(profile: WoundProfile, story_progress: float) -> Dict:
        """Returns the current status of the Revelation Ladder."""
        delivered = {r.stage: True for r in profile.revelation_history}
        
        return {
            "story_progress": story_progress,
            "revelation_progress": profile.revelation_progress,
            "stages": {
                "mirror_moment": {
                    "threshold": 0.25,
                    "delivered": delivered.get("mirror_moment", False)
                },
                "cost_revealed": {
                    "threshold": 0.40,
                    "delivered": delivered.get("cost_revealed", False)
                },
                "origin_glimpsed": {
                    "threshold": 0.55,
                    "delivered": delivered.get("origin_glimpsed", False)
                },
                "choice_crystallized": {
                    "threshold": 0.70,
                    "delivered": delivered.get("choice_crystallized", False)
                },
                "murder_mirror": {
                    "threshold": 0.90,
                    "delivered": delivered.get("murder_mirror", False)
                }
            }
        }
