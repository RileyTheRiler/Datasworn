"""
Verification Script for the Cognitive Engine.
Run this to validate the NPC's ability to perceive, remember, reflect, and act.
"""
import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.npc.schemas import CognitiveState, PersonalityProfile, RelationshipState
from src.npc.engine import NPCCognitiveEngine
from src.npc.memory_stream import NPCMemoryStream

def print_separator(title):
    print(f"\n{'='*20} {title} {'='*20}")

def verify_cognitive_engine():
    print_separator("INITIALIZING JANUS")
    
    # 1. Setup State
    janus_profile = PersonalityProfile(
        name="Janus",
        role="Gatekeeper",
        narrative_seed=(
            "Janus is the ancient gatekeeper of the Void Station. He has seen civilizations rise and fall. "
            "He is bound by protocol but secretly yearns for a conversation that surprises him. "
            "He distrusts those who are loud or aggressive."
        ),
        traits=["Observant", "Stoic", "Bureaucratic"],
        current_mood="Bored"
    )
    
    state = CognitiveState(
        npc_id="janus_01",
        profile=janus_profile
    )
    
    engine = NPCCognitiveEngine()
    
    # 2. Test Scenarios
    
    # Scenario A: First Meeting (Establish Baseline)
    print_separator("TURN 1: INTRODUCTION")
    player_input = "I approach the gate. 'Greetings, watcher. I seek passage.'"
    output = engine.process_turn(state, player_input, location="Void Gate", time="08:00")
    print(f"Player: {player_input}")
    print(f"Janus: {output['narrative']}")
    print(f"State Updates: {output['state_updates']}")
    
    # Scenario B: Establish Memory
    print_separator("TURN 2: PROVIDING INFO")
    player_input = "I am a doctor from the Core Worlds. I can heal your wounded."
    output = engine.process_turn(state, player_input, location="Void Gate", time="08:05")
    print(f"Player: {player_input}")
    print(f"Janus: {output['narrative']}")
    
    # Check internal memory
    print("\n[Checking Memory Stream]")
    for m in state.memories[-2:]:
        print(f" - {m.content} (Imp: {m.importance_score})")

    # Scenario C: Recall Test
    print_separator("TURN 3: MEMORY RECALL")
    player_input = "I told you, I have medical skills. Let me in."
    output = engine.process_turn(state, player_input, location="Void Gate", time="08:10")
    print(f"Player: {player_input}")
    print(f"Janus: {output['narrative']}")
    
    # Verify retrieval pipeline implicitly by the response. 
    # If RAG works, he should acknowledge the medical skills.

    # Scenario D: Conflict & Relationship Change
    print_separator("TURN 4: CONFLICT")
    player_input = "Open the door or I'll blast it open, you rust bucket!"
    output = engine.process_turn(state, player_input, location="Void Gate", time="08:15")
    print(f"Player: {player_input}")
    print(f"Janus: {output['narrative']}")
    
    # Check Mood/Relationship
    print(f"Current Mood: {state.profile.current_mood}")
    # Note: Relationship update logic in Engine is basic JSON parsing.
    # We'll check if the LLM outputted trust change.
    
    print_separator("VERIFICATION COMPLETE")

if __name__ == "__main__":
    verify_cognitive_engine()
