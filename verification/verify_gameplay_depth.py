
import sys
import os
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.smart_zones import SmartZoneManager, ZoneType
from src.narrative.reputation import MoralReputationSystem
from src.game_state import RumorState
from src.inner_voice import InnerVoiceSystem

def test_living_rumors():
    print("--- Testing Living Rumors ---")
    
    # 1. Setup Reputation (Ruthless)
    rep = MoralReputationSystem()
    rep.mercy_ruthless.value = -80 # Very Ruthless
    
    # 2. Setup Rumor
    rumor_state = RumorState()
    rumor_state.rumors["r1"] = {"id": "r1", "text": "The Iron Wraith destroyed the colony"}
    
    # 3. Create Zone
    manager = SmartZoneManager()
    zone = manager.create_zone("bar_1", ZoneType.BAR, "The Rusty Anchor", ["Jonas", "Vera"])
    
    # 4. Generate Description
    desc = zone.get_scene_description(reputation=rep, rumors=rumor_state)
    
    print("Generated Description:\n", desc)
    
    # 5. Assertions
    if "REPUTATION: FEAR" in desc:
        print("[PASS] Reputation reaction triggers.")
    else:
        print("[FAIL] Reputation reaction missing.")
        
    if "The Iron Wraith destroyed the colony" in desc:
        print("[PASS] Rumor injection successful.")
    else:
        print("[FAIL] Rumor injection missing.")

def test_narrative_echoes():
    print("\n--- Testing Narrative Echoes ---")
    
    # 1. Setup Inner Voice
    voice_system = InnerVoiceSystem()
    
    # Manual Mocking to ensure it works regardless of import structure
    mock_client = MagicMock()
    mock_client.chat.return_value = {
        "message": {
            "content": '{"voices": [{"aspect": "Cortex", "content": "Analyze threat.", "intensity": 0.5}]}'
        }
    }
    voice_system._client = mock_client
    
    # 2. Trigger with High Stress
    print("Triggering voices with Stress Level 90.0...")
    voices = voice_system.trigger_voices("Walking down a dark corridor.", stress_level=90.0)
    
    # 3. Check for Hippocampus Echo
    found_echo = False
    for v in voices:
        print(f"Voice: {v.get('aspect')} -> {v.get('content')}")
        if v.get("aspect") == "Hippocampus":
            found_echo = True
            
    if found_echo:
        print("[PASS] Stress-induced echo triggered.")
    else:
        print("[FAIL] Stress-induced echo not found.")

if __name__ == "__main__":
    test_living_rumors()
    test_narrative_echoes()
