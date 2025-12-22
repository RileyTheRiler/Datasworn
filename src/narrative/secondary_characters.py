"""
Secondary Characters Data Module.
Contains the detailed backstory, arc phases, and micro-revelation logic
for the 5 secondary crew members of the Exile Gambit.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

class ArcPhase(str, Enum):
    BEGINNING = "beginning"
    MID_GAME = "mid_game"
    CRISIS = "crisis"
    ENDING_HERO = "ending_hero"
    ENDING_TRAGEDY = "ending_tragedy"

@dataclass
class MicroRevelation:
    """A specific piece of knowledge or character depth revealed at a certain threshold."""
    id: str
    revelation_text: str
    trigger_condition: str  # Description of what triggers this
    is_revealed: bool = False

@dataclass
class CharacterArcState:
    """Current state of a character's narrative arc."""
    phase: ArcPhase = ArcPhase.BEGINNING
    trust_score: float = 0.0  # -1.0 to 1.0 (Distrust <-> Trust)
    is_hero_path: bool = True # Toggles based on player choices
    unlocked_revelations: List[str] = field(default_factory=list)

@dataclass
class SecondaryCharacter:
    """Rich data model for a secondary character."""
    id: str
    name: str
    role: str
    age: int
    
    # Core Identity
    central_problem_answer: str
    psychological_wound: str
    what_she_wants: List[str]
    what_she_fears: List[str]
    
    # Narrative Content
    backstory_summary: str
    chronological_history: Dict[str, str] # e.g. "Age 16": "Brother killed..."
    
    # Secret Knowledge (The clue they hold regarding the main Captain/Yuki plot)
    secret_knowledge: str
    
    # Dynamic Arc Content
    dialogue_opening: str
    dialogue_hero_ending: str
    dialogue_tragedy_ending: str
    
    # Interactions
    relationship_to_player_trust: str
    relationship_to_player_distrust: str
    
    # Fields with defaults MUST come after non-default fields
    secret_knowledge_revealed: bool = False
    
    # Micro Revelations specific to this char
    micro_revelations: List[MicroRevelation] = field(default_factory=list)

# ============================================================================
# DATA POPULATION (From User Prompt)
# ============================================================================

TORRES = SecondaryCharacter(
    id="torres",
    name="Elena Torres",
    role="Pilot / Navigation",
    age=34,
    central_problem_answer="Connection requires trust. Trust requires proof. Most people can't provide proof. Therefore, most connections are dangerous.",
    psychological_wound="Betrayed by the military system she believed in; court-martialed for disobeying orders to save lives.",
    what_she_wants=[
        "To find someone worthy of trust",
        "To stop being right about everyone being untrustworthy",
        "To belong somewhere that deserves her loyalty"
    ],
    what_she_fears=[
        "Trusting again and being betrayed again",
        "Becoming so closed off that she can't recognize trustworthy people",
        "Dying alone because she pushed everyone away"
    ],
    backstory_summary="Former military pilot. Court-martialed for saving her squad against orders when intelligence betrayed them. Joined Reyes because he asked her to question him.",
    chronological_history={
        "Age 16": "Brother Mateo killed in action due to officer incompetence/cover-up. Parents accepted the lie; Elena kept a 'second set of books'.",
        "Age 28": "Flight wing ambushed due to sold intel. Disobeyed orders to save herself and report the truth. Court-martialed for 'disobeying orders'.",
        "Age 30": "Drifting, blacklisted. Reyes found her drinking alone and hired her for her cynicism.",
        "Age 34": "Current day. Saw Yuki near Captain's quarters at 0300 on the night of the murder."
    },
    secret_knowledge="She saw Yuki coming from the captain's quarters around 0300 on the night of the death. No security reason for Yuki to be there.",
    dialogue_opening="I don't know you. You're the captain because the vote said so. Don't expect me to salute.",
    dialogue_hero_ending="I've spent years waiting for everyone to disappoint me. Maybe I was wrong. Maybe I just hadn't found the right people yet.",
    dialogue_tragedy_ending="I told myself I'd know real trust when I found it. Turns out, I was right all along. There isn't any.",
    relationship_to_player_trust="I don't say this often. But I trust you. Don't make me regret it.",
    relationship_to_player_distrust="I gave you a chance. That's more than most get. We're done.",
    micro_revelations=[
        MicroRevelation(
            id="torres_brother",
            revelation_text="My brother didn't die a hero. He died because his CO wanted a promotion and didn't check the recon. They gave my parents a medal to shut them up.",
            trigger_condition="Player questions her about her military service or loyalty."
        ),
        MicroRevelation(
            id="torres_sighting",
            revelation_text="I saw her. Yuki. Three A.M. coming out of the Captain's quarters. She looked... unresolved.",
            trigger_condition="Player gains HIGH trust and asks about the night of the murder."
        )
    ]
)

