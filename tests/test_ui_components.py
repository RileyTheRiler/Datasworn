import sys
import os
import unittest
from unittest.mock import MagicMock

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ui import format_quests, format_combat, format_companions
from src.game_state import QuestLoreState, WorldState, CompanionManagerState

class TestUIComponents(unittest.TestCase):

    def test_format_combat(self):
        print("\nTesting format_combat...")
        # Test inactive
        world = WorldState(combat_active=False)
        output = format_combat(world)
        self.assertIn("*Safe*", output)
        
        # Test active
        world.combat_active = True
        world.enemy_count = 3
        world.enemy_strength = 2.5
        world.threat_level = 0.8
        output = format_combat(world)
        print(f"Output:\n{output}")
        self.assertIn("COMBAT ACTIVE", output)
        self.assertIn("Enemies:** 3", output)

    def test_format_companions(self):
        print("\nTesting format_companions...")
        # Test solo
        state = CompanionManagerState()
        output = format_companions(state)
        self.assertIn("*Solo*", output)
        
        # Test active
        state.companions = {
            "garrus": {"name": "Garrus", "archetype": "sniper", "loyalty": 8}
        }
        state.active_companion = "garrus"
        output = format_companions(state)
        print(f"Output:\n{output}")
        self.assertIn("Garrus", output)
        self.assertIn("Sniper", output)

    def test_format_quests_dict(self):
        print("\nTesting format_quests (dict input)...")
        # Mock quest engine dict structure
        data = {
            "quests": {
                "quests": {
                    "q1": {
                        "quest_id": "q1", 
                        "title": "Main Quest", 
                        "description": "Desc",
                        "quest_type": "main",
                        "status": "active",
                        "objectives": [{"objective_id": "o1", "description": "Do thing", "is_completed": True}]
                    }
                }
            }
        }
        output = format_quests(data)
        print(f"Output:\n{output}")
        self.assertIn("Main Quest", output)
        self.assertIn("Do thing", output)

if __name__ == '__main__':
    unittest.main()
