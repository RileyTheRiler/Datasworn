"""
Moral Argument System.

This module implements the moral chain to ensure theme emerges through choices, not speeches.
It tracks the hero's moral weakness, immoral choices, ally criticism, and final moral self-revelation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum

class MoralWeaknessType(str, Enum):
    """Core moral weaknesses that drive immoral choices."""
    CONTROL_OBSESSION = "control_obsession"  # Need to control everything
    SELF_PRESERVATION = "self_preservation"  # Survival at any cost
    PRIDE = "pride"  # Cannot admit weakness or error
    VENGEANCE = "vengeance"  # Justice twisted into revenge
    DENIAL = "denial"  # Refusing to face truth
    ABANDONMENT_FEAR = "abandonment_fear"  # Will do anything to avoid being alone
    GUILT_AVOIDANCE = "guilt_avoidance"  # Cannot face past mistakes

class ValueSet(str, Enum):
    """Competing value systems in the moral argument."""
    JUSTICE = "justice"
    MERCY = "mercy"
    TRUTH = "truth"
    LOYALTY = "loyalty"
    SURVIVAL = "survival"
    REDEMPTION = "redemption"
    CONTROL = "control"
    FREEDOM = "freedom"

@dataclass
class MoralWeakness:
    """The hero's core moral flaw."""
    weakness_type: MoralWeaknessType
    description: str
    root_fear: str  # What drives this weakness
    manifestation: str  # How it shows up in behavior

@dataclass
class ImmoralChoice:
    """A specific immoral action with emotional justification."""
    choice_id: str
    scene_number: int
    description: str
    emotional_justification: str  # Why the hero tells themselves it's okay
    actual_harm: str  # The real damage caused
    escalation_level: int  # 1 (first), 2, 3 (most severe)
    witnesses: List[str] = field(default_factory=list)  # Who saw this

@dataclass
class AllyCriticism:
    """An ally's value-based criticism that stings the hero."""
    ally_name: str
    scene_number: int
    value_defended: ValueSet
    criticism_text: str
    why_it_stings: str  # What truth does it expose

@dataclass
class MoralSelfRevelation:
    """The moment of moral clarity (image or action, not exposition)."""
    scene_number: int
    trigger_event: str
    revelation_image: str  # Visual/action-based moment, not dialogue
    internal_shift: str  # What changes inside the hero
    is_complete: bool = False

@dataclass
class FinalDecision:
    """The choice that proves change or tragic refusal."""
    scene_number: int
    decision_description: str
    proves_change: bool  # True = hero changed, False = tragic refusal
    value_set_that_won: ValueSet
    action_that_proves_it: str  # Concrete action, not words

@dataclass
class MoralArgument:
    """The complete moral arc."""
    # Core weakness
    moral_weakness: MoralWeakness
    
    # The scripted first immoral act
    first_immoral_act: ImmoralChoice
    
    # Escalating choices
    immoral_choices: List[ImmoralChoice] = field(default_factory=list)
    
    # Ally criticism beats
    ally_criticisms: List[AllyCriticism] = field(default_factory=list)
    
    # The battle of values
    competing_values: List[ValueSet] = field(default_factory=list)
    
    # Self-revelation
    moral_self_revelation: Optional[MoralSelfRevelation] = None
    
    # Final decision
    final_decision: Optional[FinalDecision] = None
    
    # Thematic insight (one line, audience-facing)
    thematic_insight: str = ""
    
    def add_immoral_choice(self, choice: ImmoralChoice):
        """Add an immoral choice to the escalation chain."""
        self.immoral_choices.append(choice)
    
    def add_ally_criticism(self, criticism: AllyCriticism):
        """Add an ally's criticism beat."""
        self.ally_criticisms.append(criticism)
    
    def set_moral_revelation(self, revelation: MoralSelfRevelation):
        """Set the moral self-revelation moment."""
        self.moral_self_revelation = revelation
    
    def set_final_decision(self, decision: FinalDecision):
        """Set the final decision that proves change or refusal."""
        self.final_decision = decision
    
    def get_current_escalation_level(self) -> int:
        """Get the current escalation level (0-3)."""
        if not self.immoral_choices:
            return 0
        return max(c.escalation_level for c in self.immoral_choices)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "moral_weakness": {
                "type": self.moral_weakness.weakness_type.value,
                "description": self.moral_weakness.description,
                "root_fear": self.moral_weakness.root_fear,
                "manifestation": self.moral_weakness.manifestation
            },
            "first_immoral_act": {
                "choice_id": self.first_immoral_act.choice_id,
                "scene": self.first_immoral_act.scene_number,
                "description": self.first_immoral_act.description,
                "justification": self.first_immoral_act.emotional_justification,
                "harm": self.first_immoral_act.actual_harm,
                "escalation_level": self.first_immoral_act.escalation_level
            },
            "immoral_choices": [
                {
                    "choice_id": c.choice_id,
                    "scene": c.scene_number,
                    "description": c.description,
                    "justification": c.emotional_justification,
                    "harm": c.actual_harm,
                    "escalation_level": c.escalation_level,
                    "witnesses": c.witnesses
                } for c in self.immoral_choices
            ],
            "ally_criticisms": [
                {
                    "ally": a.ally_name,
                    "scene": a.scene_number,
                    "value": a.value_defended.value,
                    "criticism": a.criticism_text,
                    "why_it_stings": a.why_it_stings
                } for a in self.ally_criticisms
            ],
            "competing_values": [v.value for v in self.competing_values],
            "moral_self_revelation": {
                "scene": self.moral_self_revelation.scene_number,
                "trigger": self.moral_self_revelation.trigger_event,
                "image": self.moral_self_revelation.revelation_image,
                "shift": self.moral_self_revelation.internal_shift,
                "complete": self.moral_self_revelation.is_complete
            } if self.moral_self_revelation else None,
            "final_decision": {
                "scene": self.final_decision.scene_number,
                "description": self.final_decision.decision_description,
                "proves_change": self.final_decision.proves_change,
                "winning_value": self.final_decision.value_set_that_won.value,
                "action": self.final_decision.action_that_proves_it
            } if self.final_decision else None,
            "thematic_insight": self.thematic_insight,
            "current_escalation_level": self.get_current_escalation_level()
        }