KAI = SecondaryCharacter(
    id="kai",
    name="Kai Nakamura",
    role="Chief Engineer",
    age=28,
    central_problem_answer="Connection hurts. When people really see you, they see how broken you are. Better to numb it. Better to float.",
    psychological_wound="Impossible expectations as a child prodigy created belief that his true self is inadequate. Addiction masks the anxiety of being a 'fraud'.",
    what_she_wants=[
        "To feel okay without substances",
        "To be valued for who he is, not what he can do",
        "To stop running from the person he sees in the mirror"
    ],
    what_she_fears=[
        "Being truly seen and found wanting",
        "That he's responsible for the deaths in his past accident",
        "That he'll never be able to stop using"
    ],
    backstory_summary="Former child prodigy and Helix Dynamics engineer. Burned out from pressure, turned to stims. Fired after a fatal accident he couldn't prevent due to intoxication.",
    chronological_history={
        "Age 12": "Identified as genius. Taking advanced courses. Parents distant and demanding.",
        "Age 17": "First use of stimulants to cope with exam anxiety. Felt 'normal' for the first time.",
        "Age 24": "Collapse. Too impaired during a system failure. Three people died. Fired and blacklisted.",
        "Age 26": "Reyes found him working on a station, saw his genius and his pain.",
        "Age 28": "Current day. Skimming fuel to pay old debts. Terrified of discovery."
    },
    secret_knowledge="Engineering logs show the Captain's cabin life support had a manual override lockout engaged 10 minutes before estimated time of death. Kai missed it because he was high.",
    dialogue_opening="Yeah, engines are... they're running hot. I'm handling it. Just... give me space, okay?",
    dialogue_hero_ending="For the first time, I think I might be okay. Not because I'm brilliant. Just because I'm here. Still here.",
    dialogue_tragedy_ending="I tried. I really tried. But I could never get far enough away from myself.",
    relationship_to_player_trust="You didn't write me off. Even when you saw the shakes. Thanks, Captain.",
    relationship_to_player_distrust="I'm just the mechanic, right? Use me until I break. That's what everyone does.",
    micro_revelations=[
        MicroRevelation(
            id="kai_accident",
            revelation_text="I wasn't just tired that day at Helix. I was using. Three people died because I was too slow. That's what I am.",
            trigger_condition="Player confronts Kai about his erratic behavior with compassion."
        ),
        MicroRevelation(
            id="kai_debts",
            revelation_text="The fuel... I've been selling it. Just a little. I owe bad people, Captain. I didn't want to bring them here.",
            trigger_condition="Player investigates the fuel shortage."
        )
    ]
)

OKONKWO = SecondaryCharacter(
    id="okonkwo",
    name="Dr. Sofia Okonkwo",
    role="Medical Officer",
    age=52,
    central_problem_answer="Some truths hurt too much to share. Sometimes mercy is silence. Sometimes distance is kindness.",
    psychological_wound="Trauma of an 'impossible choice' triage decision that killed a VIP and a child. Scapegoated and lost her license.",
    what_she_wants=[
        "To help without risking catastrophic failure again",
        "To be seen as more than her worst moment",
        "To find peace with what she did"
    ],
    what_she_fears=[
        "Making another impossible choice and failing again",
        "Being close to someone she might lose",
        "That she's been wrong all along about silence being kindness"
    ],
    backstory_summary="Former top trauma surgeon. Disgraced after a triage decision went politically wrong. Reyes hired her knowing the truth.",
    chronological_history={
        "Age 38": "Mass casualty event. Chose to save a child over a waiting administrator. Administrator died. Child died later. License suspended.",
        "Age 40-46": "The Wilderness years. Unlicensed work. Drifting.",
        "Age 46": "Reyes recruited her. 'You made an impossible choice. That makes you a human doctor.'",
        "Age 52": "Current day. Knows Reyes was dying anyway. Hiding the autopsy results."
    },
    secret_knowledge="Reyes was terminally ill (3-4 weeks to live). The autopsy showed heart failure but also subtle signs of oxygen deprivation (suffocation). She calls the murder 'redundant'.",
    dialogue_opening="I've reviewed the crew's physicals. Everyone is... adequate. I have no other reports.",
    dialogue_hero_ending="I thought I was protecting everyone. I was protecting myself. From connection. From failure. I'm done with distance.",
    dialogue_tragedy_ending="Some things are better left buried. Some truths serve no one. I was right to stay distant.",
    relationship_to_player_trust="You have steady hands, Captain. Metaphorically speaking. I can work with that.",
    relationship_to_player_distrust="I will do my job. Do not ask for more.",
    micro_revelations=[
        MicroRevelation(
            id="okonkwo_triage",
            revelation_text="It wasn't a mistake. I chose the child. I'd choose the child again. But the world doesn't care about right choices, only outcomes.",
            trigger_condition="Player asks about her past medical license."
        ),
        MicroRevelation(
            id="okonkwo_autopsy",
            revelation_text="His heart stopped, yes. But his blood oxygen was too low for a sudden attack. And... he was dying anyway, Captain. Weeks, maybe.",
            trigger_condition="Player gains HIGH trust and asks for the real autopsy report."
        )
    ]
)

