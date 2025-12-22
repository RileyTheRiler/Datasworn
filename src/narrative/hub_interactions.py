"""
Hub Proximity Interaction System.

Manages walk-and-talk sequences, proximity-based conversations,
eavesdrop barks, and graceful interaction aborts.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import random

from src.barks import BarkManager, BarkType


class InteractionLeg(Enum):
    """Stages of a walk-and-talk interaction."""
    APPROACH = "approach"
    WALK = "walk"
    SIT = "sit"
    WORK = "work"
    DEPART = "depart"


@dataclass
class ProximityTrigger:
    """Defines when a proximity interaction should trigger."""
    npc_id: str
    trigger_distance: float = 5.0  # Arbitrary units
    required_location: Optional[str] = None
    required_time_range: Optional[tuple[int, int]] = None  # (start_hour, end_hour)
    cooldown_turns: int = 10
    last_triggered: int = -999


@dataclass
class WalkAndTalkSequence:
    """A multi-part proximity conversation."""
    sequence_id: str
    npc_id: str
    current_leg: InteractionLeg = InteractionLeg.APPROACH
    dialogue_parts: dict[InteractionLeg, list[str]] = field(default_factory=dict)
    destination_spot: Optional[str] = None
    completed: bool = False
    aborted: bool = False
    
    def get_current_dialogue(self) -> Optional[str]:
        """Get dialogue for current leg."""
        leg_dialogue = self.dialogue_parts.get(self.current_leg, [])
        if leg_dialogue:
            return random.choice(leg_dialogue)
        return None
    
    def advance_leg(self) -> bool:
        """Move to next leg of sequence. Returns True if sequence continues."""
        leg_order = [
            InteractionLeg.APPROACH,
            InteractionLeg.WALK,
            InteractionLeg.SIT,
            InteractionLeg.WORK,
            InteractionLeg.DEPART
        ]
        
        try:
            current_idx = leg_order.index(self.current_leg)
            if current_idx < len(leg_order) - 1:
                self.current_leg = leg_order[current_idx + 1]
                return True
            else:
                self.completed = True
                return False
        except ValueError:
            return False
    
    def abort(self) -> None:
        """Abort the interaction gracefully."""
        self.aborted = True


class HubInteractionManager:
    """Manages proximity-based camp interactions."""
    
    def __init__(self):
        self.active_sequences: dict[str, WalkAndTalkSequence] = {}
        self.proximity_triggers: dict[str, ProximityTrigger] = {}
        self.bark_manager = BarkManager()
        self.current_turn = 0
        
        # Initialize triggers for all NPCs
        self._initialize_triggers()
    
    def _initialize_triggers(self) -> None:
        """Set up proximity triggers for all NPCs."""
        npcs = ["yuki", "torres", "kai", "okonkwo", "vasquez", "ember"]
        for npc in npcs:
            self.proximity_triggers[npc] = ProximityTrigger(
                npc_id=npc,
                trigger_distance=5.0,
                cooldown_turns=10
            )
    
    def check_proximity(
        self,
        player_location: str,
        npc_locations: dict[str, str],
        current_hour: int
    ) -> Optional[str]:
        """
        Check if player proximity should trigger an interaction.
        Returns NPC ID if interaction should start.
        """
        for npc_id, npc_location in npc_locations.items():
            if npc_location != player_location:
                continue
            
            trigger = self.proximity_triggers.get(npc_id)
            if not trigger:
                continue
            
            # Check cooldown
            if self.current_turn - trigger.last_triggered < trigger.cooldown_turns:
                continue
            
            # Check time range if specified
            if trigger.required_time_range:
                start, end = trigger.required_time_range
                if not (start <= current_hour < end):
                    continue
            
            # Check if already in sequence with this NPC
            if npc_id in self.active_sequences:
                continue
            
            # Trigger!
            trigger.last_triggered = self.current_turn
            return npc_id
        
        return None
    
    def initiate_walk_and_talk(
        self,
        npc_id: str,
        context: str = "casual",
        destination_spot: Optional[str] = None
    ) -> WalkAndTalkSequence:
        """Start a walk-and-talk sequence with an NPC."""
        
        # Create dialogue based on NPC and context
        dialogue_parts = self._generate_sequence_dialogue(npc_id, context)
        
        sequence = WalkAndTalkSequence(
            sequence_id=f"{npc_id}_{self.current_turn}",
            npc_id=npc_id,
            dialogue_parts=dialogue_parts,
            destination_spot=destination_spot
        )
        
        self.active_sequences[npc_id] = sequence
        return sequence
    
    def _generate_sequence_dialogue(
        self,
        npc_id: str,
        context: str
    ) -> dict[InteractionLeg, list[str]]:
        """Generate dialogue for each leg of the sequence."""
        
        # NPC-specific dialogue templates
        templates = {
            "yuki": {
                InteractionLeg.APPROACH: [
                    "*looks up* You need something?",
                    "*pauses patrol* What is it?",
                ],
                InteractionLeg.WALK: [
                    "*walks alongside* Keep your eyes open. Always.",
                    "*gestures to perimeter* See that sensor? I check it every hour.",
                ],
                InteractionLeg.SIT: [
                    "*sits, still alert* Even here, I'm watching.",
                    "*relaxes slightly* This is... nice. Rare.",
                ],
                InteractionLeg.DEPART: [
                    "*stands* Back to work.",
                    "*nods* Thanks for the company.",
                ],
            },
            "torres": {
                InteractionLeg.APPROACH: [
                    "*warm smile* Hey! Walk with me?",
                    "*gestures* I was just heading over there. Join me?",
                ],
                InteractionLeg.WALK: [
                    "*points at sky* See that constellation? Used to navigate by it.",
                    "*thoughtful* You know, I've been thinking about our next move...",
                ],
                InteractionLeg.SIT: [
                    "*settles in* This is good. Just... being.",
                    "*leans back* Sometimes you need to stop moving, you know?",
                ],
                InteractionLeg.WORK: [
                    "*while working* Hand me that tool? Thanks.",
                    "*focused* This reminds me of working on my first ship...",
                ],
                InteractionLeg.DEPART: [
                    "*grins* We should do this more often.",
                    "*friendly wave* Catch you later.",
                ],
            },
            "kai": {
                InteractionLeg.APPROACH: [
                    "*shy smile* Oh, hi. Want to see something?",
                    "*looks up from work* I could use a break.",
                ],
                InteractionLeg.WALK: [
                    "*points* I planted these. They're growing.",
                    "*quiet* It's peaceful when you walk slowly.",
                ],
                InteractionLeg.WORK: [
                    "*while tinkering* This part is tricky. See how it connects?",
                    "*focused* I like fixing things. Making them whole again.",
                ],
                InteractionLeg.DEPART: [
                    "*grateful* Thank you for spending time with me.",
                    "*small wave* See you soon?",
                ],
            },
        }
        
        # Get NPC templates or use generic
        npc_templates = templates.get(npc_id, {
            InteractionLeg.APPROACH: ["*acknowledges you*"],
            InteractionLeg.WALK: ["*walks with you*"],
            InteractionLeg.DEPART: ["*nods goodbye*"],
        })
        
        return npc_templates
    
    def advance_sequence(self, npc_id: str) -> Optional[str]:
        """
        Advance an active sequence to next leg.
        Returns dialogue for new leg, or None if sequence ended.
        """
        sequence = self.active_sequences.get(npc_id)
        if not sequence or sequence.completed or sequence.aborted:
            return None
        
        continues = sequence.advance_leg()
        if continues:
            return sequence.get_current_dialogue()
        else:
            # Sequence complete
            del self.active_sequences[npc_id]
            return None
    
    def abort_interaction(self, npc_id: str, reason: str = "player_left") -> Optional[str]:
        """
        Gracefully abort an interaction.
        Returns abort dialogue.
        """
        sequence = self.active_sequences.get(npc_id)
        if not sequence:
            return None
        
        sequence.abort()
        
        # Generate abort dialogue
        abort_lines = {
            "yuki": ["*watches you leave* ...Fine.", "*shrugs* Your loss."],
            "torres": ["*calls after you* Hey, where you going?", "*disappointed* Oh. Okay."],
            "kai": ["*quietly* Oh... okay.", "*looks down*"],
            "okonkwo": ["*understanding nod*", "*peaceful* Another time."],
            "vasquez": ["*laughs* Can't handle my company?", "*shrugs* Suit yourself."],
            "ember": ["*confused* Did I say something wrong?", "*sad* Oh..."],
        }
        
        lines = abort_lines.get(npc_id, ["*watches you leave*"])
        abort_dialogue = random.choice(lines)
        
        # Clean up
        del self.active_sequences[npc_id]
        
        return abort_dialogue
    
    def generate_eavesdrop_bark(
        self,
        active_npc: str,
        eavesdropper_npc: str,
        acoustic_group: int
    ) -> Optional[str]:
        """
        Generate a bark from an NPC overhearing a conversation.
        Only works if NPCs are in same acoustic group.
        """
        
        # Check if there's an active sequence
        if active_npc not in self.active_sequences:
            return None
        
        # Generate contextual eavesdrop bark
        eavesdrop_templates = {
            "yuki": ["*from nearby* Keep it down.", "*glances over*"],
            "torres": ["*chuckles from across the fire*", "*listens in with interest*"],
            "kai": ["*pretends not to listen but clearly is*", "*shy smile from workbench*"],
            "okonkwo": ["*observes quietly*", "*knowing look*"],
            "vasquez": ["*shouts over* What's so interesting?", "*laughs* I heard that!"],
            "ember": ["*peeks around corner*", "*curious*"],
        }
        
        lines = eavesdrop_templates.get(eavesdropper_npc, ["*listens*"])
        return random.choice(lines)
    
    def update_turn(self) -> None:
        """Advance the turn counter."""
        self.current_turn += 1
        self.bark_manager.update_cooldowns()
    
    def get_active_interactions(self) -> list[str]:
        """Get list of NPCs currently in active interactions."""
        return list(self.active_sequences.keys())
    
    def to_dict(self) -> dict:
        """Serialize state."""
        return {
            "current_turn": self.current_turn,
            "active_sequences": {
                npc_id: {
                    "sequence_id": seq.sequence_id,
                    "current_leg": seq.current_leg.value,
                    "completed": seq.completed,
                    "aborted": seq.aborted,
                }
                for npc_id, seq in self.active_sequences.items()
            },
            "proximity_triggers": {
                npc_id: {
                    "last_triggered": trigger.last_triggered,
                }
                for npc_id, trigger in self.proximity_triggers.items()
            }
        }
