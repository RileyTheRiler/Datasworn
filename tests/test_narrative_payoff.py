import unittest
from unittest.mock import MagicMock, ANY
from dataclasses import dataclass
from typing import List

# Import necessary classes
# We use try/except block to handle potential import errors if environment isn't fully set up
try:
    from src.narrative_orchestrator import NarrativeOrchestrator
    from src.smart_event_detection import SmartEventDetector, DetectedEvent, EventType
    from src.narrative_memory import PlantType, NarrativeMemory
except ImportError:
    # If imports fail, we'll define mocks for the purpose of the test structure
    pass

class TestNarrativePayoff(unittest.TestCase):
    def setUp(self):
        # Create the orchestrator
        # We mock the heavy dependencies to avoid complex initialization
        self.orchestrator = NarrativeOrchestrator()
        
        # Mock the event detector
        self.mock_detector = MagicMock()
        self.orchestrator.event_detector = self.mock_detector
        
        # Mock the narrative memory to check calls
        self.orchestrator.narrative_memory = MagicMock()

    def test_process_interaction_plants_promise(self):
        """Test that a detected PROMISE event is correctly planted in memory."""
        
        # Setup the mock event
        mock_event = MagicMock()
        mock_event.event_type = EventType.PROMISE
        mock_event.description = "I promise to return"
        mock_event.severity = 5
        mock_event.entities = ["Hero", "Villain"]
        mock_event.location = "Castle"
        
        # Configure detector to return this event
        self.mock_detector.detect_events.return_value = [mock_event]
        
        # Call the method under test
        self.orchestrator.process_interaction(
            player_input="I swear it.",
            narrative_output="The hero raised their sword. 'I promise to return,' they shouted.",
            location="Castle",
            active_npcs=[]
        )
        
        # Verify detect_events was called
        self.mock_detector.detect_events.assert_called_once()
        
        # Verify plant_element was called with correct mapping
        self.orchestrator.narrative_memory.plant_element.assert_called_with(
            plant_type=PlantType.PROMISE,
            description="I promise to return (promise)", # expected format
            importance=5,
            involved_characters=["Hero", "Villain"],
            related_themes=["Castle"]
        )

    def test_process_interaction_plants_threat(self):
        """Test that a detected KILL/THREAT event is mapped to THREAT plant."""
        
        mock_event = MagicMock()
        mock_event.event_type = EventType.THREAT
        mock_event.description = "You will pay for this"
        mock_event.severity = 8
        mock_event.entities = ["Villain"]
        mock_event.location = "Dungeon"
        
        self.mock_detector.detect_events.return_value = [mock_event]
        
        self.orchestrator.process_interaction(
            player_input="Go ahead, try.",
            narrative_output="The villain laughed. 'You will pay for this!'",
            location="Dungeon",
            active_npcs=[]
        )
        
        self.orchestrator.narrative_memory.plant_element.assert_called_with(
            plant_type=PlantType.THREAT,
            description="You will pay for this (threat)",
            importance=8,
            involved_characters=["Villain"],
            related_themes=["Dungeon"]
        )

if __name__ == '__main__':
    unittest.main()
