"""
Unit tests for the Tactical Blueprint Generator.
"""

import sys
import os
import unittest

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.blueprint_generator import (
    extract_cover_spots,
    extract_entry_points,
    get_zone_layout_description,
    get_npc_disposition_color,
    calculate_npc_grid_position,
    generate_tactical_prompt,
    extract_tactical_metadata,
    generate_cache_key,
    ZONE_COVER_SPOTS,
    ZONE_ENTRY_POINTS,
)


class TestZoneDataExtraction(unittest.TestCase):
    """Test zone-specific tactical data extraction."""
    
    def test_extract_cover_spots_bar(self):
        """Bar zones should have bar counter, tables, columns."""
        cover = extract_cover_spots("bar")
        self.assertTrue(any("bar counter" in c.lower() for c in cover))
        self.assertTrue(any("table" in c.lower() for c in cover))
    
    def test_extract_cover_spots_military(self):
        """Military zones should have barricades and blast shields."""
        cover = extract_cover_spots("military")
        self.assertTrue(any("barricade" in c.lower() for c in cover))
        self.assertTrue(any("blast" in c.lower() or "shield" in c.lower() for c in cover))
    
    def test_extract_cover_spots_unknown_zone(self):
        """Unknown zones should return default cover."""
        cover = extract_cover_spots("unknown_zone_type")
        self.assertEqual(len(cover), 1)
        self.assertIn("obstacles", cover[0].lower())
    
    def test_extract_entry_points_bar(self):
        """Bar zones should have main entrance and back door."""
        entries = extract_entry_points("bar")
        self.assertTrue(any("main" in e.lower() for e in entries))
        self.assertTrue(any("back" in e.lower() for e in entries))
    
    def test_extract_entry_points_wilderness(self):
        """Wilderness should have open terrain entry."""
        entries = extract_entry_points("wilderness")
        self.assertTrue(any("open" in e.lower() or "all directions" in e.lower() for e in entries))
    
    def test_get_zone_layout_description(self):
        """Zone layouts should return non-empty descriptions."""
        for zone_type in ["bar", "market", "military", "industrial", "derelict", "wilderness"]:
            layout = get_zone_layout_description(zone_type)
            self.assertIsInstance(layout, str)
            self.assertGreater(len(layout), 10)


class TestNPCProcessing(unittest.TestCase):
    """Test NPC disposition and positioning."""
    
    def test_npc_disposition_hostile(self):
        """Hostile NPCs should be red."""
        npc = {"disposition": "hostile", "role": "raider"}
        self.assertEqual(get_npc_disposition_color(npc), "red")
    
    def test_npc_disposition_friendly(self):
        """Friendly NPCs should be green."""
        npc = {"disposition": "friendly", "role": "merchant"}
        self.assertEqual(get_npc_disposition_color(npc), "green")
    
    def test_npc_disposition_neutral(self):
        """Neutral NPCs should be yellow."""
        npc = {"disposition": "neutral", "role": "bystander"}
        self.assertEqual(get_npc_disposition_color(npc), "yellow")
    
    def test_npc_disposition_guard_role(self):
        """Guards should be orange (potentially hostile)."""
        npc = {"disposition": "neutral", "role": "security guard"}
        self.assertEqual(get_npc_disposition_color(npc), "orange")
    
    def test_npc_grid_position_single(self):
        """Single NPC should be centered."""
        pos = calculate_npc_grid_position(0, 1, 600, 500)
        self.assertEqual(pos[0], 300)  # Center x
        self.assertGreater(pos[1], 0)
        self.assertLess(pos[1], 250)  # Upper half
    
    def test_npc_grid_position_multiple(self):
        """Multiple NPCs should be distributed."""
        positions = [
            calculate_npc_grid_position(i, 3, 600, 500)
            for i in range(3)
        ]
        # All should be in different positions
        x_coords = [p[0] for p in positions]
        self.assertEqual(len(set(x_coords)), 3)  # All unique


