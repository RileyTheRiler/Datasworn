"""
Verification script for Story Premise and Designing Principle.
Tests both the local module logic and the FastAPI integration.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from src.server import app
from src.narrative.story_structure import (
    get_story_structure, 
    LOCKED_PREMISE, 
    DESIGNING_PRINCIPLE,
    THEMES,
    IRONIC_CORE
)

client = TestClient(app)

def verify_story_logic():
    print("\n--- Verifying Story Module Logic ---")
    structure = get_story_structure()
    
    assert structure.premise == LOCKED_PREMISE
    assert structure.designing_principle == DESIGNING_PRINCIPLE
    assert structure.themes == THEMES
    assert structure.ironic_core == IRONIC_CORE
    
    print("[OK] Local Module Logic Verified")
    return True

def verify_story_api():
    print("\n--- Verifying Narrative API Endpoint ---")
    
    response = client.get("/api/narrative/premise")
    
    if response.status_code == 200:
        data = response.json()
        print(f"[OK] Response Received")
        
        # Verify Content
        assert data["premise"] == LOCKED_PREMISE
        assert data["designing_principle"] == DESIGNING_PRINCIPLE
        assert data["themes"] == THEMES
        assert data["ironic_core"] == IRONIC_CORE
        
        print(f"  - Premise: {data['premise'][:60]}...")
        print(f"  - Designing Principle: {data['designing_principle']}")
        print(f"  - Themes: {len(data['themes'])} active")
        
        print("[OK] API Endpoint Verified")
        return True
    else:
        print(f"[FAIL] API Failed with status {response.status_code}")
        print(response.text)
        return False

def run_all_tests():
    print("======================================================================")
    print("  STORY DNA VERIFICATION")
    print("======================================================================")
    
    logic_ok = verify_story_logic()
    api_ok = verify_story_api()
    
    if logic_ok and api_ok:
        print("\n======================================================================")
        print("  VERIFICATION COMPLETE: THE PREMISE IS LOCKED")
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
