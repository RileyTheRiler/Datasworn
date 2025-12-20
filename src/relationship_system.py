"""
Relationship Web System for Starforged AI Game Master.
Tracks trust, suspicion, and inter-crew dynamics.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import random
from datetime import datetime
from src.psych_profile import PsychologicalEngine, EmotionalState, NPCPsyche


@dataclass
class CrewPerception:
    """How the crew collectively perceives the player."""
    perceived_traits: dict[str, float] = field(default_factory=dict)  # e.g., "reliable": 0.7
    reputation_score: float = 0.5  # 0.0 (pariah) to 1.0 (hero)
    notable_actions: list[str] = field(default_factory=list)  # Recent memorable things
    
    def to_dict(self) -> dict:
        return {
            "perceived_traits": self.perceived_traits,
            "reputation_score": self.reputation_score,
            "notable_actions": self.notable_actions[-5:],  # Last 5
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CrewPerception":
        return cls(
            perceived_traits=data.get("perceived_traits", {}),
            reputation_score=data.get("reputation_score", 0.5),
            notable_actions=data.get("notable_actions", []),
        )

@dataclass
class EmotionalMemory:
    """A record of the player's emotional state during an interaction."""
    emotion: EmotionalState
    timestamp: datetime
    context: str  # What was happening
    intensity: float = 0.5  # How strong the emotion was


