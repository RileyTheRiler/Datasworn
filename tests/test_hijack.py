import sys
import os
import unittest
from unittest.mock import MagicMock
import json

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.inner_voice import InnerVoiceSystem
from src.director import DirectorAgent

class TestHijack(unittest.TestCase):
    def test_hijack_detection(self):
        voice = InnerVoiceSystem()
        
        # Test No Hijack
        self.assertIsNone(voice.check_hijack())
        
        # Test Hijack
        voice.aspects["amygdala"].dominance = 0.95
        hijack = voice.check_hijack()
        self.assertIsNotNone(hijack)
        self.assertEqual(hijack["aspect"], "Amygdala")
        self.assertIn("RAGE FUGUE", hijack["description"])

    def test_director_override(self):
        director = DirectorAgent()
        director.inner_voice.aspects["cortex"].dominance = 0.95
        
        # Mock LLM to avoid real calls
        director.inner_voice.trigger_voices = MagicMock(return_value=[])
        
        plan = director.analyze({}, "Mock session")
        
        self.assertIn("!!! NEURAL HIJACK IN PROGRESS !!!", plan.notes_for_narrator)
        self.assertIn("ANALYSIS PARALYSIS", plan.notes_for_narrator)
        self.assertIn("The mind snaps.", plan.beats)

if __name__ == "__main__":
    unittest.main()
