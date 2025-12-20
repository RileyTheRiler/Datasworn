"""
Branching Narrative System.

This module tracks major divergences in the story path, allowing the game to
understand "what could have been" and track the chosen timeline.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
import uuid
import uuid as uuid_lib

@dataclass
class BranchOption:
    """A possible path at a branch point."""
    option_id: str
    description: str
    consequence_hint: str
    chosen: bool = False

@dataclass
class BranchPoint:
    """A major narrative divergence."""
    branch_id: str
    scene: int
    description: str
    options: List[BranchOption] = field(default_factory=list)
    resolved: bool = False

@dataclass
class BranchingNarrativeSystem:
    """
    Manages the tree of narrative choices.
    """
    branches: Dict[str, BranchPoint] = field(default_factory=dict)
    
    def propose_branch(self, description: str, current_scene: int, 
                      options: List[Dict[str, str]]) -> str:
        """
        Create a new major decision point.
        """
        branch_id = str(uuid_lib.uuid4())
        
        branch_options = []
        for i, opt in enumerate(options):
            branch_options.append(BranchOption(
                option_id=f"{branch_id}_opt_{i}",
                description=opt["description"],
                consequence_hint=opt.get("hint", "")
            ))
            
        self.branches[branch_id] = BranchPoint(
            branch_id=branch_id,
            scene=current_scene,
            description=description,
            options=branch_options
        )
        return branch_id

    def commit_choice(self, branch_id: str, option_index: int):
        """
        Lock in a choice for a branch point.
        """
        if branch_id in self.branches:
            branch = self.branches[branch_id]
            if 0 <= option_index < len(branch.options):
                branch.options[option_index].chosen = True
                branch.resolved = True

    def get_active_branches(self) -> List[BranchPoint]:
        """Return unresolved branches."""
        return [b for b in self.branches.values() if not b.resolved]

    def to_dict(self) -> dict:
        return {
            "branches": {
                bid: {
                    "branch_id": b.branch_id,
                    "scene": b.scene,
                    "description": b.description,
                    "resolved": b.resolved,
                    "options": [
                        {
                            "option_id": o.option_id,
                            "description": o.description,
                            "consequence_hint": o.consequence_hint,
                            "chosen": o.chosen
                        }
                        for o in b.options
                    ]
                }
                for bid, b in self.branches.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BranchingNarrativeSystem":
        sys = cls()
        for bid, b_data in data.get("branches", {}).items():
            options = [
                BranchOption(
                    option_id=o["option_id"],
                    description=o["description"],
                    consequence_hint=o["consequence_hint"],
                    chosen=o["chosen"]
                )
                for o in b_data.get("options", [])
            ]
            
            sys.branches[bid] = BranchPoint(
                branch_id=b_data["branch_id"],
                scene=b_data["scene"],
                description=b_data["description"],
                options=options,
                resolved=b_data["resolved"]
            )
        return sys
