"""
Verification script for The Murder Solution Mirror endpoint.
Tests all archetypes and validates the API response structure.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import directly to avoid narrative module __init__ issues
from src.character_identity import WoundType

# Import the MirrorSystem class directly
import importlib.util
spec = importlib.util.spec_from_file_location(
    "murder_mirror", 
    Path(__file__).parent.parent / "src" / "narrative" / "murder_mirror.py"
)
murder_mirror = importlib.util.module_from_spec(spec)
spec.loader.exec_module(murder_mirror)
MirrorSystem = murder_mirror.MirrorSystem


def test_mirror_system():
    """Test the MirrorSystem directly without API."""
    print("=" * 80)
    print("TESTING MIRROR SYSTEM DIRECTLY")
    print("=" * 80)
    
    # Test all implemented archetypes
    test_archetypes = [
        WoundType.CONTROLLER,
        WoundType.JUDGE,
        WoundType.GHOST,
        WoundType.FUGITIVE,
        WoundType.CYNIC,
        WoundType.SAVIOR,
        WoundType.DESTROYER,
        WoundType.IMPOSTOR,
        WoundType.PARANOID,
        WoundType.NARCISSIST,
        WoundType.COWARD
    ]
    
    for wound in test_archetypes:
        print(f"\n{'=' * 80}")
        print(f"ARCHETYPE: {wound.value.upper()}")
        print(f"{'=' * 80}")
        
        revelation = MirrorSystem.generate_revelation(wound)
        
        # Validate structure
        assert "phases" in revelation, f"Missing 'phases' for {wound.value}"
        assert "meta_analysis" in revelation, f"Missing 'meta_analysis' for {wound.value}"
        assert len(revelation["phases"]) == 5, f"Expected 5 phases, got {len(revelation['phases'])}"
        
        # Print key content
        print(f"\nWhat Mirror Shows: {revelation['meta_analysis']['what_mirror_shows']}")
        print(f"\nParallel: {revelation['meta_analysis']['parallel']}")
        print(f"\nPhase 4 - The Mirror:")
        print(f"{revelation['phases'][3]['dialogue'][:200]}...")
        print(f"\nPhase 5 - The Question:")
        print(f"{revelation['phases'][4]['question']}")
        
    print(f"\n{'=' * 80}")
    print("✓ All archetypes tested successfully!")
    print(f"{'=' * 80}")

def test_api_endpoint():
    """Test the API endpoint (requires server to be running)."""
    import requests
    
    print("\n" + "=" * 80)
    print("TESTING API ENDPOINT")
    print("=" * 80)
    
    base_url = "http://localhost:8000"
    
    # First, check if server is running
    try:
        response = requests.get(f"{base_url}/")
        print(f"✓ Server is running: {response.json()}")
    except Exception as e:
        print(f"✗ Server not running: {e}")
        print("  Start the server with: python src/server.py")
        return
    
    # Test the murder resolution endpoint
    # Note: This requires a session to exist with a psyche profile
    try:
        response = requests.get(f"{base_url}/api/narrative/murder-resolution?session_id=default")
        
        if response.status_code == 404:
            print("✗ No session found. Start a new game first.")
            print("  You can test the MirrorSystem directly without a session.")
            return
        elif response.status_code == 400:
            print("✗ No psychological profile found in session.")
            print("  The session needs to have played enough to develop a wound profile.")
            return
        
        response.raise_for_status()
        data = response.json()
        
        print(f"\n✓ API Response received!")
        print(f"  Player Wound: {data['player_wound']}")
        print(f"  Phases: {len(data['revelation']['phases'])}")
        print(f"\n  Phase 4 - The Mirror (excerpt):")
        print(f"  {data['revelation']['phases'][3]['dialogue'][:150]}...")
        
    except Exception as e:
        print(f"✗ API test failed: {e}")

if __name__ == "__main__":
    # Test the core logic first
    test_mirror_system()
    
    # Then test the API if available
    print("\n")
    test_api_endpoint()
    
    print("\n" + "=" * 80)
    print("VERIFICATION COMPLETE")
    print("=" * 80)
