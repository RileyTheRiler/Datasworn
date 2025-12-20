import sys
import os
import unittest
from fastapi.testclient import TestClient

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.server import app, SESSIONS
from src.game_state import create_initial_state

class TestServerIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Manually seed a session
        SESSIONS["default"] = create_initial_state("TestChar")
        
    def test_get_psyche(self):
        response = self.client.get("/api/psyche/default")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("voice_dominance", data)
        self.assertIn("profile", data)

    def test_director_integration_mock(self):
        # SESSIONS["default"] is a TypedDict.
        # SESSIONS["default"]["psyche"] is a PsycheState (BaseModel)
        # SESSIONS["default"]["psyche"].profile is a PsychologicalProfile (BaseModel)
        SESSIONS["default"]["psyche"].profile.traits["paranoia"] = 0.9
        
        response = self.client.get("/api/psyche/default")
        data = response.json()
        self.assertEqual(data["profile"]["traits"]["paranoia"], 0.9)

if __name__ == "__main__":
    unittest.main()
