import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.character_identity import CharacterIdentity, IdentityScore, IdentityArchetype
from src.psych_profile import PsychologicalProfile, PsychologicalEngine

class TestCharacterIdentity(unittest.TestCase):
    def test_identity_evolution(self):
        identity = CharacterIdentity()
        self.assertEqual(identity.archetype, IdentityArchetype.UNKNOWN)
        
        # Action 1: Violence
        identity.update_scores(IdentityScore(violence=0.5), "Attacked scavengers head-on")
        self.assertEqual(identity.archetype, IdentityArchetype.BRUTE)
        self.assertEqual(identity.scores.violence, 0.5)
        self.assertEqual(identity.dissonance_score, 0.0) # Initial establishment has no dissonance
        
        # Action 2: More Violence (Consistent)
        identity.update_scores(IdentityScore(violence=0.3), "Smashed the door down")
        self.assertEqual(identity.scores.violence, 0.8)
        self.assertAlmostEqual(identity.dissonance_score, 0.0, places=2)
        
        # Action 3: Stealth (Dissonant for a Brute)
        identity.update_scores(IdentityScore(stealth=0.4), "Tried to sneak past the guards")
        self.assertGreater(identity.dissonance_score, 0.0)
        self.assertEqual(identity.scores.stealth, 0.4)
        
    def test_archetype_switch(self):
        identity = CharacterIdentity()
        
        # Establish as Shadow
        identity.update_scores(IdentityScore(stealth=0.6), "Sneaked in")
        self.assertEqual(identity.archetype, IdentityArchetype.SHADOW)
        
        # Evolution into Brute
        identity.update_scores(IdentityScore(violence=0.8), "Rampage")
        self.assertEqual(identity.archetype, IdentityArchetype.BRUTE)
        
    def test_integration(self):
        profile = PsychologicalProfile()
        engine = PsychologicalEngine()
        
        # Evolve via engine
        engine.evolve_from_event(profile, "You brutally killed the guard.", outcome="strong_hit")
        
        self.assertEqual(profile.identity.archetype, IdentityArchetype.BRUTE)
        self.assertGreater(profile.identity.scores.violence, 0.0)
        
        # Dissonant action
        engine.evolve_from_event(profile, "You hid in the shadows like a coward.", outcome="weak_hit")
        self.assertGreater(profile.identity.dissonance_score, 0.0)

if __name__ == "__main__":
    unittest.main()
