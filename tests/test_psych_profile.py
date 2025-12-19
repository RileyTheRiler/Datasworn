import sys
import os
import unittest
from unittest.mock import MagicMock
import json

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.psych_profile import PsychProfile, PsychoAnalyst

class TestPsychProfile(unittest.TestCase):
    def test_profile_update(self):
        profile = PsychProfile()
        profile.update_trait("aggression", 0.1)
        self.assertEqual(profile.aggression, 0.6)
        
        # Test new fields
        profile.update_trait("sunk_cost_fallacy", 0.5)
        self.assertEqual(profile.sunk_cost_fallacy, 0.5)

    def test_analyist_mock_turn_exhaustive(self):
        # Setup mock client
        mock_client = MagicMock()
        
        mock_response = {
            "message": {
                "content": json.dumps({
                    "trait_updates": {"aggression": 0.2, "discipline": -0.1},
                    "bias_updates": {"sunk_cost_fallacy": 0.3},
                    "new_values": ["Justice"],
                    "new_taboos": ["Killing innocents"],
                    "decision_analysis": "Player risked safety for justice."
                })
            }
        }
        mock_client.chat.return_value = mock_response
        
        # Inject mock directly
        analyst = PsychoAnalyst(_client=mock_client)
        analyst.analyze_turn("I save the civilian instead of the data", "Burning station")
        
        self.assertAlmostEqual(analyst.profile.aggression, 0.7)
        self.assertAlmostEqual(analyst.profile.discipline, 0.4)
        self.assertAlmostEqual(analyst.profile.sunk_cost_fallacy, 0.3)
        self.assertIn("Justice", analyst.profile.core_values)
        self.assertIn("Killing innocents", analyst.profile.taboos)
        self.assertEqual(len(analyst.profile.decision_log), 1)

    def test_subversion_mock(self):
        # Setup mock client
        mock_client = MagicMock()
        
        mock_response = {
            "message": {
                "content": json.dumps({
                    "type": "subversion",
                    "target_vector": "Sunk Cost Fallacy",
                    "suggestion": "The data they saved is corrupted."
                })
            }
        }
        mock_client.chat.return_value = mock_response
        
        # Inject mock directly
        analyst = PsychoAnalyst(_client=mock_client)
        analyst.profile.sunk_cost_fallacy = 0.8
        
        suggestion = analyst.propose_subversion("Context")
        self.assertEqual(suggestion, "[Sunk Cost Fallacy] The data they saved is corrupted.")

if __name__ == "__main__":
    unittest.main()
