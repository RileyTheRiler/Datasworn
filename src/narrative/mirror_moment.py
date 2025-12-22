"""
Stage 1: Mirror Moment.
The player sees their pattern reflected in another character.
Triggers at 25% story progress.
"""

from typing import Dict, TypedDict
from dataclasses import dataclass
from src.character_identity import WoundType, WoundProfile
from src.narrative.revelation_tracking import RevelationStage
import uuid

@dataclass
class MirrorScene:
    """A mirror moment where the player observes their pattern in another."""
    mirror_character: str
    discovery_type: str  # "log", "witnessed_scene", "conversation"
    content: str
    seed_planted: str
    
    def to_dict(self) -> dict:
        return {
            "mirror_character": self.mirror_character,
            "discovery_type": self.discovery_type,
            "content": self.content,
            "seed_planted": self.seed_planted
        }

# Mirror scenes for each archetype
MIRROR_SCENES: Dict[WoundType, MirrorScene] = {
    WoundType.CONTROLLER: MirrorScene(
        mirror_character="Captain Reyes",
        discovery_type="log",
        content=(
            "**Captain's Log, Day 47**\n\n"
            "The crew doesn't understand why I need to know everything. Torres thinks I'm paranoid. "
            "Kai avoids me because I keep checking on his work.\n\n"
            "But if I don't control the variables, who will? This ship, this crew—they're my responsibility. "
            "If something goes wrong because I didn't anticipate it, that's on me. I've seen teams dissolve "
            "because one person thought they knew better than the system.\n\n"
            "Maria used to say I was trying to hold water in my fists. That the tighter I squeezed, "
            "the more slipped through. She left because she couldn't stand being one of my 'variables.'\n\n"
            "I'm at peace now. Settle your accounts, Marcus. Before the systems decide for you."
        ),
        seed_planted="The captain's obsessive need for control. Later, Ember will ask: 'Did you see yourself?'"
    ),
    
    WoundType.JUDGE: MirrorScene(
        mirror_character="Torres",
        discovery_type="witnessed_scene",
        content=(
            "You witness Torres confronting Kai in the corridor.\n\n"
            "**Torres:** (cold) 'Again? This is pathetic. You know the rules. You know what you're doing to yourself. "
            "And you do it anyway.'\n\n"
            "**Kai:** 'It's not that simple—'\n\n"
            "**Torres:** 'It is that simple. You're an addict who can't control himself. That makes you a liability. "
            "That makes you dangerous. The captain should have left you at the last port.'\n\n"
            "**Kai:** (quietly) 'You don't know what it's like.'\n\n"
            "**Torres:** 'I know enough. Weak is weak. No excuse changes that.'\n\n"
            "Torres walks away. Kai stands there, diminished."
        ),
        seed_planted="Torres's harsh judgment without nuance. Later: 'You saw how Torres talked to Kai. You do the same thing. Just quieter.'"
    ),
    
    WoundType.GHOST: MirrorScene(
        mirror_character="Dr. Okonkwo",
        discovery_type="witnessed_scene",
        content=(
            "You observe Ember approaching Dr. Okonkwo in the med bay.\n\n"
            "**Ember:** 'Dr. Okonkwo? Can I ask you something personal?'\n\n"
            "**Dr. Okonkwo:** (stiffens slightly) 'I'm rather busy preparing inventory—'\n\n"
            "**Ember:** 'It's just... you've been on a lot of ships, right? How do you handle losing people? "
            "I've never... I'm afraid I won't know what to do if someone here...'\n\n"
            "**Dr. Okonkwo:** 'The best thing is to focus on your duties. Emotion clouds judgment. "
            "Keep your distance, and the losses are manageable.'\n\n"
            "**Ember:** 'But doesn't that get lonely?'\n\n"
            "**Dr. Okonkwo:** (pause, then crisply) 'I need to finish this inventory. "
            "We can discuss ship's protocols another time.'\n\n"
            "She turns away. Ember leaves, dejected."
        ),
        seed_planted="Dr. Okonkwo's professional detachment as protection. Later: 'Dr. Okonkwo never lets anyone in. She's already said goodbye to everyone. You do that too—I can tell.'"
    ),
    
    WoundType.FUGITIVE: MirrorScene(
        mirror_character="Vasquez",
        discovery_type="conversation",
        content=(
            "You discover documents in Vasquez's belongings—a manifest with a different name, "
            "a photo of him with people he's never mentioned, a half-written letter:\n\n"
            "*'I can't come back. Not after what I did. It's better if you think I'm dead.'*\n\n"
            "Later, Vasquez catches you looking.\n\n"
            "**Vasquez:** (smile fading) 'Ah. You found that.'\n\n"
            "[Player can respond in various ways]\n\n"
            "**Vasquez:** 'We all have a \"before,\" don't we? Some of us just ran farther from it. "
            "I don't think you're in any position to talk about running from the past.'"
        ),
        seed_planted="Vasquez's running is laid bare. His line about running may land harder than expected."
    ),
    
    WoundType.CYNIC: MirrorScene(
        mirror_character="Torres",
        discovery_type="conversation",
        content=(
            "During a quiet moment, Torres explains her philosophy:\n\n"
            "**Torres:** 'You want to know why I don't trust anyone on this ship? I learned. "
            "Back in the military, I trusted my squad. Trusted my commander. They left me to die when it was convenient.'\n\n"
            "[Player can respond]\n\n"
            "**Torres:** 'Trust is a luxury. A weakness. Every time you trust someone, you're handing them a weapon. "
            "It's just a matter of when they use it.'\n\n"
            "**Torres:** 'I know what you're thinking—that's paranoid. That's sad. But I'm still alive. "
            "The people who trusted me? Some of them aren't.'"
        ),
        seed_planted="Torres's cynicism stated plainly. Later: 'Torres's philosophy. You agreed with it. But look where it's gotten both of you—alone.'"
    ),
    
    WoundType.SAVIOR: MirrorScene(
        mirror_character="Captain Reyes",
        discovery_type="conversation",
        content=(
            "Dr. Okonkwo shares memories of the captain:\n\n"
            "**Dr. Okonkwo:** 'Marcus was a good man. But he had a... pattern. He needed to save people. "
            "He thought if he could build a crew of the blacklisted and the broken, he could prove "
            "that people save people, not systems.'\n\n"
            "**Player:** 'Isn't that admirable?'\n\n"
            "**Dr. Okonkwo:** 'In moderation. But he couldn't stop. He gave Yuki a choice between "
            "exposure or confession because he thought he could \"settle her accounts\" for her. "
            "He didn't realize that some people don't want a second chance—they just want to survive.'\n\n"
            "**Dr. Okonkwo:** (pointed) 'He made other people's redemption his personal mission. "
            "In the end, it was a mission that got him killed.'"
        ),
        seed_planted="The captain's savior complex as a flaw. Later: 'The captain did that too. Made everyone's problem his problem. You're doing the same thing with me. With Kai. Why do you need us to need you?'"
    )
}

