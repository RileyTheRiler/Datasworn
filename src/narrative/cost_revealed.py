"""
Stage 2: Cost Revealed.
The player's pattern directly hurts someone or costs them something valuable.
Triggers at 40% story progress.
"""

from typing import Dict, TypedDict
from dataclasses import dataclass
from src.character_identity import WoundType, WoundProfile
from src.narrative.revelation_tracking import RevelationStage
import uuid

@dataclass
class CostScene:
    """A scene where the player's behavior causes direct harm or loss."""
    victim: str
    harm_description: str
    impact_dialogue: str
    consequence_type: str # "relationship_damage", "info_loss", "moral_injury"
    
    def to_dict(self) -> dict:
        return {
            "victim": self.victim,
            "harm_description": self.harm_description,
            "impact_dialogue": self.impact_dialogue,
            "consequence_type": self.consequence_type
        }

# Cost scenes for each archetype
COST_SCENES: Dict[WoundType, CostScene] = {
    WoundType.CONTROLLER: CostScene(
        victim="Torres",
        harm_description="The player's demand for control causes Torres to withhold crucial information.",
        impact_dialogue=(
            "**Torres:** (coldly) 'You want to know what I saw the night the captain died? I'll tell you: nothing. That's my story now.'\n\n"
            "**Player:** 'But you know something—'\n\n"
            "**Torres:** 'Maybe I did. But you lost the right to hear it when you went through my things. "
            "When you demanded answers like you were entitled to my life.'\n\n"
            "**Torres:** 'You wanted control? Here it is. I'm controlling what you know. How does it feel?'"
        ),
        consequence_type="info_loss"
    ),
    
    WoundType.JUDGE: CostScene(
        victim="Kai",
        harm_description="The player's harsh judgment accelerates Kai's addiction spiral.",
        impact_dialogue=(
            "**Dr. Okonkwo:** 'Kai's gotten worse. He's isolating. His usage has increased.'\n\n"
            "**Player:** 'That's not my responsibility—'\n\n"
            "**Dr. Okonkwo:** 'He told me what you said. That he was a liability. That he was weak. "
            "He believed you. Why wouldn't he? You seemed so certain.'\n\n"
            "**Dr. Okonkwo:** 'Your judgment didn't help him. It confirmed his worst fears about himself. "
            "Now he's not just using—he's given up.'"
        ),
        consequence_type="moral_injury"
    ),
    
    WoundType.GHOST: CostScene(
        victim="Ember",
        harm_description="The player's emotional distance pushed Ember toward an unsafe connection.",
        impact_dialogue=(
            "**Ember:** (shaken) 'Vasquez said he understood me. Said he'd look out for me. I thought he was my friend.'\n\n"
            "**Player:** 'What happened?'\n\n"
            "**Ember:** 'He needed something. Information. And I gave it to him because I thought... "
            "because he was the only one who talked to me like a person.'\n\n"
            "**Ember:** (quietly) 'I tried to talk to you. But you never... you were never really here. "
            "So I talked to him instead.'"
        ),
        consequence_type="relationship_damage"
    ),
    
    WoundType.FUGITIVE: CostScene(
        victim="Ember",
        harm_description="The player's lies and deflection create a sense of betrayal.",
        impact_dialogue=(
            "**Ember:** 'I told you about my past. About the servitude, about escaping. I trusted you with that.'\n\n"
            "**Player:** [Deflection]\n\n"
            "**Ember:** 'But you've never told me anything real. Every time I ask about before, you change the subject. "
            "I've been trusting someone I don't even know.'\n\n"
            "**Ember:** 'Were you ever going to tell me the truth? Or am I just someone you're using until you can run again?'"
        ),
        consequence_type="relationship_damage"
    ),
    
    WoundType.CYNIC: CostScene(
        victim="Vasquez",
        harm_description="The player's distrust creates a self-fulfilling prophecy of betrayal.",
        impact_dialogue=(
            "**Vasquez:** 'You know what? You were right about me. Is that what you want to hear?'\n\n"
            "**Player:** 'What are you talking about?'\n\n"
            "**Vasquez:** 'I was going to help you. The information about the cargo—I was going to share it. "
            "But you treated me like a criminal from day one. So why shouldn't I be one?'\n\n"
            "**Vasquez:** 'You expected me to betray you. So I'm going to. Congratulations—you were right all along. Feel better?'"
        ),
        consequence_type="info_loss"
    ),
    
    WoundType.SAVIOR: CostScene(
        victim="Kai",
        harm_description="The player's 'help' creates damaging dependence.",
        impact_dialogue=(
            "**Dr. Okonkwo:** 'Kai hasn't made any progress in recovery. Do you know why?'\n\n"
            "**Player:** 'I've been helping him—'\n\n"
            "**Dr. Okonkwo:** 'That's the problem. You've been helping him so much he doesn't have to help himself. "
            "Every time he struggles, you're there. Every time he fails, you fix it.'\n\n"
            "**Dr. Okonkwo:** 'He'll never get better as long as you keep saving him. You've made yourself his crutch. "
            "He can't walk without you—and that's not recovery. That's dependence.'"
        ),
        consequence_type="moral_injury"
    )
}

class CostRevealedSystem:
    @staticmethod
    def get_cost_scene(wound: WoundType, story_progress: float = 0.0) -> Dict:
        """
        Retrieves the Cost Revealed scene for the player's wound type.
        
        Args:
            wound: The player's dominant wound type
            story_progress: Current story progress (0.0 to 1.0)
            
        Returns:
            Scene data with cost content
        """
        # Check progress threshold
        if story_progress < 0.40:
            return {
                "error": "Cost Revealed not yet available",
                "required_progress": 0.40,
                "current_progress": story_progress
            }
        
        scene_id = str(uuid.uuid4())
        
        # Get scene data, fallback to Controller if not found
        scene = COST_SCENES.get(wound, COST_SCENES[WoundType.CONTROLLER])
        
        return {
            "scene_id": scene_id,
            "stage": "cost_revealed",
            "trigger_progress": 0.40,
            "victim": scene.victim,
            "consequence_type": scene.consequence_type,
            "harm_description": scene.harm_description,
            "dialogue": scene.impact_dialogue,
            "player_wound": wound.value
        }
    
    @staticmethod
    def record_delivery(
        profile: WoundProfile,
        scene_id: str,
        wound_type: WoundType
    ) -> RevelationStage:
        """
        Records that the Cost Revealed moment was delivered.
        """
        record = RevelationStage(
            stage="cost_revealed",
            delivered=True,
            scene_id=scene_id,
            player_response="confronted",
            archetype_at_delivery=wound_type.value
        )
        
        profile.revelation_history.append(record)
        profile.revelation_progress = max(profile.revelation_progress, 0.40)
        
        return record

    @staticmethod
    def process_response(
        profile: WoundProfile, 
        scene_id: str, 
        response_type: str, 
        wound_type: WoundType
    ) -> RevelationStage:
        """
        Processes the player's response to the Cost Revealed moment.
        """
        record = RevelationStage(
            stage="cost_revealed",
            delivered=True,
            scene_id=scene_id,
            player_response=response_type,
            archetype_at_delivery=wound_type.value
        )
        
        profile.revelation_history.append(record)
        profile.revelation_progress = max(profile.revelation_progress, 0.40)
        
        return record
