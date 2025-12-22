"""
Core Story Structure & DNA.

This module locks the "North Star" of the narrative: the Premise and the Designing Principle.
It serves as the immutable reference for all narrative choices, ensuring consistency
with the themes of irony, projection, and the "Mirror" mechanic.
"""

from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class StoryStructure:
    premise: str
    designing_principle: str
    themes: List[str]
    design_metaphors: Dict[str, str]
    ironic_core: str

# LOCKED STORY DNA
# DO NOT CHANGE without a major narrative refactor.

LOCKED_PREMISE = (
    "A detective running from their own psychological wounds investigates a murder on a "
    "claustrophobic ship, only to discover the killer’s motive is a dark mirror of their own flaw."
)

DESIGNING_PRINCIPLE = "The Investigation is a Mirror."

THEMES = [
    "Projection: We see in others what we fear in ourselves.",
    "Isolation vs. Connection: The ship is a bottle; the crew are the reagents.",
    "The Cost of Truth: Knowing the truth requires destroying the illusion of safety.",
    "Redemption: Can only be chosen, never forced."
]

DESIGN_METAPHORS = {
    "The Ship": "A Pressure Cooker / A Locked Room.",
    "The Investigation": "Peeling back layers of an onion (or specialized hull plating).",
    "The Killer": "The Shadow Self.",
    "The Clock": "Decay/Rust. Things aren't just happening; they are breaking down."
}

IRONIC_CORE = (
    "The detective seeks to solve the murder to restore order/justice, but the act of solving it "
    "forces them to confront the internal disorder/injustice they have been fleeing."
)

def get_story_structure() -> StoryStructure:
    """Returns the locked story structure."""
    return StoryStructure(
        premise=LOCKED_PREMISE,
        designing_principle=DESIGNING_PRINCIPLE,
        themes=THEMES,
        design_metaphors=DESIGN_METAPHORS,
        ironic_core=IRONIC_CORE
    )