VASQUEZ = SecondaryCharacter(
    id="vasquez",
    name="Miguel Vasquez",
    role="Cargo Master",
    age=41,
    central_problem_answer="Connection is a tool. Warmth is a performance. Give people what they need and they'll give you what you want.",
    psychological_wound="Orphaned and learned love is conditional on utility. An 'Impostor' who performs connection to survive.",
    what_she_wants=[
        "To stop performing and just... be",
        "Someone to see through the mask and still want him",
        "To find out if there's anything under the mask at all"
    ],
    what_she_fears=[
        "That there's no 'real' Vasquez",
        "Being truly seen and found empty",
        "Genuine connection (he doesn't know how)"
    ],
    backstory_summary="Career smuggler and con artist. Fell from a big score betrayal. Hiding on the Gambit with a fake identity.",
    chronological_history={
        "Age 0-16": "Orphan in port city. Learned to be useful to survive.",
        "Age 35": "Big medical supply heist went wrong. Partners betrayed him. Lost everything.",
        "Age 38": "Joined Gambit as 'Miguel Vasquez', logistics specialist.",
        "Age 41": "Current day. Carrying stolen Helix Dynamics addiction meds (worth a fortune, could save Kai). Pressured by Yuki."
    },
    secret_knowledge="He is smuggling high-grade addiction treatments stolen from Helix Dynamics. Yuki knows and is pressuring him. Ideally, he should give them to Kai.",
    dialogue_opening="Captain! Looking sharp. Anything you need, you come to me. I'm the guy who gets things.",
    dialogue_hero_ending="I've been pretending my whole life. But somewhere in the last three years... I started actually caring. About this ship. About you people.",
    dialogue_tragedy_ending="I almost believed it. Almost let myself think I could be... real. But I know how this ends. Better to leave first.",
    relationship_to_player_trust="You're good. You see right through me, don't you? It's... relaxing, actually.",
    relationship_to_player_distrust="Hey, we're all friends here! (His smile is perfect and completely empty)",
    micro_revelations=[
        MicroRevelation(
            id="vasquez_mask",
            revelation_text="Yeah, I've been playing you. Playing everyone. It's what I do. But I'm tired, Captain.",
            trigger_condition="Player catches him in a lie or calls out his insincerity."
        ),
        MicroRevelation(
            id="vasquez_cargo",
            revelation_text="The crate isn't machine parts. It's Helix-grade neural stabilizers. Pure gold on the black market. Or... a cure for Kai.",
            trigger_condition="Player investigates the cargo bay or confronts him about Yuki's pressure."
        )
    ]
)

