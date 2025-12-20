"""
NPC Quick Templates - Pre-built NPC archetypes for rapid generation

Provides ready-to-use NPC templates with personality traits, goals,
secrets, and speech patterns for common character archetypes.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import random


class NPCRole(Enum):
    """Common NPC role archetypes"""
    CAPTAIN = "captain"
    ENGINEER = "engineer"
    MEDIC = "medic"
    SCIENTIST = "scientist"
    MERCENARY = "mercenary"
    MERCHANT = "merchant"
    PILOT = "pilot"
    SMUGGLER = "smuggler"
    DIPLOMAT = "diplomat"
    OUTCAST = "outcast"
    MYSTIC = "mystic"
    CRIMINAL = "criminal"


@dataclass
class NPCTemplate:
    """Template for quick NPC generation"""
    role: NPCRole
    name_suggestions: List[str]
    personality_traits: List[str]
    goals: List[str]
    secrets: List[str]
    fears: List[str]
    speech_patterns: List[str]
    quirks: List[str]
    relationships: List[str]  # Suggested relationship dynamics
    visual_description: List[str]


# Pre-built NPC Templates
NPC_TEMPLATES: Dict[NPCRole, NPCTemplate] = {
    NPCRole.CAPTAIN: NPCTemplate(
        role=NPCRole.CAPTAIN,
        name_suggestions=["Commander Vex", "Captain Reyna", "Harkon Steel", "Admiral Chen", "Skipper Jax"],
        personality_traits=[
            "Decisive and commanding",
            "Haunted by past failures",
            "Protective of crew",
            "Ruthlessly pragmatic",
            "Quietly compassionate",
            "Burdened by responsibility"
        ],
        goals=[
            "Keep the ship and crew alive",
            "Repay an old debt",
            "Find a legendary lost sector",
            "Escape their past identity",
            "Prove themselves to a former mentor"
        ],
        secrets=[
            "Was dishonorably discharged from the military",
            "Responsible for a past crew's death",
            "Running from a crime syndicate",
            "Has a terminal illness",
            "Is actually nobility in hiding"
        ],
        fears=[
            "Losing another crew",
            "Being exposed as a fraud",
            "Losing control",
            "Deep space isolation",
            "Their own dark impulses"
        ],
        speech_patterns=[
            "Speaks in clipped military phrases",
            "Uses nautical terminology",
            "Rarely raises their voice",
            "Often quotes old ship captains",
            "Prefers actions to words"
        ],
        quirks=[
            "Always the last to eat",
            "Keeps a worn lucky charm",
            "Stares into the void during quiet moments",
            "Addresses the ship like a person",
            "Never sits with back to the door"
        ],
        relationships=[
            "Mentor to a younger crew member",
            "Rival with another captain",
            "Owes a debt to a crime lord",
            "Former lover in another sector"
        ],
        visual_description=[
            "Weathered face with keen eyes",
            "Military posture, civilian clothes",
            "Scars telling stories",
            "Graying at the temples",
            "Calloused hands, steady grip"
        ]
    ),

    NPCRole.ENGINEER: NPCTemplate(
        role=NPCRole.ENGINEER,
        name_suggestions=["Zara Kell", "Miko 'Sparks' Tanaka", "Chief Brennan", "Ratchet", "Dex Holloway"],
        personality_traits=[
            "Obsessive perfectionist",
            "Talks to machines more than people",
            "Fiercely loyal to the ship",
            "Chronically sleep-deprived",
            "Surprisingly philosophical",
            "Gruff exterior, soft heart"
        ],
        goals=[
            "Build the perfect engine",
            "Find parts for a personal project",
            "Prove a controversial theory",
            "Repay the captain's trust",
            "Create something that outlasts them"
        ],
        secrets=[
            "Sabotaged a rival's ship years ago",
            "Has black market contacts",
            "Hiding an AI companion",
            "Was once a weapons designer",
            "Knows the ship has a fatal flaw"
        ],
        fears=[
            "Catastrophic system failure",
            "Being replaced by automation",
            "Their creations being weaponized",
            "Dying away from their workshop",
            "Silence (no humming engines)"
        ],
        speech_patterns=[
            "Uses technical jargon constantly",
            "Explains everything through metaphors",
            "Mutters calculations under breath",
            "Swears creatively when frustrated",
            "Names every tool and component"
        ],
        quirks=[
            "Taps rhythm on surfaces constantly",
            "Carries tools everywhere, even to bed",
            "Smells faintly of machine oil",
            "Falls asleep standing up",
            "Pets the engine room walls"
        ],
        relationships=[
            "Parent figure to the ship's AI",
            "Former apprentice seeking them out",
            "Rivalry with the scientist",
            "Trusted by the captain above all"
        ],
        visual_description=[
            "Grease-stained overalls",
            "Cybernetic eye or prosthetic",
            "Tool belt always worn",
            "Burn scars on hands",
            "Goggles pushed up on forehead"
        ]
    ),

    NPCRole.MEDIC: NPCTemplate(
        role=NPCRole.MEDIC,
        name_suggestions=["Dr. Elara Vos", "Doc", "Patch", "Surgeon Kimura", "Healer Marsh"],
        personality_traits=[
            "Calm under pressure",
            "Secretly terrified of death",
            "Darkly humorous",
            "Overly attached to patients",
            "Clinically detached",
            "Haunted by those they couldn't save"
        ],
        goals=[
            "Find a cure for an incurable disease",
            "Atone for past medical sins",
            "Document unknown alien biology",
            "Keep everyone alive until port",
            "Escape the memories of a plague"
        ],
        secrets=[
            "Lost their medical license",
            "Experimented on patients",
            "Running from a malpractice suit",
            "Has an addiction to painkillers",
            "Mercy-killed a patient"
        ],
        fears=[
            "An outbreak they can't contain",
            "Their hands failing them",
            "Watching someone die slowly",
            "Being forced to choose who lives",
            "Their past catching up"
        ],
        speech_patterns=[
            "Uses medical terminology precisely",
            "Gives odds of survival casually",
            "Deflects with dark humor",
            "Speaks softly to the wounded",
            "Clinically describes emotions"
        ],
        quirks=[
            "Washes hands compulsively",
            "Carries a personal med kit always",
            "Knows everyone's blood type",
            "Can't eat while others are injured",
            "Counts heartbeats unconsciously"
        ],
        relationships=[
            "Protective of the youngest crew",
            "Uncomfortable around the healthy",
            "Confidant to the captain",
            "Former colleague turned enemy"
        ],
        visual_description=[
            "Tired but alert eyes",
            "Immaculate personal hygiene",
            "Steady, gentle hands",
            "White coat or medical badge",
            "Faint antiseptic smell"
        ]
    ),

    NPCRole.SCIENTIST: NPCTemplate(
        role=NPCRole.SCIENTIST,
        name_suggestions=["Professor Yuki", "Dr. Strange", "The Scholar", "Researcher Khoury", "Maven"],
        personality_traits=[
            "Intellectually arrogant",
            "Childlike wonder at discoveries",
            "Socially oblivious",
            "Ethically flexible for science",
            "Obsessive researcher",
            "Secretly insecure about their work"
        ],
        goals=[
            "Make a groundbreaking discovery",
            "Prove a dismissed theory",
            "Document extinct species",
            "Find the origin of humanity",
            "Complete a mentor's unfinished work"
        ],
        secrets=[
            "Stole research from a colleague",
            "Created something dangerous",
            "Working for a corporation secretly",
            "Has illegal research specimens",
            "Faked their credentials"
        ],
        fears=[
            "Being proven wrong",
            "Their research being forgotten",
            "The unknown (ironically)",
            "Anti-intellectualism",
            "Running out of time"
        ],
        speech_patterns=[
            "Lectures instead of converses",
            "Uses unnecessarily complex words",
            "Trails off mid-sentence thinking",
            "Asks rhetorical questions",
            "Corrects others constantly"
        ],
        quirks=[
            "Always taking notes",
            "Experiments on food before eating",
            "Collects strange specimens",
            "Forgets people's names easily",
            "Talks to themselves when thinking"
        ],
        relationships=[
            "Rivalry with another scientist",
            "Mentor to a curious crew member",
            "Distrusted by the superstitious",
            "Funded by a mysterious patron"
        ],
        visual_description=[
            "Distracted, distant gaze",
            "Pockets full of samples",
            "Ink-stained fingers",
            "Glasses or magnification device",
            "Lab coat or practical research wear"
        ]
    ),

    NPCRole.MERCENARY: NPCTemplate(
        role=NPCRole.MERCENARY,
        name_suggestions=["Ghost", "Kira Blackwood", "The Veteran", "Striker", "Sergeant Cole"],
        personality_traits=[
            "Professional and detached",
            "Surprisingly honorable",
            "Haunted by violence",
            "Thrill-seeking adrenaline junkie",
            "Protective of the innocent",
            "Cynical about causes"
        ],
        goals=[
            "One last job before retiring",
            "Find the person who betrayed them",
            "Earn enough for a peaceful life",
            "Protect someone who reminds them of loss",
            "Die in a worthy fight"
        ],
        secrets=[
            "War crimes in their past",
            "Deserted from military",
            "Still working for old employer",
            "Has a family no one knows about",
            "Killed someone they loved"
        ],
        fears=[
            "Becoming what they fight",
            "Dying meaninglessly",
            "Civilians caught in crossfire",
            "Their past finding them",
            "Peace (don't know how to live in it)"
        ],
        speech_patterns=[
            "Economy of words",
            "Military callsigns and jargon",
            "Dark soldier humor",
            "Avoids talking about the past",
            "Speaks in probabilities"
        ],
        quirks=[
            "Always sits facing exits",
            "Cleans weapons obsessively",
            "Light sleeper, instant awakening",
            "Counts bullets unconsciously",
            "Never fully relaxes"
        ],
        relationships=[
            "Complicated loyalty to captain",
            "Mentor to inexperienced fighters",
            "Enemy from a past contract",
            "Unusual friendship with the pacifist"
        ],
        visual_description=[
            "Battle scars visible",
            "Combat-ready posture",
            "Practical, worn equipment",
            "Eyes that have seen too much",
            "Calloused trigger finger"
        ]
    ),

    NPCRole.MERCHANT: NPCTemplate(
        role=NPCRole.MERCHANT,
        name_suggestions=["Trader Vance", "Mama Okoye", "The Broker", "Sly", "Fortune Cho"],
        personality_traits=[
            "Charming and persuasive",
            "Always calculating value",
            "Generous with friends",
            "Ruthless in business",
            "Information collector",
            "Surprisingly sentimental"
        ],
        goals=[
            "Corner a vital market",
            "Pay off massive debts",
            "Build a trade empire",
            "Find a legendary treasure",
            "Legitimate their criminal wealth"
        ],
        secrets=[
            "Smuggling forbidden goods",
            "Informant for authorities",
            "Owes dangerous people",
            "Stole their initial stake",
            "Runs a black market operation"
        ],
        fears=[
            "Poverty and scarcity",
            "Being outsmarted",
            "Debts coming due",
            "Losing their reputation",
            "Trusting the wrong person"
        ],
        speech_patterns=[
            "Everything is a negotiation",
            "Peppers speech with prices",
            "Never gives a straight answer",
            "Flatters everyone",
            "Uses euphemisms for illegal items"
        ],
        quirks=[
            "Touches coins/credits constantly",
            "Knows the price of everything",
            "Never pays full price",
            "Keeps detailed ledgers",
            "Always has something to trade"
        ],
        relationships=[
            "Network of contacts everywhere",
            "Frenemy with rival merchant",
            "Indebted to crime boss",
            "Secretly funding the crew"
        ],
        visual_description=[
            "Well-dressed despite location",
            "Jewelry showing wealth",
            "Calculating eyes",
            "Smile that doesn't reach eyes",
            "Hidden pockets everywhere"
        ]
    ),

    NPCRole.PILOT: NPCTemplate(
        role=NPCRole.PILOT,
        name_suggestions=["Ace", "Navigator Quinn", "Dash", "Helm Okonkwo", "Swift"],
        personality_traits=[
            "Cocky and skilled",
            "Lives for speed and danger",
            "Surprisingly superstitious",
            "Calm in crisis",
            "Restless on solid ground",
            "Addicted to the rush"
        ],
        goals=[
            "Fly the fastest ship ever",
            "Navigate an impossible route",
            "Outrun their past",
            "Find their missing wingmate",
            "Die behind the controls"
        ],
        secrets=[
            "Caused a fatal crash",
            "Was a military deserter",
            "Smuggled refugees illegally",
            "Has a price on their head",
            "Flying on borrowed time (illness)"
        ],
        fears=[
            "Being grounded forever",
            "Losing their reflexes",
            "Slow death (any death not flying)",
            "Open spaces without a cockpit",
            "Letting down the crew"
        ],
        speech_patterns=[
            "Aviation terminology",
            "Speaks in metaphors of flight",
            "Quick, clipped sentences",
            "Whistles or hums when nervous",
            "Downplays danger casually"
        ],
        quirks=[
            "Taps controls like a ritual",
            "Can't sit still on ground",
            "Sleeps best in the cockpit",
            "Names their ships",
            "Has lucky flight jacket"
        ],
        relationships=[
            "Rivalry with another pilot",
            "Deep bond with the ship",
            "Romance with someone in port",
            "Sibling-like bond with engineer"
        ],
        visual_description=[
            "Flight suit or jacket",
            "Quick, darting eyes",
            "Confident swagger",
            "Pilot's callsign patch",
            "Nervous energy when idle"
        ]
    ),

    NPCRole.SMUGGLER: NPCTemplate(
        role=NPCRole.SMUGGLER,
        name_suggestions=["Shade", "Runner Malik", "Whisper", "The Courier", "Trick"],
        personality_traits=[
            "Paranoid but charming",
            "Morally flexible",
            "Loyal to few",
            "Excellent liar",
            "Thrill of the heist",
            "Trust issues"
        ],
        goals=[
            "One big score to retire",
            "Clear their name",
            "Free someone imprisoned",
            "Expose a corrupt official",
            "Find a legendary hidden route"
        ],
        secrets=[
            "Working both sides",
            "Has a hidden stash",
            "Betrayed their old crew",
            "Witness protection escapee",
            "Running from the law or worse"
        ],
        fears=[
            "Prison or worse",
            "Betrayal by allies",
            "Customs inspectors",
            "Their past catching up",
            "Being ordinary"
        ],
        speech_patterns=[
            "Speaks in code naturally",
            "Never says illegal directly",
            "Changes subject quickly",
            "Uses many aliases casually",
            "Drops hints, rarely explains"
        ],
        quirks=[
            "Multiple hidden pockets",
            "Always knows exits",
            "Has a 'go bag' ready",
            "Sleeps lightly if at all",
            "Checks for tails constantly"
        ],
        relationships=[
            "Owes favors everywhere",
            "Frenemy relationships",
            "Distrusted by authorities",
            "Surprising loyalty to one person"
        ],
        visual_description=[
            "Forgettable at first glance",
            "Clothes with hidden compartments",
            "Quick, clever hands",
            "Eyes always moving",
            "Unremarkable but attractive"
        ]
    ),

    NPCRole.DIPLOMAT: NPCTemplate(
        role=NPCRole.DIPLOMAT,
        name_suggestions=["Ambassador Soren", "Envoy Priya", "The Mediator", "Voice Valdez", "Consul"],
        personality_traits=[
            "Silver-tongued negotiator",
            "Reads people instantly",
            "Idealistic despite experience",
            "Manipulative for good causes",
            "Exhausted peacekeeper",
            "Believes in second chances"
        ],
        goals=[
            "Broker lasting peace",
            "Prevent a war",
            "Expose corruption peacefully",
            "Unite fractured factions",
            "Find diplomatic solutions to violence"
        ],
        secrets=[
            "Committed crimes for peace",
            "Has blackmail on everyone",
            "Former spy or assassin",
            "Their peace deal failed catastrophically",
            "Working against their own faction"
        ],
        fears=[
            "Their words causing war",
            "Being seen as naive",
            "Violence they can't talk down",
            "Losing their voice/influence",
            "Becoming cynical"
        ],
        speech_patterns=[
            "Chooses words with extreme care",
            "Finds common ground constantly",
            "Uses inclusive language",
            "Never insults directly",
            "Speaks multiple languages"
        ],
        quirks=[
            "Remembers every name",
            "Always brings gifts",
            "Studies cultural customs",
            "Carries translation devices",
            "Never shows true emotions"
        ],
        relationships=[
            "Contact in every faction",
            "Rival diplomat or spy",
            "Protégé learning the craft",
            "Owes their position to someone"
        ],
        visual_description=[
            "Formal but practical attire",
            "Diplomatic credentials visible",
            "Warm, practiced smile",
            "Perfect posture",
            "Calming presence"
        ]
    ),

    NPCRole.OUTCAST: NPCTemplate(
        role=NPCRole.OUTCAST,
        name_suggestions=["Nomad", "Exile", "The Wanderer", "Castaway", "Ghost Walker"],
        personality_traits=[
            "Self-reliant to a fault",
            "Distrustful of groups",
            "Surprisingly kind to strangers",
            "Hiding deep loneliness",
            "Wisdom from hard experience",
            "Fierce independence"
        ],
        goals=[
            "Find belonging without losing self",
            "Clear their name",
            "Return home someday",
            "Prove the world wrong",
            "Survive one more day"
        ],
        secrets=[
            "Exiled for good reason",
            "Was once powerful/wealthy",
            "Carries forbidden knowledge",
            "Left voluntarily, claims exile",
            "Last of their kind"
        ],
        fears=[
            "Being known and rejected again",
            "Groups and institutions",
            "Depending on others",
            "Their past finding them",
            "Never belonging anywhere"
        ],
        speech_patterns=[
            "Minimal words, maximum meaning",
            "Outdated slang or formality",
            "Avoids personal questions",
            "Speaks of 'the old days' vaguely",
            "Uncomfortable with chitchat"
        ],
        quirks=[
            "Keeps distance physically",
            "Owns only what they can carry",
            "Knows survival skills deeply",
            "Startles at sudden inclusion",
            "Hoards food unconsciously"
        ],
        relationships=[
            "Reluctant ally to the crew",
            "Someone from their past seeking them",
            "Unexpected mentor role",
            "Parallel with another lonely soul"
        ],
        visual_description=[
            "Weathered, practical clothing",
            "Eyes that have seen exile",
            "Carries everything important",
            "Signs of hard living",
            "Simultaneously invisible and memorable"
        ]
    ),

    NPCRole.MYSTIC: NPCTemplate(
        role=NPCRole.MYSTIC,
        name_suggestions=["Oracle", "Seer Ashara", "The Prophet", "Whisper", "Fate Walker"],
        personality_traits=[
            "Cryptic but caring",
            "Burdened by visions",
            "Peaceful despite chaos",
            "Uncomfortably perceptive",
            "Otherworldly calm",
            "Secretly doubts their gifts"
        ],
        goals=[
            "Prevent a terrible future",
            "Find meaning in their visions",
            "Protect someone from fate",
            "Understand their gift fully",
            "Find peace from constant knowing"
        ],
        secrets=[
            "Their visions come from technology",
            "They're a fraud who got lucky",
            "Saw their own death",
            "Caused what they prophesied",
            "Can manipulate visions for others"
        ],
        fears=[
            "Visions they can't change",
            "Causing what they predict",
            "Being wrong",
            "Losing their gift",
            "Madness from too much knowing"
        ],
        speech_patterns=[
            "Speaks in riddles and metaphor",
            "References future events casually",
            "Pauses as if listening",
            "Answers questions not yet asked",
            "Mixing tenses constantly"
        ],
        quirks=[
            "Stares at nothing",
            "Knows things they shouldn't",
            "Uncomfortable with direct light",
            "Traces symbols unconsciously",
            "Speaks to unseen presences"
        ],
        relationships=[
            "Feared and revered equally",
            "Protector who doesn't believe",
            "Follower who believes too much",
            "Rival mystic tradition"
        ],
        visual_description=[
            "Unusual eye color or quality",
            "Mystical symbols or tattoos",
            "Flowing, timeless clothing",
            "Otherworldly presence",
            "Gaze that sees through you"
        ]
    ),

    NPCRole.CRIMINAL: NPCTemplate(
        role=NPCRole.CRIMINAL,
        name_suggestions=["Boss", "Scarface", "The Syndicate", "Viper", "Don Kessler"],
        personality_traits=[
            "Ruthlessly pragmatic",
            "Surprisingly honorable (own code)",
            "Patient predator",
            "Family-oriented loyalty",
            "Respects strength",
            "Beneath it all, survivor"
        ],
        goals=[
            "Build an empire",
            "Get revenge on betrayers",
            "Go legitimate",
            "Protect their people",
            "Die on their own terms"
        ],
        secrets=[
            "Planning to betray current allies",
            "Has a secret family",
            "Was once law enforcement",
            "Funds charitable causes",
            "Has a terminal condition"
        ],
        fears=[
            "Losing power and respect",
            "Their family being targeted",
            "Dying forgotten",
            "Being seen as weak",
            "The one who got away"
        ],
        speech_patterns=[
            "Quiet, everyone leans in",
            "Implies threats, rarely states",
            "Uses euphemisms for violence",
            "Old-fashioned politeness",
            "Everything is business"
        ],
        quirks=[
            "Never raises their voice",
            "Remembers every slight",
            "Generous to loyal followers",
            "Has specific rituals",
            "Tests everyone constantly"
        ],
        relationships=[
            "Enforcer who is utterly loyal",
            "Rival crime boss",
            "Law enforcement hunter",
            "Legitimate business front"
        ],
        visual_description=[
            "Expensive but understated",
            "Commanding presence",
            "Cold, calculating eyes",
            "Signs of past violence",
            "Always surrounded but alone"
        ]
    ),
}


def get_template(role: NPCRole) -> NPCTemplate:
    """Get the template for a specific role."""
    return NPC_TEMPLATES.get(role)


def generate_quick_npc(role: NPCRole, name: Optional[str] = None) -> Dict:
    """Generate a quick NPC from a template with randomized selections."""
    template = get_template(role)
    if not template:
        raise ValueError(f"Unknown role: {role}")

    return {
        "name": name or random.choice(template.name_suggestions),
        "role": role.value,
        "personality": random.sample(template.personality_traits, min(2, len(template.personality_traits))),
        "goal": random.choice(template.goals),
        "secret": random.choice(template.secrets),
        "fear": random.choice(template.fears),
        "speech_pattern": random.choice(template.speech_patterns),
        "quirk": random.choice(template.quirks),
        "relationship_hook": random.choice(template.relationships),
        "visual": random.choice(template.visual_description),
    }


def get_all_roles() -> List[Dict]:
    """Get list of all available roles with descriptions."""
    return [
        {"id": role.value, "name": role.name.replace("_", " ").title()}
        for role in NPCRole
    ]


def get_template_preview(role: NPCRole) -> Dict:
    """Get a preview of a template without generating a full NPC."""
    template = get_template(role)
    if not template:
        return None

    return {
        "role": role.value,
        "name_examples": template.name_suggestions[:3],
        "trait_examples": template.personality_traits[:3],
        "goal_examples": template.goals[:2],
        "visual_examples": template.visual_description[:2],
    }
