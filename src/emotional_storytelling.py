"""
Emotional Storytelling System - TLOU-Style Narrative Depth.
Implements bond tracking, quiet moments, and relationship arcs.

Designed to create emotionally resonant stories through:
- Character bond phases (Stranger → Family)
- Mandated quiet moments between intensity
- Environmental storytelling prompts
- Callback references to early moments
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import random


# ============================================================================
# Bond Phases
# ============================================================================

class BondPhase(Enum):
    """Phases of relationship between player and NPC."""
    STRANGER = "stranger"  # Just met, no trust
    ACQUAINTANCE = "acquaintance"  # Know each other, wary
    ALLY = "ally"  # Trust established, work together
    FRIEND = "friend"  # Care about each other
    FAMILY = "family"  # Would die for each other
    BROKEN = "broken"  # Trust destroyed


# Bond phase progression thresholds
BOND_THRESHOLDS = {
    BondPhase.STRANGER: 0,
    BondPhase.ACQUAINTANCE: 20,
    BondPhase.ALLY: 40,
    BondPhase.FRIEND: 60,
    BondPhase.FAMILY: 85,
}


@dataclass
class BondEvent:
    """An event that affects a bond."""
    description: str
    bond_change: int  # Positive or negative
    scene: int
    is_shared_trauma: bool = False  # Trauma bonds faster
    is_betrayal: bool = False  # Can break bonds


@dataclass
class CharacterBond:
    """Tracks the bond between player and an NPC."""
    npc_name: str
    phase: BondPhase = BondPhase.STRANGER
    bond_value: int = 0  # 0-100, affects phase transitions
    shared_moments: list[str] = field(default_factory=list)
    shared_traumas: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    first_met_scene: int = 0
    last_interaction_scene: int = 0
    
    def add_event(self, event: BondEvent) -> str | None:
        """
        Process a bond event, potentially changing the relationship.
        Returns phase change notification if one occurred.
        """
        old_phase = self.phase
        
        # Betrayal can break bonds
        if event.is_betrayal:
            self.conflicts.append(event.description)
            self.bond_value = max(0, self.bond_value - 30)
            if self.phase in [BondPhase.FRIEND, BondPhase.FAMILY]:
                self.phase = BondPhase.BROKEN
                return f"Bond with {self.npc_name} is BROKEN"
        
        # Shared trauma accelerates bonding
        if event.is_shared_trauma:
            self.shared_traumas.append(event.description)
            event.bond_change = int(event.bond_change * 1.5)
        
        # Update bond value
        self.bond_value = max(0, min(100, self.bond_value + event.bond_change))
        self.last_interaction_scene = event.scene
        
        if event.bond_change > 0:
            self.shared_moments.append(event.description)
        
        # Check for phase transition
        new_phase = self._calculate_phase()
        if new_phase != old_phase and new_phase != BondPhase.BROKEN:
            self.phase = new_phase
            return f"Bond with {self.npc_name} deepened to {new_phase.value.upper()}"
        
        return None
    
    def _calculate_phase(self) -> BondPhase:
        """Calculate current phase based on bond value."""
        if self.phase == BondPhase.BROKEN:
            return BondPhase.BROKEN
        
        for phase in reversed(list(BondPhase)):
            if phase in BOND_THRESHOLDS and self.bond_value >= BOND_THRESHOLDS[phase]:
                return phase
        return BondPhase.STRANGER
    
    def get_narrative_context(self) -> str:
        """Generate context for narrator about this relationship."""
        lines = [f"[BOND: {self.npc_name} - {self.phase.value.upper()}]"]
        
        if self.phase == BondPhase.STRANGER:
            lines.append("This is a new relationship. Trust must be earned.")
        elif self.phase == BondPhase.ACQUAINTANCE:
            lines.append("Cautious familiarity. Still testing each other.")
        elif self.phase == BondPhase.ALLY:
            lines.append("Reliable partnership. They have each other's back.")
        elif self.phase == BondPhase.FRIEND:
            lines.append("Genuine care. Comfortable silence. Shared jokes.")
        elif self.phase == BondPhase.FAMILY:
            lines.append("Unbreakable. Would sacrifice everything for each other.")
        elif self.phase == BondPhase.BROKEN:
            lines.append("Trust destroyed. Tension in every interaction.")
        
        # Add callback material
        if self.shared_moments:
            lines.append(f"Shared memory: \"{self.shared_moments[-1]}\"")
        if self.shared_traumas:
            lines.append(f"Survived together: \"{self.shared_traumas[-1]}\"")
        
        return "\n".join(lines)


# ============================================================================
# Quiet Moments
# ============================================================================

class QuietMomentType(Enum):
    """Types of quiet moments between action."""
    CAMPFIRE = "campfire"  # Rest and reflection
    DISCOVERY = "discovery"  # Finding something beautiful/meaningful
    CONVERSATION = "conversation"  # Character development talk
    MEMORY = "memory"  # Flashback or reminiscence
    NATURE = "nature"  # The giraffe scene equivalent
    HUMOR = "humor"  # Light moment to release tension
    GRIEF = "grief"  # Processing loss


QUIET_MOMENT_PROMPTS = {
    QuietMomentType.CAMPFIRE: [
        "They find a moment of safety. A fire. A shared meal. What do they talk about?",
        "The night is quiet. Stars visible. A rare moment without threat.",
        "Time to rest. Time to remember why they're fighting.",
    ],
    QuietMomentType.DISCOVERY: [
        "Something beautiful survives in this harsh world. What do they find?",
        "A view that makes them stop. Breathe. Remember wonder exists.",
        "An artifact from before—someone's treasured possession, left behind.",
    ],
    QuietMomentType.CONVERSATION: [
        "A question that's been waiting. Now there's time to ask it.",
        "Something needs to be said between them. The silence is heavy.",
        "They share something they've never told anyone.",
    ],
    QuietMomentType.MEMORY: [
        "Something triggers a memory. Before all this. When things were different.",
        "They find something that belonged to someone lost.",
        "A smell, a sound—suddenly they're somewhere else, somewhen else.",
    ],
    QuietMomentType.NATURE: [
        "Life, despite everything. Something beautiful and alive.",
        "The world doesn't care about their struggle. It's still beautiful.",
        "A moment of peace that feels almost wrong given everything.",
    ],
    QuietMomentType.HUMOR: [
        "Something absurd. A laugh that surprises them both.",
        "A joke—maybe inappropriate, but needed.",
        "They find themselves smiling. It's been a while.",
    ],
    QuietMomentType.GRIEF: [
        "The weight of what they've lost finally lands.",
        "There's nothing to say. They sit with the grief together.",
        "Tears they've been holding back. No one's watching now.",
    ],
}


@dataclass
class QuietMomentTracker:
    """
    Tracks when quiet moments should occur.
    Ensures breathing room between intensity.
    """
    scenes_since_quiet: int = 0
    scenes_since_action: int = 0
    tension_fatigue: float = 0.0  # Builds during high-intensity sequences
    last_quiet_type: QuietMomentType | None = None
    
    def record_scene(self, was_intense: bool) -> None:
        """Record a scene and update tracking."""
        if was_intense:
            self.scenes_since_quiet += 1
            self.scenes_since_action = 0
            self.tension_fatigue = min(1.0, self.tension_fatigue + 0.2)
        else:
            self.scenes_since_action += 1
            self.tension_fatigue = max(0.0, self.tension_fatigue - 0.1)
    
    def needs_quiet_moment(self) -> bool:
        """Check if a quiet moment is needed."""
        # After 3+ intense scenes, mandate quiet
        if self.scenes_since_quiet >= 3:
            return True
        # High tension fatigue
        if self.tension_fatigue >= 0.8:
            return True
        return False
    
    def get_quiet_moment(self, context: str = "") -> dict:
        """
        Generate a quiet moment suggestion.
        Returns type and prompt for the narrator.
        """
        # Select type based on context
        if "death" in context.lower() or "loss" in context.lower():
            moment_type = QuietMomentType.GRIEF
        elif "won" in context.lower() or "victory" in context.lower():
            moment_type = QuietMomentType.HUMOR
        else:
            # Avoid repeating last type
            available = [t for t in QuietMomentType if t != self.last_quiet_type]
            moment_type = random.choice(available)
        
        self.last_quiet_type = moment_type
        self.scenes_since_quiet = 0
        self.tension_fatigue = 0.0
        
        prompts = QUIET_MOMENT_PROMPTS[moment_type]
        
        return {
            "type": moment_type.value,
            "prompt": random.choice(prompts),
            "narrator_instruction": "Write a QUIET scene. No action. Focus on character, emotion, small details.",
        }


# ============================================================================
# Bond Manager
# ============================================================================

class BondManager:
    """Manages all character bonds and quiet moments."""
    
    def __init__(self):
        self.bonds: dict[str, CharacterBond] = {}
        self.quiet_tracker = QuietMomentTracker()
        self.callbacks: list[dict] = []  # Moments worth referencing later
    
    def get_or_create_bond(self, npc_name: str, scene: int = 0) -> CharacterBond:
        """Get existing bond or create new one."""
        name_lower = npc_name.lower()
        if name_lower not in self.bonds:
            self.bonds[name_lower] = CharacterBond(
                npc_name=npc_name,
                first_met_scene=scene,
            )
        return self.bonds[name_lower]
    
    def record_bond_event(
        self,
        npc_name: str,
        description: str,
        bond_change: int,
        scene: int,
        is_shared_trauma: bool = False,
        is_betrayal: bool = False,
    ) -> str | None:
        """Record an event affecting a bond."""
        bond = self.get_or_create_bond(npc_name, scene)
        
        event = BondEvent(
            description=description,
            bond_change=bond_change,
            scene=scene,
            is_shared_trauma=is_shared_trauma,
            is_betrayal=is_betrayal,
        )
        
        result = bond.add_event(event)
        
        # Store significant moments for callbacks
        if is_shared_trauma or bond.phase in [BondPhase.FRIEND, BondPhase.FAMILY]:
            self.callbacks.append({
                "npc": npc_name,
                "moment": description,
                "scene": scene,
                "phase": bond.phase.value,
            })
        
        return result
    
    def get_deepest_bond(self) -> CharacterBond | None:
        """Get the character with the strongest bond."""
        if not self.bonds:
            return None
        return max(self.bonds.values(), key=lambda b: b.bond_value)
    
    def get_callback_for_climax(self) -> str | None:
        """Get an early moment to reference at a climactic point."""
        if not self.callbacks:
            return None
        # Prefer early callbacks for maximum impact
        early_callbacks = sorted(self.callbacks, key=lambda c: c["scene"])
        if early_callbacks:
            cb = early_callbacks[0]
            return f"Remember when: \"{cb['moment']}\" (with {cb['npc']}, scene {cb['scene']})"
        return None
    
    def get_all_bonds_context(self) -> str:
        """Generate context for all significant bonds."""
        if not self.bonds:
            return ""
        
        significant = [b for b in self.bonds.values() if b.phase != BondPhase.STRANGER]
        if not significant:
            return ""
        
        lines = ["[CHARACTER BONDS]"]
        for bond in sorted(significant, key=lambda b: b.bond_value, reverse=True):
            lines.append(bond.get_narrative_context())
        
        return "\n\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "bonds": {
                name: {
                    "npc_name": bond.npc_name,
                    "phase": bond.phase.value,
                    "bond_value": bond.bond_value,
                    "shared_moments": bond.shared_moments,
                    "shared_traumas": bond.shared_traumas,
                    "conflicts": bond.conflicts,
                    "first_met_scene": bond.first_met_scene,
                    "last_interaction_scene": bond.last_interaction_scene,
                }
                for name, bond in self.bonds.items()
            },
            "quiet_tracker": {
                "scenes_since_quiet": self.quiet_tracker.scenes_since_quiet,
                "scenes_since_action": self.quiet_tracker.scenes_since_action,
                "tension_fatigue": self.quiet_tracker.tension_fatigue,
            },
            "callbacks": self.callbacks,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BondManager":
        manager = cls()
        
        for name, bond_data in data.get("bonds", {}).items():
            bond = CharacterBond(
                npc_name=bond_data.get("npc_name", name),
                phase=BondPhase(bond_data.get("phase", "stranger")),
                bond_value=bond_data.get("bond_value", 0),
                shared_moments=bond_data.get("shared_moments", []),
                shared_traumas=bond_data.get("shared_traumas", []),
                conflicts=bond_data.get("conflicts", []),
                first_met_scene=bond_data.get("first_met_scene", 0),
                last_interaction_scene=bond_data.get("last_interaction_scene", 0),
            )
            manager.bonds[name] = bond
        
        qt_data = data.get("quiet_tracker", {})
        manager.quiet_tracker.scenes_since_quiet = qt_data.get("scenes_since_quiet", 0)
        manager.quiet_tracker.scenes_since_action = qt_data.get("scenes_since_action", 0)
        manager.quiet_tracker.tension_fatigue = qt_data.get("tension_fatigue", 0.0)
        
        manager.callbacks = data.get("callbacks", [])
        
        return manager


# ============================================================================
# Convenience Functions
# ============================================================================

def create_bond_manager() -> BondManager:
    """Create a new bond manager."""
    return BondManager()


def evaluate_bond_context(
    npc_name: str,
    bond_value: int,
    shared_trauma: bool = False,
) -> str:
    """Quick bond context generation."""
    manager = BondManager()
    bond = manager.get_or_create_bond(npc_name, 0)
    bond.bond_value = bond_value
    bond.phase = bond._calculate_phase()
    
    if shared_trauma:
        bond.shared_traumas.append("They survived something together")
    
    return bond.get_narrative_context()
