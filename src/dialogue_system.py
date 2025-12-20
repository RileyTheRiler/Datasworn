"""
Dialogue System

Branching conversation system with skill checks, relationship tracking,
and disposition-gated options.

Creates more structured and meaningful NPC interactions.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from enum import Enum
from src.psych_profile import EmotionalState


class Disposition(Enum):
    """NPC disposition toward the player."""
    HOSTILE = "hostile"
    SUSPICIOUS = "suspicious"
    NEUTRAL = "neutral"
    FRIENDLY = "friendly"
    LOYAL = "loyal"


class DialogueOutcome(Enum):
    """Outcomes of dialogue choices."""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILURE = "failure"
    SPECIAL = "special"


@dataclass
class DialogueOption:
    """A single dialogue choice."""
    id: str
    text: str
    skill_check: Optional[str] = None  # e.g., "heart", "shadow"
    difficulty: int = 0  # Add modifier for skill check
    required_disposition: Optional[Disposition] = None
    required_reputation: Optional[int] = None
    required_item: Optional[str] = None
    changes_disposition: int = 0  # -2 to +2
    leads_to: Optional[str] = None  # ID of next node
    ends_dialogue: bool = False
    effects: List[str] = field(default_factory=list)
    hidden: bool = False
    
    # Emotional Gating
    required_emotion: Optional[List[EmotionalState]] = None  # Must match one of these
    restricted_emotion: Optional[List[EmotionalState]] = None  # Cannot match any of these

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "skill_check": self.skill_check,
            "difficulty": self.difficulty,
            "required_disposition": self.required_disposition.value if self.required_disposition else None,
            "required_reputation": self.required_reputation,
            "required_item": self.required_item,
            "changes_disposition": self.changes_disposition,
            "leads_to": self.leads_to,
            "ends_dialogue": self.ends_dialogue,
            "effects": self.effects,
            "hidden": self.hidden,
        }


@dataclass
class DialogueNode:
    """A node in a dialogue tree."""
    id: str
    speaker: str
    text: str
    options: List[DialogueOption] = field(default_factory=list)
    is_entry: bool = False
    on_enter_effects: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "speaker": self.speaker,
            "text": self.text,
            "options": [o.to_dict() for o in self.options],
            "is_entry": self.is_entry,
            "on_enter_effects": self.on_enter_effects,
        }


@dataclass
class DialogueResult:
    """Result of a dialogue interaction."""
    option_chosen: DialogueOption
    outcome: DialogueOutcome
    roll_result: Optional[str] = None  # "strong_hit", "weak_hit", "miss"
    disposition_change: int = 0
    effects_triggered: List[str] = field(default_factory=list)
    new_disposition: Optional[Disposition] = None
    dialogue_ended: bool = False
    next_node_id: Optional[str] = None


@dataclass
class NPCDialogueState:
    """Persistent state for an NPC's dialogue."""
    npc_id: str
    disposition: Disposition = Disposition.NEUTRAL
    conversation_count: int = 0
    topics_discussed: List[str] = field(default_factory=list)
    secrets_revealed: List[str] = field(default_factory=list)
    trust_level: float = 0.0  # 0-1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "npc_id": self.npc_id,
            "disposition": self.disposition.value,
            "conversation_count": self.conversation_count,
            "topics_discussed": self.topics_discussed,
            "secrets_revealed": self.secrets_revealed,
            "trust_level": self.trust_level,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NPCDialogueState":
        return cls(
            npc_id=data["npc_id"],
            disposition=Disposition(data.get("disposition", "neutral")),
            conversation_count=data.get("conversation_count", 0),
            topics_discussed=data.get("topics_discussed", []),
            secrets_revealed=data.get("secrets_revealed", []),
            trust_level=data.get("trust_level", 0.0),
        )


