
import sys
import os
from pprint import pprint

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from src.narrative.exile_gambit import get_ship_data, get_all_zones, get_zone_details
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def verify_ship_identity():
    print("--- Verifying Ship Identity ---")
    data = get_ship_data()
    pprint(data)
    assert data["name"] == "Exile Gambit"
    assert "Trapped Together" in data["themes"]
    print("✅ Ship Identity Verified")

def verify_zones_list():
    print("\n--- Verifying Zones List ---")
    zones = get_all_zones()
    pprint(zones)
    assert len(zones) == 8
    ids = [z["id"] for z in zones]
    assert "bridge" in ids
    assert "quarters_captain" in ids
    print("✅ Zones List Verified")

def verify_zone_details():
    print("\n--- Verifying Zone Details (Bridge) ---")
    # Test without archetype
    bridge = get_zone_details("bridge")
    assert bridge["name"] == "The Bridge"
    assert len(bridge["details"]) > 0
    assert len(bridge["archetype_seeds"]) == 0 # Default is empty if no archetype provided
    
    # Test WITH archetype
    print("Testing Controller Archetype Seeds...")
    bridge_controller = get_zone_details("bridge", player_archetype="Controller")
    print(f"Seeds found: {bridge_controller['archetype_seeds']}")
    assert len(bridge_controller['archetype_seeds']) > 0
    assert any("Control" in s or "0.003" in s for s in bridge_controller['archetype_seeds'])
    
    # Test Ghost Archetype
    print("Testing Ghost Archetype Seeds...")
    bridge_ghost = get_zone_details("bridge", player_archetype="Ghost")
    print(f"Seeds found: {bridge_ghost['archetype_seeds']}")
    assert len(bridge_ghost['archetype_seeds']) > 0
    assert any("empty chair" in s for s in bridge_ghost['archetype_seeds'])

    print("✅ Zone Details Verified")

def verify_captains_quarters():
    print("\n--- Verifying Captain's Quarters ---")
    quarters = get_zone_details("quarters_captain")
    assert quarters["keeper"] == "Sealed (Investigation)"
    assert any("Unmade bed" in d["name"] for d in quarters["details"])
    print("✅ Captain's Quarters Verified")

if __name__ == "__main__":
    verify_ship_identity()
    verify_zones_list()
    verify_zone_details()
    verify_captains_quarters()
    print("\n🎉 ALL SHIP DATA VERIFIED SUCCESSFULLY")
