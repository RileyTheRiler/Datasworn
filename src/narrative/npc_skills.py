"""
NPC Skill Progression System.

This module allows NPCs to grow in competence over time, gaining XP and levels
in core competencies (Combat, Tech, Social).
"""

from dataclasses import dataclass, field
from typing import Dict, Optional

@dataclass
class NPCSkills:
    combat: int = 1
    tech: int = 1
    social: int = 1
    xp: int = 0
    level: int = 1

@dataclass
class NPCSkillSystem:
    """
    Tracks NPC competence and growth.
    """
    npc_skills: Dict[str, NPCSkills] = field(default_factory=dict)
    
    def get_skills(self, npc_id: str) -> NPCSkills:
        if npc_id not in self.npc_skills:
            self.npc_skills[npc_id] = NPCSkills()
        return self.npc_skills[npc_id]

    def award_xp(self, npc_id: str, amount: int) -> bool:
        """
        Give XP to an NPC. Returns True if they leveled up.
        """
        skills = self.get_skills(npc_id)
        skills.xp += amount
        
        # Simple Level Up Logic: 10 XP per level
        if skills.xp >= skills.level * 10:
            skills.level += 1
            skills.xp = 0 # Reset for next level (simple approach)
            
            # Boost a random stat
            import random
            roll = random.random()
            if roll < 0.33: skills.combat += 1
            elif roll < 0.66: skills.tech += 1
            else: skills.social += 1
            
            return True
        return False

    def to_dict(self) -> dict:
        return {
            "npc_skills": {
                nid: {
                    "combat": s.combat,
                    "tech": s.tech,
                    "social": s.social,
                    "xp": s.xp,
                    "level": s.level
                }
                for nid, s in self.npc_skills.items()
            }
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NPCSkillSystem":
        sys = cls()
        for nid, s_data in data.get("npc_skills", {}).items():
            sys.npc_skills[nid] = NPCSkills(
                combat=s_data["combat"],
                tech=s_data["tech"],
                social=s_data["social"],
                xp=s_data["xp"],
                level=s_data["level"]
            )
        return sys
