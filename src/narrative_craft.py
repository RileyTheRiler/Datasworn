"""
Narrative Craft Engine - Master-Level Storytelling.
Genre conventions, McKee's Story principles, archetype tracking, and cliché avoidance.

Based on Robert McKee's "Story" and narrative craft fundamentals.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import random


# ============================================================================
# Genre System
# ============================================================================

class Genre(Enum):
    """Story genres with distinct conventions."""
    SPACE_OPERA = "space_opera"
    NOIR = "noir"
    HORROR = "horror"
    MYSTERY = "mystery"
    THRILLER = "thriller"
    WESTERN = "western"
    ROMANCE = "romance"
    TRAGEDY = "tragedy"
    COMEDY = "comedy"
    ADVENTURE = "adventure"


@dataclass
class GenreConventions:
    """Conventions and techniques for a specific genre."""
    genre: Genre
    tone: str
    pacing: str
    key_elements: list[str]
    atmosphere: list[str]
    typical_conflicts: list[str]
    avoid: list[str]  # What NOT to do in this genre
    prose_style: str
    scene_endings: str  # How to end scenes


GENRE_TEMPLATES = {
    Genre.SPACE_OPERA: GenreConventions(
        genre=Genre.SPACE_OPERA,
        tone="Epic, romantic, larger-than-life",
        pacing="Sweeping with moments of intimate character focus",
        key_elements=[
            "Vast scale (galaxies, civilizations)",
            "Clear moral stakes",
            "Heroic sacrifice",
            "Technology as wonder, not manual",
            "Found family",
        ],
        atmosphere=["awe", "wonder", "destiny", "vastness"],
        typical_conflicts=["Empire vs Rebellion", "Duty vs Love", "Past vs Future"],
        avoid=["Hard science exposition", "Mundane logistics", "Moral ambiguity in villains"],
        prose_style="Lyrical, sweeping descriptions. Emotions run high. Stars are characters.",
        scene_endings="End on revelation, decision, or visual grandeur.",
    ),
    Genre.NOIR: GenreConventions(
        genre=Genre.NOIR,
        tone="Cynical, morally ambiguous, fatalistic",
        pacing="Slow burn punctuated by violence",
        key_elements=[
            "Flawed protagonist",
            "Femme fatale or homme fatal",
            "Urban decay",
            "Corruption everywhere",
            "The past won't stay buried",
        ],
        atmosphere=["shadow", "rain", "smoke", "neon", "isolation"],
        typical_conflicts=["Justice vs Law", "Love vs Survival", "Truth vs Safety"],
        avoid=["Happy endings", "Clear heroes", "Simple solutions"],
        prose_style="Terse, punchy sentences. Similes like bruises. First-person world-weariness.",
        scene_endings="End on a bitter observation, an unanswered question, or violence.",
    ),
    Genre.HORROR: GenreConventions(
        genre=Genre.HORROR,
        tone="Dread, violation, the uncanny",
        pacing="Build slowly, unleash in bursts",
        key_elements=[
            "The monster represents something",
            "Isolation (physical or social)",
            "Transgression",
            "Body horror or cosmic horror",
            "Complicity",
        ],
        atmosphere=["wrongness", "silence before sound", "the familiar made strange"],
        typical_conflicts=["Self vs Monster", "Sanity vs Truth", "Survival vs Humanity"],
        avoid=["Over-explaining the monster", "Jump scares without buildup", "Competent authorities"],
        prose_style="Sensory details that feel wrong. Short paragraphs. Restraint then release.",
        scene_endings="End before the horror fully resolves. Let imagination work.",
    ),
    Genre.MYSTERY: GenreConventions(
        genre=Genre.MYSTERY,
        tone="Puzzling, cerebral, fair-play",
        pacing="Steady accumulation of clues and reversals",
        key_elements=[
            "The detective (amateur or professional)",
            "Clues planted fairly",
            "Red herrings that make sense later",
            "A closed circle of suspects",
            "The reveal recontextualizes everything",
        ],
        atmosphere=["suspicion", "secrets", "observation", "the ordinary hiding extraordinary"],
        typical_conflicts=["Truth vs Protection", "Justice vs Mercy", "Order vs Chaos"],
        avoid=["Withholding clues from reader", "Deus ex machina solutions", "Unmotivated reveals"],
        prose_style="Precise observation. Details that reward attention. Dialogue as duel.",
        scene_endings="End on a new question, a clue, or a suspect's reaction.",
    ),
    Genre.THRILLER: GenreConventions(
        genre=Genre.THRILLER,
        tone="Urgent, paranoid, high-stakes",
        pacing="Relentless. Breathless. Escalating.",
        key_elements=[
            "Ticking clock",
            "Conspiracy or hidden threat",
            "Protagonist out of their depth",
            "Trust no one",
            "Personal stakes within larger stakes",
        ],
        atmosphere=["paranoia", "urgency", "pursuit", "the net closing"],
        typical_conflicts=["Individual vs System", "Truth vs Safety", "Escape vs Confrontation"],
        avoid=["Slow reflection", "Safe havens that stay safe", "Reliable allies"],
        prose_style="Short sentences. Present tense feeling. Cliffhangers everywhere.",
        scene_endings="End mid-action, mid-revelation, or on betrayal.",
    ),
    Genre.TRAGEDY: GenreConventions(
        genre=Genre.TRAGEDY,
        tone="Inevitable, earned, cathartic",
        pacing="Rising action toward inescapable fall",
        key_elements=[
            "Hamartia (fatal flaw)",
            "Hubris",
            "The choice that seals fate",
            "Recognition too late",
            "Catharsis through suffering",
        ],
        atmosphere=["doom", "nobility", "waste", "what could have been"],
        typical_conflicts=["Character vs Self", "Pride vs Wisdom", "Love vs Duty"],
        avoid=["Rescue from consequences", "Unearned redemption", "Villain-blaming"],
        prose_style="Elevated but human. The weight of choices. Irony the reader sees coming.",
        scene_endings="End on the weight of what's been done or what's coming.",
    ),
}


# ============================================================================
# McKee's Story Structure
# ============================================================================

class StoryBeat(Enum):
    """Major story beats from McKee's structure."""
    INCITING_INCIDENT = "inciting_incident"  # Life knocked out of balance
    PROGRESSIVE_COMPLICATION = "progressive_complication"  # Rising stakes
    CRISIS = "crisis"  # Dilemma - impossible choice
    CLIMAX = "climax"  # The choice and its consequence
    RESOLUTION = "resolution"  # New equilibrium


