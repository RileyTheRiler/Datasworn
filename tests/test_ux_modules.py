"""
Tests for UX improvement modules.
"""

import pytest
from dataclasses import dataclass
from typing import List


# ============================================================================
# Vow Tracker Tests
# ============================================================================

class TestVowTracker:
    """Tests for vow_tracker.py"""

    def test_format_vow_for_display(self):
        """Test vow formatting with progress calculation."""
        from src.vow_tracker import format_vow_for_display

        display = format_vow_for_display(
            name="Find the saboteur",
            rank="dangerous",
            ticks=20,  # 50% progress
        )

        assert display.name == "Find the saboteur"
        assert display.rank == "dangerous"
        assert display.progress_boxes == 5  # 20 ticks / 4 = 5 boxes
        assert display.progress_percent == 50.0
        assert display.phase == "developing"
        assert not display.is_fulfilled
        assert not display.is_forsaken

    def test_vow_phase_detection(self):
        """Test that vow phases are detected correctly."""
        from src.vow_tracker import get_vow_phase

        # Establishing phase (0-25%)
        phase, action, tension = get_vow_phase(0.1)
        assert phase == "establishing"

        # Developing phase (25-50%)
        phase, action, tension = get_vow_phase(0.3)
        assert phase == "developing"

        # Approaching climax (50-75%)
        phase, action, tension = get_vow_phase(0.6)
        assert phase == "approaching_climax"

        # Ready to fulfill (75-100%)
        phase, action, tension = get_vow_phase(0.8)
        assert phase == "ready_to_fulfill"

    def test_calculate_mark_progress(self):
        """Test progress calculation for marking progress."""
        from src.vow_tracker import calculate_mark_progress

        # Dangerous vow: 2 boxes (8 ticks) per mark
        result = calculate_mark_progress(current_ticks=0, rank="dangerous")
        assert result["new_ticks"] == 8
        assert result["boxes_filled"] == 2

        # Epic vow: 1 tick per mark
        result = calculate_mark_progress(current_ticks=0, rank="epic")
        assert result["new_ticks"] == 1
        assert result["boxes_filled"] == 0  # Less than 1 box

        # Test milestone detection
        result = calculate_mark_progress(current_ticks=8, rank="dangerous")
        assert result["new_ticks"] == 16  # 40%
        assert len(result["milestones"]) == 1  # Crossed 25%

    def test_vow_reminder_generation(self):
        """Test narrative reminder generation."""
        from src.vow_tracker import generate_vow_reminder, format_vow_for_display

        vows = [
            format_vow_for_display("Find the saboteur", "dangerous", 30),
            format_vow_for_display("Escape the sector", "formidable", 10),
        ]

        reminder = generate_vow_reminder(vows)

        assert "[ACTIVE VOWS" in reminder
        assert "Find the saboteur" in reminder
        assert "█" in reminder  # Progress bar


# ============================================================================
# Consequence Tracker Tests
# ============================================================================

class TestConsequenceTracker:
    """Tests for consequence_tracker.py"""

    def test_add_consequence(self):
        """Test adding a consequence."""
        from src.consequence_tracker import (
            ConsequenceTracker,
            ConsequenceType,
            ConsequenceSeverity,
        )

        tracker = ConsequenceTracker()
        c = tracker.add_consequence(
            description="Guards are suspicious",
            type=ConsequenceType.SUSPICION,
            severity=ConsequenceSeverity.MODERATE,
            source="Compel (weak hit)",
        )

        assert c.description == "Guards are suspicious"
        assert c.type == ConsequenceType.SUSPICION
        assert c.severity == ConsequenceSeverity.MODERATE
        assert not c.resolved

    def test_resolve_consequence(self):
        """Test resolving a consequence."""
        from src.consequence_tracker import ConsequenceTracker

        tracker = ConsequenceTracker()
        c = tracker.add_consequence("Test consequence")

        success = tracker.resolve_consequence(c.id, "Talked my way out")

        assert success
        assert c.resolved
        assert c.resolution == "Talked my way out"

    def test_escalate_consequence(self):
        """Test consequence escalation."""
        from src.consequence_tracker import (
            ConsequenceTracker,
            ConsequenceSeverity,
        )

        tracker = ConsequenceTracker()
        c = tracker.add_consequence(
            description="Minor issue",
            severity=ConsequenceSeverity.MINOR,
        )

        tracker.escalate_consequence(c.id)

        assert c.severity == ConsequenceSeverity.MODERATE
        assert c.escalation_count == 1

    def test_get_stale_consequences(self):
        """Test finding stale consequences."""
        from src.consequence_tracker import ConsequenceTracker

        tracker = ConsequenceTracker()
        tracker.add_consequence("Old issue")

        # Advance 6 turns
        for _ in range(6):
            tracker.advance_turn()

        stale = tracker.get_stale_consequences(turns_threshold=5)
        assert len(stale) == 1

    def test_consequence_from_roll(self):
        """Test consequence suggestions from rolls."""
        from src.consequence_tracker import generate_consequence_from_roll

        # Strong hit - no consequence
        result = generate_consequence_from_roll("strong_hit", "Face Danger", "")
        assert result is None

        # Weak hit - minor consequence
        result = generate_consequence_from_roll("weak_hit", "Face Danger", "")
        assert result is not None
        assert result["severity"] == "minor"

        # Miss - moderate consequence
        result = generate_consequence_from_roll("miss", "Face Danger", "")
        assert result is not None
        assert result["severity"] == "moderate"


