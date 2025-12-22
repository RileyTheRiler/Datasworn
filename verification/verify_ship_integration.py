"""
Verification script for Ship as Character integration.
Tests ship data, environmental storytelling integration, and ship state management.
"""

import sys
import os
from pprint import pprint

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def test_ship_data():
    """Test basic ship data and zones."""
    print("=" * 60)
    print("TEST 1: Ship Data Module")
    print("=" * 60)
    
    from src.narrative.exile_gambit import get_ship_data, get_all_zones, get_zone_details
    
    # Test ship identity
    ship = get_ship_data()
    assert ship["name"] == "Exile Gambit"
    assert "Second Chances" in ship["themes"]
    print("✅ Ship identity loaded")
    
    # Test zones list
    zones = get_all_zones()
    assert len(zones) == 8
    print(f"✅ {len(zones)} zones loaded")
    
    # Test zone details
    bridge = get_zone_details("bridge")
    assert bridge["name"] == "The Bridge"
    assert len(bridge["details"]) > 0
    print(f"✅ Bridge has {len(bridge['details'])} environmental details")
    
    # Test archetype seeds
    bridge_controller = get_zone_details("bridge", player_archetype="Controller")
    assert len(bridge_controller["archetype_seeds"]) > 0
    print(f"✅ Controller archetype has {len(bridge_controller['archetype_seeds'])} seeds in Bridge")
    
    print()

def test_environmental_integration():
    """Test ship zone integration with environmental storytelling."""
    print("=" * 60)
    print("TEST 2: Environmental Storytelling Integration")
    print("=" * 60)
    
    from src.environmental_storytelling import EnvironmentalStoryGenerator
    
    generator = EnvironmentalStoryGenerator()
    
    # Test ship zone discovery
    discovery = generator.generate_ship_zone_discovery("engineering", scene=5)
    assert discovery is not None
    assert "Engineering" in discovery.implied_story
    print(f"✅ Generated discovery for Engineering zone")
    print(f"   Description: {discovery.description[:80]}...")
    
    # Test archetype seeds
    seeds = generator.get_zone_archetype_seeds("bridge", "Ghost")
    assert len(seeds) > 0
    print(f"✅ Found {len(seeds)} Ghost archetype seeds for Bridge")
    print(f"   Example: {seeds[0][:80]}...")
    
    print()

def test_ship_state_manager():
    """Test dynamic ship state management."""
    print("=" * 60)
    print("TEST 3: Ship State Manager")
    print("=" * 60)
    
    from src.narrative.ship_state import ShipStateManager, ShipEvent, ZoneStatus
    
    manager = ShipStateManager()
    
    # Test initial state
    assert manager.days_to_port == 8
    assert manager.get_zone_status("quarters_captain") == ZoneStatus.SEALED
    print("✅ Initial state correct (Captain's quarters sealed)")
    
    # Test event application
    changes = manager.apply_event(ShipEvent.TENSION_RISES, scene=3)
    assert len(changes) > 0
    assert manager.common_area_usage < 0.5
    print(f"✅ Tension event applied: {changes[0]}")
    
    # Test pressure calculation
    pressure = manager._calculate_pressure()
    assert 0.0 <= pressure <= 1.0
    print(f"✅ Pressure level: {pressure:.2f} - {manager.get_pressure_description()}")
    
    # Test day advancement
    status = manager.advance_day()
    assert manager.days_to_port == 7
    assert manager.fuel_level < 1.0
    print(f"✅ Day advanced: {status['days_to_port']} days to port")
    
    # Test serialization
    data = manager.to_dict()
    restored = ShipStateManager.from_dict(data)
    assert restored.days_to_port == manager.days_to_port
    print("✅ Serialization/deserialization works")
    
    print()

def test_narrator_context():
    """Test narrator context generation."""
    print("=" * 60)
    print("TEST 4: Narrator Context")
    print("=" * 60)
    
    from src.narrative.ship_state import ShipStateManager, ShipEvent
    
    manager = ShipStateManager()
    manager.apply_event(ShipEvent.KAI_SPIRALS, scene=10)
    manager.advance_day()
    manager.advance_day()
    
    context = manager.get_narrator_context()
    assert "SHIP STATE CONTEXT" in context
    assert "engineering: damaged" in context.lower()
    print("✅ Narrator context generated:")
    print(context)
    
    print()

def test_integration_flow():
    """Test complete integration flow."""
    print("=" * 60)
    print("TEST 5: Complete Integration Flow")
    print("=" * 60)
    
    from src.narrative.exile_gambit import get_zone_details
    from src.environmental_storytelling import EnvironmentalStoryGenerator
    from src.narrative.ship_state import ShipStateManager, ShipEvent
    
    # Scenario: Player investigates Engineering after Kai spirals
    manager = ShipStateManager()
    generator = EnvironmentalStoryGenerator()
    
    # Event occurs
    changes = manager.apply_event(ShipEvent.KAI_SPIRALS, scene=15)
    print(f"Event: Kai spirals")
    print(f"Changes: {changes}")
    
    # Player enters Engineering
    zone = get_zone_details("engineering", player_archetype="Hedonist")
    print(f"\nPlayer enters {zone['name']}")
    print(f"Status: {manager.get_zone_status('engineering').value}")
    print(f"Atmosphere: {zone['atmosphere']}")
    
    # Generate discovery
    discovery = generator.generate_ship_zone_discovery("engineering", player_archetype="Hedonist", scene=15)
    print(f"\nDiscovery: {discovery.description}")
    
    # Check archetype seeds
    if zone["archetype_seeds"]:
        print(f"\nHedonist sees: {zone['archetype_seeds'][0]}")
    
    print("\n✅ Complete integration flow works!")
    print()

if __name__ == "__main__":
    try:
        test_ship_data()
        test_environmental_integration()
        test_ship_state_manager()
        test_narrator_context()
        test_integration_flow()
        
        print("=" * 60)
        print("🎉 ALL TESTS PASSED")
        print("=" * 60)
        print("\nThe Exile Gambit is ready to be a character in the story!")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
