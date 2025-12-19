"""
Vow-Driven Complications System

Generates narrative complications and obstacles directly related to
the player's active vows. Makes vows feel like living parts of the
story rather than just progress tracks.

Based on vow rank and progress phase, injects appropriate challenges.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import random


class VowRank(Enum):
    """Vow difficulty ranks."""
    TROUBLESOME = "troublesome"
    DANGEROUS = "dangerous"
    FORMIDABLE = "formidable"
    EXTREME = "extreme"
    EPIC = "epic"


class VowPhase(Enum):
    """Narrative phase of a vow based on progress."""
    ESTABLISHING = "establishing"    # 0-10% - Introduction
    DEVELOPING = "developing"        # 10-40% - Building momentum
    ESCALATING = "escalating"        # 40-70% - Rising stakes
    CLIMAX = "climax"               # 70-90% - Crisis point
    RESOLUTION = "resolution"        # 90-100% - Final push


class ComplicationType(Enum):
    """Types of vow complications."""
    OBSTACLE = "obstacle"           # Something blocking progress
    COST = "cost"                   # Something must be sacrificed
    TWIST = "twist"                 # Unexpected revelation
    RIVAL = "rival"                 # Someone working against you
    TIME_PRESSURE = "time_pressure" # Urgency increases
    MORAL_DILEMMA = "moral_dilemma" # Ethical conflict
    SETBACK = "setback"             # Progress reversed
    TEMPTATION = "temptation"       # Easy way out with consequences


@dataclass
class VowComplication:
    """A generated complication for a vow."""
    complication_type: ComplicationType
    description: str
    vow_name: str
    severity: float  # 0-1, affects narrative weight
    suggested_moves: List[str] = field(default_factory=list)
    requires_choice: bool = False
    choice_options: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "complication_type": self.complication_type.value,
            "description": self.description,
            "vow_name": self.vow_name,
            "severity": self.severity,
            "suggested_moves": self.suggested_moves,
            "requires_choice": self.requires_choice,
            "choice_options": self.choice_options,
        }


@dataclass
class TrackedVow:
    """A vow being tracked for complications."""
    name: str
    rank: VowRank
    progress: float  # 0.0 to 1.0
    created_scene: int = 0
    last_complication_scene: int = 0
    complications_generated: int = 0
    theme_keywords: List[str] = field(default_factory=list)

    @property
    def phase(self) -> VowPhase:
        """Determine current narrative phase from progress."""
        if self.progress < 0.1:
            return VowPhase.ESTABLISHING
        elif self.progress < 0.4:
            return VowPhase.DEVELOPING
        elif self.progress < 0.7:
            return VowPhase.ESCALATING
        elif self.progress < 0.9:
            return VowPhase.CLIMAX
        else:
            return VowPhase.RESOLUTION

    @property
    def complication_frequency(self) -> int:
        """How many scenes between complications for this rank."""
        frequencies = {
            VowRank.TROUBLESOME: 5,
            VowRank.DANGEROUS: 4,
            VowRank.FORMIDABLE: 3,
            VowRank.EXTREME: 2,
            VowRank.EPIC: 2,
        }
        return frequencies.get(self.rank, 3)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "rank": self.rank.value,
            "progress": self.progress,
            "created_scene": self.created_scene,
            "last_complication_scene": self.last_complication_scene,
            "complications_generated": self.complications_generated,
            "theme_keywords": self.theme_keywords,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrackedVow":
        return cls(
            name=data["name"],
            rank=VowRank(data["rank"]),
            progress=data.get("progress", 0.0),
            created_scene=data.get("created_scene", 0),
            last_complication_scene=data.get("last_complication_scene", 0),
            complications_generated=data.get("complications_generated", 0),
            theme_keywords=data.get("theme_keywords", []),
        )


# =============================================================================
# COMPLICATION TEMPLATES
# =============================================================================

COMPLICATION_TEMPLATES: Dict[VowPhase, Dict[ComplicationType, List[str]]] = {
    VowPhase.ESTABLISHING: {
        ComplicationType.OBSTACLE: [
            "You realize {vow} is more complex than anticipated",
            "An unexpected barrier appears on the path to {vow}",
            "The first step toward {vow} reveals hidden difficulties",
        ],
        ComplicationType.RIVAL: [
            "Someone else is pursuing the same goal: {vow}",
            "A competitor emerges with their own stake in {vow}",
        ],
        ComplicationType.TWIST: [
            "Your understanding of {vow} was incomplete",
            "A new detail changes how you approach {vow}",
        ],
    },
    VowPhase.DEVELOPING: {
        ComplicationType.OBSTACLE: [
            "Progress toward {vow} hits an unexpected setback",
            "A necessary resource for {vow} proves hard to obtain",
            "The path to {vow} leads through dangerous territory",
        ],
        ComplicationType.COST: [
            "Pursuing {vow} strains a relationship",
            "Progress toward {vow} demands sacrifice",
            "Something precious must be risked for {vow}",
        ],
        ComplicationType.RIVAL: [
            "Your rival in {vow} gains an advantage",
            "Opposition to {vow} becomes organized",
        ],
        ComplicationType.MORAL_DILEMMA: [
            "The right thing and {vow} seem to conflict",
            "An ally asks you to delay {vow} for their need",
        ],
    },
    VowPhase.ESCALATING: {
        ComplicationType.OBSTACLE: [
            "A major barrier threatens to halt {vow}",
            "Forces aligned against {vow} escalate their efforts",
        ],
        ComplicationType.SETBACK: [
            "Hard-won progress toward {vow} is undone",
            "A trusted element of {vow} proves unreliable",
        ],
        ComplicationType.TIME_PRESSURE: [
            "The window for {vow} is closing",
            "External events add urgency to {vow}",
            "Delay in {vow} will have consequences",
        ],
        ComplicationType.TWIST: [
            "A revelation transforms your understanding of {vow}",
            "The true nature of {vow} becomes clear",
            "What {vow} requires is not what you expected",
        ],
        ComplicationType.TEMPTATION: [
            "An easy path to {vow} appears—with strings attached",
            "Abandoning principles could advance {vow}",
        ],
    },
    VowPhase.CLIMAX: {
        ComplicationType.OBSTACLE: [
            "The final barrier to {vow} is formidable",
            "Everything opposing {vow} converges at once",
        ],
        ComplicationType.COST: [
            "Completing {vow} will demand the ultimate price",
            "The cost of {vow} becomes painfully clear",
        ],
        ComplicationType.MORAL_DILEMMA: [
            "Fulfilling {vow} requires an impossible choice",
            "The ethics of {vow} are thrown into question",
        ],
        ComplicationType.TIME_PRESSURE: [
            "This is the last chance for {vow}",
            "Now or never for {vow}",
        ],
    },
    VowPhase.RESOLUTION: {
        ComplicationType.TWIST: [
            "Even at the end, {vow} has one more surprise",
            "Victory in {vow} feels different than expected",
        ],
        ComplicationType.COST: [
            "The final step of {vow} extracts its toll",
        ],
    },
}

# Phase-appropriate suggested moves
PHASE_MOVES: Dict[VowPhase, List[str]] = {
    VowPhase.ESTABLISHING: ["Gather Information", "Make a Connection", "Secure an Advantage"],
    VowPhase.DEVELOPING: ["Face Danger", "Gain Ground", "React Under Fire"],
    VowPhase.ESCALATING: ["Face Danger", "Compel", "Clash", "Battle"],
    VowPhase.CLIMAX: ["Battle", "Fulfill Your Vow", "Face Death"],
    VowPhase.RESOLUTION: ["Fulfill Your Vow", "Forge a Bond", "Write Your Epilogue"],
}

# Obstacle content by theme
OBSTACLES = [
    "A locked door stands before you", "The path is blocked by debris",
    "Guards patrol the only route", "The system is locked down",
    "A storm makes progress impossible", "The bridge is destroyed",
    "Your contact has gone silent", "The information is encrypted",
]

COSTS = [
    "time you cannot afford to lose", "a favor you'll have to repay",
    "supplies that cannot be replaced", "trust that was hard-earned",
    "a connection that may not survive", "your peace of mind",
]

TWISTS = [
    "it was a lie all along", "someone you trusted is involved",
    "the truth is darker than you knew", "you were the backup plan",
    "they knew you were coming", "it's personal now",
]

RIVALS = [
    "a former ally", "a corporate operative", "a fellow traveler",
    "someone from your past", "an opportunistic scavenger",
]


class VowComplicationEngine:
    """
    Engine for generating vow-driven complications.

    Features:
    - Phase-aware complication generation
    - Rank-based difficulty scaling
    - Cooldown management
    - Narrator injection
    """

    def __init__(self):
        self._vows: Dict[str, TrackedVow] = {}
        self._current_scene: int = 0
        self._pending_complications: List[VowComplication] = []

    def add_vow(
        self,
        name: str,
        rank: VowRank,
        progress: float = 0.0,
        theme_keywords: List[str] = None
    ):
        """Add a vow to track."""
        self._vows[name.lower()] = TrackedVow(
            name=name,
            rank=rank,
            progress=progress,
            created_scene=self._current_scene,
            theme_keywords=theme_keywords or [],
        )

    def update_vow_progress(self, name: str, new_progress: float):
        """Update a vow's progress."""
        key = name.lower()
        if key in self._vows:
            self._vows[key].progress = max(0.0, min(1.0, new_progress))

    def remove_vow(self, name: str):
        """Remove a completed or forsaken vow."""
        key = name.lower()
        if key in self._vows:
            del self._vows[key]

    def set_scene(self, scene_number: int):
        """Set current scene number."""
        self._current_scene = scene_number

    def check_for_complications(self) -> List[TrackedVow]:
        """Check which vows are due for complications."""
        due = []
        for vow in self._vows.values():
            scenes_since = self._current_scene - vow.last_complication_scene

            # Higher chance as more scenes pass
            threshold = vow.complication_frequency

            # Climax phase gets more frequent complications
            if vow.phase == VowPhase.CLIMAX:
                threshold = max(1, threshold - 1)

            if scenes_since >= threshold:
                due.append(vow)

        return due

    def generate_complication(
        self,
        vow: TrackedVow,
        preferred_type: ComplicationType = None
    ) -> VowComplication:
        """
        Generate a complication for a vow.

        Args:
            vow: The vow to complicate
            preferred_type: Optional specific complication type

        Returns:
            Generated complication
        """
        phase = vow.phase

        # Get available types for this phase
        phase_templates = COMPLICATION_TEMPLATES.get(phase, {})
        available_types = list(phase_templates.keys())

        if not available_types:
            # Fallback to OBSTACLE
            available_types = [ComplicationType.OBSTACLE]

        # Choose type
        if preferred_type and preferred_type in available_types:
            comp_type = preferred_type
        else:
            # Weight by phase appropriateness
            if phase == VowPhase.CLIMAX:
                # Favor dramatic types
                weights = [3 if t in [ComplicationType.COST, ComplicationType.MORAL_DILEMMA]
                          else 1 for t in available_types]
            elif phase == VowPhase.ESCALATING:
                # Favor time pressure and twists
                weights = [3 if t in [ComplicationType.TIME_PRESSURE, ComplicationType.TWIST]
                          else 1 for t in available_types]
            else:
                weights = [1] * len(available_types)

            comp_type = random.choices(available_types, weights=weights, k=1)[0]

        # Get template
        templates = phase_templates.get(comp_type, COMPLICATION_TEMPLATES[VowPhase.DEVELOPING][ComplicationType.OBSTACLE])
        template = random.choice(templates)

        # Fill in vow name
        description = template.format(vow=vow.name)

        # Determine severity based on phase and rank
        base_severity = {
            VowPhase.ESTABLISHING: 0.3,
            VowPhase.DEVELOPING: 0.5,
            VowPhase.ESCALATING: 0.7,
            VowPhase.CLIMAX: 0.9,
            VowPhase.RESOLUTION: 0.6,
        }[phase]

        rank_modifier = {
            VowRank.TROUBLESOME: -0.1,
            VowRank.DANGEROUS: 0.0,
            VowRank.FORMIDABLE: 0.1,
            VowRank.EXTREME: 0.15,
            VowRank.EPIC: 0.2,
        }[vow.rank]

        severity = max(0.1, min(1.0, base_severity + rank_modifier))

        # Get suggested moves
        suggested_moves = PHASE_MOVES.get(phase, ["Face Danger"])

        # Mark vow as having received complication
        vow.last_complication_scene = self._current_scene
        vow.complications_generated += 1

        # Check if this requires a choice
        requires_choice = comp_type in [ComplicationType.MORAL_DILEMMA, ComplicationType.TEMPTATION]
        choice_options = []
        if requires_choice:
            choice_options = [
                "Accept the cost and continue",
                "Find another way",
                "Delay to gather resources",
            ]

        return VowComplication(
            complication_type=comp_type,
            description=description,
            vow_name=vow.name,
            severity=severity,
            suggested_moves=suggested_moves[:3],
            requires_choice=requires_choice,
            choice_options=choice_options,
        )

    def get_all_pending_complications(self) -> List[VowComplication]:
        """Get complications for all due vows."""
        due_vows = self.check_for_complications()
        complications = []

        for vow in due_vows:
            # Random chance to actually trigger (to add unpredictability)
            if random.random() < 0.7:  # 70% chance
                complication = self.generate_complication(vow)
                complications.append(complication)

        self._pending_complications = complications
        return complications

    def get_narrator_injection(
        self,
        complications: List[VowComplication] = None
    ) -> str:
        """
        Generate narrator injection for complications.

        Returns text to add to narrator prompt.
        """
        if complications is None:
            complications = self._pending_complications

        if not complications:
            return ""

        lines = ["[VOW COMPLICATIONS - WEAVE INTO NARRATIVE]"]

        for comp in complications[:2]:  # Limit to 2 per scene
            lines.append(f"- {comp.vow_name}: {comp.description}")
            lines.append(f"  (Type: {comp.complication_type.value}, Severity: {comp.severity:.1f})")

            if comp.suggested_moves:
                lines.append(f"  Suggested moves: {', '.join(comp.suggested_moves)}")

        lines.append("[END VOW COMPLICATIONS - incorporate naturally]")

        return "\n".join(lines)

    def get_vow_context(self, vow_name: str) -> str:
        """Get narrative context for a specific vow."""
        key = vow_name.lower()
        vow = self._vows.get(key)

        if not vow:
            return ""

        phase_desc = {
            VowPhase.ESTABLISHING: "just beginning",
            VowPhase.DEVELOPING: "building momentum",
            VowPhase.ESCALATING: "reaching critical mass",
            VowPhase.CLIMAX: "at its crisis point",
            VowPhase.RESOLUTION: "nearing completion",
        }

        return f"[{vow.name}] ({vow.rank.value}, {int(vow.progress*100)}% complete, {phase_desc[vow.phase]})"

    def get_all_vows_context(self) -> str:
        """Get narrative context for all active vows."""
        if not self._vows:
            return ""

        lines = ["ACTIVE VOWS:"]
        for vow in self._vows.values():
            lines.append(self.get_vow_context(vow.name))

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize engine state."""
        return {
            "vows": {k: v.to_dict() for k, v in self._vows.items()},
            "current_scene": self._current_scene,
            "pending_complications": [c.to_dict() for c in self._pending_complications],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VowComplicationEngine":
        """Deserialize engine state."""
        engine = cls()
        engine._vows = {
            k: TrackedVow.from_dict(v)
            for k, v in data.get("vows", {}).items()
        }
        engine._current_scene = data.get("current_scene", 0)
        return engine


# =============================================================================
# INTEGRATION HELPERS
# =============================================================================

def sync_vows_from_game_state(
    engine: VowComplicationEngine,
    vow_states: List[Dict[str, Any]]
) -> None:
    """
    Sync vow tracking with game state vows.

    Args:
        engine: The complication engine
        vow_states: List of vow dicts from game state
    """
    # Map rank strings to enum
    rank_map = {
        "troublesome": VowRank.TROUBLESOME,
        "dangerous": VowRank.DANGEROUS,
        "formidable": VowRank.FORMIDABLE,
        "extreme": VowRank.EXTREME,
        "epic": VowRank.EPIC,
    }

    # Track existing vow names
    current_names = set(engine._vows.keys())
    state_names = set()

    for vow_data in vow_states:
        name = vow_data.get("name", "Unknown Vow")
        key = name.lower()
        state_names.add(key)

        rank_str = vow_data.get("rank", "dangerous")
        rank = rank_map.get(rank_str, VowRank.DANGEROUS)

        # Calculate progress from ticks (each rank has different scale)
        ticks = vow_data.get("ticks", 0)
        max_ticks = {
            "troublesome": 12,
            "dangerous": 20,
            "formidable": 30,
            "extreme": 36,
            "epic": 40,
        }.get(rank_str, 40)
        progress = min(1.0, ticks / max_ticks)

        if key in engine._vows:
            # Update existing
            engine._vows[key].progress = progress
            engine._vows[key].rank = rank
        else:
            # Add new
            engine.add_vow(name, rank, progress)

    # Remove vows no longer in state (completed/forsaken)
    for name in current_names - state_names:
        engine.remove_vow(name)


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("VOW COMPLICATIONS ENGINE TEST")
    print("=" * 60)

    engine = VowComplicationEngine()

    # Add test vows
    engine.add_vow("Find my father's killer", VowRank.EXTREME, progress=0.55)
    engine.add_vow("Deliver the cargo", VowRank.DANGEROUS, progress=0.25)
    engine.add_vow("Master the ancient texts", VowRank.EPIC, progress=0.8)

    # Simulate several scenes
    for scene in range(1, 8):
        engine.set_scene(scene)
        print(f"\n--- Scene {scene} ---")

        # Check for complications
        complications = engine.get_all_pending_complications()

        if complications:
            print("Complications triggered:")
            for comp in complications:
                print(f"  • [{comp.vow_name}] {comp.description}")
                print(f"    Type: {comp.complication_type.value}, Severity: {comp.severity:.2f}")
                if comp.suggested_moves:
                    print(f"    Moves: {', '.join(comp.suggested_moves)}")
        else:
            print("No complications this scene.")

    # Test narrator injection
    print("\n--- Narrator Injection ---")
    engine.set_scene(10)
    complications = engine.get_all_pending_complications()
    injection = engine.get_narrator_injection(complications)
    print(injection)

    # Test vow context
    print("\n--- Vow Context ---")
    print(engine.get_all_vows_context())
