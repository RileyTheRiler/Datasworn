"""
Comprehensive Integration Tests for All Psychology Systems.
"""

import pytest
from src.psych_profile import PsychologicalProfile, EmotionalState, TraumaScar, ValueSystem, ValueConflict, Compulsion
from src.barks import BarkManager, BarkType
from src.intent_predictor import NGramPredictor, IntentCategory
from src.story_graph import StoryDAG, NodeType, ActNumber

def test_barks_react_to_emotion():
    """NPCs react to player's emotional state."""
    manager = BarkManager()
    profile = PsychologicalProfile()
    
    # Anxious player
    profile.current_emotion = EmotionalState.ANXIOUS
    bark = manager.generate_bark("Security", BarkType.FRIENDLY, psych_profile=profile)
    
    assert bark is not None
    assert any(word in bark.text.lower() for word in ["pale", "shaking", "nervous", "alright"])

def test_barks_react_to_trauma():
    """NPCs react to player's trauma scars."""
    manager = BarkManager()
    profile = PsychologicalProfile()
    
    profile.trauma_scars.append(TraumaScar(name="Shattered Trust", description="...", trait_modifier={}))
    bark = manager.generate_bark("Crew", BarkType.FRIENDLY, psych_profile=profile)
    
    assert bark is not None
    assert any(word in bark.text.lower() for word in ["distance", "trust", "away"])

def test_intent_prediction_from_compulsion():
    """Intent predictor detects compulsion patterns."""
    predictor = NGramPredictor()
    profile = PsychologicalProfile()
    
    # Add a stim compulsion
    profile.compulsions.append(Compulsion(trigger="stim", uses=5, satisfaction=0.2, threshold=3))
    
    predictions = predictor.predict_from_profile(profile)
    
    assert len(predictions) > 0
    # Should predict REST (seeking relief)
    intents = [p[0] for p in predictions]
    assert IntentCategory.REST in intents

def test_intent_prediction_from_stress():
    """High stress makes predictions erratic."""
    predictor = NGramPredictor()
    profile = PsychologicalProfile()
    
    profile.stress_level = 0.9
    predictions = predictor.predict_from_profile(profile)
    
    assert len(predictions) > 0
    # Should predict REST or MOVEMENT (flee)
    intents = [p[0] for p in predictions]
    assert IntentCategory.REST in intents or IntentCategory.MOVEMENT in intents

def test_story_node_trauma_gating():
    """Story nodes can be gated by trauma."""
    dag = StoryDAG()
    profile = PsychologicalProfile()
    
    # Create a trauma-gated node
    start = dag.add_node(NodeType.SCENE, "Start")
    trauma_node = dag.add_node(NodeType.SCENE, "Confrontation")
    dag.nodes[trauma_node].psych_requirements = {"trauma": "Shattered Trust"}
    
    dag.add_edge(start, trauma_node)
    dag.current_node = start
    
    # Without trauma, node is unavailable
    available = dag.get_available_transitions(profile)
    assert len(available) == 0
    
    # With trauma, node unlocks
    profile.trauma_scars.append(TraumaScar(name="Shattered Trust", description="...", trait_modifier={}))
    available = dag.get_available_transitions(profile)
    assert len(available) == 1

def test_story_node_sanity_gating():
    """Story nodes can require minimum sanity."""
    dag = StoryDAG()
    profile = PsychologicalProfile()
    
    start = dag.add_node(NodeType.SCENE, "Start")
    sane_node = dag.add_node(NodeType.SCENE, "Rational Choice")
    dag.nodes[sane_node].psych_requirements = {"min_sanity": 0.5}
    
    dag.add_edge(start, sane_node)
    dag.current_node = start
    
    # Low sanity blocks node
    profile.sanity = 0.3
    available = dag.get_available_transitions(profile)
    assert len(available) == 0
    
    # High sanity unlocks
    profile.sanity = 0.8
    available = dag.get_available_transitions(profile)
    assert len(available) == 1

def test_full_integration_loop():
    """
    End-to-end test: Stress -> Trauma -> Barks change -> Intent shifts -> Story gates.
    """
    profile = PsychologicalProfile()
    bark_mgr = BarkManager()
    predictor = NGramPredictor()
    dag = StoryDAG()
    
    # 1. Start calm
    assert profile.stress_level == 0.0
    
    # 2. Accumulate stress (simulated)
    profile.stress_level = 0.9
    
    # 3. Intent prediction changes
    predictions = predictor.predict_from_profile(profile)
    intents = [p[0] for p in predictions]
    assert IntentCategory.REST in intents or IntentCategory.MOVEMENT in intents
    
    # 4. Acquire trauma
    profile.trauma_scars.append(TraumaScar(name="Shattered Trust", description="...", trait_modifier={}))
    profile.stress_level = 0.4  # Reset after trauma
    
    # 5. Barks change
    bark = bark_mgr.generate_bark("NPC", BarkType.FRIENDLY, psych_profile=profile)
    assert "distance" in bark.text.lower() or "trust" in bark.text.lower()
    
    # 6. Story nodes unlock
    trauma_node = dag.add_node(NodeType.SCENE, "Dark Path")
    dag.nodes[trauma_node].psych_requirements = {"trauma": "Shattered Trust"}
    start = dag.add_node(NodeType.SCENE, "Start")
    dag.add_edge(start, trauma_node)
    dag.current_node = start
    
    available = dag.get_available_transitions(profile)
    assert len(available) == 1
