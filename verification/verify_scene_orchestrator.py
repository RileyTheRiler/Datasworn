"""
Verification script for Scene Beat Orchestrator.
Tests that generated scenes serve the "Investigation is a Mirror" premise.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from src.server import app
from src.narrative.scene_beat_orchestrator import get_scene_orchestrator
from src.character_identity import WoundType

client = TestClient(app)

def verify_local_logic():
    print("\n--- Verifying Scene Orchestrator Logic ---")
    orchestrator = get_scene_orchestrator()
    
    # Test scene generation for each archetype
    archetypes_tested = []
    for archetype in [WoundType.CONTROLLER, WoundType.JUDGE, WoundType.GHOST, WoundType.SAVIOR]:
        scene = orchestrator.generate_investigation_scene(
            player_archetype=archetype,
            story_progress=0.5,
            context="general"
        )
        
        # Verify scene structure
        assert scene.premise_alignment == "The Investigation is a Mirror"
        assert len(scene.choices) >= 2
        assert scene.archetype_focus == archetype
        
        # Verify all choices mirror the wound
        for choice in scene.choices:
            assert choice.mirrors_wound, f"Choice {choice.id} missing mirrors_wound"
        
        # Verify at least one growth choice
        growth_choices = [c for c in scene.choices if c.is_growth_choice]
        assert len(growth_choices) >= 1, f"No growth choice for {archetype.value}"
        
        # Verify premise alignment score
        alignment_score = orchestrator.validate_premise_alignment(scene)
        assert alignment_score >= 0.7, f"Low alignment score: {alignment_score}"
        
        archetypes_tested.append(archetype.value)
        print(f"  - {archetype.value}: {len(scene.choices)} choices, alignment={alignment_score:.2f}")
    
    print(f"[OK] Tested {len(archetypes_tested)} archetypes")
    return True

def verify_api():
    print("\n--- Verifying Scene Generation API ---")
    
    # Test scene generation via API
    request_data = {
        "player_archetype": "CONTROLLER",
        "story_progress": 0.45,
        "context": "general"
    }
    
    response = client.post("/api/narrative/generate-scene", json=request_data)
    
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Response Received")
        
        # Verify content
        assert data["premise_alignment"] == "The Investigation is a Mirror"
        assert data["alignment_score"] >= 0.7
        assert len(data["choices"]) >= 2
        
        # Verify all choices have mirror descriptions
        for choice in data["choices"]:
            assert "mirrors_wound" in choice
            assert choice["mirrors_wound"], "Empty mirrors_wound field"
        
        # Verify at least one growth choice
        growth_choices = [c for c in data["choices"] if c["is_growth_choice"]]
        assert len(growth_choices) >= 1
        
        print(f"  - Scene ID: {data['scene_id']}")
        print(f"  - Alignment Score: {data['alignment_score']:.2f}")
        print(f"  - Choices: {len(data['choices'])}")
        print(f"  - Growth Options: {len(growth_choices)}")
        print(f"  - Character Web: {data['character_web_integration']['npc_involved']}")
        
        print("[OK] API Endpoint Verified")
        return True
    else:
        print(f"[FAIL] API Failed with status {response.status_code}")
        print(response.text)
        return False

def verify_mirror_principle():
    print("\n--- Verifying 'Mirror' Principle ---")
    orchestrator = get_scene_orchestrator()
    
    # Generate scene for Controller
    scene = orchestrator.generate_investigation_scene(
        player_archetype=WoundType.CONTROLLER,
        story_progress=0.5
    )
    
    # Verify each choice reflects control theme
    for choice in scene.choices:
        assert "control" in choice.mirrors_wound.lower() or "growth" in choice.mirrors_wound.lower()
    
    print("[OK] All choices mirror the player's wound")
    return True

def run_all_tests():
    print("======================================================================")
    print("  SCENE BEAT ORCHESTRATOR VERIFICATION")
    print("======================================================================")
    
    logic_ok = verify_local_logic()
    api_ok = verify_api()
    mirror_ok = verify_mirror_principle()
    
    if logic_ok and api_ok and mirror_ok:
        print("\n======================================================================")
        print("  VERIFICATION COMPLETE: SCENES SERVE THE MIRROR PRINCIPLE")
        print("======================================================================")
        return True
    else:
        return False

if __name__ == "__main__":
    try:
        if run_all_tests():
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error during verification: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
