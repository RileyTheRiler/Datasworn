"""
Stage 4: Choice Crystallized.
Handles the logic for the scene where Ember names the player's pattern directly.
"""

from typing import Dict, TypedDict, Optional
from src.character_identity import WoundType, WoundProfile
from src.narrative.revelation_tracking import RevelationStage, BehaviorInstance
import uuid

class CrystallizedScene(TypedDict):
    dialogue: str
    ember_observation: str
    player_pattern_name: str

# Scene content for each archetype
SCENE_DATA: Dict[WoundType, CrystallizedScene] = {
    WoundType.CONTROLLER: {
        "dialogue": (
            "You never stop, do you?\n\n"
            "It's not about the murder. I've watched you. You're like this with everything. "
            "Every question has to have an answer. Every person is a puzzle to solve. Everything has to make sense.\n\n"
            "But it doesn't. The universe doesn't make sense. People don't make sense. "
            "The captain is dead and no amount of knowing why will bring him back.\n\n"
            "You're not investigating. You're trying to control death itself. And you can't."
        ),
        "ember_observation": "Ember watches you organizing your notes, her expression sad but firm.",
        "player_pattern_name": "The Controller"
    },
    WoundType.JUDGE: {
        "dialogue": (
            "Can I tell you something? You scare me a little.\n\n"
            "Because you're always so certain. About everyone. Kai is weak. Vasquez is a liar. Torres is cold. "
            "You sorted everyone the first day you met them.\n\n"
            "But people are more than one thing. Kai is weak AND he's kind. Vasquez lies AND he's helped me. "
            "Torres is cold AND she's protective.\n\n"
            "When you look at someone and only see one thing... that's not justice. "
            "That's just making the world simple enough that you can handle it."
        ),
        "ember_observation": "Ember hesitates, then steps closer, as if testing a boundary.",
        "player_pattern_name": "The Judge"
    },
    WoundType.GHOST: {
        "dialogue": (
            "You're not really here. Did you know that?\n\n"
            "You're on the ship. You do things. But it's like... you left part of yourself somewhere else. "
            "Or you're already thinking about the next ship, the next job, the next place you'll be.\n\n"
            "I've told you real things. About my life, my fears. And every time, you nod and then redirect. "
            "You never share anything real back.\n\n"
            "Are you even here? Or are you already gone?"
        ),
        "ember_observation": "Ember looks right through you, as if seeing a ghost.",
        "player_pattern_name": "The Ghost"
    },
    WoundType.FUGITIVE: {
        "dialogue": (
            "I know. You never want to talk about it. And that's fine. But I've been watching you. "
            "The way you freeze when someone asks about your past. The way you keep your bag packed. "
            "The way you're always ready to leave.\n\n"
            "You're running from something. And I don't need to know what. But I wonder if you know. "
            "If you've been running so long you forgot what you're running from.\n\n"
            "At some point, you're not running from something. You're just running. And then where do you go?"
        ),
        "ember_observation": "Ember points to your go-bag, sitting ready by the door.",
        "player_pattern_name": "The Fugitive"
    },
    WoundType.CYNIC: {
        "dialogue": (
            "Do you trust anyone? At all?\n\n"
            "Trust gets people killed, you say. Maybe. But so does not trusting. "
            "You're so afraid of being betrayed that you push everyone away before they can get close.\n\n"
            "I tried to be your friend. So did Kai. Even Torres respects you. But you look at us like we're threats. "
            "Like we're all just waiting to hurt you.\n\n"
            "What if we're not? What if we're just... people? And you're so certain we'll betray you that you're making sure we will?"
        ),
        "ember_observation": "Ember crosses her arms, looking hurt but defiant.",
        "player_pattern_name": "The Cynic"
    },
    WoundType.SAVIOR: {
        "dialogue": (
            "You don't have to save me. You know that, right?\n\n"
            "I know. You want to help everyone. Kai, me, the whole ship. "
            "But sometimes it feels like... you need us to need you. Like if we were fine on our own, you wouldn't know what to do with yourself.\n\n"
            "The captain was like that. He needed people to save. And when they didn't need saving, he'd find problems that weren't there.\n\n"
            "You're not responsible for me. I can take care of myself. Can you let me?"
        ),
        "ember_observation": "Ember steps back, creating a deliberate physical distance.",
        "player_pattern_name": "The Savior"
    }
}

class ChoiceCrystallizedSystem:
    @staticmethod
    def get_scene(wound: WoundType) -> Dict:
        """
        Retrieves the Choice Crystallized scene for the player's wound type.
        Falls back to Controller if specific wound not implemented.
        """
        scene_id = str(uuid.uuid4())
        
        data = SCENE_DATA.get(wound, SCENE_DATA[WoundType.CONTROLLER])
        
        return {
            "scene_id": scene_id,
            "stage": "choice_crystallized",
            "ember_observation": data["ember_observation"],
            "dialogue": data["dialogue"],
            "pattern_name": data["player_pattern_name"],
            "choices": [
                {
                    "id": "engage",
                    "text": "Listen to her. Admit there's truth in it.",
                    "type": "engaged"
                },
                {
                    "id": "deflect",
                    "text": "Change the subject. Focus on the investigation.",
                    "type": "deflected"
                },
                {
                    "id": "attack",
                    "text": "Get angry. Tell her she doesn't know what she's talking about.",
                    "type": "attacked"
                }
            ]
        }

    @staticmethod
    def record_delivery(
        profile: WoundProfile,
        scene_id: str,
        wound_type: WoundType
    ) -> RevelationStage:
        """
        Records that the Choice Crystallized moment was delivered.
        """
        record = RevelationStage(
            stage="choice_crystallized",
            delivered=True,
            scene_id=scene_id,
            player_response="pending", 
            archetype_at_delivery=wound_type.value
        )
        
        profile.revelation_history.append(record)
        profile.revelation_progress = max(profile.revelation_progress, 0.70)
        
        return record


    @staticmethod
    def process_response(
        profile: WoundProfile, 
        scene_id: str, 
        response_type: str, 
        wound_type: WoundType
    ) -> RevelationStage:
        """
        Records the player's response to the revelation.
        """
        
        # Create tracking record
        record = RevelationStage(
            stage="choice_crystallized",
            delivered=True,
            scene_id=scene_id,
            player_response=response_type,
            archetype_at_delivery=wound_type.value
        )
        
        # Add to history
        profile.revelation_history.append(record)
        
        # Update progress
        profile.revelation_progress = 0.75  # Set progress marker
        
        # If they engaged or accepted, we might bump "dark wisdom" or similar stats here
        if response_type == "engaged" or response_type == "accepted":
            # Small boost to self-knowledge/resolution chance?
            pass
            
        return record
