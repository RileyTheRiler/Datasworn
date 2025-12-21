import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.character_identity import CharacterIdentity, IdentityScore, IdentityArchetype
from src.psych_profile import PsychologicalProfile, PsychologicalEngine

print("Starting manual test...")
profile = PsychologicalProfile()
engine = PsychologicalEngine()
print("Initial Archetype:", profile.identity.archetype)

engine.evolve_from_event(profile, "You brutally killed the guard.", outcome="strong_hit")
print("After Violent Event - Archetype:", profile.identity.archetype)
print("After Violent Event - Violence Score:", profile.identity.scores.violence)

engine.evolve_from_event(profile, "You hid in the shadows like a coward.", outcome="weak_hit")
print("After Stealth Event - Dissonance:", profile.identity.dissonance_score)
print("Manual test complete.")