class MirrorMomentSystem:
    @staticmethod
    def get_mirror_scene(wound: WoundType, story_progress: float = 0.0) -> Dict:
        """
        Retrieves the Mirror Moment scene for the player's wound type.
        
        Args:
            wound: The player's dominant wound type
            story_progress: Current story progress (0.0 to 1.0)
            
        Returns:
            Scene data with mirror content
        """
        # Check progress threshold
        if story_progress < 0.25:
            return {
                "error": "Mirror Moment not yet available",
                "required_progress": 0.25,
                "current_progress": story_progress
            }
        
        scene_id = str(uuid.uuid4())
        
        # Get scene data, fallback to Controller if not found
        scene = MIRROR_SCENES.get(wound, MIRROR_SCENES[WoundType.CONTROLLER])
        
        return {
            "scene_id": scene_id,
            "stage": "mirror_moment",
            "trigger_progress": 0.25,
            "mirror_character": scene.mirror_character,
            "discovery_type": scene.discovery_type,
            "content": scene.content,
            "seed_planted": scene.seed_planted,
            "player_wound": wound.value
        }
    
    @staticmethod
    def record_delivery(
        profile: WoundProfile,
        scene_id: str,
        wound_type: WoundType
    ) -> RevelationStage:
        """
        Records that the Mirror Moment was delivered.
        """
        record = RevelationStage(
            stage="mirror_moment",
            delivered=True,
            scene_id=scene_id,
            player_response="observed",  # Mirror moments are passive observations
            archetype_at_delivery=wound_type.value
        )
        
        profile.revelation_history.append(record)
        profile.revelation_progress = max(profile.revelation_progress, 0.25)
        
        return record

    @staticmethod
    def process_response(
        profile: WoundProfile, 
        scene_id: str, 
        response_type: str, 
        wound_type: WoundType
    ) -> RevelationStage:
        """
        Processes the player's response to the Mirror Moment.
        """
        # Mirror moments are largely passive, but we record the acknowledgement
        record = RevelationStage(
            stage="mirror_moment",
            delivered=True,
            scene_id=scene_id,
            player_response=response_type,
            archetype_at_delivery=wound_type.value
        )
        
        # Update history if not already present (avoid duplicates for same scene)
        profile.revelation_history.append(record)
        profile.revelation_progress = max(profile.revelation_progress, 0.25)
        
        return record