@dataclass
class CrewMember:
    """A single crew member on the research vessel."""
    id: str
    name: str
    role: str  # e.g., "Captain", "Engineer", "Medic"
    trust: float = 0.5       # 0.0 (hostile) to 1.0 (loyal)
    suspicion: float = 0.0   # 0.0 (oblivious) to 1.0 (knows your secrets)
    secrets: list[str] = field(default_factory=list)  # What they're hiding
    known_facts: list[str] = field(default_factory=list)  # What they know about the player
    is_threat: bool = False  # Assigned by mystery generator
    psyche: NPCPsyche | None = None  # Optional NPC psychological state
    emotional_history: list[EmotionalMemory] = field(default_factory=list)
    
    def modify_trust(self, delta: float):
        self.trust = max(0.0, min(1.0, self.trust + delta))
        
    def modify_suspicion(self, delta: float):
        self.suspicion = max(0.0, min(1.0, self.suspicion + delta))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "trust": self.trust,
            "suspicion": self.suspicion,
            "secrets": self.secrets,
            "known_facts": self.known_facts,
            "is_threat": self.is_threat,
            "psyche": self.psyche.model_dump() if self.psyche else None,
            "emotional_history": [{"emotion": m.emotion.value, "timestamp": m.timestamp.isoformat(), "context": m.context} for m in self.emotional_history[-5:]]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CrewMember":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class RelationshipWeb:
    """Manages all crew relationships."""
    crew: dict[str, CrewMember] = field(default_factory=dict)
    perception: CrewPerception = field(default_factory=CrewPerception)
    
    def __post_init__(self):
        if not self.crew:
            self._initialize_crew()
            
    def _initialize_crew(self):
        """Initialize the 6 crew members."""
        defaults = [
            CrewMember("captain", "Commander Vasquez", "Captain", trust=0.4, secrets=["Knows about Protocol 99"]),
            CrewMember("engineer", "Chen Wei", "Chief Engineer", trust=0.6, secrets=["Sabotaged the backup drive"]),
            CrewMember("medic", "Dr. Okonkwo", "Ship's Doctor", trust=0.7, secrets=["Has been drugging the crew"]),
            CrewMember("scientist", "Dr. Petrova", "Lead Researcher", trust=0.5, secrets=["The experiment was her idea"]),
            CrewMember("security", "Reyes", "Security Chief", trust=0.3, secrets=["Former military black ops"]),
            CrewMember("pilot", "Nyx", "Pilot/Navigator", trust=0.5, secrets=["Is not who they claim to be"]),
        ]
        for c in defaults:
            self.crew[c.id] = c
            
    def apply_action(self, action_type: str, target_id: str, context: str = "", 
                     psych_profile: "PsychologicalProfile" = None) -> dict:
        """
        Modify relationships based on player action.
        Returns a dict describing the change for narrative injection.
        """
        if target_id not in self.crew:
            return {"effect": "none", "message": "Target not found."}
            
        target = self.crew[target_id]
        effect = {"target": target.name, "trust_delta": 0.0, "suspicion_delta": 0.0}
        
        engine = PsychologicalEngine() if psych_profile else None
        
        # Action type mappings
        if action_type == "help":
            effect["trust_delta"] = 0.1
            target.modify_trust(0.1)
        elif action_type == "lie":
            effect["suspicion_delta"] = 0.15
            target.modify_suspicion(0.15)
            # If caught...
            if random.random() < target.suspicion:
                effect["trust_delta"] = -0.2
                target.modify_trust(-0.2)
                effect["caught"] = True
        elif action_type == "threaten":
            effect["trust_delta"] = -0.3
            effect["suspicion_delta"] = 0.2
            target.modify_trust(-0.3)
            target.modify_suspicion(0.2)
        elif action_type == "confide":
            # Sharing a secret builds trust but gives them leverage
            effect["trust_delta"] = 0.2
            effect["suspicion_delta"] = 0.1  # They now know something
            target.modify_trust(0.2)
            target.modify_suspicion(0.1)
            target.known_facts.append(context)
        elif action_type == "investigate":
            # Digging into their past
            effect["suspicion_delta"] = 0.1
            target.modify_suspicion(0.1)
            # Chance to discover a secret
            if random.random() > 0.5 and target.secrets:
                effect["discovered_secret"] = target.secrets[0]
                
        # Psychological Impact
        if engine and psych_profile:
            # Impact opinions in psych profile
            if effect["trust_delta"] != 0:
                engine.update_opinion(psych_profile, target.name, effect["trust_delta"])
            
            # Action-specific psychological shifts
            if action_type == "threaten":
                engine.update_stress(psych_profile, 0.1)
                psych_profile.current_emotion = EmotionalState.ANGRY
            elif action_type == "lie" and effect.get("caught"):
                engine.update_stress(psych_profile, 0.2)
                psych_profile.current_emotion = EmotionalState.GUILTY
            elif action_type == "confide":
                psych_profile.current_emotion = EmotionalState.HOPEFUL

        # NPC Psychological Evolution
        if target.psyche:
            if action_type == "threaten":
                target.psyche.current_emotion = EmotionalState.AFRAID
                target.psyche.instability = min(1.0, target.psyche.instability + 0.1)
            elif action_type == "help":
                target.psyche.current_emotion = EmotionalState.HOPEFUL
                target.psyche.instability = max(0.0, target.psyche.instability - 0.05)
            elif action_type == "lie" and effect.get("caught"):
                target.psyche.current_emotion = EmotionalState.SUSPICIOUS
                target.psyche.instability = min(1.0, target.psyche.instability + 0.15)
            elif action_type == "confide":
                target.psyche.current_emotion = EmotionalState.PEACEFUL

        return effect
    
    def get_betrayal_candidates(self) -> list[CrewMember]:
        """Get crew members likely to betray the player."""
        return [c for c in self.crew.values() if c.trust < 0.3 and c.suspicion > 0.6]
    
    def get_ally_candidates(self) -> list[CrewMember]:
        """Get crew members who might help the player."""
        return [c for c in self.crew.values() if c.trust > 0.7]

    # =========================================================================
    # NPC PSYCHOLOGICAL TELLS
    # =========================================================================

    def get_npc_reaction_to_emotion(self, npc_id: str, player_emotion: EmotionalState) -> str:
        """
        Get how an NPC reacts to the player's visible emotional state.
        Returns a narrative hint for the Director.
        """
        if npc_id not in self.crew:
            return ""
        
        npc = self.crew[npc_id]
        
        reactions = {
            EmotionalState.ANXIOUS: {
                "high_suspicion": f"{npc.name} notices your nervousness. Their eyes narrow.",
                "low_suspicion": f"{npc.name} seems oblivious to your anxiety.",
            },
            EmotionalState.ANGRY: {
                "high_trust": f"{npc.name} looks concerned at your anger. They try to calm you.",
                "low_trust": f"{npc.name} backs away slightly, hand near their belt.",
            },
            EmotionalState.AFRAID: {
                "is_threat": f"{npc.name} smiles, almost imperceptibly, at your fear.",
                "not_threat": f"{npc.name} looks worried for you.",
            },
            EmotionalState.SUSPICIOUS: {
                "high_suspicion": f"{npc.name} meets your suspicious gaze. They're watching you too.",
                "low_suspicion": f"{npc.name} seems confused by your scrutiny.",
            },
        }
        
        emotion_reactions = reactions.get(player_emotion, {})
        
        if npc.is_threat and "is_threat" in emotion_reactions:
            return emotion_reactions["is_threat"]
        elif npc.suspicion > 0.5 and "high_suspicion" in emotion_reactions:
            return emotion_reactions["high_suspicion"]
        elif npc.trust > 0.6 and "high_trust" in emotion_reactions:
            return emotion_reactions["high_trust"]
        elif npc.trust < 0.4 and "low_trust" in emotion_reactions:
            return emotion_reactions["low_trust"]
        elif "low_suspicion" in emotion_reactions:
            return emotion_reactions["low_suspicion"]
        
        return ""

    # =========================================================================
    # SOCIAL PERCEPTION
    # =========================================================================

    def update_perception(self, action_type: str, outcome: str = None):
        """
        Update how the crew perceives the player based on visible actions.
        """
        trait_map = {
            "help": ("reliable", 0.1),
            "threaten": ("dangerous", 0.15),
            "lie": ("deceptive", 0.1),
            "confide": ("vulnerable", 0.1),
            "investigate": ("nosy", 0.05),
        }
        
        if action_type in trait_map:
            trait, delta = trait_map[action_type]
            current = self.perception.perceived_traits.get(trait, 0.0)
            self.perception.perceived_traits[trait] = min(1.0, current + delta)
        
        # Reputation based on outcome
        if outcome == "strong_hit":
            self.perception.reputation_score = min(1.0, self.perception.reputation_score + 0.05)
            self.perception.notable_actions.append(f"Succeeded at {action_type}")
        elif outcome == "miss":
            self.perception.reputation_score = max(0.0, self.perception.reputation_score - 0.05)
            self.perception.notable_actions.append(f"Failed at {action_type}")

    def get_perception_context(self) -> str:
        """
        Generate a context string for narrator injection.
        """
        lines = ["[CREW PERCEPTION]"]
        lines.append(f"Reputation: {self.perception.reputation_score:.0%}")
        
        if self.perception.perceived_traits:
            trait_strs = [f"{k}: {v:.0%}" for k, v in sorted(self.perception.perceived_traits.items(), key=lambda x: x[1], reverse=True)[:3]]
            lines.append(f"Seen as: {', '.join(trait_strs)}")
        
        if self.perception.notable_actions:
            lines.append(f"Recent: {self.perception.notable_actions[-1]}")
        
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {"crew": {k: v.to_dict() for k, v in self.crew.items()}}

    @classmethod
    def from_dict(cls, data: dict) -> "RelationshipWeb":
        web = cls(crew={})
        for k, v in data.get("crew", {}).items():
            web.crew[k] = CrewMember.from_dict(v)
        return web