class TestPromptGeneration(unittest.TestCase):
    """Test tactical prompt generation."""
    
    def test_generate_tactical_prompt_basic(self):
        """Prompt should include location and zone type."""
        game_state = {
            "world": {
                "current_location": "The Rusty Anchor",
                "location_type": "bar",
                "npcs": [],
                "combat_active": False
            },
            "memory": {"current_scene": ""},
            "combat_state": {}
        }
        prompt = generate_tactical_prompt(game_state)
        
        self.assertIn("Rusty Anchor", prompt)
        self.assertIn("BAR", prompt.upper())
        self.assertIn("grid", prompt.lower())
    
    def test_generate_tactical_prompt_with_npcs(self):
        """Prompt should include NPC markers."""
        game_state = {
            "world": {
                "current_location": "Market",
                "location_type": "market",
                "npcs": [
                    {"name": "Vendor", "role": "merchant", "disposition": "neutral"},
                    {"name": "Guard", "role": "security", "disposition": "hostile"}
                ],
                "combat_active": False
            },
            "memory": {},
            "combat_state": {}
        }
        prompt = generate_tactical_prompt(game_state)
        
        self.assertIn("Vendor", prompt)
        self.assertIn("Guard", prompt)
        self.assertIn("yellow", prompt.lower())
        self.assertIn("red", prompt.lower())
    
    def test_generate_tactical_prompt_combat(self):
        """Combat active should add combat context."""
        game_state = {
            "world": {
                "current_location": "Firefight Zone",
                "location_type": "industrial",
                "npcs": [],
                "combat_active": True
            },
            "memory": {},
            "combat_state": {"in_combat": True}
        }
        prompt = generate_tactical_prompt(game_state)
        
        self.assertIn("COMBAT", prompt.upper())


class TestMetadataExtraction(unittest.TestCase):
    """Test tactical metadata extraction."""
    
    def test_extract_tactical_metadata_basic(self):
        """Metadata should include location, zone, cover, entries."""
        game_state = {
            "world": {
                "current_location": "Test Location",
                "location_type": "residential",
                "npcs": [],
                "combat_active": False
            }
        }
        metadata = extract_tactical_metadata(game_state)
        
        self.assertEqual(metadata["location"], "Test Location")
        self.assertEqual(metadata["zone_type"], "residential")
        self.assertIn("cover_spots", metadata)
        self.assertIn("entry_points", metadata)
        self.assertIn("npcs", metadata)
    
    def test_extract_tactical_metadata_with_npcs(self):
        """Metadata should include processed NPC data."""
        game_state = {
            "world": {
                "current_location": "Test",
                "location_type": "bar",
                "npcs": [
                    {"name": "Bob", "role": "bartender", "disposition": "friendly"}
                ],
                "combat_active": False
            }
        }
        metadata = extract_tactical_metadata(game_state)
        
        self.assertEqual(len(metadata["npcs"]), 1)
        self.assertEqual(metadata["npcs"][0]["name"], "Bob")
        self.assertEqual(metadata["npcs"][0]["color"], "green")


class TestCaching(unittest.TestCase):
    """Test cache key generation."""
    
    def test_cache_key_consistency(self):
        """Same state should produce same cache key."""
        game_state = {
            "world": {
                "current_location": "Test",
                "location_type": "bar",
                "npcs": [],
                "combat_active": False
            }
        }
        key1 = generate_cache_key(game_state)
        key2 = generate_cache_key(game_state)
        
        self.assertEqual(key1, key2)
    
    def test_cache_key_changes_on_location(self):
        """Different location should produce different key."""
        state1 = {"world": {"current_location": "A", "location_type": "bar", "npcs": [], "combat_active": False}}
        state2 = {"world": {"current_location": "B", "location_type": "bar", "npcs": [], "combat_active": False}}
        
        key1 = generate_cache_key(state1)
        key2 = generate_cache_key(state2)
        
        self.assertNotEqual(key1, key2)
    
    def test_cache_key_changes_on_npc_count(self):
        """Adding NPC should change cache key."""
        state1 = {"world": {"current_location": "A", "location_type": "bar", "npcs": [], "combat_active": False}}
        state2 = {"world": {"current_location": "A", "location_type": "bar", "npcs": [{"name": "X"}], "combat_active": False}}
        
        key1 = generate_cache_key(state1)
        key2 = generate_cache_key(state2)
        
        self.assertNotEqual(key1, key2)


if __name__ == "__main__":
    unittest.main()