@dataclass
class McKeeGuidance:
    """Guidance based on current story position."""
    current_beat: StoryBeat
    guidance: str
    narrator_instruction: str
    avoid: list[str]


MCKEE_BEAT_GUIDANCE = {
    StoryBeat.INCITING_INCIDENT: McKeeGuidance(
        current_beat=StoryBeat.INCITING_INCIDENT,
        guidance="Something has upset the balance. The protagonist cannot return to status quo.",
        narrator_instruction="Establish what's at stake. Make the disruption personal.",
        avoid=["Abstract threats", "Protagonist passivity", "Reversible problems"],
    ),
    StoryBeat.PROGRESSIVE_COMPLICATION: McKeeGuidance(
        current_beat=StoryBeat.PROGRESSIVE_COMPLICATION,
        guidance="Each attempt to restore balance makes things worse. Stakes escalate.",
        narrator_instruction="Every solution creates new problems. Raise difficulty progressively.",
        avoid=["Plateau tension", "Easy wins", "Repetitive obstacles"],
    ),
    StoryBeat.CRISIS: McKeeGuidance(
        current_beat=StoryBeat.CRISIS,
        guidance="The protagonist faces an impossible choice. Both options cost something real.",
        narrator_instruction="Present a true dilemma. No good option. Define character through choice.",
        avoid=["Obvious right answer", "External rescue", "Delayed decision"],
    ),
    StoryBeat.CLIMAX: McKeeGuidance(
        current_beat=StoryBeat.CLIMAX,
        guidance="The choice is made. Irreversible action. Maximum conflict.",
        narrator_instruction="Show the choice in action. Consequences immediate and visible.",
        avoid=["Half-measures", "Interrupted climax", "Anticlimax"],
    ),
    StoryBeat.RESOLUTION: McKeeGuidance(
        current_beat=StoryBeat.RESOLUTION,
        guidance="New equilibrium. The character is changed. The world is changed.",
        narrator_instruction="Show transformation through action, not exposition. Brief.",
        avoid=["Long denouement", "Explaining the theme", "Undoing the climax"],
    ),
}