class DialogueSystem:
    """
    Engine for structured dialogue with NPCs.

    Features:
    - Branching dialogue trees
    - Skill-based dialogue options
    - Disposition tracking
    - Requirement-gated options
    - Effect triggers
    """

    def __init__(self):
        self._dialogues: Dict[str, Dict[str, DialogueNode]] = {}  # npc_id -> {node_id -> node}
        self._npc_states: Dict[str, NPCDialogueState] = {}
        self._active_dialogue: Optional[str] = None  # Current NPC ID
        self._current_node: Optional[str] = None

    def register_dialogue(self, npc_id: str, nodes: List[DialogueNode]):
        """Register a dialogue tree for an NPC."""
        self._dialogues[npc_id] = {node.id: node for node in nodes}

    def get_npc_state(self, npc_id: str) -> NPCDialogueState:
        """Get or create state for an NPC."""
        if npc_id not in self._npc_states:
            self._npc_states[npc_id] = NPCDialogueState(npc_id=npc_id)
        return self._npc_states[npc_id]

    def start_dialogue(self, npc_id: str) -> Optional[DialogueNode]:
        """
        Start a dialogue with an NPC.

        Returns the entry node or None if no dialogue exists.
        """
        if npc_id not in self._dialogues:
            return None

        dialogue = self._dialogues[npc_id]

        # Find entry node
        for node in dialogue.values():
            if node.is_entry:
                self._active_dialogue = npc_id
                self._current_node = node.id

                # Update state
                state = self.get_npc_state(npc_id)
                state.conversation_count += 1

                return node

        return None

    def get_available_options(
        self,
        npc_id: str = None,
        player_stats: Dict[str, int] = None,
        player_items: List[str] = None,
        reputation: int = 0,
        psych_profile: "PsychologicalProfile" = None
    ) -> List[DialogueOption]:
        """
        Get options available to the player in current dialogue.

        Filters based on requirements.
        """
        npc_id = npc_id or self._active_dialogue
        if not npc_id or npc_id not in self._dialogues:
            return []

        if not self._current_node:
            return []

        dialogue = self._dialogues[npc_id]
        node = dialogue.get(self._current_node)
        if not node:
            return []

        npc_state = self.get_npc_state(npc_id)
        available = []

        for option in node.options:
            if option.hidden:
                continue

            # Check disposition requirement
            if option.required_disposition:
                disposition_order = list(Disposition)
                current_idx = disposition_order.index(npc_state.disposition)
                required_idx = disposition_order.index(option.required_disposition)
                if current_idx < required_idx:
                    continue

            # Check reputation requirement
            if option.required_reputation is not None:
                if reputation < option.required_reputation:
                    continue

            # Check item requirement
            if option.required_item:
                if player_items and option.required_item not in player_items:
                    continue

            # Emotional gating
            if psych_profile:
                # 1. Restricted Emotions (Block if current emotion matches)
                if option.restricted_emotion:
                    if psych_profile.current_emotion in option.restricted_emotion:
                        continue
                
                # 2. Required Emotions (Block if current emotion DOES NOT match)
                if option.required_emotion:
                    if psych_profile.current_emotion not in option.required_emotion:
                        continue

            available.append(option)

        return available

    def select_option(
        self,
        option_id: str,
        skill_roll: Optional[str] = None,  # "strong_hit", "weak_hit", "miss"
        npc_id: str = None
    ) -> DialogueResult:
        """
        Select a dialogue option and process results.

        Args:
            option_id: ID of the chosen option
            skill_roll: Result of skill check if required
            npc_id: NPC being talked to

        Returns:
            DialogueResult with outcome
        """
        npc_id = npc_id or self._active_dialogue
        if not npc_id or npc_id not in self._dialogues:
            return DialogueResult(
                option_chosen=DialogueOption(id="error", text="No dialogue active"),
                outcome=DialogueOutcome.FAILURE,
            )

        dialogue = self._dialogues[npc_id]
        node = dialogue.get(self._current_node)

        if not node:
            return DialogueResult(
                option_chosen=DialogueOption(id="error", text="Invalid node"),
                outcome=DialogueOutcome.FAILURE,
            )

        # Find the chosen option
        chosen = None
        for opt in node.options:
            if opt.id == option_id:
                chosen = opt
                break

        if not chosen:
            return DialogueResult(
                option_chosen=DialogueOption(id="error", text="Invalid option"),
                outcome=DialogueOutcome.FAILURE,
            )

        npc_state = self.get_npc_state(npc_id)
        effects = []

        # Determine outcome
        if chosen.skill_check and skill_roll:
            if skill_roll == "strong_hit":
                outcome = DialogueOutcome.SUCCESS
                disposition_change = chosen.changes_disposition + 1
            elif skill_roll == "weak_hit":
                outcome = DialogueOutcome.PARTIAL
                disposition_change = chosen.changes_disposition
            else:  # miss
                outcome = DialogueOutcome.FAILURE
                disposition_change = min(0, chosen.changes_disposition - 1)
        else:
            outcome = DialogueOutcome.SUCCESS
            disposition_change = chosen.changes_disposition

        # Apply disposition change
        if disposition_change != 0:
            new_disp = self._adjust_disposition(npc_state.disposition, disposition_change)
            npc_state.disposition = new_disp
            effects.append(f"Disposition changed to {new_disp.value}")

        # Update trust level
        if disposition_change > 0:
            npc_state.trust_level = min(1.0, npc_state.trust_level + 0.1)
        elif disposition_change < 0:
            npc_state.trust_level = max(0.0, npc_state.trust_level - 0.1)

        # Process effects
        effects.extend(chosen.effects)

        # Determine next node
        dialogue_ended = chosen.ends_dialogue
        next_node = chosen.leads_to

        if next_node:
            self._current_node = next_node
        elif chosen.ends_dialogue:
            self._active_dialogue = None
            self._current_node = None

        return DialogueResult(
            option_chosen=chosen,
            outcome=outcome,
            roll_result=skill_roll,
            disposition_change=disposition_change,
            effects_triggered=effects,
            new_disposition=npc_state.disposition,
            dialogue_ended=dialogue_ended,
            next_node_id=next_node,
        )

    def _adjust_disposition(self, current: Disposition, change: int) -> Disposition:
        """Adjust disposition by a delta."""
        disposition_order = list(Disposition)
        current_idx = disposition_order.index(current)
        new_idx = max(0, min(len(disposition_order) - 1, current_idx + change))
        return disposition_order[new_idx]

    def get_current_node(self) -> Optional[DialogueNode]:
        """Get the current dialogue node."""
        if not self._active_dialogue or not self._current_node:
            return None

        dialogue = self._dialogues.get(self._active_dialogue, {})
        return dialogue.get(self._current_node)

    def end_dialogue(self) -> None:
        """End the current dialogue."""
        self._active_dialogue = None
        self._current_node = None

    def is_in_dialogue(self) -> bool:
        """Check if currently in a dialogue."""
        return self._active_dialogue is not None

    def get_narrator_context(self, npc_id: str = None) -> str:
        """Generate dialogue context for narrator."""
        npc_id = npc_id or self._active_dialogue
        if not npc_id:
            return ""

        state = self.get_npc_state(npc_id)

        lines = [f"[DIALOGUE STATE: {npc_id.title()}]"]
        lines.append(f"Disposition: {state.disposition.value}")
        lines.append(f"Trust: {state.trust_level:.0%}")
        lines.append(f"Conversations: {state.conversation_count}")

        if state.topics_discussed:
            lines.append(f"Topics covered: {', '.join(state.topics_discussed[-3:])}")

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize system state."""
        return {
            "npc_states": {k: v.to_dict() for k, v in self._npc_states.items()},
            "active_dialogue": self._active_dialogue,
            "current_node": self._current_node,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DialogueSystem":
        """Deserialize system state."""
        system = cls()
        system._npc_states = {
            k: NPCDialogueState.from_dict(v)
            for k, v in data.get("npc_states", {}).items()
        }
        system._active_dialogue = data.get("active_dialogue")
        system._current_node = data.get("current_node")
        return system


# =============================================================================
# HELPER: CREATE SIMPLE DIALOGUES
# =============================================================================

def create_simple_dialogue(
    npc_id: str,
    greeting: str,
    topics: Dict[str, str],  # topic_id -> response
    farewell: str = "Farewell, traveler."
) -> List[DialogueNode]:
    """
    Create a simple dialogue tree.

    Args:
        npc_id: NPC identifier
        greeting: Opening line
        topics: Dict mapping topic IDs to NPC responses
        farewell: Closing line

    Returns:
        List of DialogueNodes
    """
    nodes = []

    # Create entry node
    options = []
    for topic_id, _ in topics.items():
        options.append(DialogueOption(
            id=f"ask_{topic_id}",
            text=f"Ask about {topic_id}",
            leads_to=f"topic_{topic_id}",
        ))

    options.append(DialogueOption(
        id="goodbye",
        text="I should go.",
        ends_dialogue=True,
    ))

    nodes.append(DialogueNode(
        id="entry",
        speaker=npc_id,
        text=greeting,
        options=options,
        is_entry=True,
    ))

    # Create topic nodes
    for topic_id, response in topics.items():
        topic_options = [opt for opt in options if opt.id != f"ask_{topic_id}"]

        nodes.append(DialogueNode(
            id=f"topic_{topic_id}",
            speaker=npc_id,
            text=response,
            options=topic_options,
        ))

    return nodes


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("DIALOGUE SYSTEM TEST")
    print("=" * 60)

    system = DialogueSystem()

    # Create test dialogue
    dialogue = [
        DialogueNode(
            id="entry",
            speaker="Captain Vex",
            text="What do you want? I'm busy.",
            options=[
                DialogueOption(
                    id="friendly",
                    text="I hear you're looking for crew.",
                    leads_to="interested",
                    changes_disposition=1,
                ),
                DialogueOption(
                    id="intimidate",
                    text="I'm here for information. Now.",
                    skill_check="iron",
                    leads_to="threatened",
                    changes_disposition=-1,
                ),
                DialogueOption(
                    id="secret",
                    text="Your old friend sends regards.",
                    required_disposition=Disposition.FRIENDLY,
                    leads_to="secret_topic",
                    changes_disposition=2,
                    hidden=False,
                ),
                DialogueOption(
                    id="leave",
                    text="Never mind.",
                    ends_dialogue=True,
                ),
            ],
            is_entry=True,
        ),
        DialogueNode(
            id="interested",
            speaker="Captain Vex",
            text="Crew, you say? What skills do you have?",
            options=[
                DialogueOption(
                    id="pilot",
                    text="I can fly anything.",
                    skill_check="edge",
                    leads_to="hired",
                    effects=["Gained potential job opportunity"],
                ),
                DialogueOption(
                    id="leave",
                    text="I'll think about it.",
                    ends_dialogue=True,
                ),
            ],
        ),
        DialogueNode(
            id="threatened",
            speaker="Captain Vex",
            text="You've got nerve. I respect that. What information?",
            options=[
                DialogueOption(
                    id="ask_cargo",
                    text="What's in your cargo hold?",
                    leads_to="entry",
                ),
                DialogueOption(
                    id="leave",
                    text="I've heard enough.",
                    ends_dialogue=True,
                ),
            ],
        ),
        DialogueNode(
            id="hired",
            speaker="Captain Vex",
            text="You're in. Report to the ship at dawn.",
            options=[
                DialogueOption(
                    id="accept",
                    text="I'll be there.",
                    ends_dialogue=True,
                    effects=["Joined Captain Vex's crew"],
                    changes_disposition=1,
                ),
            ],
        ),
    ]

    system.register_dialogue("vex", dialogue)

    # Test dialogue flow
    print("\n--- Starting Dialogue ---")
    node = system.start_dialogue("vex")
    if node:
        print(f"{node.speaker}: {node.text}")

        # Get available options
        options = system.get_available_options()
        print("\nOptions:")
        for i, opt in enumerate(options):
            skill = f" [{opt.skill_check.upper()} roll]" if opt.skill_check else ""
            print(f"  {i+1}. {opt.text}{skill}")

        # Choose friendly option
        print("\n--- Choosing 'friendly' option ---")
        result = system.select_option("friendly")
        print(f"Outcome: {result.outcome.value}")
        print(f"Disposition: {result.new_disposition.value}")

        # Get next node
        node = system.get_current_node()
        if node:
            print(f"\n{node.speaker}: {node.text}")

    # Test narrator context
    print("\n--- Narrator Context ---")
    print(system.get_narrator_context())
