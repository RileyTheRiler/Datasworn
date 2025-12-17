"""
LangGraph Workflow for Starforged AI Game Master.
Assembles the complete state graph with persistence.
"""

from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Literal

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from src.game_state import GameState, create_initial_state
from src.nodes import (
    router_node,
    rules_engine_node,
    oracle_interpreter_node,
    director_node,
    narrator_node,
    approval_node,
    world_state_manager_node,
    command_node,
)


def route_after_router(state: GameState) -> Literal["rules_engine", "oracle", "director", "narrator", "approval", "command", "end"]:
    """Conditional routing after router node."""
    route = state.get("route", "narrative")

    if route == "move":
        return "rules_engine"
    elif route == "oracle":
        return "oracle"
    elif route == "director":
        return "director"
    elif route == "approval":
        return "approval"
    elif route == "command":
        return "command"
    elif route == "end_turn":
        return "end"
    else:
        # For pure narrative, route through director first
        return "director"


def route_after_approval(state: GameState) -> Literal["narrator", "world_state", "end"]:
    """Conditional routing after approval node."""
    session = state.get("session")
    decision = session.user_decision if session else "accept"

    if decision == "retry":
        return "narrator"
    else:
        return "world_state"


def create_game_graph(checkpoint_path: str = "saves/game_sessions.db") -> StateGraph:
    """
    Create and return the compiled game graph.

    Args:
        checkpoint_path: Path to SQLite database for checkpointing.

    Returns:
        Compiled StateGraph ready for invocation.
    """
    # Ensure saves directory exists
    Path(checkpoint_path).parent.mkdir(parents=True, exist_ok=True)

    # Create the graph builder
    builder = StateGraph(GameState)

    # Add all nodes
    builder.add_node("router", router_node)
    builder.add_node("rules_engine", rules_engine_node)
    builder.add_node("oracle", oracle_interpreter_node)
    builder.add_node("director", director_node)
    builder.add_node("narrator", narrator_node)
    builder.add_node("approval", approval_node)
    builder.add_node("world_state", world_state_manager_node)
    builder.add_node("command", command_node)

    # Define edges
    builder.add_edge(START, "router")

    # Conditional edges from router
    builder.add_conditional_edges(
        "router",
        route_after_router,
        {
            "rules_engine": "rules_engine",
            "oracle": "oracle",
            "director": "director",
            "narrator": "narrator",
            "approval": "approval",
            "command": "command",
            "end": END,
        }
    )

    # Rules engine and oracle both go to director (which then goes to narrator)
    builder.add_edge("rules_engine", "director")
    builder.add_edge("oracle", "director")
    
    # Director goes to narrator
    builder.add_edge("director", "narrator")

    # Narrator goes to approval
    builder.add_edge("narrator", "approval")

    # Conditional edges from approval
    builder.add_conditional_edges(
        "approval",
        route_after_approval,
        {
            "narrator": "narrator",
            "world_state": "world_state",
            "end": END,
        }
    )

    # World state goes to end
    builder.add_edge("world_state", END)
    
    # Command goes to end
    builder.add_edge("command", END)

    # Set up checkpointer
    conn = sqlite3.connect(checkpoint_path, check_same_thread=False)
    checkpointer = SqliteSaver(conn)

    # Compile the graph
    graph = builder.compile(checkpointer=checkpointer)

    return graph


# ============================================================================
# Helper functions for game control
# ============================================================================

def start_game(character_name: str, session_id: str, checkpoint_path: str = "saves/game_sessions.db"):
    """
    Start a new game session.

    Args:
        character_name: Name of the player character.
        session_id: Unique session identifier.
        checkpoint_path: Path to checkpoint database.

    Returns:
        Initial result from the graph.
    """
    graph = create_game_graph(checkpoint_path)
    initial_state = create_initial_state(character_name)

    config = {"configurable": {"thread_id": session_id}}

    # Add an initial system message
    initial_state["messages"] = [
        {
            "role": "system",
            "content": f"Beginning a new Starforged adventure for {character_name}."
        }
    ]

    result = graph.invoke(initial_state, config)
    return result


def process_turn(player_input: str, session_id: str, checkpoint_path: str = "saves/game_sessions.db"):
    """
    Process a player turn.

    Args:
        player_input: The player's action or statement.
        session_id: Session identifier for checkpointing.
        checkpoint_path: Path to checkpoint database.

    Returns:
        Result from the graph (may include interrupt for approval).
    """
    graph = create_game_graph(checkpoint_path)
    config = {"configurable": {"thread_id": session_id}}

    # Get current state and add the new message
    state_update = {
        "messages": [{"role": "user", "content": player_input}],
    }

    result = graph.invoke(state_update, config)
    return result


def resume_after_approval(
    decision: str,
    session_id: str,
    edited_text: str = "",
    checkpoint_path: str = "saves/game_sessions.db"
):
    """
    Resume the graph after user approval.

    Args:
        decision: "accept", "retry", or "edit"
        session_id: Session identifier.
        edited_text: If decision is "edit", the edited narrative text.
        checkpoint_path: Path to checkpoint database.

    Returns:
        Final result from the graph.
    """
    from langgraph.types import Command

    graph = create_game_graph(checkpoint_path)
    config = {"configurable": {"thread_id": session_id}}

    resume_value = {"decision": decision}
    if decision == "edit" and edited_text:
        resume_value["edited_text"] = edited_text

    result = graph.invoke(Command(resume=resume_value), config)
    return result


def save_game(session_id: str, filepath: str, checkpoint_path: str = "saves/game_sessions.db"):
    """
    Export game state to a JSON file.

    Args:
        session_id: Session to export.
        filepath: Output JSON file path.
        checkpoint_path: Path to checkpoint database.
    """
    import json

    graph = create_game_graph(checkpoint_path)
    config = {"configurable": {"thread_id": session_id}}

    state = graph.get_state(config)

    # Convert to JSON-serializable format
    export_data = {
        "session_id": session_id,
        "state": state.values if state else {},
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, default=str)


def load_game(filepath: str, checkpoint_path: str = "saves/game_sessions.db") -> str:
    """
    Restore game state from a JSON file.

    Args:
        filepath: Input JSON file path.
        checkpoint_path: Path to checkpoint database.

    Returns:
        Session ID of the restored game.
    """
    import json

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    session_id = data.get("session_id", "restored_session")
    state = data.get("state", {})

    graph = create_game_graph(checkpoint_path)
    config = {"configurable": {"thread_id": session_id}}

    # Re-invoke with the loaded state to restore checkpoint
    graph.invoke(state, config)

    return session_id
