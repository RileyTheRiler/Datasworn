"""
Stage 3: Origin Glimpsed.
The player (and character) sees where their behavior comes from—what fear, loss, or trauma created it.
Triggers at 55% story progress.
"""

from typing import Dict, TypedDict
from dataclasses import dataclass
from src.character_identity import WoundType, WoundProfile
from src.narrative.revelation_tracking import RevelationStage
import uuid

@dataclass
class OriginScene:
    """A moment where the player's backstory connects to their present behavior."""
    trigger_event: str
    reaction_prompt: str
    revelation_content: str
    connection_insight: str
    
    def to_dict(self) -> dict:
        return {
            "trigger_event": self.trigger_event,
            "reaction_prompt": self.reaction_prompt,
            "revelation_content": self.revelation_content,
            "connection_insight": self.connection_insight
        }

# Origin scenes for each archetype
ORIGIN_SCENES: Dict[WoundType, OriginScene] = {
    WoundType.CONTROLLER: OriginScene(
        trigger_event="A sudden crisis where control is impossible (e.g., ship power failure, critical malfunction).",
        reaction_prompt="Ember notices you freeze with a look of specific terror. 'You looked... terrified. Not like normal scared. Like you'd been there before.'",
        revelation_content=(
            "**Player (Optional Share):** 'There was someone. Before. I couldn't save them because I didn't know enough. "
            "Didn't prepare enough. They died because I missed something.'\n\n"
            "**Ember:** 'So that's why you need to know everything. You think if you control enough, it won't happen again.'"
        ),
        connection_insight="The control obsession comes from a past loss they blame themselves for."
    ),
    
    WoundType.JUDGE: OriginScene(
        trigger_event="A moment where a rule must be broken to save someone.",
        reaction_prompt="Torres watches you hesitate. 'You're thinking about the regulations. Even now. Who taught you that rules matter more than people?'",
        revelation_content=(
            "**Player (Optional Share):** 'I saw what happens when the rules break down. On my homeworld... chaos wasn't freedom. "
            "It was a massacre. Order is the only thing keeping us alive.'\n\n"
            "**Torres:** 'So you judge everyone to make sure the walls stay up. Because you're scared of what's outside them.'"
        ),
        connection_insight="The judgment is a defense against the chaos of their past."
    ),
    
    WoundType.GHOST: OriginScene(
        trigger_event="A sensory trigger—a song, a smell, a phrase—reminds the player of a loss.",
        reaction_prompt="You freeze, staring at nothing. Ember asks: 'What's wrong? You look like you've seen a ghost.'",
        revelation_content=(
            "**Player (Optional Share):** 'That song. Someone I knew used to... hum it. "
            "Someone I left before I could lose them.'\n\n"
            "**Ember:** 'So you leave first now. Every time. Before anyone can leave you.'"
        ),
        connection_insight="The emotional distance is armor against grief."
    ),
    
    WoundType.FUGITIVE: OriginScene(
        trigger_event="An official patrol hails the ship or demands ID.",
        reaction_prompt="Your hand goes to your weapon instinctively. Vasquez notices. 'That's not a spacer's reaction. That's a soldier's. Or a convict's.'",
        revelation_content=(
            "**Player (Optional Share):** 'I didn't just leave. I escaped. And if they find me, I don't go to prison. I go back.'\n\n"
            "**Vasquez:** 'So everyone's a potential informant. And every port is a trap. You're not living, you're just not getting caught.'"
        ),
        connection_insight="The evasiveness is survival, based on a real threat."
    ),
    
    WoundType.CYNIC: OriginScene(
        trigger_event="Torres asks why you're really here.",
        reaction_prompt="Torres: 'You never told me. Running to something, or running from?'",
        revelation_content=(
            "**Player (Optional Share):** 'There was someone I trusted completely. Believed in. And they... used that. "
            "Used me. When I wasn't useful anymore, they were gone.'\n\n"
            "**Torres:** 'So now you don't trust anyone. Because if you don't, they can't do that again.'"
        ),
        connection_insight="The cynicism is a wound response. They're not cruel—they're scared of being used."
    ),
    
    WoundType.SAVIOR: OriginScene(
        trigger_event="Someone refuses your help, and it stings more than it should.",
        reaction_prompt="Dr. Okonkwo observes your frustration. 'It hurts, doesn't it? When they don't need you. Makes you wonder if you exist at all.'",
        revelation_content=(
            "**Player (Optional Share):** 'I promised myself I'd be useful. That I'd never be helpless again. "
            "If I can't fix things, what good am I?'\n\n"
            "**Dr. Okonkwo:** 'So you save people to prove you're worth keeping around.'"
        ),
        connection_insight="The savior complex is a defense against feelings of worthlessness."
    )
}

class OriginGlimpsedSystem:
    @staticmethod
    def get_origin_scene(wound: WoundType, story_progress: float = 0.0) -> Dict:
        """
        Retrieves the Origin Glimpsed scene for the player's wound type.
        
        Args:
            wound: The player's dominant wound type
            story_progress: Current story progress (0.0 to 1.0)
            
        Returns:
            Scene data with origin content
        """
        # Check progress threshold
        if story_progress < 0.55:
            return {
                "error": "Origin Glimpsed not yet available",
                "required_progress": 0.55,
                "current_progress": story_progress
            }
        
        scene_id = str(uuid.uuid4())
        
        # Get scene data, fallback to Controller if not found
        scene = ORIGIN_SCENES.get(wound, ORIGIN_SCENES[WoundType.CONTROLLER])
        
        return {
            "scene_id": scene_id,
            "stage": "origin_glimpsed",
            "trigger_progress": 0.55,
            "trigger_event": scene.trigger_event,
            "prompt": scene.reaction_prompt,
            "revelation": scene.revelation_content,
            "insight": scene.connection_insight,
            "player_wound": wound.value
        }
    
    @staticmethod
    def record_delivery(
        profile: WoundProfile,
        scene_id: str,
        wound_type: WoundType
    ) -> RevelationStage:
        """
        Records that the Origin Glimpsed moment was delivered.
        """
        record = RevelationStage(
            stage="origin_glimpsed",
            delivered=True,
            scene_id=scene_id,
            player_response="acknowledged", # Default response, could be updated if player shares
            archetype_at_delivery=wound_type.value
        )
        
        profile.revelation_history.append(record)
        profile.revelation_progress = max(profile.revelation_progress, 0.55)
        
        return record

    @staticmethod
    def process_response(
        profile: WoundProfile, 
        scene_id: str, 
        response_type: str, 
        wound_type: WoundType
    ) -> RevelationStage:
        """
        Processes the player's response to the Origin Glimpsed moment.
        """
        record = RevelationStage(
            stage="origin_glimpsed",
            delivered=True,
            scene_id=scene_id,
            player_response=response_type,
            archetype_at_delivery=wound_type.value
        )
        
        profile.revelation_history.append(record)
        profile.revelation_progress = max(profile.revelation_progress, 0.55)
        
        return record
