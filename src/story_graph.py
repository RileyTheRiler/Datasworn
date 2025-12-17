"""
Story DAG (Directed Acyclic Graph) for Narrative Flow.
Ensures the story always moves forward without loops.

Based on Game AI Pro patterns for graph-based narrative.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable
import json


# ============================================================================
# Narrative Node Types
# ============================================================================

class NodeType(Enum):
    """Types of narrative nodes."""
    SCENE = "scene"  # A narrative moment
    CHOICE = "choice"  # Player decision point
    CONSEQUENCE = "consequence"  # Result of a choice
    MILESTONE = "milestone"  # Major story beat
    ACT_BREAK = "act_break"  # Act transition
    ENDING = "ending"  # Terminal node


class ActNumber(Enum):
    """Story act structure (3-act or 5-act)."""
    PROLOGUE = 0
    ACT_1 = 1  # Setup
    ACT_2 = 2  # Confrontation
    ACT_3 = 3  # Resolution
    EPILOGUE = 4


# ============================================================================
# Story Nodes
# ============================================================================

@dataclass
class StoryNode:
    """A single node in the story graph."""
    node_id: str
    node_type: NodeType
    title: str
    description: str = ""
    
    # Story structure
    act: ActNumber = ActNumber.ACT_1
    is_required: bool = False  # Must visit this node
    is_visited: bool = False
    
    # Content triggers
    trigger_condition: str = ""  # When this node becomes available
    on_enter: str = ""  # Script to run when entering
    
    # Narrative metadata
    tension_level: float = 0.5  # 0-1 for pacing
    themes: list[str] = field(default_factory=list)
    involved_npcs: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "title": self.title,
            "description": self.description,
            "act": self.act.value,
            "is_required": self.is_required,
            "is_visited": self.is_visited,
            "tension_level": self.tension_level,
            "themes": self.themes,
            "involved_npcs": self.involved_npcs,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "StoryNode":
        return cls(
            node_id=data.get("node_id", ""),
            node_type=NodeType(data.get("node_type", "scene")),
            title=data.get("title", ""),
            description=data.get("description", ""),
            act=ActNumber(data.get("act", 1)),
            is_required=data.get("is_required", False),
            is_visited=data.get("is_visited", False),
            tension_level=data.get("tension_level", 0.5),
            themes=data.get("themes", []),
            involved_npcs=data.get("involved_npcs", []),
        )


@dataclass
class StoryEdge:
    """A directed edge between story nodes."""
    from_node: str
    to_node: str
    condition: str = ""  # When this path is available
    label: str = ""  # Player-facing name for this choice
    weight: float = 1.0  # Preference weight for AI selection
    
    def to_dict(self) -> dict:
        return {
            "from_node": self.from_node,
            "to_node": self.to_node,
            "condition": self.condition,
            "label": self.label,
            "weight": self.weight,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "StoryEdge":
        return cls(
            from_node=data.get("from_node", ""),
            to_node=data.get("to_node", ""),
            condition=data.get("condition", ""),
            label=data.get("label", ""),
            weight=data.get("weight", 1.0),
        )


# ============================================================================
# Story DAG
# ============================================================================

class StoryDAG:
    """
    Directed Acyclic Graph for narrative flow control.
    Ensures stories move forward without loops.
    """
    
    def __init__(self):
        self.nodes: dict[str, StoryNode] = {}
        self.edges: list[StoryEdge] = []
        self.current_node: str = ""
        self.visited_nodes: list[str] = []
        self._node_counter = 0
    
    def _generate_id(self, node_type: NodeType) -> str:
        """Generate unique node ID."""
        self._node_counter += 1
        return f"{node_type.value}_{self._node_counter:03d}"
    
    def add_node(
        self,
        node_type: NodeType,
        title: str,
        description: str = "",
        act: ActNumber = ActNumber.ACT_1,
        is_required: bool = False,
        tension_level: float = 0.5,
        **kwargs,
    ) -> str:
        """Add a new node to the story graph."""
        node_id = self._generate_id(node_type)
        
        node = StoryNode(
            node_id=node_id,
            node_type=node_type,
            title=title,
            description=description,
            act=act,
            is_required=is_required,
            tension_level=tension_level,
            themes=kwargs.get("themes", []),
            involved_npcs=kwargs.get("involved_npcs", []),
        )
        
        self.nodes[node_id] = node
        return node_id
    
    def add_edge(
        self,
        from_node: str,
        to_node: str,
        condition: str = "",
        label: str = "",
        weight: float = 1.0,
    ) -> bool:
        """
        Add an edge between nodes.
        Validates that this doesn't create a cycle.
        
        Returns:
            True if edge was added, False if it would create a cycle
        """
        if from_node not in self.nodes or to_node not in self.nodes:
            return False
        
        # Check for cycle
        if self._would_create_cycle(from_node, to_node):
            return False
        
        # Validate act progression (can only go forward or stay same)
        from_act = self.nodes[from_node].act.value
        to_act = self.nodes[to_node].act.value
        if to_act < from_act:
            return False  # Can't go backward in acts
        
        edge = StoryEdge(
            from_node=from_node,
            to_node=to_node,
            condition=condition,
            label=label,
            weight=weight,
        )
        
        self.edges.append(edge)
        return True
    
    def _would_create_cycle(self, from_node: str, to_node: str) -> bool:
        """Check if adding this edge would create a cycle."""
        # DFS from to_node to see if we can reach from_node
        visited = set()
        stack = [to_node]
        
        while stack:
            current = stack.pop()
            if current == from_node:
                return True  # Would create cycle
            
            if current in visited:
                continue
            visited.add(current)
            
            # Add all nodes reachable from current
            for edge in self.edges:
                if edge.from_node == current:
                    stack.append(edge.to_node)
        
        return False
    
    def get_available_transitions(self) -> list[StoryEdge]:
        """Get edges available from current node."""
        if not self.current_node:
            # Find starting nodes (nodes with no incoming edges)
            incoming = {e.to_node for e in self.edges}
            starting = [n for n in self.nodes if n not in incoming]
            # Return as pseudo-edges
            return [StoryEdge(from_node="", to_node=n, label=self.nodes[n].title) for n in starting]
        
        return [e for e in self.edges if e.from_node == self.current_node]
    
    def transition_to(self, node_id: str) -> bool:
        """
        Move to a new node.
        
        Returns:
            True if transition was valid
        """
        if node_id not in self.nodes:
            return False
        
        # Validate transition is allowed
        available = {e.to_node for e in self.get_available_transitions()}
        if self.current_node and node_id not in available:
            return False
        
        # Update state
        old_node = self.current_node
        self.current_node = node_id
        self.visited_nodes.append(node_id)
        self.nodes[node_id].is_visited = True
        
        return True
    
    def get_current_act(self) -> ActNumber:
        """Get the current story act."""
        if not self.current_node or self.current_node not in self.nodes:
            return ActNumber.ACT_1
        return self.nodes[self.current_node].act
    
    def get_progress(self) -> dict:
        """Get story progress metrics."""
        total_required = sum(1 for n in self.nodes.values() if n.is_required)
        visited_required = sum(1 for n in self.nodes.values() if n.is_required and n.is_visited)
        
        # Find all endings
        endings = [n for n in self.nodes.values() if n.node_type == NodeType.ENDING]
        visited_endings = [n for n in endings if n.is_visited]
        
        return {
            "current_node": self.current_node,
            "current_act": self.get_current_act().name,
            "nodes_visited": len(self.visited_nodes),
            "total_nodes": len(self.nodes),
            "required_completed": f"{visited_required}/{total_required}",
            "has_reached_ending": len(visited_endings) > 0,
        }
    
    def get_narrative_context(self) -> str:
        """Generate context for the narrator about story position."""
        if not self.current_node or self.current_node not in self.nodes:
            return "[STORY: Beginning of adventure]"
        
        node = self.nodes[self.current_node]
        lines = [f"[STORY POSITION]"]
        lines.append(f"Current: {node.title}")
        lines.append(f"Act: {node.act.name}")
        
        if node.tension_level > 0.7:
            lines.append("Pacing: CLIMACTIC")
        elif node.tension_level > 0.4:
            lines.append("Pacing: Rising tension")
        else:
            lines.append("Pacing: Breathing room")
        
        if node.themes:
            lines.append(f"Themes: {', '.join(node.themes)}")
        
        # Available transitions
        transitions = self.get_available_transitions()
        if transitions:
            options = [e.label or self.nodes.get(e.to_node, StoryNode("", NodeType.SCENE, "")).title 
                      for e in transitions[:3]]
            lines.append(f"Possible paths: {', '.join(options)}")
        
        return "\n".join(lines)
    
    def validate_dag(self) -> tuple[bool, list[str]]:
        """
        Validate the DAG has no cycles and all required paths exist.
        
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        # Check for unreachable nodes
        starting_nodes = self._get_starting_nodes()
        reachable = self._get_all_reachable(starting_nodes)
        
        for node_id in self.nodes:
            if node_id not in reachable:
                issues.append(f"Node '{node_id}' is unreachable")
        
        # Check that required nodes are on the main path
        for node in self.nodes.values():
            if node.is_required and node.node_id not in reachable:
                issues.append(f"Required node '{node.node_id}' is unreachable")
        
        # Check for at least one ending
        endings = [n for n in self.nodes.values() if n.node_type == NodeType.ENDING]
        if not endings:
            issues.append("No ending nodes defined")
        
        # Check endings are reachable
        for ending in endings:
            if ending.node_id not in reachable:
                issues.append(f"Ending '{ending.node_id}' is unreachable")
        
        return len(issues) == 0, issues
    
    def _get_starting_nodes(self) -> set[str]:
        """Get nodes with no incoming edges."""
        incoming = {e.to_node for e in self.edges}
        return {n for n in self.nodes if n not in incoming}
    
    def _get_all_reachable(self, starting: set[str]) -> set[str]:
        """Get all nodes reachable from starting nodes."""
        reachable = set()
        stack = list(starting)
        
        while stack:
            current = stack.pop()
            if current in reachable:
                continue
            reachable.add(current)
            
            for edge in self.edges:
                if edge.from_node == current:
                    stack.append(edge.to_node)
        
        return reachable
    
    def to_dict(self) -> dict:
        return {
            "nodes": {nid: n.to_dict() for nid, n in self.nodes.items()},
            "edges": [e.to_dict() for e in self.edges],
            "current_node": self.current_node,
            "visited_nodes": self.visited_nodes,
            "_node_counter": self._node_counter,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "StoryDAG":
        dag = cls()
        dag._node_counter = data.get("_node_counter", 0)
        dag.current_node = data.get("current_node", "")
        dag.visited_nodes = data.get("visited_nodes", [])
        
        for nid, ndata in data.get("nodes", {}).items():
            dag.nodes[nid] = StoryNode.from_dict(ndata)
        
        for edata in data.get("edges", []):
            dag.edges.append(StoryEdge.from_dict(edata))
        
        return dag


# ============================================================================
# Pre-built Story Templates
# ============================================================================

def create_three_act_template() -> StoryDAG:
    """Create a basic 3-act story structure."""
    dag = StoryDAG()
    
    # Act 1: Setup
    inciting = dag.add_node(
        NodeType.MILESTONE, "Inciting Incident",
        act=ActNumber.ACT_1, is_required=True, tension_level=0.4,
        themes=["discovery", "call to action"],
    )
    
    # Act 1 to 2 transition
    first_threshold = dag.add_node(
        NodeType.ACT_BREAK, "First Threshold",
        act=ActNumber.ACT_1, is_required=True, tension_level=0.5,
        themes=["commitment", "point of no return"],
    )
    
    # Act 2: Confrontation
    midpoint = dag.add_node(
        NodeType.MILESTONE, "Midpoint",
        act=ActNumber.ACT_2, is_required=True, tension_level=0.6,
        themes=["revelation", "raising stakes"],
    )
    
    dark_night = dag.add_node(
        NodeType.MILESTONE, "Dark Night of the Soul",
        act=ActNumber.ACT_2, is_required=True, tension_level=0.8,
        themes=["despair", "all is lost"],
    )
    
    # Act 2 to 3 transition
    second_threshold = dag.add_node(
        NodeType.ACT_BREAK, "Second Threshold",
        act=ActNumber.ACT_2, is_required=True, tension_level=0.7,
        themes=["resolve", "final push"],
    )
    
    # Act 3: Resolution
    climax = dag.add_node(
        NodeType.MILESTONE, "Climax",
        act=ActNumber.ACT_3, is_required=True, tension_level=1.0,
        themes=["confrontation", "ultimate test"],
    )
    
    resolution = dag.add_node(
        NodeType.ENDING, "Resolution",
        act=ActNumber.ACT_3, is_required=True, tension_level=0.3,
        themes=["new equilibrium", "lessons learned"],
    )
    
    # Connect the structure
    dag.add_edge(inciting, first_threshold)
    dag.add_edge(first_threshold, midpoint)
    dag.add_edge(midpoint, dark_night)
    dag.add_edge(dark_night, second_threshold)
    dag.add_edge(second_threshold, climax)
    dag.add_edge(climax, resolution)
    
    return dag


def create_vow_story(vow_name: str) -> StoryDAG:
    """Create a story structure for pursuing a vow."""
    dag = StoryDAG()
    
    # Vow structure matches Ironsworn progression
    swear = dag.add_node(
        NodeType.MILESTONE, f"Swear Vow: {vow_name}",
        act=ActNumber.ACT_1, is_required=True, tension_level=0.5,
    )
    
    first_progress = dag.add_node(
        NodeType.SCENE, "First Steps",
        act=ActNumber.ACT_1, tension_level=0.4,
    )
    
    complication = dag.add_node(
        NodeType.CONSEQUENCE, "Unexpected Complication",
        act=ActNumber.ACT_2, tension_level=0.6,
    )
    
    ally_or_enemy = dag.add_node(
        NodeType.CHOICE, "Make a Connection",
        act=ActNumber.ACT_2, tension_level=0.5,
    )
    
    crisis = dag.add_node(
        NodeType.MILESTONE, "Crisis Point",
        act=ActNumber.ACT_2, is_required=True, tension_level=0.8,
    )
    
    fulfill = dag.add_node(
        NodeType.ENDING, f"Fulfill Vow: {vow_name}",
        act=ActNumber.ACT_3, tension_level=0.9,
    )
    
    forsake = dag.add_node(
        NodeType.ENDING, f"Forsake Vow: {vow_name}",
        act=ActNumber.ACT_3, tension_level=0.7,
    )
    
    # Connect
    dag.add_edge(swear, first_progress)
    dag.add_edge(first_progress, complication)
    dag.add_edge(complication, ally_or_enemy)
    dag.add_edge(ally_or_enemy, crisis)
    dag.add_edge(crisis, fulfill, label="Succeed")
    dag.add_edge(crisis, forsake, label="Give Up")
    
    return dag
