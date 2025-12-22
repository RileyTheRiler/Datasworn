"""
Camp Dialogue System.

Camp-specific dialogue packs for greetings, chores, arc progression,
and player affordances (gifts, gambling, drinking, etc.).
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional
import random


class CampDialogueContext(Enum):
    """Types of camp-specific dialogue."""
    GREETING = "greeting"
    ANTAGONIZE = "antagonize"
    CHORE_HELP = "chore_help"
    CHORE_DECLINE = "chore_decline"
    ARC_PROGRESS = "arc_progress"
    GIFT_ACCEPT = "gift_accept"
    GIFT_REJECT = "gift_reject"
    GAMBLING = "gambling"
    DRINKING = "drinking"
    SITTING_TOGETHER = "sitting_together"
    MORNING_CHAT = "morning_chat"
    EVENING_CHAT = "evening_chat"


# =============================================================================
# CAMP DIALOGUE BANKS
# =============================================================================

CAMP_DIALOGUE = {
    "yuki": {
        CampDialogueContext.GREETING: {
            "low_trust": [
                "*nods curtly* Keep moving.",
                "What do you want?",
                "*doesn't look up from weapon maintenance*",
            ],
            "neutral": [
                "*brief nod*",
                "Morning.",
                "*acknowledges your presence with a glance*",
            ],
            "high_trust": [
                "Hey. Everything okay?",
                "*small smile* Didn't expect to see you up this early.",
                "Good to see you.",
            ],
        },
        CampDialogueContext.ANTAGONIZE: {
            "low_trust": [
                "*hand moves to weapon* Walk away. Now.",
                "You're testing my patience.",
                "*cold stare* Don't.",
            ],
            "neutral": [
                "*raises eyebrow* Really?",
                "Not in the mood.",
                "*turns away*",
            ],
            "high_trust": [
                "*sighs* What's gotten into you?",
                "Come on. Not today.",
                "*looks disappointed* Expected better from you.",
            ],
        },
        CampDialogueContext.CHORE_HELP: {
            "default": [
                "*surprised* You're... offering to help? *pause* Fine. Check the perimeter sensors.",
                "Could use another set of eyes on the security logs. If you're serious.",
                "*studies you* Alright. Help me clean these weapons. Properly.",
            ],
        },
        CampDialogueContext.SITTING_TOGETHER: {
            "low_trust": [
                "*shifts away slightly*",
                "*silence*",
            ],
            "neutral": [
                "*quiet presence*",
                "Peaceful here.",
            ],
            "high_trust": [
                "*relaxes slightly* Sometimes it's good to just... sit.",
                "Thanks for the company.",
                "*comfortable silence*",
            ],
        },
    },
    
    "torres": {
        CampDialogueContext.GREETING: {
            "low_trust": [
                "*wary* What brings you here?",
                "*guarded* Morning.",
            ],
            "neutral": [
                "Hey there.",
                "*friendly wave*",
                "Another day, huh?",
            ],
            "high_trust": [
                "*warm smile* There you are! Was hoping I'd see you.",
                "Perfect timing. I just made coffee.",
                "*genuine pleasure* Good morning, friend.",
            ],
        },
        CampDialogueContext.CHORE_HELP: {
            "default": [
                "Absolutely! Here, help me with these navigation charts.",
                "*grins* Always happy to have company. Grab that wrench.",
                "Sure thing. Two hands are better than one.",
            ],
        },
        CampDialogueContext.EVENING_CHAT: {
            "default": [
                "*staring at stars* You ever wonder what's out there? Beyond all this?",
                "*by the fire* Reminds me of nights back home. Before everything changed.",
                "You know, I've been thinking about the routes we've taken. The choices.",
            ],
        },
        CampDialogueContext.GAMBLING: {
            "default": [
                "*shuffles cards* Feeling lucky? Let's play.",
                "*grins* I'll go easy on you. Maybe.",
                "Cards? Now you're speaking my language.",
            ],
        },
    },
    
    "kai": {
        CampDialogueContext.GREETING: {
            "low_trust": [
                "*barely looks up* Busy.",
                "*quiet* Hi.",
            ],
            "neutral": [
                "*small smile* Hello.",
                "*nods while working*",
            ],
            "high_trust": [
                "*lights up* Oh! I wanted to show you something.",
                "*genuine warmth* Good to see you.",
                "*puts down tools* Perfect timing. Take a break with me?",
            ],
        },
        CampDialogueContext.CHORE_HELP: {
            "default": [
                "*grateful* Really? That would be wonderful. Here, hold this steady.",
                "Thank you. I've been struggling with this calibration.",
                "*shy smile* I'd appreciate that. It's delicate work.",
            ],
        },
        CampDialogueContext.MORNING_CHAT: {
            "default": [
                "*tending plants* These are growing well. Small victories, you know?",
                "Morning is my favorite time. Everything feels... possible.",
                "*quiet* I like the peace before everyone wakes up.",
            ],
        },
    },
    
    "okonkwo": {
        CampDialogueContext.GREETING: {
            "low_trust": [
                "*measured* Good day.",
                "*observes you carefully*",
            ],
            "neutral": [
                "*warm* Hello.",
                "*welcoming nod*",
            ],
            "high_trust": [
                "*genuine smile* I was hoping we'd have a chance to talk.",
                "Come, sit. I just made tea.",
                "*pleased* Wonderful to see you.",
            ],
        },
        CampDialogueContext.SITTING_TOGETHER: {
            "neutral": [
                "*offers tea* Sometimes we just need to be present.",
                "*peaceful silence*",
            ],
            "high_trust": [
                "You carry a lot. I see it.",
                "*gentle* You don't have to say anything. I'm here.",
                "This reminds me of home. Quiet moments with friends.",
            ],
        },
        CampDialogueContext.DRINKING: {
            "default": [
                "*raises cup* To surviving another day.",
                "Not usually one for drinking, but... *small smile* ...today calls for it.",
                "*thoughtful* Sometimes we need to mark the moments.",
            ],
        },
    },
    
    "vasquez": {
        CampDialogueContext.GREETING: {
            "low_trust": [
                "*suspicious* What do you need?",
                "*eyes narrow*",
            ],
            "neutral": [
                "*casual* Hey.",
                "*nods* What's up?",
            ],
            "high_trust": [
                "*big grin* There's my favorite person!",
                "*laughs* About time you showed up!",
                "*friendly punch on shoulder* Where've you been?",
            ],
        },
        CampDialogueContext.GAMBLING: {
            "default": [
                "*deals cards* Let's see what you've got.",
                "*confident* Hope you brought something to bet.",
                "*winks* Don't worry, I'll let you win. Once.",
            ],
        },
        CampDialogueContext.DRINKING: {
            "default": [
                "*pours drink* Here's to bad decisions and good company!",
                "*raises glass* Salud!",
                "Now THIS is how you end a day!",
            ],
        },
        CampDialogueContext.GIFT_ACCEPT: {
            "default": [
                "*surprised* For me? *genuine* Thanks. Really.",
                "*examines gift* This is... actually perfect. How'd you know?",
                "*grins* You're alright. Don't let anyone tell you different.",
            ],
        },
    },
    
    "ember": {
        CampDialogueContext.GREETING: {
            "low_trust": [
                "*shy* Hi...",
                "*looks away*",
            ],
            "neutral": [
                "*small wave*",
                "Hey.",
            ],
            "high_trust": [
                "*excited* Oh! I drew something for you!",
                "*runs over* I've been waiting for you!",
                "*bright smile* Want to see what I made?",
            ],
        },
        CampDialogueContext.CHORE_HELP: {
            "default": [
                "*eager* Yes! I want to learn!",
                "Can you show me how? I'll pay attention, I promise.",
                "*enthusiastic* I'll do my best!",
            ],
        },
        CampDialogueContext.EVENING_CHAT: {
            "default": [
                "*looking at fire* The flames make shapes. Do you see them?",
                "Torres tells the best stories. Have you heard the one about the ghost ship?",
                "*quiet* Do you think we'll be okay? All of us?",
            ],
        },
        CampDialogueContext.GIFT_ACCEPT: {
            "default": [
                "*eyes wide* For me? *clutches it* Thank you!",
                "*overwhelmed* I... I don't know what to say. Thank you.",
                "*carefully takes it* I'll keep this safe. Always.",
            ],
        },
    },
}


# =============================================================================
# ARC-SPECIFIC DIALOGUE
# =============================================================================

ARC_DIALOGUE = {
    "yuki": {
        "trust_building": [
            "*after long silence* I didn't kill the captain because I wanted to. I killed them because I had to.",
            "You remind me of someone. Someone I failed to protect.",
        ],
        "conflict": [
            "*tense* You're getting too close. To the truth. To me.",
            "Don't ask me about that night. Please.",
        ],
        "resolution": [
            "*quiet* I thought I'd carry this alone forever. Thank you for... understanding.",
            "Maybe I don't have to be the monster I thought I was.",
        ],
    },
    "torres": {
        "trust_building": [
            "I've been running for so long. Sometimes I forget what I'm running from.",
            "*wistful* I had a family once. Before the war.",
        ],
        "conflict": [
            "You don't understand what I've done. What I've lost.",
            "*angry* Don't pretend you know me!",
        ],
        "resolution": [
            "*tears* Maybe it's time to stop running. To face it.",
            "Thank you for not giving up on me.",
        ],
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_camp_dialogue(
    npc_id: str,
    context: CampDialogueContext,
    trust_level: float = 0.5,
    arc_step: Optional[str] = None
) -> str:
    """Get camp dialogue for an NPC."""
    
    # Check for arc-specific dialogue first
    if arc_step and npc_id in ARC_DIALOGUE:
        arc_lines = ARC_DIALOGUE[npc_id].get(arc_step, [])
        if arc_lines:
            return random.choice(arc_lines)
    
    # Get regular camp dialogue
    npc_dialogue = CAMP_DIALOGUE.get(npc_id, {})
    context_dialogue = npc_dialogue.get(context, {})
    
    # Determine trust category
    if trust_level < 0.3:
        trust_category = "low_trust"
    elif trust_level > 0.7:
        trust_category = "high_trust"
    else:
        trust_category = "neutral"
    
    # Try to get trust-specific dialogue
    if trust_category in context_dialogue:
        lines = context_dialogue[trust_category]
        if lines:
            return random.choice(lines)
    
    # Fall back to default
    if "default" in context_dialogue:
        lines = context_dialogue["default"]
        if lines:
            return random.choice(lines)
    
    # Ultimate fallback
    return f"*{npc_id} acknowledges you*"


def get_time_appropriate_dialogue(
    npc_id: str,
    hour: int,
    trust_level: float = 0.5
) -> str:
    """Get dialogue appropriate for the time of day."""
    from src.daily_scripts import get_time_of_day, TimeOfDay
    
    time = get_time_of_day(hour)
    
    if time in [TimeOfDay.DAWN, TimeOfDay.MORNING]:
        return get_camp_dialogue(npc_id, CampDialogueContext.MORNING_CHAT, trust_level)
    elif time in [TimeOfDay.EVENING, TimeOfDay.NIGHT]:
        return get_camp_dialogue(npc_id, CampDialogueContext.EVENING_CHAT, trust_level)
    else:
        return get_camp_dialogue(npc_id, CampDialogueContext.GREETING, trust_level)


def get_all_camp_contexts() -> list[CampDialogueContext]:
    """Get all available camp dialogue contexts."""
    return list(CampDialogueContext)
