"""
World Simulation Backend Verification Script.
Tests all simulation systems, config loading, and integration points.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.world.simulation.config_loader import get_config_loader
from src.world.simulation.simulation_loop import SimulationLoop
from src.world.simulation.traffic import Vector3
from src.world.simulation.law import Crime
from src.world.simulation.weather import WeatherState
import time


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_config_loading():
    """Test configuration loading."""
    print_section("TEST 1: Configuration Loading")
    
    try:
        loader = get_config_loader()
        config = loader.load_simulation_config()
        
        print("[OK] Simulation config loaded successfully")
        print(f"  - Traffic max ships: {config.traffic.max_ships_per_sector}")
        print(f"  - Law suspicion decay: {config.law.suspicion_decay_rate}")
        print(f"  - Wildlife spawn multiplier: {config.wildlife.spawn_density_multiplier}")
        print(f"  - Weather forecast steps: {config.weather.forecast_steps}")
        print(f"  - Global tick rate: {config.global_settings.tick_rate}")
        
        regions = loader.load_regions()
        print(f"\n[OK] Regional metadata loaded: {len(regions)} regions")
        for region_id, region in regions.items():
            print(f"  - {region.name} ({region_id}): {region.biome}, law={region.law_presence.patrol_density}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Config loading failed: {e}")
        return False


def test_traffic_system():
    """Test traffic system."""
    print_section("TEST 2: Traffic System")
    
    try:
        loader = get_config_loader()
        config = loader.load_simulation_config()
        
        from src.world.simulation.traffic import TrafficSystem, PatrolRoute
        traffic = TrafficSystem(config.traffic)
        
        # Add a patrol route
        waypoints = [
            Vector3(0, 0, 0),
            Vector3(5, 0, 0),
            Vector3(5, 5, 0),
            Vector3(0, 5, 0),
        ]
        patrol = PatrolRoute(
            faction="Keepers",
            waypoints=waypoints,
            patrol_frequency=0.5,
            scan_range=2.0
        )
        traffic.add_patrol_route("Keepers", patrol)
        
        print("[OK] Traffic system initialized")
        print(f"  - Patrol routes: {len(traffic.patrol_routes)}")
        
        # Run a few ticks
        player_pos = Vector3(2, 2, 0)
        events = []
        for i in range(5):
            tick_events = traffic.tick(0.1, "test_sector", player_pos)
            events.extend(tick_events)
        
        print(f"[OK] Ran 5 ticks, generated {len(events)} events")
        print(f"  - Active ships: {len(traffic.active_ships)}")
        print(f"  - Congestion: {traffic.get_congestion('test_sector'):.2f}")
        
        # Test serialization
        state = traffic.to_dict()
        restored = TrafficSystem.from_dict(state, config.traffic)
        print(f"[OK] Serialization successful")
        
        return True
    except Exception as e:
        print(f"[FAIL] Traffic system failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_law_system():
    """Test law enforcement system."""
    print_section("TEST 3: Law Enforcement System")
    
    try:
        loader = get_config_loader()
        config = loader.load_simulation_config()
        
        from src.world.simulation.law import LawSystem
        law = LawSystem(config.law)
        
        print("[OK] Law system initialized")
        
        # Report a crime
        crime = law.report_crime(
            crime_type="assault",
            severity=3,
            location="test_sector",
            witnesses=["npc_1", "npc_2"],
            factions=["Keepers"]
        )
        
        print(f"[OK] Crime reported: {crime.crime_id}")
        print(f"  - Suspicion (Keepers): {law.get_suspicion('Keepers'):.2f}")
        print(f"  - Witness reports: {len(law.witness_reports)}")
        
        # Run ticks to trigger investigation
        player_state = {
            'crimes_committed': [],
            'reputation': {},
            'honor': 0.5,
            'current_posture': 'normal',
            'weapon_readied': False,
            'intoxication_level': 0.0,
            'disguise_active': None
        }
        
        events = []
        for i in range(10):
            tick_events = law.tick(0.1, player_state)
            events.extend(tick_events)
        
        print(f"[OK] Ran 10 ticks, generated {len(events)} events")
        print(f"  - Active investigations: {len(law.active_investigations)}")
        print(f"  - Active pursuits: {len(law.active_pursuits)}")
        print(f"  - Total bounty: {law.get_total_bounty()} credits")
        
        # Test suspicion decay
        initial_suspicion = law.get_suspicion('Keepers')
        for i in range(20):
            law.tick(0.5, player_state)  # 10 hours total
        final_suspicion = law.get_suspicion('Keepers')
        print(f"[OK] Suspicion decay: {initial_suspicion:.2f} -> {final_suspicion:.2f}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Law system failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_wildlife_system():
    """Test wildlife ecosystem."""
    print_section("TEST 4: Wildlife System")
    
    try:
        loader = get_config_loader()
        config = loader.load_simulation_config()
        
        from src.world.simulation.wildlife import WildlifeSystem
        wildlife = WildlifeSystem(config.wildlife)
        
        print("[OK] Wildlife system initialized")
        
        # Initialize populations
        wildlife.initialize_population("nebula_drifter", "dense_nebula", 20, False)
        wildlife.initialize_population("void_leviathan", "dense_nebula", 1, True, ["nebula_drifter"])
        
        print(f"[OK] Initialized 2 species populations")
        
        # Run ticks
        player_pos = (0.0, 0.0, 0.0)
        events = []
        for i in range(10):
            tick_events = wildlife.tick(0.1, "dense_nebula", player_pos)
            events.extend(tick_events)
        
        print(f"[OK] Ran 10 ticks, generated {len(events)} events")
        print(f"  - Active creatures: {len(wildlife.active_creatures)}")
        print(f"  - Nebula drifter count: {wildlife.get_population_count('nebula_drifter', 'dense_nebula')}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Wildlife system failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_weather_system():
    """Test weather simulation."""
    print_section("TEST 5: Weather System")
    
    try:
        loader = get_config_loader()
        config = loader.load_simulation_config()
        
        from src.world.simulation.weather import WeatherSystem
        weather = WeatherSystem(config.weather)
        
        print("[OK] Weather system initialized")
        
        # Set initial weather
        weather.set_weather("test_sector", WeatherState.CLEAR)
        
        initial_weather = weather.get_weather("test_sector")
        print(f"[OK] Initial weather: {initial_weather.state.value}")
        
        # Run ticks to trigger transitions
        events = []
        for i in range(20):
            tick_events = weather.tick(0.5, "test_sector")  # 10 hours total
            events.extend(tick_events)
        
        final_weather = weather.get_weather("test_sector")
        print(f"[OK] Ran 20 ticks, generated {len(events)} events")
        print(f"  - Final weather: {final_weather.state.value}")
        print(f"  - Active hazards: {len(weather.active_hazards)}")
        
        # Test forecast
        forecast = weather.get_forecast("test_sector")
        print(f"[OK] Forecast: {[s.value for s in forecast]}")
        
        # Test modifiers
        modifiers = weather.get_modifiers("test_sector")
        print(f"[OK] Current modifiers: visibility={modifiers.get('visibility', 1.0):.2f}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Weather system failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simulation_loop():
    """Test central simulation loop."""
    print_section("TEST 6: Simulation Loop Integration")
    
    try:
        sim_loop = SimulationLoop()
        
        print("[OK] Simulation loop initialized")
        
        # Initialize from a region
        sim_loop.initialize_from_region("core_nexus")
        print("[OK] Initialized from region: core_nexus")
        
        # Mock game state
        game_state = {
            'world': {
                'current_location': 'core_nexus',
                'location_type': 'settled_space'
            },
            'character': {
                'name': 'Test Player',
                'crimes_committed': [],
                'reputation': {},
                'honor': 0.5,
                'current_posture': 'normal',
                'weapon_readied': False,
                'intoxication_level': 0.0,
                'disguise_active': None
            }
        }
        
        # Run 100 ticks
        all_events = []
        for i in range(100):
            events = sim_loop.tick(game_state)
            all_events.extend(events)
        
        print(f"[OK] Ran 100 simulation ticks")
        print(f"  - Total events generated: {len(all_events)}")
        
        # Count event types
        event_types = {}
        for event in all_events:
            event_type = event.get('type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        print(f"  - Event type breakdown:")
        for event_type, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True):
            print(f"    * {event_type}: {count}")
        
        # Test state persistence
        state = sim_loop.to_dict()
        restored_loop = SimulationLoop.from_dict(state)
        print(f"[OK] State serialization successful")
        
        return True
    except Exception as e:
        print(f"[FAIL] Simulation loop failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_player_integration():
    """Test player state integration."""
    print_section("TEST 7: Player State Integration")
    
    try:
        from src.game_state import Character
        
        # Create character with new fields
        character = Character(name="Test Character")
        
        print("[OK] Character created with simulation fields")
        print(f"  - Crimes committed: {len(character.crimes_committed)}")
        print(f"  - Reputation: {character.reputation}")
        print(f"  - Honor: {character.honor}")
        print(f"  - Posture: {character.current_posture}")
        print(f"  - Weapon readied: {character.weapon_readied}")
        
        # Add a crime
        character.crimes_committed.append({
            'crime_type': 'theft',
            'severity': 2,
            'timestamp': time.time()
        })
        
        # Modify reputation
        character.reputation['Keepers'] = -0.3
        character.honor = 0.4
        
        print(f"[OK] Modified player state")
        print(f"  - Crimes: {len(character.crimes_committed)}")
        print(f"  - Keeper reputation: {character.reputation['Keepers']}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Player integration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_npc_memory():
    """Test NPC memory tokens."""
    print_section("TEST 8: NPC Memory Tokens")
    
    try:
        from src.npc.schemas import CognitiveState, PersonalityProfile
        
        # Create NPC with memory
        profile = PersonalityProfile(
            name="Test NPC",
            role="Guard",
            traits=["vigilant", "strict"]
        )
        
        cognitive = CognitiveState(
            npc_id="npc_test_1",
            profile=profile
        )
        
        print("[OK] NPC cognitive state created")
        
        # Add crime memory
        cognitive.witnessed_crimes.append({
            'crime_id': 'crime_1',
            'perpetrator_description': 'tall figure in dark cloak',
            'severity': 4,
            'timestamp': time.time(),
            'decay_progress': 0.0
        })
        
        # Add disturbance memory
        cognitive.disturbance_memory.append({
            'event_type': 'gunfire',
            'location': 'docking_bay',
            'timestamp': time.time(),
            'decay_progress': 0.0,
            'severity': 3
        })
        
        print(f"[OK] Added memories")
        print(f"  - Witnessed crimes: {len(cognitive.witnessed_crimes)}")
        print(f"  - Disturbances: {len(cognitive.disturbance_memory)}")
        
        # Test decay
        cognitive.decay_memories(5.0)  # 5 hours
        print(f"[OK] Decayed memories (5 hours)")
        print(f"  - Crime decay: {cognitive.witnessed_crimes[0]['decay_progress']:.2f}")
        
        # Test disguise clearing
        cognitive.clear_memories_by_disguise()
        print(f"[OK] Cleared by disguise")
        print(f"  - Remaining crimes: {len(cognitive.witnessed_crimes)}")
        
        return True
    except Exception as e:
        print(f"[FAIL] NPC memory failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all verification tests."""
    print("\n" + "="*70)
    print("  WORLD SIMULATION BACKEND VERIFICATION")
    print("="*70)
    
    tests = [
        ("Configuration Loading", test_config_loading),
        ("Traffic System", test_traffic_system),
        ("Law Enforcement System", test_law_system),
        ("Wildlife System", test_wildlife_system),
        ("Weather System", test_weather_system),
        ("Simulation Loop", test_simulation_loop),
        ("Player State Integration", test_player_integration),
        ("NPC Memory Tokens", test_npc_memory),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[FAIL] {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print_section("VERIFICATION SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\n{'='*70}")
    print(f"  Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"{'='*70}\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