EMBER = SecondaryCharacter(
    id="ember",
    name="Ember Quinn",
    role="Apprentice",
    age=19,
    central_problem_answer="Connection is the only thing that matters. Everything else is just waiting to die.",
    psychological_wound="Pre-wounded/Innocent. Escaped indentured servitude. Reyes was the first to 'choose' her without transaction.",
    what_she_wants=[
        "To belong somewhere",
        "To find people who are real",
        "To understand why people hurt each other"
    ],
    what_she_fears=[
        "That the captain was an exception and no one else is safe",
        "That she'll have to become hard to survive",
        "That the world will crush her hope"
    ],
    backstory_summary="Runaway indentured servant. Stowed away 4 months ago. Reyes adopted her.",
    chronological_history={
        "Age 0-18": "Contract child on mining colony. Inderntured.",
        "Age 18": "Ran away before contract was sold to harsher mine.",
        "4 months ago": "Found by Torres on Gambit. Reyes let her stay. 'Where are you running to?'",
        "Current day": "Grieving Reyes. Observed an argument between Yuki and Reyes the night before death."
    },
    secret_knowledge="Heard Yuki and Reyes arguing the night before the murder. Yuki: 'You don't have the right.' Reyes: 'I'm giving you a chance.'",
    dialogue_opening="I'm scrubbing the filters, Captain. I promise I'm earning my keep. You won't even know I'm here.",
    dialogue_hero_ending="I spent my whole life being no one. Now I'm someone. I'm Ember. And I'm home.",
    dialogue_tragedy_ending="I wanted to believe in you. But maybe the contract holders were right. People are just... what they are.",
    relationship_to_player_trust="You remind me of him. Reyes. You actually listen.",
    relationship_to_player_distrust="Is this what I have to do to stay? Okay. I'll do it.",
    micro_revelations=[
        MicroRevelation(
            id="ember_eavesdrop",
            revelation_text="They were arguing. Yuki and the Captain. She sounded scared. He sounded... sad. He said 'Don't make me do this the hard way.'",
            trigger_condition="Player treats Ember with kindness and asks about the Captain."
        )
    ]
)

# Global Registry
SECONDARY_CHARACTERS = {
    "torres": TORRES,
    "kai": KAI,
    "okonkwo": OKONKWO,
    "vasquez": VASQUEZ,
    "ember": EMBER
}

# ============================================================================
# API FUNCTIONS
# ============================================================================

def get_character_data(char_id: str) -> Dict[str, Any]:
    """
    Retrieve full character dictionary for API response.
    """
    char = SECONDARY_CHARACTERS.get(char_id.lower())
    if not char:
        return None
        
    return {
        "id": char.id,
        "name": char.name,
        "role": char.role,
        "age": char.age,
        "central_problem_answer": char.central_problem_answer,
        "psychological_wound": char.psychological_wound,
        "wants": char.what_she_wants,
        "fears": char.what_she_fears,
        "backstory": char.backstory_summary,
        "history": char.chronological_history,
        "secret_knowledge": char.secret_knowledge, # Usually hidden unless revealed, but sending for GM view
        "dialogue_samples": {
            "opening": char.dialogue_opening,
            "hero_ending": char.dialogue_hero_ending,
            "tragedy_ending": char.dialogue_tragedy_ending
        },
        "micro_revelations": [
            {
                "id": r.id, 
                "text": r.revelation_text, 
                "trigger": r.trigger_condition,
                "is_revealed": r.is_revealed
            } 
            for r in char.micro_revelations
        ]
    }

def check_micro_revelation(char_id: str, context: Dict[str, Any]) -> Optional[MicroRevelation]:
    """
    Check if a micro-revelation should trigger based on context.
    Context should include: 'trust_score', 'topic', 'player_archetype'
    """
    char = SECONDARY_CHARACTERS.get(char_id.lower())
    if not char:
        return None
        
    trust = context.get("trust_score", 0.0)
    topic = context.get("topic", "").lower()
    
    # Simple logic for now - normally would check state flags
    # This simulates the logic described in the prompt
    
    for rev in char.micro_revelations:
        if rev.is_revealed:
            continue
            
        # Hardcoded logic mapping to the English descriptions
        triggered = False
        
        if char.id == "torres":
            if rev.id == "torres_brother" and "military" in topic:
                triggered = True
            elif rev.id == "torres_sighting" and trust > 0.7 and "murder" in topic:
                triggered = True
                
        elif char.id == "kai":
            if rev.id == "kai_accident" and "compassion" in topic: # simplistic tag check
                triggered = True
            elif rev.id == "kai_debts" and "fuel" in topic:
                triggered = True
                
        elif char.id == "okonkwo":
            if rev.id == "okonkwo_triage" and "license" in topic:
                triggered = True
            elif rev.id == "okonkwo_autopsy" and trust > 0.8 and "autopsy" in topic:
                triggered = True
                
        elif char.id == "vasquez":
            if rev.id == "vasquez_mask" and "lie" in topic:
                triggered = True
            elif rev.id == "vasquez_cargo" and "cargo" in topic:
                triggered = True
                
        elif char.id == "ember":
            if rev.id == "ember_eavesdrop" and trust > 0.5 and "captain" in topic:
                triggered = True
                
        if triggered:
            # We don't auto-set is_revealed here to strictly separate query from mutation
            # unless we passed a mutable state object.
            # Ideally returns the potential revelation.
            return rev
            
    return None
