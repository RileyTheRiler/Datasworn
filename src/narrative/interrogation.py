"""
Interrogation System Engine.

This module manages the structured dialogue trees for "Interrogation Scenes".
It tracks "Archetype Signals" based on player choices and manages
relationship changes (trust/suspicion) dynamically.
"""

from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from src.character_identity import WoundType

class InterrogationSignal(str, Enum):
    # Mapping to WoundTypes for simplicity, but can be distinct if needed
    CONTROLLER = "controller"
    JUDGE = "judge"
    MANIPULATOR = "manipulator"
    TRICKSTER = "trickster"
    PRAGMATIC = "pragmatic" # Maps to Neutral/Logic
    RESILIENT = "resilient" # Maps to Resilient/Growth
    GROWTH = "growth"       # General positive signal
    SAVIOR = "savior"
    GHOST = "ghost"
    
@dataclass
class InterrogationChoice:
    id: str
    text: str # Player dialogue
    next_node_id: str
    
    # Impacts
    signals: List[InterrogationSignal] = field(default_factory=list)
    trust_change: float = 0.0
    suspicion_change: float = 0.0
    
    # Conditions (if None, always available)
    # This is a bit tricky to serialize, so we might resolve dynamic availability in the Scene class
    condition: Optional[Callable[[Any], bool]] = None 
    
    def is_available(self, context: Any) -> bool:
        if self.condition:
            return self.condition(context)
        return True

@dataclass
class InterrogationNode:
    id: str
    npc_text: str # What the NPC says
    choices: List[InterrogationChoice] = field(default_factory=list)
    
    # Side effects when entering this node
    on_enter: Optional[Callable[[Any], None]] = None
    
    # If this is an end node, choices might be empty
    is_terminal: bool = False

class InterrogationScene:
    """Base class for a specific interrogation scenario."""
    
    def __init__(self):
        self.nodes: Dict[str, InterrogationNode] = {}
        self.start_node_id: str = "start"
        self.npc_id: str = "unknown"
        
    def get_node(self, node_id: str) -> Optional[InterrogationNode]:
        return self.nodes.get(node_id)
        
    def build_graph(self):
        """Override to define nodes and choices."""
        pass

@dataclass
class InterrogationState:
    """The runtime state of an active interrogation."""
    scene_id: str
    npc_id: str
    current_node_id: str
    history: List[str] = field(default_factory=list) # List of choice IDs made
    signals_accumulated: Dict[str, int] = field(default_factory=dict)
    
    # Relationship tracking
    trust_delta: float = 0.0
    suspicion_delta: float = 0.0
    
    is_complete: bool = False
    outcome: Optional[str] = None # "success", "failure", "neutral"

