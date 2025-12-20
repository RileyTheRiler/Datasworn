"""
Narrative Orchestrator Utilities

Helper functions to integrate the narrative orchestrator with game state.
"""

from src.narrative_orchestrator import NarrativeOrchestrator
from src.game_state import GameState, NarrativeOrchestratorState
from src.narrator import build_narrative_prompt


def initialize_orchestrator(game_state: GameState) -> NarrativeOrchestrator:
    """
    Initialize or restore the narrative orchestrator from game state.
    
    Args:
        game_state: The current game state
        
    Returns:
        Configured NarrativeOrchestrator instance
    """
    # Check if we have saved orchestrator data
    if game_state['narrative_orchestrator'].orchestrator_data:
        orchestrator = NarrativeOrchestrator.from_dict(
            game_state['narrative_orchestrator'].orchestrator_data
        )
    else:
        # Create new orchestrator
        orchestrator = NarrativeOrchestrator()
    
    # Attach to narrator
    build_narrative_prompt._orchestrator = orchestrator
    
    return orchestrator


def save_orchestrator(game_state: GameState, orchestrator: NarrativeOrchestrator):
    """
    Save orchestrator state to game state.
    
    Args:
        game_state: The game state to update
        orchestrator: The orchestrator to save
    """
    game_state['narrative_orchestrator'].orchestrator_data = orchestrator.to_dict()


def process_narrative_turn(
    game_state: GameState,
    orchestrator: NarrativeOrchestrator,
    generated_narrative: str,
):
    """
    Process a narrative turn - update orchestrator and save state.
    
    Call this after generating narrative to maintain all tracking systems.
    
    Args:
        game_state: Current game state
        orchestrator: The narrative orchestrator
        generated_narrative: The narrative that was just generated
    """
    # Process the narrative
    orchestrator.process_generated_narrative(
        generated_narrative,
        location=game_state['world'].current_location,
        active_npcs=game_state['memory'].active_npcs,
    )
    
    # Advance scene
    orchestrator.advance_scene()
    
    # Save to game state
    save_orchestrator(game_state, orchestrator)


# =============================================================================
# Example Integration Pattern
# =============================================================================

def example_integration():
    """
    Example showing how to integrate orchestrator into your game loop.
    """
    from src.game_state import create_initial_state
    from src.narrator import generate_narrative, NarratorConfig
    
    # 1. Initialize game
    game_state = create_initial_state("Kira")
    
    # 2. Initialize orchestrator
    orchestrator = initialize_orchestrator(game_state)
    
    # 3. Game loop
    for turn in range(10):
        # Get player input (simulated)
        player_input = "I investigate the console"
        
        # Generate narrative (orchestrator guidance is automatic)
        narrative = generate_narrative(
            player_input=player_input,
            location=game_state['world'].current_location,
            character_name=game_state['character'].name,
            config=NarratorConfig(),
        )
        
        # Process the turn
        process_narrative_turn(game_state, orchestrator, narrative)
        
        print(f"Turn {turn + 1}: {narrative[:100]}...")
    
    # 4. Save game (orchestrator state is in game_state)
    # save_game(game_state)
