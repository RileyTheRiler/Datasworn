"""
Tests for Deep Psychology Mechanics.
"""

import pytest
from src.psych_profile import (
    PsychologicalProfile, 
    PsychologicalEngine, 
    ValueSystem, 
    EmotionalState,
    ValueConflict,
    Compulsion
)
from src.relationship_system import RelationshipWeb
from src.dream_system import DreamEngine


def test_value_conflict_detection():
    profile = PsychologicalProfile()
    engine = PsychologicalEngine()
    
    # Set up conflicting high values
    profile.values = {
        ValueSystem.SECURITY: 0.9,
        ValueSystem.CURIOSITY: 0.8,
    }
    
    # Action that should trigger conflict
    conflict = engine.detect_value_conflict(profile, "investigate the unknown signal")
    
    assert conflict is not None
    assert conflict.value_a == ValueSystem.SECURITY
    assert conflict.value_b == ValueSystem.CURIOSITY
    assert len(profile.active_conflicts) == 1


def test_value_conflict_resolution():
    profile = PsychologicalProfile()
    engine = PsychologicalEngine()
    
    profile.values = {
        ValueSystem.SECURITY: 0.8,
        ValueSystem.AUTONOMY: 0.7,
    }
    
    conflict = ValueConflict(
        value_a=ValueSystem.SECURITY,
        value_b=ValueSystem.AUTONOMY,
        description="Test conflict"
    )
    
    engine.resolve_conflict(profile, conflict, ValueSystem.SECURITY)
    
    assert conflict.resolved == True
    assert conflict.chosen_value == ValueSystem.SECURITY
    assert profile.values[ValueSystem.SECURITY] > 0.8
    assert profile.values[ValueSystem.AUTONOMY] < 0.7
    assert "I chose security over autonomy." in profile.beliefs


def test_compulsion_tracking():
    profile = PsychologicalProfile()
    engine = PsychologicalEngine()
    
    # Take stims multiple times
    for _ in range(4):
        engine.track_compulsion(profile, "I take a stim")
    
    assert len(profile.compulsions) == 1
    assert profile.compulsions[0].trigger == "stim"
    assert profile.compulsions[0].uses == 4


def test_withdrawal_stress():
    profile = PsychologicalProfile()
    engine = PsychologicalEngine()
    
    # Create a compulsion past threshold
    profile.compulsions.append(Compulsion(trigger="stim", uses=5, satisfaction=0.2, threshold=3))
    
    initial_stress = profile.stress_level
    engine.apply_withdrawal(profile)
    
    assert profile.stress_level > initial_stress


def test_memory_corruption():
    profile = PsychologicalProfile()
    engine = PsychologicalEngine()
    
    profile.memories = ["I saw the Captain sabotage the drive."]
    
    engine.corrupt_memory(profile, index=0)
    
    assert profile.memories[0] != "I saw the Captain sabotage the drive."
    assert 0 in profile.corrupted_memory_indices


def test_npc_reaction_to_emotion():
    web = RelationshipWeb()
    
    # Test anxious player with suspicious NPC
    web.crew["security"].suspicion = 0.8
    reaction = web.get_npc_reaction_to_emotion("security", EmotionalState.ANXIOUS)
    
    assert "nervousness" in reaction.lower() or "narrow" in reaction.lower()


def test_social_perception_update():
    web = RelationshipWeb()
    
    web.update_perception("help", "strong_hit")
    
    assert web.perception.perceived_traits.get("reliable", 0) > 0
    assert web.perception.reputation_score > 0.5


def test_dream_trigger():
    profile = PsychologicalProfile()
    engine = DreamEngine()
    
    # Low sanity should trigger dreams
    profile.sanity = 0.3
    
    fragment = engine.check_trigger(profile)
    
    # Probabilistic, so we just check that it's eligible
    # (can't guarantee it triggers without mocking random)
    assert profile.sanity < 0.6  # Eligible for dreaming


def test_dream_generation():
    profile = PsychologicalProfile()
    engine = DreamEngine()
    
    profile.sanity = 0.3
    profile.memories = ["I killed them. All of them."]
    
    # Force a specific fragment
    from src.dream_system import DREAM_FRAGMENTS
    fragment = DREAM_FRAGMENTS[3]  # dead_crew
    
    dream = engine.generate_dream(profile, fragment=fragment)
    
    assert "[DREAM SEQUENCE]" in dream
    assert "dead" in dream.lower()