class InterrogationManager:
    """Manages the active interrogation session."""
    
    def __init__(self):
        self.active_state: Optional[InterrogationState] = None
        self.current_scene: Optional[InterrogationScene] = None
        self.scenes_registry: Dict[str, InterrogationScene] = {}
        
    def register_scene(self, scene_id: str, scene: InterrogationScene):
        self.scenes_registry[scene_id] = scene
        
    def start_interrogation(self, scene_id: str, relationship_web=None, player_wound_profile=None) -> InterrogationNode:
        if scene_id not in self.scenes_registry:
            raise ValueError(f"Scene {scene_id} not found.")
            
        scene = self.scenes_registry[scene_id]
        scene.build_graph() # Ensure graph is built
        
        self.current_scene = scene
        self.active_state = InterrogationState(
            scene_id=scene_id,
            npc_id=scene.npc_id,
            current_node_id=scene.start_node_id
        )
        
        node = scene.get_node(scene.start_node_id)
        
        # Inject Archetype Response if available
        if relationship_web and player_wound_profile:
            from src.character_identity import WoundType
            dominant_wound = player_wound_profile.dominant_wound
            wound_str = dominant_wound.value if hasattr(dominant_wound, 'value') else str(dominant_wound)
            
            # Fetch response
            archetype_response = relationship_web.get_npc_archetype_response(scene.npc_id, wound_str)
            
            if archetype_response:
                # Prepend the archetype reaction to the standard text
                # We use a copy of the node to avoid permanently mutating the scene template
                node = InterrogationNode(
                    id=node.id,
                    npc_text=f"{archetype_response}\n\n{node.npc_text}",
                    choices=node.choices,
                    on_enter=node.on_enter,
                    is_terminal=node.is_terminal
                )

        if node and node.on_enter:
            # We would pass game state here in a real implementation
            pass
            
        return node
        
    def advance(self, choice_id: str) -> InterrogationNode:
        if not self.active_state or not self.current_scene:
            raise RuntimeError("No active interrogation.")
            
        current_node = self.current_scene.get_node(self.active_state.current_node_id)
        if not current_node:
             raise RuntimeError(f"Node {self.active_state.current_node_id} not found.")
             
        # Find the choice
        selected_choice = next((c for c in current_node.choices if c.id == choice_id), None)
        if not selected_choice:
            raise ValueError(f"Invalid choice ID {choice_id}")
            
        # Apply impacts
        self.active_state.history.append(choice_id)
        for signal in selected_choice.signals:
            curr = self.active_state.signals_accumulated.get(signal.value, 0)
            self.active_state.signals_accumulated[signal.value] = curr + 1
            
        # Track relationship changes
        self.active_state.trust_delta += selected_choice.trust_change
        self.active_state.suspicion_delta += selected_choice.suspicion_change
            
        # Track relationship changes
        self.active_state.trust_delta += selected_choice.trust_change
        self.active_state.suspicion_delta += selected_choice.suspicion_change
            
        # Transition
        next_node_id = selected_choice.next_node_id
        self.active_state.current_node_id = next_node_id
        
        # Resolve next node
        next_node = self.current_scene.get_node(next_node_id)
        
        if next_node.is_terminal:
            self.active_state.is_complete = True
            
        return next_node
        
    def get_state_dict(self):
        if not self.active_state:
            return None
        return {
            "scene_id": self.active_state.scene_id,
            "npc_id": self.active_state.npc_id,
            "current_node_id": self.active_state.current_node_id,
            "signals": self.active_state.signals_accumulated,
            "trust_delta": self.active_state.trust_delta,
            "suspicion_delta": self.active_state.suspicion_delta,
            "is_complete": self.active_state.is_complete
        }
    
    def apply_signals_to_wound_profile(self, wound_profile):
        """
        Apply accumulated signals to the player's WoundProfile.
        Maps InterrogationSignal -> WoundType and increments scores.
        """
        from src.character_identity import WoundType
        
        signal_to_wound = {
            InterrogationSignal.CONTROLLER.value: WoundType.CONTROLLER,
            InterrogationSignal.JUDGE.value: WoundType.JUDGE,
            InterrogationSignal.MANIPULATOR.value: WoundType.MANIPULATOR,
            InterrogationSignal.TRICKSTER.value: WoundType.TRICKSTER,
            InterrogationSignal.SAVIOR.value: WoundType.SAVIOR,
            InterrogationSignal.GHOST.value: WoundType.GHOST,
            InterrogationSignal.RESILIENT.value: WoundType.UNKNOWN, # Positive signal
            InterrogationSignal.GROWTH.value: WoundType.UNKNOWN,
        }
        
        if not self.active_state:
            return
            
        for signal_name, count in self.active_state.signals_accumulated.items():
            wound_type = signal_to_wound.get(signal_name)
            if wound_type and wound_type != WoundType.UNKNOWN:
                # Increment wound score
                current = wound_profile.scores.scores.get(wound_type, 0.0)
                wound_profile.scores.scores[wound_type] = min(1.0, current + (count * 0.05))
        
        # Recalculate dominant wound
        if wound_profile.scores.scores:
            dominant = max(wound_profile.scores.scores.items(), key=lambda x: x[1])
            wound_profile.dominant_wound = dominant[0]
    
    def to_dict(self) -> dict:
        """Serialize manager state."""
        return {
            "active_state": {
                "scene_id": self.active_state.scene_id,
                "npc_id": self.active_state.npc_id,
                "current_node_id": self.active_state.current_node_id,
                "history": self.active_state.history,
                "signals": self.active_state.signals_accumulated,
                "trust_delta": self.active_state.trust_delta,
                "suspicion_delta": self.active_state.suspicion_delta,
                "is_complete": self.active_state.is_complete,
                "outcome": self.active_state.outcome
            } if self.active_state else None
        }
    
    @classmethod
    def from_dict(cls, data: dict, scenes_registry: Dict[str, 'InterrogationScene']) -> 'InterrogationManager':
        """Deserialize manager state."""
        manager = cls()
        manager.scenes_registry = scenes_registry
        
        if data.get("active_state"):
            state_data = data["active_state"]
            manager.active_state = InterrogationState(
                scene_id=state_data["scene_id"],
                npc_id=state_data["npc_id"],
                current_node_id=state_data["current_node_id"],
                history=state_data.get("history", []),
                signals_accumulated=state_data.get("signals", {}),
                trust_delta=state_data.get("trust_delta", 0.0),
                suspicion_delta=state_data.get("suspicion_delta", 0.0),
                is_complete=state_data.get("is_complete", False),
                outcome=state_data.get("outcome")
            )
            manager.current_scene = scenes_registry.get(state_data["scene_id"])
        
        return manager
