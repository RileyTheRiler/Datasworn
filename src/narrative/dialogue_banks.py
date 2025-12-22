"""
Dialogue Banks: Archetype × NPC Combinations

This module provides dialogue variations based on the player's detected archetype.
Each NPC adjusts their tone, content, and approach based on who the player is becoming.

Structure:
- 5 NPCs: Torres, Kai, Dr. Okonkwo, Vasquez, Ember
- 6 Core Archetypes: Controller, Judge, Ghost, Fugitive, Cynic, Savior
- Relationship Stages: Early, Mid, Late game
- Trust Modifiers: Trust built vs. trust broken
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class DialogueContext(str, Enum):
    """Context types for dialogue selection."""
    FIRST_MEETING = "first_meeting"
    CASUAL = "casual"
    MURDER_QUESTION = "murder_question"
    ARCHETYPE_SPECIFIC = "archetype_specific"

class RelationshipStage(str, Enum):
    """Relationship progression stages."""
    EARLY = "early"
    MID = "mid"
    LATE = "late"

@dataclass
class DialogueLine:
    """A single line of dialogue with metadata."""
    text: str
    context: DialogueContext
    requires_trust: Optional[float] = None  # Minimum trust required (-1.0 to 1.0)
    requires_broken_trust: bool = False

# ============================================================================
# TORRES DIALOGUE BANK
# ============================================================================

TORRES_BASELINE = {
    "first_meeting": [
        "You're the new investigator. I'm Torres. Pilot. I keep us flying.",
        "I don't know you. I don't trust you. That's not personal—I don't trust anyone I haven't vetted. Prove yourself and we'll talk."
    ],
    "casual": [
        "Need something? I'm running diagnostics.",
        "The captain trusted too easily. Look where that got him."
    ],
    "murder_question": [
        "I have opinions. But opinions aren't evidence. When I have something concrete, I'll share it."
    ]
}

TORRES_CONTROLLER = {
    "early": [
        "You've been busy. Searching quarters, demanding answers. Efficient, I suppose. But you're making enemies.",
        "You want to control this investigation? Fine. But control isn't the same as understanding."
    ],
    "mid": [
        "I've been watching you. The way you need to know everything. The way uncertainty makes you push harder.",
        "The captain had the same pattern. Couldn't let anything be unknown. It consumed him."
    ],
    "late": [
        "You've searched everyone's quarters. Read everyone's private files. And what have you learned? Not who killed him. Just how little control you actually have.",
        "Some things can't be forced. Some truths only come when you stop demanding them."
    ],
    "trust_built": [
        "I respect your thoroughness. But remember—people aren't puzzles. They're people. Treat them that way and they'll give you more than you could ever take."
    ],
    "trust_broken": [
        "You went through my things without asking. You demanded instead of earned. We're done. Whatever I know, you'll never hear it from me."
    ]
}

TORRES_JUDGE = {
    "early": [
        "You've already decided about everyone, haven't you? I can see it. The way you categorize us. Guilty. Innocent. Suspicious.",
        "Life isn't that clean. People aren't that simple."
    ],
    "mid": [
        "You condemned Kai for his addiction. Did you ask why he uses? Did you care?",
        "Judgment is easy. Understanding is hard. The captain understood that. Do you?"
    ],
    "late": [
        "I've been court-martialed. Did you know that? The military decided I was wrong, so I must be wrong.",
        "But I wasn't wrong. I was inconvenient. That's different. Think about that before you pass your next verdict."
    ],
    "trust_built": [
        "You're learning that people are more than one thing. That's growth. Keep going."
    ],
    "trust_broken": [
        "You judged me before you knew me. That tells me everything I need to know about your 'justice.'"
    ]
}

TORRES_GHOST = {
    "early": [
        "You're hard to read. I respect that, actually. But there's a difference between privacy and absence.",
        "Are you here? Or are you already planning your exit?"
    ],
    "mid": [
        "Everyone on this ship has reached out to you. Kai. Ember. Even Vasquez. You deflect every time.",
        "Why are you here if you won't be here?"
    ],
    "late": [
        "I've known soldiers who did what you do. Kept everyone at arm's length. Survived alone.",
        "They survived. But they didn't live. There's a difference."
    ],
    "trust_built": [
        "You stayed. For that conversation. You were actually present. That means something."
    ],
    "trust_broken": [
        "You were never really here, were you? Just passing through. Like everyone always is."
    ]
}

TORRES_FUGITIVE = {
    "early": [
        "You never talk about before. Where you came from. What you left.",
        "That's fine. We all have pasts. But the past has a way of catching up."
    ],
    "mid": [
        "I asked the captain about you once. He said you 'arrived with baggage.' Never unpacked.",
        "What are you carrying? And how long can you carry it?"
    ],
    "late": [
        "I know what running looks like. I've done it myself—running from what the military did to me.",
        "The difference is I stopped. I faced it. You haven't."
    ],
    "trust_built": [
        "Whatever you're running from—when you're ready to stop, I'll be here. No judgment. Just presence."
    ],
    "trust_broken": [
        "You can't run forever. But you can run long enough to lose everything that matters."
    ]
}

TORRES_CYNIC = {
    "early": [
        "You don't trust anyone. I understand that. I don't either.",
        "But there's a difference between earned distrust and preemptive destruction."
    ],
    "mid": [
        "You expect everyone to betray you. So you treat them like enemies before they have a chance to be friends.",
        "I used to do that. Still do, sometimes. It's safe. It's also lonely."
    ],
    "late": [
        "I've watched you push away everyone who tried to connect. Ember. Kai. Even Vasquez, and he's genuinely trying.",
        "You're creating the isolation you fear. You know that, right?"
    ],
    "trust_built": [
        "You trusted me. I don't know why, but you did. I won't betray that. Maybe that proves something."
    ],
    "trust_broken": [
        "You were right not to trust me. Because I don't trust you either. We're the same—two people too broken to connect."
    ]
}

TORRES_SAVIOR = {
    "early": [
        "You want to save everyone. I can see it in how you talk to the crew.",
        "But we're not broken machines you can fix."
    ],
    "mid": [
        "The captain tried to save everyone too. Every intervention, every second chance.",
        "It didn't work. Not because he failed. Because people have to save themselves."
    ],
    "late": [
        "You need us to need you. I've figured that out. It's not about us—it's about you feeling useful.",
        "What happens when we don't need saving anymore?"
    ],
    "trust_built": [
        "You stopped trying to fix me. You just asked what I needed. That's different. That's real."
    ],
    "trust_broken": [
        "I'm not your redemption project. I'm a person. Learn the difference."
    ]
}

# ============================================================================
# KAI DIALOGUE BANK
# ============================================================================

KAI_BASELINE = {
    "first_meeting": [
        "Oh—hey. You're the one asking questions. I'm Kai. Engineering.",
        "I keep the ship running. Most of the time. Sorry, I'm a little... scattered today."
    ],
    "casual": [
        "Did you need something? I'm in the middle of... actually, I don't remember what I was doing.",
        "The captain used to check on me. Every day. I miss that."
    ],
    "murder_question": [
        "I don't know anything. I was... I wasn't paying attention that night."
    ]
}

KAI_CONTROLLER = {
    "early": [
        "You're very... organized. All those notes. All those questions.",
        "I can't think like that. Everything in my head is more like... static."
    ],
    "mid": [
        "You keep pushing for answers. I understand needing to know. I need to know things too—like will I make it through tomorrow?",
        "But some things can't be forced. My brain, for example. I can't force it to be quiet."
    ],
    "late": [
        "I've been watching you try to control everything. The investigation. The crew. The outcome.",
        "It doesn't work, you know. Some things just... happen. No matter how hard you plan."
    ],
    "trust_built": [
        "You've been patient with me. That's rare. Most people just want me to be useful.",
        "You want me to be... okay. That's different."
    ],
    "trust_broken": [
        "You keep telling me what to do. How to get better. What I need.",
        "But you don't know what I need. No one does. Maybe not even me."
    ]
}

KAI_JUDGE = {
    "early": [
        "I know what you're thinking. About the drugs. About me.",
        "Go ahead. Judge me. Everyone does."
    ],
    "mid": [
        "You think I'm weak. That I choose this. That I could just... stop.",
        "It's not that simple. It's never that simple. But you don't care about simple, do you? You care about categories."
    ],
    "late": [
        "The captain never judged me. He just... saw me. As a person, not a problem.",
        "I wish you could do that. I wish anyone could."
    ],
    "trust_built": [
        "You're the first person in a long time who looked at me without deciding what I was.",
        "I don't know what to do with that. But... thank you."
    ],
    "trust_broken": [
        "You called me weak. Maybe you're right. But you know what? Your strength looks a lot like cruelty from where I'm standing."
    ]
}

KAI_GHOST = {
    "early": [
        "You're quiet. I like that, actually. Most people talk too much.",
        "But sometimes... sometimes silence is just another wall."
    ],
    "mid": [
        "I used to think I wanted everyone to leave me alone. Then I got what I wanted.",
        "It's not better. Being alone. It's just... emptier."
    ],
    "late": [
        "You and me—we're both hiding, aren't we? You behind silence. Me behind substances.",
        "At least I know what I'm running from. Do you?"
    ],
    "trust_built": [
        "You stayed. When I was having a bad night. You just... sat there.",
        "That meant more than you know. Presence. Just presence."
    ],
    "trust_broken": [
        "I tried to talk to you. Really talk. But you weren't there. Not really.",
        "I don't blame you. Some of us can't connect. I get it."
    ]
}

KAI_SAVIOR = {
    "early": [
        "You want to help me. I can tell. Everyone wants to help me.",
        "But you can't fix me. I'm not a broken machine you can repair."
    ],
    "mid": [
        "The captain tried to save me too. Every day, another intervention. Another plan.",
        "It didn't work. Not because he failed. Because I have to want it. And most days, I don't know what I want."
    ],
    "late": [
        "You need me to need you. I've figured that out. It's not about me—it's about you feeling useful.",
        "I don't want to be someone's project. I want to be seen."
    ],
    "trust_built": [
        "You stopped trying to fix me. You just... asked what I needed.",
        "No one's ever done that before. Most people assume they know."
    ],
    "trust_broken": [
        "I can't be your reason for existing. I can barely be my own reason.",
        "Please. Let me fail sometimes. Let me struggle. Let me be."
    ]
}

# ============================================================================
# DR. OKONKWO DIALOGUE BANK
# ============================================================================

OKONKWO_BASELINE = {
    "first_meeting": [
        "I'm Dr. Okonkwo. I take care of the crew's physical and, when needed, mental health.",
        "I've already examined the captain's body. Cause of death: heart failure. If you want details, you'll need to earn my trust first."
    ],
    "casual": [
        "Everyone carries something. Weight they don't show. My job is to help when they're ready.",
        "The captain carried more than anyone knew. I couldn't save him. Maybe no one could."
    ],
    "murder_question": [
        "The autopsy is complete. Heart failure. Natural causes, as far as I can determine."
    ]
}

OKONKWO_CONTROLLER = {
    "early": [
        "You want the full autopsy report. I understand the impulse—knowledge feels like power.",
        "But some knowledge is a burden. Are you prepared for that?"
    ],
    "mid": [
        "You've been investigating relentlessly. Every corner, every file, every secret.",
        "In medicine, we call that hypervigilance. It's usually a response to feeling helpless."
    ],
    "late": [
        "I've watched you try to control this investigation like a physician trying to control death.",
        "It doesn't work. Death doesn't obey. Neither does truth."
    ],
    "trust_built": [
        "The captain was dying. Before the murder. He had weeks left.",
        "I'm telling you because I think you can handle it. Because you've shown me you're more than your need to control."
    ],
    "trust_broken": [
        "You demanded information like it was your right. Medicine doesn't work that way. Trust doesn't work that way."
    ]
}

OKONKWO_GHOST = {
    "early": [
        "You keep your distance. I recognize the pattern—it's one I use myself.",
        "Professional distance, I tell myself. But that's just a respectable word for hiding."
    ],
    "mid": [
        "Isolation is a form of self-protection. It's also slow poison.",
        "I've treated patients who died surrounded by people they never let in. It's the loneliest way to go."
    ],
    "late": [
        "We're alike, you and I. We both hide behind competence and distance.",
        "But I'm starting to wonder if the thing we're protecting is worth the cost."
    ],
    "trust_built": [
        "You let me in. A little. That's more than I expected—more than I've allowed myself.",
        "Maybe we can both learn to stop hiding."
    ],
    "trust_broken": [
        "You kept me at arm's length. I understand. I do the same. But it still hurts."
    ]
}

OKONKWO_JUDGE = {
    "early": [
        "Medicine requires diagnosis—categorization. In that way, we're similar.",
        "But I've learned that people resist categories. They're always more complicated than their symptoms."
    ],
    "mid": [
        "You've rendered verdicts on everyone. Kai is weak. Torres is cold. Vasquez is fake.",
        "And you? What category do you put yourself in?"
    ],
    "late": [
        "I made an impossible choice once. The medical board judged me for it. Ended my career.",
        "They were wrong. Not about the outcome—about the judgment. Some choices have no right answer."
    ],
    "trust_built": [
        "The captain was dying. The murder was almost... redundant.",
        "What do you do with that? What category does that fit?"
    ],
    "trust_broken": [
        "You judged me for my past. For my choices. You don't have that right."
    ]
}

# ============================================================================
# VASQUEZ DIALOGUE BANK
# ============================================================================

VASQUEZ_BASELINE = {
    "first_meeting": [
        "Well, hello! New face on the ship. I'm Vasquez—cargo, logistics, general problem-solver.",
        "You need anything, I'm your guy. Door's always open. Metaphorically. Actually, literally too."
    ],
    "casual": [
        "How are you holding up? This whole murder thing—it's a lot.",
        "If you need to talk, I'm here. I'm a good listener. People tell me things."
    ],
    "murder_question": [
        "The captain? Tragic. He was a good man. I wish I knew more, but I was in the cargo bay all night."
    ]
}

VASQUEZ_CONTROLLER = {
    "early": [
        "You're thorough, I'll give you that. Going through everything with a fine-tooth comb.",
        "I respect the method. Just don't expect everyone to be as cooperative as me."
    ],
    "mid": [
        "I've been trying to help you, you know. Feeding you information. Maybe you've noticed?",
        "You're welcome, by the way."
    ],
    "late": [
        "You're looking at me differently now. Like you're waiting for the angle.",
        "Smart. There's always an angle. Question is whether you can see what it is."
    ],
    "trust_built": [
        "You see through me. Most people don't.",
        "I don't know if that's a relief or terrifying. Maybe both."
    ],
    "trust_broken": [
        "Okay. You got me. I've been managing what you know.",
        "But here's the thing—I wasn't lying. I was curating. There's a difference."
    ]
}

VASQUEZ_CYNIC = {
    "early": [
        "You don't believe a word I say, do you? I can see it in your eyes.",
        "That's okay. Healthy skepticism. I'd be suspicious of me too."
    ],
    "mid": [
        "Most people want to be liked. Want to believe I'm genuine.",
        "You're different. You see everyone as a potential threat. That's lonely, isn't it?"
    ],
    "late": [
        "I'll tell you a secret—I actually like you. Despite everything.",
        "You probably don't believe that either. But it's true. You're the most honest person on this ship, in your own twisted way."
    ],
    "trust_built": [
        "You trusted me. Against your every instinct, you trusted me.",
        "I'm not going to betray that. I know you're waiting for me to. But I'm not."
    ],
    "trust_broken": [
        "You were right not to trust me. I respect that, actually. At least you're consistent."
    ]
}

VASQUEZ_GHOST = {
    "early": [
        "You're a quiet one, huh? Hard to read.",
        "I like a challenge. Most people wear their hearts on their sleeves. You've got yours locked up somewhere."
    ],
    "mid": [
        "I've been trying to connect with you. Conversations. Shared meals. You keep slipping away.",
        "What are you afraid of?"
    ],
    "late": [
        "I used to think I wanted to be alone. Then I got what I wanted.",
        "Don't make my mistake. Whatever you're protecting, it's not worth the loneliness."
    ],
    "trust_built": [
        "You let me in. I wasn't sure you could.",
        "For what it's worth—I'll try to be worth it. For once."
    ],
    "trust_broken": [
        "You kept me out. I tried, but you wouldn't let me in. That's on you, not me."
    ]
}

# ============================================================================
# EMBER DIALOGUE BANK
# ============================================================================

EMBER_BASELINE = {
    "first_meeting": [
        "You're the one asking questions about the captain. I'm Ember.",
        "I'm watching everyone. I've been watching my whole life. It's how you survive."
    ],
    "casual": [
        "Did you ever wonder what's between the stars? Not the planets or the stations. The nothing.",
        "I think about it a lot. The empty spaces. What fills them."
    ],
    "murder_question": [
        "I don't know who killed him. But I know he was sad the night before. Really sad."
    ]
}

EMBER_CONTROLLER = {
    "early": [
        "You have a lot of lists. I've noticed. Notes about everyone.",
        "My contract holders kept lists too. About productivity. About worth."
    ],
    "mid": [
        "You need to know everything. I can see it—the way uncertainty makes you uncomfortable.",
        "My mom was like that. Before she sold me. She needed to control everything."
    ],
    "late": [
        "You never stop. Every question has to have an answer. Every person has to be figured out.",
        "But some things can't be known. Some people can't be controlled. What happens when you meet something you can't solve?"
    ],
    "trust_built": [
        "You stopped. For once, you just... stopped trying to figure me out.",
        "You just listened. That's new."
    ],
    "trust_broken": [
        "You're doing it again. The thing where you need to know everything about me.",
        "I'm not a puzzle. I'm a person."
    ]
}

EMBER_JUDGE = {
    "early": [
        "You've already decided about people. I can see it in how you look at them.",
        "You look at Kai like he's a problem. At Torres like she's a threat. At Vasquez like he's a liar."
    ],
    "mid": [
        "What about me? What have you decided I am?",
        "Don't lie. You've categorized everyone else. I want to know my category."
    ],
    "late": [
        "You scare me a little. Because you're so certain.",
        "But people aren't certain. People are complicated. What if you're wrong about everyone?"
    ],
    "trust_built": [
        "You're learning. I can see it. You're starting to see people as more than their worst moments.",
        "That's brave. It's easier to judge."
    ],
    "trust_broken": [
        "You judged me. For stowing away. For running. For being a kid who didn't know better.",
        "I hope you never get judged like you judge others. It would break you."
    ]
}

EMBER_GHOST = {
    "early": [
        "You're not really here, are you? You're... somewhere else.",
        "I've known people like that. They survive but they don't live."
    ],
    "mid": [
        "I've tried to talk to you. About real things. About what I'm feeling.",
        "Every time, you change the subject. Or you leave. It's like you're allergic to connection."
    ],
    "late": [
        "Why won't you let anyone in?",
        "I've told you real things. About my life, my fears. And every time, you pull away. Are you even here? Or are you already gone?"
    ],
    "trust_built": [
        "You stayed. For once, you stayed for the whole conversation.",
        "That means you're still in there somewhere. The real you."
    ],
    "trust_broken": [
        "I give up. I tried to reach you. But you're not reachable.",
        "I hope you find someone who can get through. Because it won't be me."
    ]
}

EMBER_FUGITIVE = {
    "early": [
        "You never talk about before. Where you came from.",
        "I don't either, usually. But I told you. And you still haven't told me."
    ],
    "mid": [
        "We're both running from something, aren't we? I can tell.",
        "I'm running from servitude. What are you running from?"
    ],
    "late": [
        "I told you my story. All of it. The servitude, the escape, everything.",
        "And you've told me nothing. It's not fair. What happened? What made you who you are? Why can't you say?"
    ],
    "trust_built": [
        "Thank you. For telling me. Finally.",
        "I know that was hard. It's hard for me too. But now we're real to each other."
    ],
    "trust_broken": [
        "You're still running. Even now.",
        "I hope you stop someday. But I can't wait forever."
    ]
}

EMBER_CYNIC = {
    "early": [
        "You look at people like they're going to hurt you. All the time.",
        "I used to do that too. Some of the overseers—you had to watch them constantly."
    ],
    "mid": [
        "You expect everyone to be bad. That must be exhausting.",
        "What happened to you? To make you see threats everywhere?"
    ],
    "late": [
        "I trusted you. Did you know that? From early on.",
        "You probably don't believe me. You don't believe anyone. But it's true. Doesn't it get exhausting? Expecting everyone to be bad?"
    ],
    "trust_built": [
        "You trusted me back. I didn't think you could.",
        "Maybe there's hope for you after all."
    ],
    "trust_broken": [
        "You pushed me away. Like everyone else. I tried to connect and you assumed I had an angle.",
        "I didn't. I was just... lonely. But you couldn't see that."
    ]
}

# ============================================================================
# DIALOGUE BANK REGISTRY
# ============================================================================

DIALOGUE_BANKS = {
    "torres": {
        "baseline": TORRES_BASELINE,
        "controller": TORRES_CONTROLLER,
        "judge": TORRES_JUDGE,
        "ghost": TORRES_GHOST,
        "fugitive": TORRES_FUGITIVE,
        "cynic": TORRES_CYNIC,
        "savior": TORRES_SAVIOR,
    },
    "kai": {
        "baseline": KAI_BASELINE,
        "controller": KAI_CONTROLLER,
        "judge": KAI_JUDGE,
        "ghost": KAI_GHOST,
        "savior": KAI_SAVIOR,
    },
    "okonkwo": {
        "baseline": OKONKWO_BASELINE,
        "controller": OKONKWO_CONTROLLER,
        "ghost": OKONKWO_GHOST,
        "judge": OKONKWO_JUDGE,
    },
    "vasquez": {
        "baseline": VASQUEZ_BASELINE,
        "controller": VASQUEZ_CONTROLLER,
        "cynic": VASQUEZ_CYNIC,
        "ghost": VASQUEZ_GHOST,
    },
    "ember": {
        "baseline": EMBER_BASELINE,
        "controller": EMBER_CONTROLLER,
        "judge": EMBER_JUDGE,
        "ghost": EMBER_GHOST,
        "fugitive": EMBER_FUGITIVE,
        "cynic": EMBER_CYNIC,
    }
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_dialogue(
    npc_id: str,
    archetype: str,
    relationship_stage: RelationshipStage,
    trust_score: float,
    context: DialogueContext = DialogueContext.CASUAL
) -> Optional[str]:
    """
    Retrieve appropriate dialogue for an NPC based on player archetype and relationship state.
    
    Args:
        npc_id: NPC identifier (torres, kai, okonkwo, vasquez, ember)
        archetype: Player's dominant archetype (controller, judge, ghost, etc.)
        relationship_stage: Current relationship stage (early, mid, late)
        trust_score: Current trust level (-1.0 to 1.0)
        context: Dialogue context (first_meeting, casual, murder_question, etc.)
    
    Returns:
        Dialogue string or None if not found
    """
    npc_id = npc_id.lower()
    archetype = archetype.lower()
    
    if npc_id not in DIALOGUE_BANKS:
        return None
    
    npc_bank = DIALOGUE_BANKS[npc_id]
    
    # Handle baseline contexts first
    if context in [DialogueContext.FIRST_MEETING, DialogueContext.CASUAL, DialogueContext.MURDER_QUESTION]:
        baseline = npc_bank.get("baseline", {})
        lines = baseline.get(context.value, [])
        if lines:
            import random
            return random.choice(lines)
    
    # Handle archetype-specific dialogue
    if archetype not in npc_bank:
        # Fallback to baseline casual if archetype not found
        baseline = npc_bank.get("baseline", {})
        lines = baseline.get("casual", [])
        if lines:
            import random
            return random.choice(lines)
        return None
    
    archetype_bank = npc_bank[archetype]
    
    # Determine which dialogue set to use based on trust and stage
    if trust_score > 0.7:
        # High trust - check for trust_built dialogue
        if "trust_built" in archetype_bank:
            lines = archetype_bank["trust_built"]
            if lines:
                import random
                return random.choice(lines)
    elif trust_score < -0.3:
        # Low trust - check for trust_broken dialogue
        if "trust_broken" in archetype_bank:
            lines = archetype_bank["trust_broken"]
            if lines:
                import random
                return random.choice(lines)
    
    # Use stage-based dialogue
    stage_key = relationship_stage.value
    if stage_key in archetype_bank:
        lines = archetype_bank[stage_key]
        if lines:
            import random
            return random.choice(lines)
    
    # Final fallback to baseline
    baseline = npc_bank.get("baseline", {})
    lines = baseline.get("casual", [])
    if lines:
        import random
        return random.choice(lines)
    
    return None


def get_relationship_stage(interaction_count: int) -> RelationshipStage:
    """
    Determine relationship stage based on interaction count.
    
    Args:
        interaction_count: Number of interactions with this NPC
    
    Returns:
        RelationshipStage enum value
    """
    if interaction_count < 3:
        return RelationshipStage.EARLY
    elif interaction_count < 8:
        return RelationshipStage.MID
    else:
        return RelationshipStage.LATE
