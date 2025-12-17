"""
Campaign Truths - Static World Settings Document.
Stores the immutable "truths" of the campaign setting.

These are injected into the Narrator context to ensure
consistent tone and world rules across all generated content.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ============================================================================
# Truth Categories
# ============================================================================

class TruthCategory(Enum):
    """Categories of campaign truths."""
    CATACLYSM = "cataclysm"  # Why humanity is in the Forge
    MAGIC = "magic"  # Supernatural elements
    TECHNOLOGY = "technology"  # Tech level and reliability
    AI = "ai"  # Artificial intelligence status
    RELIGION = "religion"  # Faith and belief systems
    SOCIETY = "society"  # Social structure
    ALIENS = "aliens"  # Non-human life
    WAR = "war"  # Conflict state


@dataclass
class CampaignTruth:
    """A single campaign truth."""
    category: TruthCategory
    name: str
    description: str
    narrative_implications: list[str] = field(default_factory=list)


# ============================================================================
# Starforged Default Truths
# ============================================================================

# These are the canonical Ironsworn: Starforged setting options
STARFORGED_TRUTHS = {
    TruthCategory.CATACLYSM: [
        CampaignTruth(
            category=TruthCategory.CATACLYSM,
            name="The Exodus",
            description="We fled a dying Earth. The sun expanded, forcing humanity into the Forge.",
            narrative_implications=[
                "Earth is a sacred memory, often referenced with reverence",
                "Old Earth artifacts are precious relics",
                "The journey was generations long—cultural drift occurred",
            ],
        ),
        CampaignTruth(
            category=TruthCategory.CATACLYSM,
            name="The Plague",
            description="A biological horror swept through humanity. We fled to survive.",
            narrative_implications=[
                "Disease is deeply feared",
                "Quarantine protocols are strict",
                "Some settlements reject outsiders entirely",
            ],
        ),
        CampaignTruth(
            category=TruthCategory.CATACLYSM,
            name="The Machine War",
            description="Our creations turned against us. We escaped their reach.",
            narrative_implications=[
                "AI is distrusted or banned",
                "Automated systems are viewed with suspicion",
                "Some machines may have followed us",
            ],
        ),
    ],
    TruthCategory.AI: [
        CampaignTruth(
            category=TruthCategory.AI,
            name="AI is Outlawed",
            description="Creating true AI is forbidden. Those who do are exiled or worse.",
            narrative_implications=[
                "No helpful AI companions",
                "Automated systems are 'dumb' by design",
                "Rogue AI is the stuff of nightmares",
            ],
        ),
        CampaignTruth(
            category=TruthCategory.AI,
            name="AI is Rare but Exists",
            description="Some AI entities exist in the Forge, remnants or new creations.",
            narrative_implications=[
                "AI encounters are significant events",
                "Attitudes toward AI vary by culture",
                "Some worship AI as oracles",
            ],
        ),
        CampaignTruth(
            category=TruthCategory.AI,
            name="AI is Common",
            description="AI is integrated into daily life, though not always trusted.",
            narrative_implications=[
                "Ships often have AI pilots",
                "The line between tool and person is blurred",
                "AI rights are a political issue",
            ],
        ),
    ],
    TruthCategory.MAGIC: [
        CampaignTruth(
            category=TruthCategory.MAGIC,
            name="No Magic",
            description="The Forge is a place of science, however unreliable.",
            narrative_implications=[
                "Supernatural events have rational explanations",
                "Technology is the only power",
                "Claims of magic are superstition",
            ],
        ),
        CampaignTruth(
            category=TruthCategory.MAGIC,
            name="Rare Supernatural",
            description="Strange powers exist but are poorly understood.",
            narrative_implications=[
                "Psionics or 'gifts' are rare mutations",
                "Those with powers are feared or revered",
                "No one truly understands how it works",
            ],
        ),
        CampaignTruth(
            category=TruthCategory.MAGIC,
            name="Mystic Forces",
            description="The Forge is suffused with strange energies.",
            narrative_implications=[
                "Magic is common but dangerous",
                "Ancient precursors may have been magical",
                "The supernatural is part of daily life",
            ],
        ),
    ],
    TruthCategory.ALIENS: [
        CampaignTruth(
            category=TruthCategory.ALIENS,
            name="We Are Alone",
            description="No intelligent alien life has been found. The silence is deafening.",
            narrative_implications=[
                "Humanity is isolated",
                "Finding alien life would be paradigm-shifting",
                "Ancient ruins suggest we're not first",
            ],
        ),
        CampaignTruth(
            category=TruthCategory.ALIENS,
            name="First Contact",
            description="We've encountered alien species. Relations are complicated.",
            narrative_implications=[
                "Trade and conflict with aliens",
                "Cultural exchange and misunderstanding",
                "Some humans live among aliens",
            ],
        ),
    ],
}


# ============================================================================
# Campaign Truths Manager
# ============================================================================

@dataclass
class CampaignTruths:
    """
    Manages the selected truths for a campaign.
    Provides narrative context for the Narrator agent.
    """
    truths: dict[TruthCategory, CampaignTruth] = field(default_factory=dict)
    custom_truths: list[str] = field(default_factory=list)
    
    def set_truth(self, category: TruthCategory, truth: CampaignTruth) -> None:
        """Set a truth for a category."""
        self.truths[category] = truth
    
    def add_custom_truth(self, truth: str) -> None:
        """Add a custom campaign truth."""
        self.custom_truths.append(truth)
    
    def get_narrative_context(self) -> str:
        """
        Generate narrative context for the Narrator.
        This is injected into the system prompt.
        """
        lines = ["[CAMPAIGN TRUTHS]"]
        
        for category, truth in self.truths.items():
            lines.append(f"\n{category.value.upper()}: {truth.name}")
            lines.append(f"  {truth.description}")
            if truth.narrative_implications:
                lines.append(f"  → {truth.narrative_implications[0]}")
        
        if self.custom_truths:
            lines.append("\nCUSTOM WORLD RULES:")
            for custom in self.custom_truths:
                lines.append(f"  • {custom}")
        
        return "\n".join(lines)
    
    def get_forbidden_elements(self) -> list[str]:
        """Get elements that shouldn't appear based on truths."""
        forbidden = []
        
        ai_truth = self.truths.get(TruthCategory.AI)
        if ai_truth and ai_truth.name == "AI is Outlawed":
            forbidden.append("helpful AI companions")
            forbidden.append("friendly robots")
        
        magic_truth = self.truths.get(TruthCategory.MAGIC)
        if magic_truth and magic_truth.name == "No Magic":
            forbidden.append("magical powers")
            forbidden.append("spells")
            forbidden.append("supernatural abilities")
        
        aliens_truth = self.truths.get(TruthCategory.ALIENS)
        if aliens_truth and aliens_truth.name == "We Are Alone":
            forbidden.append("alien species")
            forbidden.append("extraterrestrial beings")
        
        return forbidden
    
    def to_dict(self) -> dict:
        return {
            "truths": {
                cat.value: {
                    "name": truth.name,
                    "description": truth.description,
                    "implications": truth.narrative_implications,
                }
                for cat, truth in self.truths.items()
            },
            "custom_truths": self.custom_truths,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CampaignTruths":
        truths = cls()
        
        for cat_str, truth_data in data.get("truths", {}).items():
            category = TruthCategory(cat_str)
            truth = CampaignTruth(
                category=category,
                name=truth_data.get("name", ""),
                description=truth_data.get("description", ""),
                narrative_implications=truth_data.get("implications", []),
            )
            truths.truths[category] = truth
        
        truths.custom_truths = data.get("custom_truths", [])
        return truths


# ============================================================================
# Convenience Functions
# ============================================================================

def create_default_campaign() -> CampaignTruths:
    """Create campaign with default Starforged truths."""
    truths = CampaignTruths()
    
    # Select first option from each category as default
    for category, options in STARFORGED_TRUTHS.items():
        if options:
            truths.set_truth(category, options[0])
    
    return truths


def create_dark_campaign() -> CampaignTruths:
    """Create a darker campaign setting."""
    truths = CampaignTruths()
    
    # Machine War cataclysm
    truths.set_truth(TruthCategory.CATACLYSM, STARFORGED_TRUTHS[TruthCategory.CATACLYSM][2])
    # AI is outlawed
    truths.set_truth(TruthCategory.AI, STARFORGED_TRUTHS[TruthCategory.AI][0])
    # No magic
    truths.set_truth(TruthCategory.MAGIC, STARFORGED_TRUTHS[TruthCategory.MAGIC][0])
    # We are alone
    truths.set_truth(TruthCategory.ALIENS, STARFORGED_TRUTHS[TruthCategory.ALIENS][0])
    
    truths.add_custom_truth("Hope is hard-won; despair is the default")
    truths.add_custom_truth("Trust is rare; betrayal is common")
    
    return truths


def create_mystical_campaign() -> CampaignTruths:
    """Create a more mystical campaign setting."""
    truths = CampaignTruths()
    
    # Exodus cataclysm
    truths.set_truth(TruthCategory.CATACLYSM, STARFORGED_TRUTHS[TruthCategory.CATACLYSM][0])
    # AI is rare
    truths.set_truth(TruthCategory.AI, STARFORGED_TRUTHS[TruthCategory.AI][1])
    # Mystic forces
    truths.set_truth(TruthCategory.MAGIC, STARFORGED_TRUTHS[TruthCategory.MAGIC][2])
    # First contact
    truths.set_truth(TruthCategory.ALIENS, STARFORGED_TRUTHS[TruthCategory.ALIENS][1])
    
    truths.add_custom_truth("The Forge hides ancient secrets")
    truths.add_custom_truth("The supernatural is real but poorly understood")
    
    return truths