# ============================================================================
# Move Suggester Tests
# ============================================================================

class TestMoveSuggester:
    """Tests for move_suggester.py"""

    def test_suggest_moves_combat(self):
        """Test move suggestions for combat actions."""
        from src.move_suggester import suggest_moves

        suggestions = suggest_moves("I attack the guard with my weapon")

        assert len(suggestions) > 0
        move_names = [s.move_name for s in suggestions]
        assert any("Strike" in name or "Fray" in name for name in move_names)

    def test_suggest_moves_social(self):
        """Test move suggestions for social actions."""
        from src.move_suggester import suggest_moves

        suggestions = suggest_moves("I try to convince the captain to help us")

        assert len(suggestions) > 0
        move_names = [s.move_name for s in suggestions]
        assert any("Compel" in name for name in move_names)

    def test_suggest_moves_exploration(self):
        """Test move suggestions for exploration."""
        from src.move_suggester import suggest_moves

        suggestions = suggest_moves("I search the room for clues")

        assert len(suggestions) > 0
        move_names = [s.move_name for s in suggestions]
        assert any("Gather" in name or "Explore" in name for name in move_names)

    def test_get_move_help(self):
        """Test getting move help."""
        from src.move_suggester import get_move_help

        help_data = get_move_help("Face Danger")

        assert help_data is not None
        assert help_data["name"] == "Face Danger"
        assert "trigger" in help_data
        assert "outcomes" in help_data

    def test_should_suggest_moves(self):
        """Test when to show move suggestions."""
        from src.move_suggester import should_suggest_moves

        # Should suggest for action descriptions
        assert should_suggest_moves("I try to sneak past the guards")

        # Should not suggest for commands
        assert not should_suggest_moves("!status")

        # Should not suggest for short inputs
        assert not should_suggest_moves("ok")


# ============================================================================
# Session Continuity Tests
# ============================================================================

class TestSessionContinuity:
    """Tests for session_continuity.py"""

    def test_session_tracker_events(self):
        """Test recording events."""
        from src.session_continuity import SessionTracker

        tracker = SessionTracker()
        tracker.record_event(
            description="Discovered a hidden passage",
            event_type="discovery",
            importance=0.7,
        )

        assert len(tracker.events) == 1
        assert tracker.events[0].description == "Discovered a hidden passage"

    def test_record_roll(self):
        """Test recording rolls."""
        from src.session_continuity import SessionTracker

        tracker = SessionTracker()
        tracker.record_roll("Face Danger", "miss", "Failed to escape")

        assert len(tracker.events) == 1
        assert tracker.events[0].importance == 0.7  # Miss has high importance

    def test_record_npc_encounter(self):
        """Test recording NPC encounters."""
        from src.session_continuity import SessionTracker

        tracker = SessionTracker()
        tracker.record_npc_encounter("Captain Vasquez")
        tracker.record_npc_encounter("Captain Vasquez")  # Duplicate

        assert len(tracker.npcs_encountered) == 1
        assert "Captain Vasquez" in tracker.npcs_encountered

    def test_generate_recap(self):
        """Test recap generation."""
        from src.session_continuity import SessionTracker, generate_session_recap

        tracker = SessionTracker()
        tracker.record_event("Swore a vow", "vow", 0.8)
        tracker.record_npc_encounter("Engineer Chen")
        tracker.record_location_visit("Engine Room")

        recap = generate_session_recap(tracker)

        assert "Previously" in recap
        assert "Engineer Chen" in recap or "Engine Room" in recap

    def test_generate_cliffhanger(self):
        """Test cliffhanger generation."""
        from src.session_continuity import (
            SessionTracker,
            generate_cliffhanger,
        )

        tracker = SessionTracker()
        tracker.record_vow_change("Find the truth", "sworn")

        cliffhanger = generate_cliffhanger(tracker, "", 0.8)

        assert len(cliffhanger) > 0
        assert "oath" in cliffhanger.lower() or "truth" in cliffhanger.lower()

    def test_session_summary(self):
        """Test session summary generation."""
        from src.session_continuity import (
            SessionTracker,
            generate_session_summary,
        )

        tracker = SessionTracker()
        tracker.record_event("Important discovery", "discovery", 0.9)
        tracker.tension_high_point = 0.85

        summary = generate_session_summary(tracker)

        assert summary.mood == "intense"  # High tension
        assert len(summary.major_events) > 0


# ============================================================================
# Config and Logging Tests
# ============================================================================

class TestConfig:
    """Tests for config.py"""

    def test_config_defaults(self):
        """Test default configuration values."""
        from src.config import GameConfig

        config = GameConfig()

        assert config.paths.feedback_db == "saves/feedback_learning.db"
        assert config.llm.temperature == 0.85
        assert config.director.tension_threshold_high == 0.8

    def test_config_reload(self):
        """Test config reloading."""
        from src.config import reload_config

        config = reload_config()

        assert config is not None
        assert hasattr(config, "paths")


class TestLogging:
    """Tests for logging_config.py"""

    def test_get_logger(self):
        """Test getting a logger."""
        from src.logging_config import get_logger

        logger = get_logger("test")

        assert logger is not None
        assert "starforged" in logger.name

    def test_logged_operation(self):
        """Test LoggedOperation context manager."""
        from src.logging_config import get_logger, LoggedOperation

        logger = get_logger("test")

        with LoggedOperation(logger, "test operation"):
            pass  # Operation succeeds

        # Should not raise


# ============================================================================
# Run tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
