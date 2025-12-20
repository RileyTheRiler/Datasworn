"""
Test suite for NPC API endpoint.
"""
import sys
import os
import unittest
from fastapi.testclient import TestClient

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.server import app, SESSIONS
from src.game_state import create_initial_state
from src.relationship_system import RelationshipWeb


class TestNPCEndpoint(unittest.TestCase):
    """Test cases for /api/npc/{npc_id} endpoint."""

    def setUp(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        # Create a test session with relationships
        SESSIONS["default"] = create_initial_state("TestChar")
        
        # Initialize relationships
        relationships = RelationshipWeb()
        SESSIONS["default"]["relationships"].crew = {
            k: v.to_dict() for k, v in relationships.crew.items()
        }

    def tearDown(self):
        """Clean up after tests."""
        if "default" in SESSIONS:
            del SESSIONS["default"]

    def test_get_npc_by_id(self):
        """Test fetching NPC by their ID."""
        response = self.client.get("/api/npc/captain")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn("name", data)
        self.assertIn("role", data)
        self.assertIn("trust", data)
        self.assertIn("suspicion", data)
        self.assertIn("disposition", data)
        self.assertIn("image_url", data)

    def test_get_npc_by_name(self):
        """Test fetching NPC by their name (case-insensitive)."""
        response = self.client.get("/api/npc/Commander%20Vasquez")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data["name"], "Commander Vasquez")
        self.assertEqual(data["role"], "Captain")

    def test_get_npc_case_insensitive(self):
        """Test that NPC lookup is case-insensitive."""
        response1 = self.client.get("/api/npc/CAPTAIN")
        response2 = self.client.get("/api/npc/captain")
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response1.json()["name"], response2.json()["name"])

    def test_get_npc_not_found(self):
        """Test 404 response for unknown NPC."""
        response = self.client.get("/api/npc/unknown_character")
        self.assertEqual(response.status_code, 404)

    def test_get_npc_session_not_found(self):
        """Test 404 response when session doesn't exist."""
        response = self.client.get("/api/npc/captain?session_id=nonexistent")
        self.assertEqual(response.status_code, 404)
        self.assertIn("Session not found", response.json()["detail"])

    def test_disposition_calculation(self):
        """Test that disposition is calculated correctly based on trust/suspicion."""
        # Modify trust levels in session
        SESSIONS["default"]["relationships"].crew["captain"]["trust"] = 0.8
        
        response = self.client.get("/api/npc/captain")
        data = response.json()
        
        # High trust should result in "loyal" disposition
        self.assertEqual(data["disposition"], "loyal")
        
        # Test hostile disposition
        SESSIONS["default"]["relationships"].crew["security"]["trust"] = 0.2
        SESSIONS["default"]["relationships"].crew["security"]["suspicion"] = 0.7
        
        response = self.client.get("/api/npc/security")
        data = response.json()
        self.assertEqual(data["disposition"], "hostile")

    def test_known_facts_returned(self):
        """Test that known_facts are included in response."""
        # Add known facts
        SESSIONS["default"]["relationships"].crew["medic"]["known_facts"] = [
            "Saved your life during the incident",
            "Has access to medical supplies"
        ]
        
        response = self.client.get("/api/npc/medic")
        data = response.json()
        
        self.assertIn("known_facts", data)
        self.assertEqual(len(data["known_facts"]), 2)

    def test_image_url_fallback(self):
        """Test that missing image_url uses placeholder."""
        response = self.client.get("/api/npc/captain")
        data = response.json()
        
        # Should have a fallback image URL
        self.assertIn("image_url", data)
        self.assertTrue(len(data["image_url"]) > 0)


if __name__ == "__main__":
    unittest.main()