# ============================================================================
# Archetype System (Hero's Journey + Character Functions)
# ============================================================================

class CharacterArchetype(Enum):
    """Jungian/Campbell character archetypes."""
    HERO = "hero"
    MENTOR = "mentor"
    THRESHOLD_GUARDIAN = "threshold_guardian"
    HERALD = "herald"
    SHAPESHIFTER = "shapeshifter"
    SHADOW = "shadow"
    TRICKSTER = "trickster"
    ALLY = "ally"


ARCHETYPE_FUNCTIONS = {
    CharacterArchetype.HERO: {
        "function": "Protagonist who undergoes transformation",
        "story_role": "Drives action, makes crucial decisions, changes",
        "narrator_note": "Show internal conflict. Growth through challenge.",
    },
    CharacterArchetype.MENTOR: {
        "function": "Provides wisdom, gifts, or training",
        "story_role": "Prepares hero but cannot take the journey for them",
        "narrator_note": "Must step back at crucial moments. Wisdom with cost.",
    },
    CharacterArchetype.THRESHOLD_GUARDIAN: {
        "function": "Tests hero's commitment at transitions",
        "story_role": "Obstacles that prove worthiness",
        "narrator_note": "Not necessarily enemies. Sometimes themselves.",
    },
    CharacterArchetype.HERALD: {
        "function": "Announces change, delivers the call",
        "story_role": "Catalyst for journey beginning",
        "narrator_note": "Brief but memorable. Changes everything.",
    },
    CharacterArchetype.SHAPESHIFTER: {
        "function": "Uncertainty, keeps hero guessing",
        "story_role": "Loyalty unclear, possibly love interest",
        "narrator_note": "Consistency in inconsistency. Hidden motives.",
    },
    CharacterArchetype.SHADOW: {
        "function": "Represents what hero fears becoming",
        "story_role": "Main antagonist, dark mirror",
        "narrator_note": "Must have understandable motivation. Not pure evil.",
    },
    CharacterArchetype.TRICKSTER: {
        "function": "Comic relief, truth-teller, chaos",
        "story_role": "Cuts tension, speaks truth no one else will",
        "narrator_note": "Humor with purpose. Often wisest.",
    },
    CharacterArchetype.ALLY: {
        "function": "Support, humanize hero through relationship",
        "story_role": "Friendship, loyalty, sometimes sacrifice",
        "narrator_note": "Must have own desires. Not just helpful.",
    },
}


# ============================================================================
# Cliché Avoidance System
# ============================================================================

CLICHES_TO_AVOID = {
    "opening": [
        "It was a dark and stormy night",
        "Waking up / looking in mirror",
        "Info-dump prologue",
        "Prophecy exposition",
    ],
    "character": [
        "Chosen one without earning it",
        "Dead parents as only motivation",
        "Woman in refrigerator (killed to motivate male)",
        "Villain explains plan before killing",
        "Last-second betrayal with no setup",
    ],
    "action": [
        "Shooting a moving target without aiming",
        "Villain leaving hero to die slowly",
        "Outrunning explosion",
        "Unlimited ammo / no reload",
    ],
    "dialogue": [
        "As you know, Bob... (expository dialogue)",
        "I have a bad feeling about this",
        "We've got company",
        "It's quiet... too quiet",
    ],
    "ending": [
        "It was all a dream",
        "Love conquers all (unearned)",
        "Deus ex machina rescue",
        "Villain dies through own hubris with no hero action",
    ],
}


