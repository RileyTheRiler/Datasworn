"""
Quick-Start Character Presets

Pre-built characters for players who want to jump into the game quickly.
Each preset includes stats, assets, vows, and rich narrative context.
"""

from typing import Dict, List, Any
from src.game_state import CharacterStats


class QuickStartCharacter:
    """A pre-built character ready for immediate play."""

    def __init__(
        self,
        id: str,
        name: str,
        title: str,
        description: str,
        background_story: str,
        stats: CharacterStats,
        asset_ids: List[str],
        vow: str,
        personality_traits: List[str],
        starting_scene: str,
        special_mechanics: Dict[str, Any] = None
    ):
        self.id = id
        self.name = name
        self.title = title
        self.description = description
        self.background_story = background_story
        self.stats = stats
        self.asset_ids = asset_ids
        self.vow = vow
        self.personality_traits = personality_traits
        self.starting_scene = starting_scene
        self.special_mechanics = special_mechanics or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "background_story": self.background_story,
            "stats": {
                "edge": self.stats.edge,
                "heart": self.stats.heart,
                "iron": self.stats.iron,
                "shadow": self.stats.shadow,
                "wits": self.stats.wits,
            },
            "asset_ids": self.asset_ids,
            "vow": self.vow,
            "personality_traits": self.personality_traits,
            "starting_scene": self.starting_scene,
            "special_mechanics": self.special_mechanics,
        }


# ============================================================================
# Quick-Start Character Presets
# ============================================================================

