import sys
import os
import unittest

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.memory_system import MemoryPalace

class TestMemoryPalace(unittest.TestCase):
    def test_unlocks(self):
        palace = MemoryPalace()
        # Initial state: default fragments locked
        self.assertTrue(palace.fragments["mem_001"].is_locked)
        
        # Test Unlock
        # Profile passing Amygdala > 0.7
        profile = {
            "amygdala_dominance": 0.8,
            "cortex_dominance": 0.2
        }
        
        unlocked = palace.check_unlocks(profile)
        self.assertEqual(len(unlocked), 1)
        self.assertEqual(unlocked[0].title, "The Launch")
        self.assertFalse(palace.fragments["mem_001"].is_locked)
        self.assertTrue(palace.fragments["mem_002"].is_locked)

if __name__ == "__main__":
    unittest.main()
