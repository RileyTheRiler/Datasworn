"""
Test the complete feedback learning loop.
Verifies that preferences are learned and automatically injected into prompts.
"""

import pytest
from src.feedback_learning import (
    FeedbackLearningEngine,
    GeneratedParagraph,
    PreferenceProfile,
    PromptModifier,
    ExampleRetriever
)

def test_feedback_recording():
    """Test that feedback is recorded correctly."""
    engine = FeedbackLearningEngine(db_path=":memory:")
    
    context = {
        "pacing": "fast",
        "tone": "tense",
        "scene_type": "action",
        "session_number": 1,
    }
    
    # Record some feedback
    para_id = engine.record_feedback(
        "The corridor explodes. You dive left.",
        accepted=True,
        context=context
    )
    
    assert para_id is not None
    
    # Verify it was saved
    stats = engine.db.get_statistics()
    assert stats["total_paragraphs"] == 1
    assert stats["accepted"] == 1

def test_preference_analysis():
    """Test that preferences are extracted from feedback patterns."""
    engine = FeedbackLearningEngine(db_path=":memory:")
    
    # Create pattern: short sentences accepted, long sentences rejected
    for i in range(25):
        if i % 2 == 0:
            # Short, accepted
            engine.record_feedback(
                "You run. The door slams. Silence.",
                accepted=True,
                context={"pacing": "fast", "tone": "tense", "session_number": i}
            )
        else:
            # Long, rejected
            engine.record_feedback(
                "You find yourself running through the corridor, and suddenly the door slams behind you with a loud noise, leaving you in complete silence.",
                accepted=False,
                context={"pacing": "fast", "tone": "tense", "session_number": i}
            )
    
    # Analyze preferences
    profile = engine.run_preference_analysis()
    
    assert profile is not None
    assert profile.total_decisions_analyzed == 25
    # Short sentences should be preferred
    assert profile.preferred_sentence_length[0] < 10  # Min length should be low

def test_prompt_modification():
    """Test that learned preferences generate prompt modifications."""
    profile = PreferenceProfile(
        preferred_sentence_length=(8.0, 12.0),
        forbidden_words=["suddenly", "very"],
        max_paragraph_words=100,
        preferred_ending_style="question",
        total_decisions_analyzed=50,
    )
    
    modifier = PromptModifier(profile)
    modifications = modifier.generate_modifications()
    
    assert modifications != ""
    assert "8-12 words" in modifications
    assert "suddenly" in modifications
    assert "question" in modifications.lower()

def test_few_shot_retrieval():
    """Test that similar examples are retrieved for few-shot prompting."""
    engine = FeedbackLearningEngine(db_path=":memory:")
    
    # Add some accepted examples with specific tone
    for i in range(5):
        engine.record_feedback(
            f"Tense example {i}. Short. Punchy.",
            accepted=True,
            context={"pacing": "fast", "tone": "tense", "session_number": i}
        )
    
    # Add some rejected examples
    for i in range(3):
        engine.record_feedback(
            f"This is a very long and rambling rejected example number {i}.",
            accepted=False,
            context={"pacing": "fast", "tone": "tense", "session_number": i}
        )
    
    # Retrieve examples
    retriever = ExampleRetriever(engine.db)
    positive = retriever.get_positive_examples(
        {"pacing": "fast", "tone": "tense"},
        n=3
    )
    
    assert len(positive) == 3
    assert all("Tense example" in ex for ex in positive)

def test_complete_feedback_loop():
    """
    End-to-end test: Record feedback → Analyze → Generate modifications → Inject.
    """
    engine = FeedbackLearningEngine(db_path=":memory:")
    
    # Simulate 25 decisions with clear pattern
    good_examples = [
        "You freeze. The shadow moves.",
        "Metal groans. Pressure drops.",
        "Run. Now.",
    ]
    
    bad_examples = [
        "You suddenly find yourself very scared and you can't help but run away.",
        "It seemed to be a very dangerous situation that appeared out of nowhere.",
    ]
    
    for i in range(10):
        for good in good_examples:
            engine.record_feedback(
                good,
                accepted=True,
                context={"pacing": "fast", "tone": "tense", "session_number": i}
            )
        for bad in bad_examples:
            engine.record_feedback(
                bad,
                accepted=False,
                context={"pacing": "fast", "tone": "tense", "session_number": i}
            )
    
    # Should have 50 total decisions
    stats = engine.db.get_statistics()
    assert stats["total_paragraphs"] == 50
    
    # Analyze preferences
    profile = engine.run_preference_analysis()
    assert profile.total_decisions_analyzed == 50
    
    # Should detect forbidden words
    assert any(word in profile.forbidden_words for word in ["suddenly", "very", "seemed"])
    
    # Generate modifications
    modifier = PromptModifier(profile)
    modifications = modifier.generate_modifications()
    
    # Should include guidance
    assert "Never use" in modifications or "forbidden" in modifications.lower()
    
    # Get few-shot examples
    retriever = ExampleRetriever(engine.db)
    few_shot = retriever.build_few_shot_prompt(
        {"pacing": "fast", "tone": "tense"},
        n_positive=2,
        n_negative=1
    )
    
    assert "EXAMPLES THE PLAYER LOVED" in few_shot
    assert "freeze" in few_shot.lower() or "metal" in few_shot.lower()

def test_automatic_reanalysis():
    """Test that preferences are re-analyzed after 10 new decisions."""
    engine = FeedbackLearningEngine(db_path=":memory:")
    
    # Record 25 decisions
    for i in range(25):
        engine.record_feedback(
            f"Example {i}",
            accepted=True,
            context={"session_number": i}
        )
    
    # First analysis
    profile1 = engine.analyze_preferences()
    engine.db.save_preferences(profile1)
    engine.current_profile = profile1
    
    assert profile1.total_decisions_analyzed == 25
    
    # Add 10 more decisions
    for i in range(25, 35):
        engine.record_feedback(
            f"Example {i}",
            accepted=True,
            context={"session_number": i}
        )
    
    # Check if reanalysis is needed
    stats = engine.db.get_statistics()
    should_reanalyze = stats["total_paragraphs"] - profile1.total_decisions_analyzed >= 10
    
    assert should_reanalyze
    
    # Reanalyze
    profile2 = engine.analyze_preferences()
    assert profile2.total_decisions_analyzed == 35