# ============================================================================
# Symbolism & Motif Tracking
# ============================================================================

@dataclass
class Motif:
    """A recurring symbol or image."""
    name: str
    meaning: str
    appearances: list[str] = field(default_factory=list)
    should_recur_at: list[str] = field(default_factory=list)  # e.g., "climax", "death"


@dataclass
class ForeshadowingElement:
    """Something planted for later payoff."""
    setup: str
    intended_payoff: str
    scene_planted: int
    urgency: str = "when_appropriate"  # "soon", "climax", "when_appropriate"
    paid_off: bool = False


# ============================================================================
# Narrative Craft Engine
# ============================================================================

class NarrativeCraftEngine:
    """
    Master-level storytelling guidance for the narrator.
    Tracks genre, structure, archetypes, and craft elements.
    """
    
    def __init__(self, genre: Genre = Genre.SPACE_OPERA):
        self.genre = genre
        self.conventions = GENRE_TEMPLATES.get(genre, GENRE_TEMPLATES[Genre.SPACE_OPERA])
        self.current_beat = StoryBeat.INCITING_INCIDENT
        self.motifs: list[Motif] = []
        self.foreshadowing: list[ForeshadowingElement] = []
        self.character_archetypes: dict[str, CharacterArchetype] = {}
        self.scenes_in_current_beat: int = 0
    
    def set_genre(self, genre: Genre) -> None:
        """Change the genre."""
        self.genre = genre
        self.conventions = GENRE_TEMPLATES.get(genre, GENRE_TEMPLATES[Genre.SPACE_OPERA])
    
    def advance_beat(self) -> None:
        """Move to the next story beat."""
        beats = list(StoryBeat)
        idx = beats.index(self.current_beat)
        if idx < len(beats) - 1:
            self.current_beat = beats[idx + 1]
            self.scenes_in_current_beat = 0
    
    def add_motif(self, name: str, meaning: str) -> None:
        """Add a recurring motif."""
        self.motifs.append(Motif(name=name, meaning=meaning))
    
    def add_foreshadowing(self, setup: str, payoff: str, scene: int) -> None:
        """Plant foreshadowing."""
        self.foreshadowing.append(ForeshadowingElement(
            setup=setup, intended_payoff=payoff, scene_planted=scene
        ))
    
    def assign_archetype(self, character: str, archetype: CharacterArchetype) -> None:
        """Assign archetype to character."""
        self.character_archetypes[character] = archetype
    
    def get_unpaid_foreshadowing(self) -> list[ForeshadowingElement]:
        """Get foreshadowing that needs payoff."""
        return [f for f in self.foreshadowing if not f.paid_off]
    
    def get_craft_context(self) -> str:
        """Generate comprehensive craft guidance for narrator."""
        lines = ["[NARRATIVE CRAFT GUIDANCE]"]
        
        # Genre
        lines.append(f"\n## GENRE: {self.genre.value.upper()}")
        lines.append(f"Tone: {self.conventions.tone}")
        lines.append(f"Prose style: {self.conventions.prose_style}")
        lines.append(f"Scene endings: {self.conventions.scene_endings}")
        lines.append(f"Atmosphere: {', '.join(self.conventions.atmosphere)}")
        lines.append(f"AVOID: {', '.join(self.conventions.avoid)}")
        
        # McKee beat
        beat_guidance = MCKEE_BEAT_GUIDANCE[self.current_beat]
        lines.append(f"\n## STORY BEAT: {self.current_beat.value.upper()}")
        lines.append(f"{beat_guidance.guidance}")
        lines.append(f"Narrator: {beat_guidance.narrator_instruction}")
        lines.append(f"AVOID: {', '.join(beat_guidance.avoid)}")
        
        # Archetypes
        if self.character_archetypes:
            lines.append("\n## CHARACTER ARCHETYPES")
            for char, arch in list(self.character_archetypes.items())[:3]:
                func = ARCHETYPE_FUNCTIONS[arch]
                lines.append(f"• {char} ({arch.value}): {func['narrator_note']}")
        
        # Foreshadowing due
        unpaid = self.get_unpaid_foreshadowing()
        if unpaid:
            lines.append("\n## FORESHADOWING TO PAY OFF")
            for f in unpaid[:2]:
                lines.append(f"• {f.setup} → {f.intended_payoff}")
        
        # Motifs
        if self.motifs:
            lines.append("\n## RECURRING MOTIFS")
            for m in self.motifs[:2]:
                lines.append(f"• {m.name}: {m.meaning}")
        
        # Cliché warning
        lines.append("\n## CLICHÉS TO AVOID")
        all_cliches = []
        for category in CLICHES_TO_AVOID.values():
            all_cliches.extend(category)
        lines.append(f"Watch for: {', '.join(random.sample(all_cliches, min(3, len(all_cliches))))}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "genre": self.genre.value,
            "current_beat": self.current_beat.value,
            "scenes_in_beat": self.scenes_in_current_beat,
            "motifs": [{"name": m.name, "meaning": m.meaning} for m in self.motifs],
            "foreshadowing": [
                {"setup": f.setup, "payoff": f.intended_payoff, "paid": f.paid_off}
                for f in self.foreshadowing
            ],
            "archetypes": {k: v.value for k, v in self.character_archetypes.items()},
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "NarrativeCraftEngine":
        try:
            genre = Genre(data.get("genre", "space_opera"))
        except ValueError:
            genre = Genre.SPACE_OPERA
        
        engine = cls(genre=genre)
        
        try:
            engine.current_beat = StoryBeat(data.get("current_beat", "inciting_incident"))
        except ValueError:
            pass
        
        engine.scenes_in_current_beat = data.get("scenes_in_beat", 0)
        
        for m in data.get("motifs", []):
            engine.motifs.append(Motif(name=m["name"], meaning=m["meaning"]))
        
        for f in data.get("foreshadowing", []):
            engine.foreshadowing.append(ForeshadowingElement(
                setup=f["setup"], intended_payoff=f["payoff"],
                scene_planted=0, paid_off=f.get("paid", False)
            ))
        
        for char, arch in data.get("archetypes", {}).items():
            try:
                engine.character_archetypes[char] = CharacterArchetype(arch)
            except ValueError:
                pass
        
        return engine


# ============================================================================
# Convenience Functions
# ============================================================================

def create_craft_engine(genre: str = "space_opera") -> NarrativeCraftEngine:
    """Create a narrative craft engine."""
    try:
        g = Genre(genre)
    except ValueError:
        g = Genre.SPACE_OPERA
    return NarrativeCraftEngine(genre=g)


def get_genre_guidance(genre: str) -> str:
    """Get quick genre guidance."""
    try:
        g = Genre(genre)
    except ValueError:
        g = Genre.SPACE_OPERA
    
    conv = GENRE_TEMPLATES.get(g)
    if not conv:
        return ""
    
    return (
        f"[GENRE: {g.value.upper()}]\n"
        f"Tone: {conv.tone}\n"
        f"Style: {conv.prose_style}\n"
        f"AVOID: {', '.join(conv.avoid)}"
    )


def get_mckee_guidance(beat: str) -> str:
    """Get McKee guidance for a story beat."""
    try:
        b = StoryBeat(beat)
    except ValueError:
        b = StoryBeat.PROGRESSIVE_COMPLICATION
    
    guidance = MCKEE_BEAT_GUIDANCE[b]
    return (
        f"[STORY BEAT: {b.value.upper()}]\n"
        f"{guidance.guidance}\n"
        f"Narrator: {guidance.narrator_instruction}"
    )