# ============================================================================
# PRESET MORAL ARGUMENTS FOR THE DETECTIVE STORY
# ============================================================================

def create_detective_moral_argument() -> MoralArgument:
    """Create the moral argument for the detective investigating the murder."""
    
    moral_weakness = MoralWeakness(
        weakness_type=MoralWeaknessType.CONTROL_OBSESSION,
        description="The detective needs to control every outcome to feel safe.",
        root_fear="If I lose control, I lose everything (like I did before).",
        manifestation="Micromanaging, refusing help, forcing 'order' on chaos."
    )
    
    first_immoral_act = ImmoralChoice(
        choice_id="first_act_001",
        scene_number=3,
        description="The detective withholds critical evidence from the crew to maintain control of the investigation.",
        emotional_justification="They can't handle the truth. I need to manage this carefully.",
        actual_harm="Crew members make uninformed decisions, trust erodes.",
        escalation_level=1,
        witnesses=["Torres"]
    )
    
    # Pre-populate with the first act
    moral_arg = MoralArgument(
        moral_weakness=moral_weakness,
        first_immoral_act=first_immoral_act,
        competing_values=[ValueSet.CONTROL, ValueSet.TRUTH, ValueSet.LOYALTY],
        thematic_insight="The need to control everything is itself a loss of control."
    )
    
    # Add escalating choices (these would be triggered during gameplay)
    moral_arg.add_immoral_choice(ImmoralChoice(
        choice_id="escalation_002",
        scene_number=7,
        description="The detective manipulates Kai into revealing information by exploiting his addiction.",
        emotional_justification="I'm helping him by keeping him focused. The truth matters more.",
        actual_harm="Kai's trust is shattered, his recovery is set back.",
        escalation_level=2,
        witnesses=["Kai", "Dr. Okonkwo"]
    ))
    
    moral_arg.add_immoral_choice(ImmoralChoice(
        choice_id="escalation_003",
        scene_number=12,
        description="The detective threatens to expose Vasquez's smuggling to force cooperation.",
        emotional_justification="He's a criminal anyway. I'm doing what's necessary.",
        actual_harm="Vasquez is cornered, desperate, and now an enemy.",
        escalation_level=3,
        witnesses=["Vasquez", "Ember"]
    ))
    
    # Add ally criticism
    moral_arg.add_ally_criticism(AllyCriticism(
        ally_name="Torres",
        scene_number=9,
        value_defended=ValueSet.TRUTH,
        criticism_text="You're not solving this. You're just controlling it. There's a difference.",
        why_it_stings="She sees that the detective's 'justice' is really about ego."
    ))
    
    return moral_arg

def get_moral_argument() -> Dict[str, Any]:
    """Get the current moral argument for the detective story."""
    moral_arg = create_detective_moral_argument()
    return moral_arg.to_dict()
