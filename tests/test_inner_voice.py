import sys
import os
import unittest
from unittest.mock import MagicMock
import json

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.inner_voice import InnerVoiceSystem
from src.psych_profile import PsychologicalProfile, ValueSystem

class TestInnerVoice(unittest.TestCase):
    def test_initialization(self):
        voice = InnerVoiceSystem()
        self.assertIn("amygdala", voice.aspects)
        self.assertIn("cortex", voice.aspects)
        self.assertIn("hippocampus", voice.aspects)
        self.assertEqual(voice.aspects["amygdala"].voice_name, "Amygdala")

    def test_sync_profile(self):
        voice = InnerVoiceSystem()
        profile = PsychologicalProfile()
        profile.traits = {"paranoia": 0.9, "resilience": 0.8}
        profile.values = {ValueSystem.CURIOSITY: 0.2, ValueSystem.SECURITY: 0.5}
        profile.stress_level = 0.5
        
        voice.sync_with_profile(profile)
        
        # Amygdala = max(paranoia, stress) = max(0.9, 0.5) = 0.9
        self.assertEqual(voice.aspects["amygdala"].dominance, 0.9)
        # Cortex = (resilience + Discipline/Order value) / 2
        # resilience=0.8, discipline=0.5 (default in profile), max(0.5, 0.5) = 0.5. (0.8+0.5)/2 = 0.65
        self.assertAlmostEqual(voice.aspects["cortex"].dominance, 0.65)
        # Hippocampus = (curiosity + memory_score) / 2 = (0.2 + 0)/2 = 0.1
        self.assertEqual(voice.aspects["hippocampus"].dominance, 0.1)

    def test_trigger_mock(self):
        mock_client = MagicMock()
        mock_response = {
            "message": {
                "content": json.dumps({
                    "voices": [
                        {"aspect": "Amygdala", "content": "RUN!", "intensity": 0.9},
                        {"aspect": "Cortex", "content": "Wait, calculate.", "intensity": 0.4}
                    ]
                })
            }
        }
        mock_client.chat.return_value = mock_response
        
        voice = InnerVoiceSystem(_client=mock_client)
        
        # Boost Amygdala
        voice.aspects["amygdala"].dominance = 1.0
        voice.aspects["cortex"].dominance = 0.5
        
        voices = voice.trigger_voices("Monster appears")
        
        self.assertEqual(len(voices), 2)
        self.assertEqual(voices[0]["aspect"], "Amygdala")
        self.assertEqual(voices[0]["content"], "RUN!")

if __name__ == "__main__":
    unittest.main()
