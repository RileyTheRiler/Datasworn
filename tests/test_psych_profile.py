import pytest
from src.psych_profile import PsychologicalProfile, PsychologicalEngine, ValueSystem, EmotionalState

def test_profile_initialization():
    profile = PsychologicalProfile()
    assert profile.sanity == 1.0
    assert profile.stress_level == 0.0
    assert ValueSystem.SECURITY in profile.values

def test_stress_update():
    profile = PsychologicalProfile()
    engine = PsychologicalEngine()
    
    engine.update_stress(profile, 0.5)
    assert profile.stress_level == 0.5
    
    engine.update_stress(profile, 0.6)  # Should cap at 1.0
    assert profile.stress_level == 1.0
    assert profile.current_emotion == EmotionalState.OVERWHELMED

def test_sanity_update():
    profile = PsychologicalProfile()
    engine = PsychologicalEngine()
    
    engine.update_sanity(profile, -0.2)
    assert profile.sanity == 0.8
    
    engine.update_sanity(profile, -1.0) # Should cap at 0.0
    assert profile.sanity == 0.0

def test_narrative_context_generation():
    profile = PsychologicalProfile()
    engine = PsychologicalEngine()
    
    profile.values = {ValueSystem.JUSTICE: 0.9}
    profile.traits = {"Honor": 0.8}
    profile.current_emotion = EmotionalState.DETERMINED
    
    context = engine.get_narrative_context(profile)
    
    assert "justice" in context
    assert "Honor" in context
    assert "DETERMINED" in context

def test_memory_unlocking():
    profile = PsychologicalProfile()
    engine = PsychologicalEngine()
    
    from src.psych_profile import MemorySeal
    profile.suppressed_memories = [
        MemorySeal(id="secret_1", description="You saw the Captain sabotage the drive.", seal_integrity=1.0)
    ]
    
    engine.unlock_memory(profile, "secret_1", 0.6)
    assert profile.suppressed_memories[0].seal_integrity == 0.4
    assert not profile.suppressed_memories[0].is_revealed
    
    engine.unlock_memory(profile, "secret_1", 0.5)
    assert profile.suppressed_memories[0].is_revealed
    assert "RECOVERED: You saw the Captain sabotage the drive." in profile.memories

def test_relationship_impact():
    from src.relationship_system import RelationshipWeb
    profile = PsychologicalProfile()
    web = RelationshipWeb()
    
    # Test help impact
    web.apply_action("help", "engineer", psych_profile=profile)
    assert profile.opinions.get("Chen Wei", 0.0) > 0.0
    
    # Test threaten impact
    web.apply_action("threaten", "captain", psych_profile=profile)
    assert profile.stress_level > 0.0
    assert profile.current_emotion == EmotionalState.ANGRY

def test_breaking_point():
    profile = PsychologicalProfile()
    engine = PsychologicalEngine()
    
    # Force high stress
    profile.stress_level = 0.95
    
    # Since it's probabilistic, we'll call direct assign_trauma first to verify logic
    scar = engine.assign_trauma(profile)
    assert len(profile.trauma_scars) == 1
    assert profile.stress_level == 0.4  # Reset
    assert profile.sanity < 1.0        # Sanity cost
    
    # Verify trait modifiers (e.g., Shattered Trust adds paranoia)
    if scar.name == "Shattered Trust":
        assert profile.traits["paranoia"] > 0.2
    elif scar.name == "Cold Logic":
        assert profile.traits["logic"] > 0.0

def test_dialogue_emotional_gating():
    from src.dialogue_system import DialogueSystem, DialogueOption, DialogueNode
    profile = PsychologicalProfile()
    system = DialogueSystem()
    
    # Setup a simple dialogue with a friendly option
    node = DialogueNode(
        id="start",
        speaker="Crew",
        text="Hello.",
        options=[
            DialogueOption(
                id="opt1", 
                text="Friendly greeting",
                restricted_emotion=[EmotionalState.RESENTFUL]
            )
        ],
        is_entry=True
    )
    system.register_dialogue("crewman", [node])
    system.start_dialogue("crewman")
    
    # Case 1: Neutral emotion -> Option available
    available = system.get_available_options(psych_profile=profile)
    assert len(available) == 1
    
    # Case 2: Resentful emotion -> Friendly option gated
    profile.current_emotion = EmotionalState.RESENTFUL
    available = system.get_available_options(psych_profile=profile)
    assert len(available) == 0

def test_move_modifiers():
    profile = PsychologicalProfile()
    engine = PsychologicalEngine()
    
    # Default: no penalty
    assert engine.get_move_modifier(profile, "heart") == 0
    
    # High stress + heart = -1
    profile.stress_level = 0.8
    assert engine.get_move_modifier(profile, "heart") == -1
    
    # Afraid + iron = -1
    profile.stress_level = 0.0
    profile.current_emotion = EmotionalState.AFRAID
    assert engine.get_move_modifier(profile, "iron") == -1
    
    # Overwhelmed = -1 on all
    profile.current_emotion = EmotionalState.OVERWHELMED
    assert engine.get_move_modifier(profile, "wits") == -1
    assert engine.get_move_modifier(profile, "edge") == -1

def test_hallucination_trigger():
    profile = PsychologicalProfile()
    engine = PsychologicalEngine()
    
    # Sanity >= 0.3 = No hallucination
    profile.sanity = 0.5
    assert engine.generate_hallucination(profile) is None
    
    # Sanity < 0.3 = Hallucination
    profile.sanity = 0.2
    hallucination = engine.generate_hallucination(profile)
    assert hallucination is not None
    assert len(hallucination) > 10  # It's a sentence

def test_evolution_heuristic():
    profile = PsychologicalProfile()
    engine = PsychologicalEngine()
    
    engine.evolve_from_event(profile, "The crew betrayed you and left you to die.", outcome="miss")
    
    assert profile.stress_level > 0.0
    assert profile.current_emotion in [EmotionalState.AFRAID, EmotionalState.SUSPICIOUS, EmotionalState.OVERWHELMED]
    assert profile.traits.get("paranoia", 0.0) > 0.0