QUICKSTART_CHARACTERS = [
    QuickStartCharacter(
        id="cryo_awakened",
        name="Subject Zero",
        title="The Awakened",
        description="An amnesiac who wakes from centuries of cryogenic sleep with no memory of their past.",
        background_story=(
            "You wake in darkness, the hiss of escaping gas filling your ears. "
            "The cryopod's lid cracks open, revealing an abandoned facility shrouded in dust. "
            "Flickering emergency lights cast shadows on empty corridors. Your name, your past, "
            "your purpose—all forgotten. Only questions remain: Who were you? Why were you frozen? "
            "And why is everyone else... gone?\n\n"
            "Your body remembers skills your mind cannot recall. Muscle memory guides your hands "
            "as you navigate the derelict station. Faded ID tags label you 'Subject Zero,' but "
            "offer no other clues. In your pocket, a cryptic data chip pulses with an encrypted message: "
            "'Find Exodus Station. Remember the truth.'\n\n"
            "The stars outside are unfamiliar. How long have you slept? Centuries? Millennia? "
            "The only certainty: you must uncover who you were to understand who you've become."
        ),
        stats=CharacterStats(
            edge=2,    # Instinctive reflexes from unknown training
            heart=1,   # Emotionally disconnected from lost past
            iron=2,    # Physically preserved, combat-ready
            shadow=1,  # No memory of deception skills
            wits=1     # Knowledge locked behind amnesia
        ),
        asset_ids=["Sleuth", "Veteran", "Vestige"],  # Investigation, combat skills, mysterious past
        vow="Discover the truth of my identity and why I was placed in cryogenic sleep",
        personality_traits=[
            "Haunted by fragmentary dreams that might be memories",
            "Distrustful of authority figures who might know the truth",
            "Pragmatic survivor, living day-to-day until answers emerge",
            "Fascinated by pre-cryosleep artifacts and technology"
        ],
        starting_scene=(
            "You stand in the cryobay of a derelict research station, emergency lights "
            "flickering overhead. Dozens of empty cryopods line the walls—all opened from the outside. "
            "Yours was the only one still sealed. A terminal blinks nearby, displaying a single "
            "corrupted log entry: 'PROJECT GENESIS - SUBJECT ZERO - STATUS: [CORRUPTED]'. "
            "In the distance, something metallic clatters in the darkness."
        ),
        special_mechanics={
            "amnesia": True,
            "memory_fragments": True,  # Special narrative system: unlock memories through play
            "identity_crisis": True,   # Psychological tension between who they were/who they are now
            "mystery_background": "cryo_experiment",  # Links to potential conspiracy
        }
    ),

    QuickStartCharacter(
        id="veteran_bounty_hunter",
        name="Kade Mercer",
        title="The Tracker",
        description="A grizzled bounty hunter with decades of experience hunting the galaxy's most dangerous targets.",
        background_story=(
            "Twenty years. That's how long you've been tracking killers, thieves, and traitors "
            "across the Forge. Your ship, the Crimson Warrant, is known in every settlement and "
            "outpost. Some call you a hero. Others call you a mercenary. You call yourself pragmatic.\n\n"
            "But your last hunt went wrong. A political target turned out to be innocent—framed by "
            "a corrupt governor. You delivered them anyway, and they died in custody. The guilt eats "
            "at you. Now, you've taken a new vow: no more taking contracts at face value. You'll "
            "find the truth yourself, even if it means burning every corrupt official in the Forge."
        ),
        stats=CharacterStats(
            edge=2,    # Quick draw and evasive maneuvers
            heart=1,   # Hardened by years of violence
            iron=3,    # Peak combat effectiveness
            shadow=2,  # Tracking and interrogation skills
            wits=2     # Strategic hunter
        ),
        asset_ids=["Bounty Hunter", "Gunslinger", "Starship"],
        vow="Expose the corrupt network that framed my last target and bring them to justice",
        personality_traits=[
            "Speaks in terse, economical sentences",
            "Never takes a contract without researching the target",
            "Protective of innocents despite gruff exterior",
            "Haunted by past mistakes"
        ],
        starting_scene=(
            "You sit in a dimly lit cantina on Outpost Vara, studying bounty postings on your datapad. "
            "Most are standard fare: pirates, smugglers, deserters. But one catches your eye—a young "
            "hacker wanted for 'terrorism' by the same governor who set you up before. The bounty is "
            "suspiciously high. Your instincts scream setup. But this time, you'll investigate first."
        ),
        special_mechanics={
            "reputation": "feared_hunter",
            "guilt_tracker": True,
        }
    ),

    QuickStartCharacter(
        id="diplomat_mediator",
        name="Ambassador Lyssa Venn",
        title="The Peacemaker",
        description="A charismatic diplomat dedicated to preventing war between feuding factions.",
        background_story=(
            "You were born on a colony ship during the Exodus, raised between cultures and factions. "
            "That unique perspective made you a natural mediator. For fifteen years, you've negotiated "
            "ceasefires, trade agreements, and treaties across the Forge. You've saved thousands of lives "
            "by preventing conflicts before they start.\n\n"
            "But now, your greatest challenge looms: two powerful factions, the Syndicate Collective and "
            "the Free Captains, stand on the brink of all-out war. A single spark could ignite a conflict "
            "that consumes entire sectors. You've been called to the neutral station Meridian to broker peace. "
            "Failure means bloodshed on an unprecedented scale."
        ),
        stats=CharacterStats(
            edge=1,    # Not built for combat
            heart=3,   # Master of empathy and persuasion
            iron=1,    # Physically unimposing
            shadow=2,  # Skilled at reading people and detecting lies
            wits=2     # Strategic political mind
        ),
        asset_ids=["Diplomat", "Empath", "Protocol Bot"],
        vow="Broker lasting peace between the Syndicate Collective and Free Captains before war erupts",
        personality_traits=[
            "Believes everyone has common ground if you look hard enough",
            "Fluent in multiple languages and cultural customs",
            "Maintains calm under pressure",
            "Idealistic but not naive"
        ],
        starting_scene=(
            "The observation deck of Meridian Station offers a view of both fleets: Syndicate warships "
            "to port, Free Captain dreadnoughts to starboard. Both are armed and waiting. You stand between "
            "them, literally and figuratively. In one hour, representatives from both sides will arrive "
            "for negotiations. Your protocol bot whispers casualty projections if talks fail: 40,000 dead "
            "in the first week."
        ),
        special_mechanics={
            "reputation": "trusted_mediator",
            "peace_talks": True,
        }
    ),

    QuickStartCharacter(
        id="scavenger_explorer",
        name="Rook Thane",
        title="The Salvager",
        description="A daring explorer who delves into derelict ships and forgotten ruins for lost treasures.",
        background_story=(
            "The Forge is littered with ghosts—abandoned stations, derelict warships, ruined colonies. "
            "While others fear these places, you see opportunity. Every wreck holds salvage, every ruin "
            "conceals secrets. You've made a fortune recovering lost technology and selling it to the "
            "highest bidder.\n\n"
            "But your last expedition changed everything. Deep in a precursor ruin, you found a star map—"
            "ancient, detailed, showing locations no modern charts include. One system is marked with a "
            "symbol you don't recognize. The map's previous owner left a warning scratched into the wall: "
            "'They're still watching.' Now you're obsessed with uncovering what lies in that marked system, "
            "even if it means facing whatever they feared."
        ),
        stats=CharacterStats(
            edge=3,    # Agile climber and quick escape artist
            heart=1,   # Self-reliant loner
            iron=1,    # Avoids direct combat
            shadow=2,  # Sneaks through dangerous areas
            wits=2     # Expert at analyzing ruins and tech
        ),
        asset_ids=["Explorer", "Scavenger", "Utility Bot"],
        vow="Reach the mysterious system marked on the precursor star map and uncover its secrets",
        personality_traits=[
            "Talks to their utility bot like a partner",
            "Can't resist exploring 'one more room'",
            "Collects strange artifacts that may or may not be valuable",
            "Thrives in zero-gravity environments"
        ],
        starting_scene=(
            "Your ship, the Salvage Rights, drifts near the edge of a debris field. Before you: "
            "the wreck of a colony ship, half-sheared by some ancient catastrophe. Your scanners detect "
            "faint power readings deep inside—something still functional after all these years. Your "
            "utility bot chirps nervously. It doesn't like this place. Neither do you. But that star map "
            "burns in your pocket, and answers might wait in the dark."
        ),
        special_mechanics={
            "treasure_hunter": True,
            "map_quest": "precursor_system",
        }
    ),

    QuickStartCharacter(
        id="tech_genius",
        name="Dr. Nyx Korren",
        title="The Engineer",
        description="A brilliant inventor haunted by the destructive potential of their own creations.",
        background_story=(
            "They called you a genius. At twenty-five, you designed the Korren Drive—a revolutionary "
            "propulsion system that cut travel time by half. Corporations fought over the patents. You "
            "became wealthy overnight.\n\n"
            "Then the weapons manufacturers came. They wanted to weaponize your drive, turn it into "
            "a devastating kinetic bombardment system. You refused. They stole your designs anyway. "
            "Within a year, the Korren Lance was used to obliterate a rebel colony—12,000 dead. Your invention. "
            "Your fault.\n\n"
            "You fled into the outer sectors, trying to disappear. But you can't run from your conscience. "
            "Now, you've vowed to create technology that saves lives instead of taking them—and to sabotage "
            "every weapons project built on your stolen work."
        ),
        stats=CharacterStats(
            edge=1,    # Clumsy in physical situations
            heart=2,   # Driven by guilt and redemption
            iron=1,    # Avoids violence
            shadow=1,  # Honest to a fault
            wits=3     # Brilliant engineer and inventor
        ),
        asset_ids=["Gearhead", "Tech", "Survey Bot"],
        vow="Destroy every military application of my stolen technology and create innovations that protect innocent lives",
        personality_traits=[
            "Obsessively tinkers with technology when anxious",
            "Distrusts corporate interests and military contracts",
            "Feels personally responsible for every life lost to their invention",
            "Finds beauty in elegant engineering solutions"
        ],
        starting_scene=(
            "Your workshop aboard the Tinker's Oath is cluttered with half-finished projects. Blueprints "
            "cover every surface. On your workbench: a defensive shield generator you've been perfecting "
            "for months. It could protect entire settlements. But your datapad shows darker news—another "
            "colony hit by a Korren Lance strike. 3,000 dead. Your survey bot beeps softly, offering comfort "
            "it knows you won't accept."
        ),
        special_mechanics={
            "inventor": True,
            "guilt_driven": True,
            "saboteur": True,
        }
    ),
]


def get_quickstart_characters() -> List[Dict[str, Any]]:
    """Return all quick-start characters as dictionaries."""
    return [char.to_dict() for char in QUICKSTART_CHARACTERS]


def get_quickstart_character_by_id(char_id: str) -> QuickStartCharacter | None:
    """Get a specific quick-start character by ID."""
    for char in QUICKSTART_CHARACTERS:
        if char.id == char_id:
            return char
    return None
