"""
Test Phase 6: Emergent Narrative & Meta-Systems
"""

from src.psych_profile import PsychologicalProfile, PsychologicalEngine, TraumaScar
from src.difficulty_scaling import PsychologicalDifficultyScaler
from src.relationship_system import CrewMember, EmotionalMemory, EmotionalState
from datetime import datetime


def test_trauma_arc_evolution():
    """Test that trauma scars evolve through therapy."""
    profile = PsychologicalProfile()
    engine = PsychologicalEngine()
    
    # Add a fresh trauma
    scar = TraumaScar(
        name="Shattered Trust",
        description="Test",
        trait_modifier={"paranoia": 0.3, "empathy": -0.2},
        therapy_sessions=0
    )
    profile.trauma_scars.append(scar)
    
    # No evolution yet
    result = engine.evolve_trauma_arc(profile, "Shattered Trust")
    assert result["transformed"] is False
    
    # After 10 sessions
    scar.therapy_sessions = 10
    result = engine.evolve_trauma_arc(profile, "Shattered Trust")
    assert result["transformed"] is True
    assert result["new_name"] == "Cautious Trust"
    assert scar.arc_stage == "healing"


def test_addiction_consequences():
    """Test that repeated stim use creates addiction."""
    profile = PsychologicalProfile()
    engine = PsychologicalEngine()
    
    # Use stim 3 times
    for _ in range(3):
        result = engine.apply_coping_mechanism(profile, "stim_injection", success=True)
    
    assert profile.addiction_level > 0.4
    assert "warning" in result


def test_isolation_consequences():
    """Test that repeated meditation creates isolation."""
    profile = PsychologicalProfile()
    engine = PsychologicalEngine()
    
    # Meditate 5 times
    for _ in range(5):
        result = engine.apply_coping_mechanism(profile, "meditate", success=True)
    
    assert profile.isolation_level > 0.4
    assert "warning" in result


def test_difficulty_scaling():
    """Test that trauma increases difficulty."""
    profile = PsychologicalProfile()
    scaler = PsychologicalDifficultyScaler()
    
    # No trauma = low difficulty
    base_diff = scaler.get_difficulty_modifier(profile)
    assert base_diff < 0.1
    
    # Add 3 traumas
    for _ in range(3):
        profile.trauma_scars.append(TraumaScar(
            name="Test",
            description="Test",
            trait_modifier={}
        ))
    
    # Difficulty should increase
    new_diff = scaler.get_difficulty_modifier(profile)
    assert new_diff >= 0.3  # At least +30%


def test_permadeath_check():
    """Test permadeath triggers."""
    profile = PsychologicalProfile()
    scaler = PsychologicalDifficultyScaler()
    
    # Sanity at 0
    profile.sanity = 0.0
    result = scaler.check_permadeath(profile)
    assert result["permadeath"] is True
    
    # Too many fresh traumas
    profile.sanity = 1.0
    for _ in range(5):
        profile.trauma_scars.append(TraumaScar(
            name="Test",
            description="Test",
            trait_modifier={},
            arc_stage="fresh"
        ))
    
    result = scaler.check_permadeath(profile)
    assert result["permadeath"] is True


def test_npc_emotional_memory():
    """Test that NPCs store emotional history."""
    npc = CrewMember(
        id="medic",
        name="Dr. Chen",
        role="Medic"
    )
    
    # Record an emotional moment
    memory = EmotionalMemory(
        emotion=EmotionalState.AFRAID,
        timestamp=datetime.now(),
        context="Player had a panic attack in med bay",
        intensity=0.9
    )
    npc.emotional_history.append(memory)
    
    assert len(npc.emotional_history) == 1
    assert npc.emotional_history[0].emotion == EmotionalState.AFRAID
