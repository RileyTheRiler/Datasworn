"""
Character Web with Four-Corner Opposition.

This module defines the structural relationships between characters using
John Truby's "Four-Corner Opposition" framework to maximize narrative conflict.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

class CharacterRole(str, Enum):
    HERO = "hero"
    NECESSARY_OPPONENT = "necessary_opponent"
    ALLY = "ally"
    FAKE_ALLY_OPPONENT = "fake_ally_opponent"
    OPTIONAL_FAKE_OPPONENT_ALLY = "optional_fake_opponent_ally"
    SUBPLOT_MIRROR = "subplot_mirror"

class TacticStyle(str, Enum):
    FORCE = "force"
    MANIPULATION = "manipulation"
    PERSUASION = "persuasion"
    STEALTH = "stealth"

@dataclass
class CharacterCorner:
    role: CharacterRole
    name: str
    goal: str
    values: List[str]
    tactic_style: TacticStyle
    exposure_logic: str # How they expose the hero's weakness

@dataclass
class ConflictMapping:
    primary: str
    secondary: str
    conflict_type: str
    likely_reversal_beat: str

@dataclass
class DoubleReversal:
    hero_revelation: str
    opponent_revelation: str
    context: str

# ============================================================================
# DATA POPULATION: THE CHARACTER WEB
# ============================================================================

CHARACTER_CORNERS = [
    CharacterCorner(
        role=CharacterRole.HERO,
        name="The Detective (Player)",
        goal="Solve the murder to restore cosmic/personal order.",
        values=["Justice", "Order", "Control", "Reputation"],
        tactic_style=TacticStyle.FORCE, # Default, can be refined by player
        exposure_logic="Their need for control prevents them from seeing the chaotic truth of their own past."
    ),
    CharacterCorner(
        role=CharacterRole.NECESSARY_OPPONENT,
        name="The Killer (Yuki)",
        goal="Complete the 'Meridians' ritual to transcend human limitation.",
        values=["Evolution", "Truth", "Ascension", "Sacrifice"],
        tactic_style=TacticStyle.MANIPULATION,
        exposure_logic="Mimics the hero's obsession but for 'higher' ends, showing the hero that their 'justice' is just another form of ego."
    ),
    CharacterCorner(
        role=CharacterRole.ALLY,
        name="Torres",
        goal="Protect the ship and find one person worth trusting.",
        values=["Loyalty", "Survival", "Skepticism", "Directness"],
        tactic_style=TacticStyle.FORCE,
        exposure_logic="Her absolute lack of trust highlights the Hero's naive belief that a 'system' (like justice) can fix everything."
    ),
    CharacterCorner(
        role=CharacterRole.FAKE_ALLY_OPPONENT,
        name="Vasquez",
        goal="Leverage the chaos for a big enough score to disappear.",
        values=["Utility", "Anonymity", "Adaptability", "Profit"],
        tactic_style=TacticStyle.PERSUASION,
        exposure_logic="His performative connection mocks the Hero's attempts at genuine leadership, suggesting everyone is just performing."
    ),
    CharacterCorner(
        role=CharacterRole.OPTIONAL_FAKE_OPPONENT_ALLY,
        name="Dr. Okonkwo",
        goal="Protect people from 'unnecessary' truths that kill.",
        values=["Mercy", "Silence", "Pragmatism", "Distance"],
        tactic_style=TacticStyle.STEALTH,
        exposure_logic="Her gatekeeping of the truth forces the Hero to question if 'The Truth' is a weapon or a medicine."
    ),
    CharacterCorner(
        role=CharacterRole.SUBPLOT_MIRROR,
        name="Kai Nakamura",
        goal="Avoid being 'found out' as a fraud/failure.",
        values=["Competence", "Numbing", "Anxiety", "Escape"],
        tactic_style=TacticStyle.STEALTH,
        exposure_logic="Reflects the Hero's 'Shadow Self' (The Fraud). If Kai fails, the Hero sees their own potential failure."
    )
]

CONFLICT_MAPS = [
    ConflictMapping(
        primary="Hero", secondary="Killer",
        conflict_type="Value Clash: Justice vs. Transcendence",
        likely_reversal_beat="Hero realizes Yuki's motive is a refined version of their own desire to 'cleanse' the ship."
    ),
    ConflictMapping(
        primary="Opponent", secondary="Ally",
        conflict_type="Method Clash: Manipulation vs. Direct Defense",
        likely_reversal_beat="Yuki uses Torres's loyalty to Reyes to lead her into a trap that Reyes actually set."
    ),
    ConflictMapping(
        primary="Ally", secondary="Fake-Ally",
        conflict_type="Foundation Clash: Raw Truth vs. Perfect Performance",
        likely_reversal_beat="Torres relies on Vasquez for 'facts' he has entirely fabricated to keep both sides happy."
    )
]

DOUBLE_REVERSALS = [
    DoubleReversal(
        hero_revelation="The Hero didn't just fail to save Yuki in the past; they actively chose their career over her safety.",
        opponent_revelation="Yuki didn't just kill Reyes for a ritual; she did it to force the Hero to finally look at her.",
        context="The final confrontation in the Engine Room."
    )
]

def get_character_web() -> Dict[str, Any]:
    """Returns the full character web with all corners and conflicts."""
    return {
        "corners": [
            {
                "role": c.role.value,
                "name": c.name,
                "goal": c.goal,
                "values": c.values,
                "tactic": c.tactic_style.value,
                "exposure": c.exposure_logic
            } for c in CHARACTER_CORNERS
        ],
        "conflicts": [
            {
                "primary": m.primary,
                "secondary": m.secondary,
                "type": m.conflict_type,
                "reversal": m.likely_reversal_beat
            } for m in CONFLICT_MAPS
        ],
        "double_reversals": [
            {
                "hero": dr.hero_revelation,
                "opponent": dr.opponent_revelation,
                "context": dr.context
            } for dr in DOUBLE_REVERSALS
        ]
    }
