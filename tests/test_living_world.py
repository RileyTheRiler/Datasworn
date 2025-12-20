
import unittest
import random
from src.starmap import StarMap, Sector, StarSystem, StarClass
from src.living_world import WorldSimulator, EventType
from src.hazards import HazardGenerator, HazardType

class TestLivingWorld(unittest.TestCase):
    def setUp(self):
        self.starmap = StarMap()
        self.starmap.generate_sector("TestSector", system_count=10)
        self.sector = Sector("TestSector")
        for sys in self.starmap.systems.values():
            self.sector.add_system(sys)
        
        self.factions = [
            {"id": "faction_a", "name": "Faction A", "influence": 0.8},
            {"id": "faction_b", "name": "Faction B", "influence": 0.4},
            {"id": "faction_c", "name": "Faction C", "influence": 0.1}
        ]

    def test_faction_territory_assignment(self):
        """Test that systems are correctly assigned to factions."""
        self.starmap.assign_faction_territories(self.sector, self.factions)
        
        assigned_factions = set()
        for sys in self.starmap.systems.values():
            if hasattr(sys, 'controlling_faction'):
                assigned_factions.add(sys.controlling_faction)
        
        self.assertIn("faction_a", assigned_factions)
        self.assertIn("faction_b", assigned_factions)
        # faction_c might not get any if influence is too low and systems are few
        
    def test_world_simulation_events(self):
        """Test that simulation generates events over time."""
        sim = WorldSimulator()
        state = {"world": {"factions": self.factions}}
        
        # Run 100 turns to guarantee some events
        all_new_events = []
        for _ in range(100):
            events = sim.simulate_turn(state, days_passed=1)
            all_new_events.extend(events)
            
        self.assertGreater(len(all_new_events), 0)
        self.assertIsInstance(all_new_events[0].event_type, EventType)
        
    def test_hazard_generation(self):
        """Test procedural hazard generation."""
        gen = HazardGenerator()
        
        hazards_seen = []
        for _ in range(100):
            h = gen.generate_travel_hazard(StarClass.RED_DWARF.value)
            if h:
                hazards_seen.append(h)
                
        self.assertGreater(len(hazards_seen), 0)
        self.assertIsInstance(hazards_seen[0].hazard_type, HazardType)

if __name__ == '__main__':
    unittest.main()
