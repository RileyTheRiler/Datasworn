"""
Impossible Choice Generator.

This module generates high-stakes dilemmas where the player must choose between
two valuable things or two evils, ensuring dramatic tension.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple
import random

class DilemmaType(Enum):
    SACRIFICE = "SACRIFICE"       # Lose A to save B
    BETRAYAL = "BETRAYAL"         # Gain X but hurt Y
    RISK = "RISK"                 # Safe low reward vs. Dangerous high reward
    IDEOLOGICAL = "IDEOLOGICAL"   # Principle A vs. Principle B

@dataclass
class DilemmaOption:
    description: str
    cost: str
    benefit: str

@dataclass
class ImpossibleDilemma:
    dilemma_type: DilemmaType
    description: str
    option_a: DilemmaOption
    option_b: DilemmaOption
    resolved: bool = False
    chosen_option: Optional[str] = None # 'A' or 'B'

@dataclass
class ImpossibleChoiceGenerator:
    """
    Creates and tracks dramatic dilemmas.
    """
    active_dilemma: Optional[ImpossibleDilemma] = None
    
    def generate_dilemma(self, context: str, npc_names: List[str]) -> ImpossibleDilemma:
        """
        Create a dilemma based on available context.
        """
        # Template-based generation (placeholder for LLM-driven in future)
        npc = random.choice(npc_names) if npc_names else "your companion"
        
        # Simple Logic: 50% Sacrifice, 50% Risk
        if random.random() < 0.5:
            dilemma = ImpossibleDilemma(
                dilemma_type=DilemmaType.SACRIFICE,
                description=f"{npc} is in danger, but the mission objective is critical.",
                option_a=DilemmaOption(
                    description=f"Save {npc}",
                    cost="Fail the mission objective",
                    benefit=f"{npc} lives"
                ),
                option_b=DilemmaOption(
                    description="Secure the objective",
                    cost=f"{npc} is left behind",
                    benefit="Mission success"
                )
            )
        else:
            dilemma = ImpossibleDilemma(
                dilemma_type=DilemmaType.RISK,
                description="A shortcut presents itself, but it passes through a radiation storm.",
                option_a=DilemmaOption(
                    description="Take the shortcut",
                    cost="High risk of injury/damage",
                    benefit="Save critical time"
                ),
                option_b=DilemmaOption(
                    description="Go the long way",
                    cost="Lose time, potential failure",
                    benefit="Safe passage"
                )
            )
            
        self.active_dilemma = dilemma
        return dilemma

    def resolve_dilemma(self, choice: str): # 'A' or 'B'
        if self.active_dilemma:
            self.active_dilemma.resolved = True
            self.active_dilemma.chosen_option = choice
            
            # Here we would trigger the ConsequenceManager or PayoffTracker
            # But the Orchestrator handles that integration

    def to_dict(self) -> dict:
        if not self.active_dilemma:
            return {"active_dilemma": None}
            
        d = self.active_dilemma
        return {
            "active_dilemma": {
                "dilemma_type": d.dilemma_type.value,
                "description": d.description,
                "option_a": {
                    "description": d.option_a.description,
                    "cost": d.option_a.cost,
                    "benefit": d.option_a.benefit
                },
                "option_b": {
                    "description": d.option_b.description,
                    "cost": d.option_b.cost,
                    "benefit": d.option_b.benefit
                },
                "resolved": d.resolved,
                "chosen_option": d.chosen_option
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ImpossibleChoiceGenerator":
        gen = cls()
        d_data = data.get("active_dilemma")
        if d_data:
            gen.active_dilemma = ImpossibleDilemma(
                dilemma_type=DilemmaType(d_data["dilemma_type"]),
                description=d_data["description"],
                option_a=DilemmaOption(**d_data["option_a"]),
                option_b=DilemmaOption(**d_data["option_b"]),
                resolved=d_data["resolved"],
                chosen_option=d_data["chosen_option"]
            )
        return gen
