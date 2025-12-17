"""
Moral Dilemma & Theme Engine - TLOU-Style Choice Systems.
Implements meaningful choices where both options cost something.

Key principles:
- No "right" answer - both choices have weight
- Consequences that matter
- Theme consistency across the campaign
- Character-defining moments
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import random


# ============================================================================
# Dilemma Types
# ============================================================================

class DilemmaType(Enum):
    """Categories of moral dilemmas."""
    SACRIFICE = "sacrifice"  # Someone must pay a price
    LOYALTY = "loyalty"  # Choose between people/factions
    MERCY = "mercy"  # Spare or punish
    TRUTH = "truth"  # Reveal or conceal
    SURVIVAL = "survival"  # Self vs. others
    JUSTICE = "justice"  # Law vs. compassion
    IDENTITY = "identity"  # Who you are vs. who you need to be


class DilemmaWeight(Enum):
    """How much this dilemma will matter."""
    MINOR = "minor"  # Character moment
    SIGNIFICANT = "significant"  # Story impact
    DEFINING = "defining"  # Changes everything


# ============================================================================
# Dilemma Structure
# ============================================================================

@dataclass
class DilemmaOption:
    """One side of a moral choice."""
    name: str
    description: str
    cost: str  # What you lose by choosing this
    gain: str  # What you preserve/gain
    themes_reinforced: list[str] = field(default_factory=list)
    character_impact: str = ""  # How this changes the player


@dataclass
class MoralDilemma:
    """A moral choice with no right answer."""
    dilemma_type: DilemmaType
    weight: DilemmaWeight
    context: str  # The situation
    question: str  # The core question
    option_a: DilemmaOption
    option_b: DilemmaOption
    time_pressure: bool = False  # Must decide now?
    witnesses: list[str] = field(default_factory=list)  # Who will remember
    
    def get_narrator_context(self) -> str:
        """Generate context for narrator about this dilemma."""
        lines = [f"[MORAL DILEMMA: {self.dilemma_type.value.upper()}]"]
        lines.append(f"Weight: {self.weight.value}")
        lines.append(f"Question: {self.question}")
        lines.append("")
        lines.append(f"OPTION A - {self.option_a.name}:")
        lines.append(f"  {self.option_a.description}")
        lines.append(f"  Cost: {self.option_a.cost}")
        lines.append("")
        lines.append(f"OPTION B - {self.option_b.name}:")
        lines.append(f"  {self.option_b.description}")
        lines.append(f"  Cost: {self.option_b.cost}")
        
        if self.time_pressure:
            lines.append("")
            lines.append("⚠️ TIME PRESSURE - Player must decide NOW")
        
        if self.witnesses:
            lines.append(f"Witnesses: {', '.join(self.witnesses)}")
        
        lines.append("")
        lines.append("NARRATOR: Present this choice without bias. Let the player feel the weight.")
        
        return "\n".join(lines)


# ============================================================================
# Dilemma Templates
# ============================================================================

DILEMMA_TEMPLATES = {
    DilemmaType.SACRIFICE: [
        MoralDilemma(
            dilemma_type=DilemmaType.SACRIFICE,
            weight=DilemmaWeight.DEFINING,
            context="Resources are critically low. Not everyone can make it.",
            question="Who lives? Who dies?",
            option_a=DilemmaOption(
                name="Save the Many",
                description="Sacrifice the few for the greater good",
                cost="Blood on your hands. Their faces in your dreams.",
                gain="The group survives. You're a pragmatist.",
                themes_reinforced=["survival", "utilitarianism"],
            ),
            option_b=DilemmaOption(
                name="Save the One",
                description="Risk everything for someone who matters",
                cost="Others may die. You chose favorites.",
                gain="You stayed human. Love meant something.",
                themes_reinforced=["love", "humanity"],
            ),
        ),
    ],
    DilemmaType.LOYALTY: [
        MoralDilemma(
            dilemma_type=DilemmaType.LOYALTY,
            weight=DilemmaWeight.SIGNIFICANT,
            context="An old ally and a new friend are at odds. Both need you.",
            question="Where does your loyalty lie?",
            option_a=DilemmaOption(
                name="Honor the Past",
                description="Stand with the one who's always been there",
                cost="The new friendship may never recover",
                gain="Loyalty means something to you",
                themes_reinforced=["loyalty", "history"],
            ),
            option_b=DilemmaOption(
                name="Embrace the New",
                description="Side with the one who represents the future",
                cost="Betraying someone who trusted you",
                gain="Growth sometimes requires letting go",
                themes_reinforced=["change", "growth"],
            ),
        ),
    ],
    DilemmaType.MERCY: [
        MoralDilemma(
            dilemma_type=DilemmaType.MERCY,
            weight=DilemmaWeight.SIGNIFICANT,
            context="Your enemy is defeated. Helpless. They've done terrible things.",
            question="Do you end it, or walk away?",
            option_a=DilemmaOption(
                name="Execute",
                description="Ensure they never hurt anyone again",
                cost="You become what you fought against",
                gain="Justice. Safety. Closure.",
                themes_reinforced=["justice", "finality"],
            ),
            option_b=DilemmaOption(
                name="Show Mercy",
                description="Break the cycle. Let them live.",
                cost="They might come back. Others might suffer.",
                gain="You're still you. There's hope for everyone.",
                themes_reinforced=["mercy", "hope"],
            ),
        ),
    ],
    DilemmaType.TRUTH: [
        MoralDilemma(
            dilemma_type=DilemmaType.TRUTH,
            weight=DilemmaWeight.SIGNIFICANT,
            context="You know something that would hurt someone you care about.",
            question="Tell them the truth, or protect them from it?",
            option_a=DilemmaOption(
                name="Reveal the Truth",
                description="They deserve to know, even if it hurts",
                cost="The pain you cause. The relationship changes.",
                gain="Trust. Honesty. They can make informed choices.",
                themes_reinforced=["truth", "respect"],
            ),
            option_b=DilemmaOption(
                name="Carry the Burden",
                description="Keep the secret. Shield them.",
                cost="The weight of lies. If they find out...",
                gain="Their peace. Their happiness. For now.",
                themes_reinforced=["protection", "sacrifice"],
            ),
        ),
    ],
    DilemmaType.SURVIVAL: [
        MoralDilemma(
            dilemma_type=DilemmaType.SURVIVAL,
            weight=DilemmaWeight.DEFINING,
            context="Taking what you need means someone else goes without.",
            question="Your survival or theirs?",
            option_a=DilemmaOption(
                name="Take It",
                description="You need it more. You have people counting on you.",
                cost="Their suffering. Your soul.",
                gain="You survive. Your people survive.",
                themes_reinforced=["survival", "pragmatism"],
            ),
            option_b=DilemmaOption(
                name="Leave It",
                description="Find another way. Even if it kills you.",
                cost="Death may be the price of your conscience",
                gain="You can still look yourself in the mirror",
                themes_reinforced=["morality", "hope"],
            ),
        ),
    ],
}


# ============================================================================
# Theme Engine
# ============================================================================

class CampaignTheme(Enum):
    """Central themes that can drive a campaign."""
    LOVE_VS_SURVIVAL = "love_vs_survival"  # TLOU core theme
    REVENGE_CYCLE = "revenge_cycle"  # TLOU2 core theme
    FINDING_HOPE = "finding_hope"  # Hope in darkness
    COST_OF_VIOLENCE = "cost_of_violence"  # Every kill has weight
    WHAT_MAKES_US_HUMAN = "what_makes_us_human"  # Identity under pressure
    REDEMPTION = "redemption"  # Can we be forgiven?
    LEGACY = "legacy"  # What do we leave behind?


THEME_GUIDANCE = {
    CampaignTheme.LOVE_VS_SURVIVAL: {
        "core_question": "What would you sacrifice for someone you love?",
        "narrator_notes": [
            "Relationships are the heart of every scene",
            "Survival choices should threaten what the player loves",
            "The climax is always about a person, not a goal",
        ],
        "recurring_imagery": ["photographs", "mementos", "protecting someone", "two figures together"],
    },
    CampaignTheme.REVENGE_CYCLE: {
        "core_question": "When does justice become vengeance?",
        "narrator_notes": [
            "Show the cost of every violent act",
            "The enemy has people who love them too",
            "Victory should feel hollow if it was won through hate",
        ],
        "recurring_imagery": ["graves", "empty hands", "mirrors", "wounds that won't heal"],
    },
    CampaignTheme.FINDING_HOPE: {
        "core_question": "What keeps you going when everything falls apart?",
        "narrator_notes": [
            "Moments of beauty matter more in darkness",
            "Small kindnesses are revolutionary",
            "The world is changing, but not dying",
        ],
        "recurring_imagery": ["light", "growing things", "children", "laughter unexpectedly"],
    },
    CampaignTheme.COST_OF_VIOLENCE: {
        "core_question": "What does every kill take from you?",
        "narrator_notes": [
            "Name the dead. They had names.",
            "Violence solves problems and creates new ones",
            "The player should feel the weight",
        ],
        "recurring_imagery": ["blood on hands", "silence after", "what's left behind"],
    },
}


@dataclass
class ThemeTracker:
    """Tracks the central theme and ensures consistency."""
    primary_theme: CampaignTheme
    theme_moments: list[str] = field(default_factory=list)
    theme_reinforced_count: int = 0
    theme_subverted_count: int = 0
    
    def record_moment(self, description: str, reinforced: bool = True) -> None:
        """Record a moment that relates to the theme."""
        self.theme_moments.append(description)
        if reinforced:
            self.theme_reinforced_count += 1
        else:
            self.theme_subverted_count += 1
    
    def get_theme_context(self) -> str:
        """Generate context for narrator about the theme."""
        guidance = THEME_GUIDANCE.get(self.primary_theme, {})
        
        lines = [f"[CAMPAIGN THEME: {self.primary_theme.value.replace('_', ' ').upper()}]"]
        lines.append(f"Core question: {guidance.get('core_question', '')}")
        
        notes = guidance.get("narrator_notes", [])
        if notes:
            lines.append("Remember:")
            for note in notes:
                lines.append(f"  • {note}")
        
        imagery = guidance.get("recurring_imagery", [])
        if imagery:
            lines.append(f"Imagery to weave in: {', '.join(imagery)}")
        
        if self.theme_moments:
            lines.append(f"Recent theme moment: \"{self.theme_moments[-1]}\"")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "primary_theme": self.primary_theme.value,
            "theme_moments": self.theme_moments[-10:],
            "theme_reinforced_count": self.theme_reinforced_count,
            "theme_subverted_count": self.theme_subverted_count,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ThemeTracker":
        theme = CampaignTheme(data.get("primary_theme", "love_vs_survival"))
        tracker = cls(primary_theme=theme)
        tracker.theme_moments = data.get("theme_moments", [])
        tracker.theme_reinforced_count = data.get("theme_reinforced_count", 0)
        tracker.theme_subverted_count = data.get("theme_subverted_count", 0)
        return tracker


# ============================================================================
# Dilemma Generator
# ============================================================================

class DilemmaGenerator:
    """Generates contextual moral dilemmas."""
    
    def __init__(self, theme: CampaignTheme = CampaignTheme.LOVE_VS_SURVIVAL):
        self.theme = theme
        self.dilemmas_used: list[str] = []
    
    def generate(
        self,
        dilemma_type: DilemmaType | None = None,
        weight: DilemmaWeight = DilemmaWeight.SIGNIFICANT,
        npc_involved: str | None = None,
    ) -> MoralDilemma:
        """Generate a moral dilemma."""
        if dilemma_type is None:
            # Select type based on theme
            theme_preferences = {
                CampaignTheme.LOVE_VS_SURVIVAL: [DilemmaType.SACRIFICE, DilemmaType.SURVIVAL],
                CampaignTheme.REVENGE_CYCLE: [DilemmaType.MERCY, DilemmaType.JUSTICE],
                CampaignTheme.FINDING_HOPE: [DilemmaType.TRUTH, DilemmaType.LOYALTY],
            }
            preferred = theme_preferences.get(self.theme, list(DilemmaType))
            dilemma_type = random.choice(preferred)
        
        # Get template
        templates = DILEMMA_TEMPLATES.get(dilemma_type, [])
        if not templates:
            templates = DILEMMA_TEMPLATES[DilemmaType.MERCY]
        
        dilemma = random.choice(templates)
        
        # Customize with NPC if provided
        if npc_involved:
            dilemma.witnesses.append(npc_involved)
            # Could further customize context based on relationship
        
        # Adjust weight
        dilemma.weight = weight
        
        return dilemma
    
    def should_present_dilemma(self, scenes_since_last: int, tension_level: float) -> bool:
        """Determine if it's time for a dilemma."""
        # Don't overwhelm with choices
        if scenes_since_last < 5:
            return False
        
        # Higher tension = more likely
        base_chance = 0.1 + (tension_level * 0.2)
        
        # Increase with time since last
        time_bonus = min(0.3, scenes_since_last * 0.03)
        
        return random.random() < (base_chance + time_bonus)


# ============================================================================
# Convenience Functions
# ============================================================================

def create_theme_tracker(theme: str = "love_vs_survival") -> ThemeTracker:
    """Create a theme tracker."""
    try:
        campaign_theme = CampaignTheme(theme)
    except ValueError:
        campaign_theme = CampaignTheme.LOVE_VS_SURVIVAL
    return ThemeTracker(primary_theme=campaign_theme)


def create_dilemma_generator(theme: str = "love_vs_survival") -> DilemmaGenerator:
    """Create a dilemma generator."""
    try:
        campaign_theme = CampaignTheme(theme)
    except ValueError:
        campaign_theme = CampaignTheme.LOVE_VS_SURVIVAL
    return DilemmaGenerator(theme=campaign_theme)


def quick_dilemma(dilemma_type: str = "mercy") -> str:
    """Generate a quick dilemma context."""
    try:
        dtype = DilemmaType(dilemma_type)
    except ValueError:
        dtype = DilemmaType.MERCY
    
    generator = DilemmaGenerator()
    dilemma = generator.generate(dilemma_type=dtype)
    return dilemma.get_narrator_context()
