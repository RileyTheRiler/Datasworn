"""
Test Phase 5: Immersion & Recovery
"""

from src.psych_profile import PsychologicalProfile, PsychologicalEngine, EmotionalState, TraumaScar
from src.mystery_generator import MysteryConfig


def test_personalized_mystery():
    """Test that mysteries are generated based on character fears."""
    profile = PsychologicalProfile()
    
    # Give character a trauma scar
    scar = TraumaScar(
        name="Shattered Trust",
        description="Test",
        trait_modifier={"paranoia": 0.3}
    )
    profile.trauma_scars.append(scar)
    
    # Generate personalized mystery
    mystery = MysteryConfig(threat_id="")
    mystery.generate_personalized_mystery(profile)
    
    # Should target betrayal fear
    assert mystery.threat_id == "medic"
    assert "confidant" in mystery.threat_motive.lower()
    assert len(mystery.clues) > 0


def test_coping_mechanisms():
    """Test coping mechanism application."""
    profile = PsychologicalProfile()
    engine = PsychologicalEngine()
    
    # High stress
    profile.stress_level = 0.9
    
    # Apply meditation (success)
    result = engine.apply_coping_mechanism(profile, "meditate", success=True)
    assert result["success"] is True
    assert profile.stress_level < 0.9
    
    # Apply stim (has sanity cost)
    profile.stress_level = 0.9
    initial_sanity = profile.sanity
    result = engine.apply_coping_mechanism(profile, "stim_injection", success=True)
    assert profile.sanity < initial_sanity


def test_trauma_healing():
    """Test trauma scar healing over time."""
    profile = PsychologicalProfile()
    engine = PsychologicalEngine()
    
    # Add a trauma scar
    scar = TraumaScar(
        name="Cold Logic",
        description="Test",
        trait_modifier={"logic": 0.4, "empathy": -0.3}
    )
    profile.trauma_scars.append(scar)
    profile.traits["logic"] = 0.6
    profile.traits["empathy"] = 0.2
    
    # Therapy session
    result = engine.heal_trauma_scar(profile, "Cold Logic", progress=1.0)
    assert result["scar"] == "Cold Logic"
    assert scar.trait_modifier["logic"] < 0.4  # Weakened
    assert profile.traits["logic"] < 0.6  # Trait reduced


def test_fear_analysis():
    """Test primary fear detection."""
    profile = PsychologicalProfile()
    
    # Default: unknown
    assert profile.get_primary_fear() == "unknown"
    
    # Add paranoia trait
    profile.traits["paranoia"] = 0.8
    assert profile.get_primary_fear() == "infiltration"
    
    # Trauma overrides trait
    scar = TraumaScar(
        name="Jittery Nerves",
        description="Test",
        trait_modifier={"caution": 0.3}
    )
    profile.trauma_scars.append(scar)
    assert profile.get_primary_fear() == "environmental_threat"
