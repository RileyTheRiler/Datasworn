"""
Quest Graph Runtime

Manages the directed graph of quest threads with prerequisites, convergence nodes,
and phase-based availability.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
import yaml
from pathlib import Path

from .state import QuestState, QuestStateManager


@dataclass
class QuestNode:
    """Represents a single quest in the graph."""
    id: str
    phase: int
    title: str
    description: str
    prerequisites: Dict[str, any] = field(default_factory=dict)  # {quests: [], flags: [], reputation: {}}
    recommended_order: int = 0
    converges_to: Optional[str] = None  # Critical node this converges to
    expires_on_phase: Optional[int] = None
    side_effects: Dict[str, List[str]] = field(default_factory=dict)  # {flags_to_set: [], world_deltas: []}
    unlock_dialogue_options: List[str] = field(default_factory=list)
    quest_type: str = "side"  # main, side, personal, faction, exploration, urgent
    
    def get_prerequisite_quests(self) -> List[str]:
        """Get list of prerequisite quest IDs."""
        return self.prerequisites.get("quests", [])
    
    def get_prerequisite_flags(self) -> List[str]:
        """Get list of prerequisite world flags."""
        return self.prerequisites.get("flags", [])
    
    def get_prerequisite_reputation(self) -> Dict[str, int]:
        """Get prerequisite reputation requirements."""
        return self.prerequisites.get("reputation", {})
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "phase": self.phase,
            "title": self.title,
            "description": self.description,
            "prerequisites": self.prerequisites,
            "recommended_order": self.recommended_order,
            "converges_to": self.converges_to,
            "expires_on_phase": self.expires_on_phase,
            "side_effects": self.side_effects,
            "unlock_dialogue_options": self.unlock_dialogue_options,
            "quest_type": self.quest_type
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "QuestNode":
        """Deserialize from dictionary."""
        return cls(
            id=data["id"],
            phase=data.get("phase", 1),
            title=data.get("title", ""),
            description=data.get("description", ""),
            prerequisites=data.get("prerequisites", {}),
            recommended_order=data.get("recommended_order", 0),
            converges_to=data.get("converges_to"),
            expires_on_phase=data.get("expires_on_phase"),
            side_effects=data.get("side_effects", {}),
            unlock_dialogue_options=data.get("unlock_dialogue_options", []),
            quest_type=data.get("quest_type", "side")
        )


@dataclass
class QuestPhase:
    """Represents a story phase/chapter."""
    id: int
    name: str
    critical_quests: List[str] = field(default_factory=list)  # Must complete to advance
    optional_threads: List[str] = field(default_factory=list)  # Available but not required
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "critical_quests": self.critical_quests,
            "optional_threads": self.optional_threads
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "QuestPhase":
        return cls(
            id=data["id"],
            name=data.get("name", f"Phase {data['id']}"),
            critical_quests=data.get("critical_quests", []),
            optional_threads=data.get("optional_threads", [])
        )


class QuestGraph:
    """
    Manages the quest graph with validation and state queries.
    
    Handles:
    - Quest prerequisites and dependencies
    - Convergence nodes (multiple paths → single node)
    - Phase transitions and quest expiration
    - Soft locks (quests waiting for world state)
    """
    
    def __init__(self):
        self.nodes: Dict[str, QuestNode] = {}
        self.phases: Dict[int, QuestPhase] = {}
        self.state_manager = QuestStateManager()
        self.world_flags: Set[str] = set()
        self.reputation: Dict[str, int] = {}  # {faction: reputation_value}
    
    def load_quests_from_yaml(self, quest_dir: str):
        """Load quest definitions from YAML files."""
        quest_path = Path(quest_dir)
        if not quest_path.exists():
            return
        
        for yaml_file in quest_path.glob("*.yaml"):
            with open(yaml_file, 'r') as f:
                quest_data = yaml.safe_load(f)
                if quest_data:
                    node = QuestNode.from_dict(quest_data)
                    self.add_quest(node)
    
    def load_phases_from_yaml(self, filepath: str):
        """Load phase definitions from YAML file."""
        path = Path(filepath)
        if not path.exists():
            return
        
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
            if data and "phases" in data:
                for phase_data in data["phases"]:
                    phase = QuestPhase.from_dict(phase_data)
                    self.phases[phase.id] = phase
    
    def add_quest(self, node: QuestNode):
        """Add a quest node to the graph."""
        self.nodes[node.id] = node
        # Initialize state as LOCKED by default
        self.state_manager.initialize_quest(node.id, QuestState.LOCKED)
    
    def check_prerequisites(self, quest_id: str) -> Tuple[bool, List[str]]:
        """
        Check if quest prerequisites are met.
        
        Returns:
            (prerequisites_met, list_of_unmet_requirements)
        """
        if quest_id not in self.nodes:
            return False, ["Quest not found"]
        
        node = self.nodes[quest_id]
        unmet = []
        
        # Check quest prerequisites
        for prereq_quest in node.get_prerequisite_quests():
            if prereq_quest not in self.state_manager.get_completed_quests():
                unmet.append(f"Quest not completed: {prereq_quest}")
        
        # Check flag prerequisites
        for flag in node.get_prerequisite_flags():
            if flag not in self.world_flags:
                unmet.append(f"World flag not set: {flag}")
        
        # Check reputation prerequisites
        for faction, required_rep in node.get_prerequisite_reputation().items():
            current_rep = self.reputation.get(faction, 0)
            if current_rep < required_rep:
                unmet.append(f"Insufficient reputation with {faction}: {current_rep}/{required_rep}")
        
        return len(unmet) == 0, unmet
    
    def update_quest_availability(self):
        """Update which quests are available based on prerequisites."""
        for quest_id, node in self.nodes.items():
            current_state = self.state_manager.get_state(quest_id)
            
            # Only check locked quests
            if current_state == QuestState.LOCKED:
                # Check if in current phase
                if node.phase <= self.state_manager.current_phase:
                    # Check prerequisites
                    prereqs_met, _ = self.check_prerequisites(quest_id)
                    if prereqs_met:
                        self.state_manager.unlock_quest(quest_id)
    
    def start_quest(self, quest_id: str) -> Tuple[bool, str]:
        """
        Start a quest.
        
        Returns:
            (success, message)
        """
        if quest_id not in self.nodes:
            return False, "Quest not found"
        
        current_state = self.state_manager.get_state(quest_id)
        if current_state != QuestState.AVAILABLE:
            return False, f"Quest not available (current state: {current_state.value})"
        
        prereqs_met, unmet = self.check_prerequisites(quest_id)
        if not prereqs_met:
            return False, f"Prerequisites not met: {', '.join(unmet)}"
        
        success = self.state_manager.start_quest(quest_id)
        if success:
            return True, f"Quest '{self.nodes[quest_id].title}' started"
        return False, "Failed to start quest"
    
    def complete_quest(self, quest_id: str, alternate: bool = False, 
                       alternate_path: str = "") -> Tuple[bool, str]:
        """
        Complete a quest and apply side effects.
        
        Returns:
            (success, message)
        """
        if quest_id not in self.nodes:
            return False, "Quest not found"
        
        current_state = self.state_manager.get_state(quest_id)
        if current_state != QuestState.IN_PROGRESS:
            return False, f"Quest not in progress (current state: {current_state.value})"
        
        # Complete the quest
        success = self.state_manager.complete_quest(quest_id, alternate, alternate_path)
        if not success:
            return False, "Failed to complete quest"
        
        # Apply side effects
        node = self.nodes[quest_id]
        flags_set = node.side_effects.get("flags_to_set", [])
        for flag in flags_set:
            self.world_flags.add(flag)
        
        # Update availability of dependent quests
        self.update_quest_availability()
        
        return True, f"Quest '{node.title}' completed"
    
    def advance_phase(self, new_phase: int):
        """Advance to a new phase and handle quest expiration."""
        old_phase = self.state_manager.current_phase
        self.state_manager.current_phase = new_phase
        
        # Find quests that expire
        expired_quests = set()
        for quest_id, node in self.nodes.items():
            if node.expires_on_phase and node.expires_on_phase <= new_phase:
                expired_quests.add(quest_id)
        
        # Expire them
        self.state_manager.expire_phase_quests(expired_quests)
        
        # Update availability for new phase
        self.update_quest_availability()
    
    def get_available_quests(self, phase: Optional[int] = None) -> List[QuestNode]:
        """Get all available quests, optionally filtered by phase."""
        # Ensure availability is up to date
        self.update_quest_availability()
        
        available_ids = self.state_manager.get_available_quests()
        quests = [self.nodes[qid] for qid in available_ids if qid in self.nodes]
        
        if phase is not None:
            quests = [q for q in quests if q.phase == phase]
        
        # Sort by recommended order
        quests.sort(key=lambda q: q.recommended_order)
        return quests
    
    def get_active_quests(self) -> List[QuestNode]:
        """Get all active (in-progress) quests."""
        active_ids = self.state_manager.get_active_quests()
        return [self.nodes[qid] for qid in active_ids if qid in self.nodes]
    
    def get_convergence_status(self, convergence_node_id: str) -> Dict[str, any]:
        """
        Check status of a convergence node.
        
        Returns info about which branches have been completed.
        """
        # Find all quests that converge to this node
        converging_quests = [
            (qid, node) for qid, node in self.nodes.items()
            if node.converges_to == convergence_node_id
        ]
        
        completed = []
        in_progress = []
        available = []
        locked = []
        
        for qid, node in converging_quests:
            state = self.state_manager.get_state(qid)
            if state in {QuestState.COMPLETED, QuestState.ALTERNATE}:
                completed.append(qid)
            elif state == QuestState.IN_PROGRESS:
                in_progress.append(qid)
            elif state == QuestState.AVAILABLE:
                available.append(qid)
            else:
                locked.append(qid)
        
        return {
            "convergence_node": convergence_node_id,
            "total_branches": len(converging_quests),
            "completed": completed,
            "in_progress": in_progress,
            "available": available,
            "locked": locked,
            "ready_to_converge": len(completed) > 0  # At least one branch completed
        }
    
    def get_critical_path_status(self, phase_id: int) -> Dict[str, any]:
        """Check if critical path quests for a phase are completed."""
        if phase_id not in self.phases:
            return {"error": "Phase not found"}
        
        phase = self.phases[phase_id]
        completed_quests = self.state_manager.get_completed_quests()
        
        critical_status = {}
        all_complete = True
        
        for quest_id in phase.critical_quests:
            is_complete = quest_id in completed_quests
            critical_status[quest_id] = is_complete
            if not is_complete:
                all_complete = False
        
        return {
            "phase": phase.name,
            "critical_quests": critical_status,
            "can_advance": all_complete
        }
    
    def to_dict(self) -> dict:
        """Serialize entire graph to dictionary."""
        return {
            "nodes": {qid: node.to_dict() for qid, node in self.nodes.items()},
            "phases": {pid: phase.to_dict() for pid, phase in self.phases.items()},
            "state": self.state_manager.to_dict(),
            "world_flags": list(self.world_flags),
            "reputation": self.reputation
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "QuestGraph":
        """Deserialize from dictionary."""
        graph = cls()
        
        # Load nodes
        for qid, node_data in data.get("nodes", {}).items():
            graph.nodes[qid] = QuestNode.from_dict(node_data)
        
        # Load phases
        for pid, phase_data in data.get("phases", {}).items():
            graph.phases[int(pid)] = QuestPhase.from_dict(phase_data)
        
        # Load state
        if "state" in data:
            graph.state_manager = QuestStateManager.from_dict(data["state"])
        
        # Load world state
        graph.world_flags = set(data.get("world_flags", []))
        graph.reputation = data.get("reputation", {})
        
        return graph
