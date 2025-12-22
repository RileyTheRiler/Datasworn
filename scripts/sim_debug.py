"""
Simulation Debug Tool - Visualization and testing utilities.
Provides heatmaps, state inspection, time fast-forward, and manual event triggering.
"""

import sys
import os
import argparse
from typing import Optional

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.world.simulation.simulation_loop import SimulationLoop
from src.world.simulation.config_loader import get_config_loader
from src.world.simulation.weather import WeatherState
import json


def print_header(title: str):
    """Print a section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def visualize_suspicion_heatmap(sim_loop: SimulationLoop):
    """Display suspicion levels as a heatmap."""
    print_header("SUSPICION HEATMAP")
    
    suspicion = sim_loop.law.player_suspicion
    
    if not suspicion:
        print("No active suspicion")
        return
    
    # Sort by suspicion level
    sorted_factions = sorted(suspicion.items(), key=lambda x: x[1], reverse=True)
    
    max_suspicion = max(suspicion.values()) if suspicion else 1.0
    
    for faction, level in sorted_factions:
        # Create visual bar
        bar_length = int((level / max_suspicion) * 40)
        bar = '#' * bar_length
        
        # Color code based on threshold
        if level >= 0.9:
            status = "[LETHAL]"
        elif level >= 0.6:
            status = "[PURSUIT]"
        elif level >= 0.3:
            status = "[INVESTIGATING]"
        else:
            status = "[WATCHING]"
        
        print(f"{faction:20s} {status:15s} {bar} {level:.2f}")


def visualize_traffic_heatmap(sim_loop: SimulationLoop):
    """Display traffic congestion as a heatmap."""
    print_header("TRAFFIC CONGESTION HEATMAP")
    
    congestion = sim_loop.traffic.congestion_map
    
    if not congestion:
        print("No congestion data")
        return
    
    sorted_sectors = sorted(congestion.items(), key=lambda x: x[1], reverse=True)
    
    for sector, level in sorted_sectors:
        bar_length = int(level * 40)
        bar = '#' * bar_length
        
        if level >= 0.7:
            status = "[HEAVY]"
        elif level >= 0.3:
            status = "[MODERATE]"
        else:
            status = "[LIGHT]"
        
        print(f"{sector:20s} {status:12s} {bar} {level:.2f}")


def visualize_wildlife_density(sim_loop: SimulationLoop):
    """Display wildlife population densities."""
    print_header("WILDLIFE DENSITY")
    
    densities = sim_loop.wildlife.biome_densities
    
    if not densities:
        print("No wildlife data")
        return
    
    for biome, species_counts in densities.items():
        print(f"\n{biome}:")
        for species, count in species_counts.items():
            # Get population cap
            pop_id = f"{species}_{biome}"
            population = sim_loop.wildlife.populations.get(pop_id)
            cap = population.population_cap if population else 0
            
            if cap > 0:
                percentage = (count / cap) * 100
                bar_length = int((count / cap) * 30)
                bar = '#' * bar_length
                print(f"  {species:20s} {bar} {count}/{cap} ({percentage:.0f}%)")
            else:
                print(f"  {species:20s} {count}")


def inspect_system_state(sim_loop: SimulationLoop):
    """Display detailed system state."""
    print_header("SYSTEM STATE INSPECTION")
    
    print("TRAFFIC:")
    print(f"  Active ships: {len(sim_loop.traffic.active_ships)}")
    print(f"  Patrol routes: {len(sim_loop.traffic.patrol_routes)}")
    print(f"  Trade routes: {len(sim_loop.traffic.trade_routes)}")
    
    print("\nLAW:")
    print(f"  Active investigations: {len(sim_loop.law.active_investigations)}")
    print(f"  Active pursuits: {len(sim_loop.law.active_pursuits)}")
    print(f"  Total bounty: {sim_loop.law.get_total_bounty()} credits")
    print(f"  Crime history: {len(sim_loop.law.crime_history)} crimes")
    
    print("\nWILDLIFE:")
    print(f"  Active creatures: {len(sim_loop.wildlife.active_creatures)}")
    print(f"  Populations tracked: {len(sim_loop.wildlife.populations)}")
    
    print("\nWEATHER:")
    print(f"  Tracked sectors: {len(sim_loop.weather.sector_weather)}")
    print(f"  Active hazards: {len(sim_loop.weather.active_hazards)}")
    
    print("\nEVENTS:")
    print(f"  Event history: {len(sim_loop.dispatcher.event_history)}")


def fast_forward_time(sim_loop: SimulationLoop, hours: float):
    """Fast-forward simulation time."""
    print_header(f"FAST-FORWARD: {hours} HOURS")
    
    game_state = {
        'world': {
            'current_location': 'test_sector',
            'location_type': 'neutral'
        },
        'character': {
            'name': 'Debug Player',
            'crimes_committed': [],
            'reputation': {},
            'honor': 0.5,
            'current_posture': 'normal',
            'weapon_readied': False,
            'intoxication_level': 0.0,
            'disguise_active': None
        }
    }
    
    # Calculate number of ticks (assuming 0.1 hour per tick)
    ticks = int(hours / 0.1)
    
    print(f"Running {ticks} ticks...")
    
    all_events = []
    for i in range(ticks):
        events = sim_loop.tick(game_state)
        all_events.extend(events)
        
        if (i + 1) % 100 == 0:
            print(f"  Progress: {i+1}/{ticks} ticks")
    
    print(f"\nCompleted! Generated {len(all_events)} events")
    
    # Summarize events
    event_types = {}
    for event in all_events:
        event_type = event.get('type', 'unknown')
        event_types[event_type] = event_types.get(event_type, 0) + 1
    
    if event_types:
        print("\nEvent summary:")
        for event_type, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {event_type}: {count}")


def set_weather(sim_loop: SimulationLoop, sector: str, weather_state: str):
    """Manually set weather for a sector."""
    print_header(f"SET WEATHER: {sector}")
    
    try:
        state = WeatherState(weather_state)
        sim_loop.weather.set_weather(sector, state)
        print(f"Weather set to: {state.value}")
        
        # Show modifiers
        modifiers = sim_loop.weather.get_modifiers(sector)
        print("\nModifiers:")
        for key, value in modifiers.items():
            print(f"  {key}: {value:.2f}")
    except ValueError:
        print(f"Invalid weather state: {weather_state}")
        print(f"Valid states: {[s.value for s in WeatherState]}")


def view_event_log(sim_loop: SimulationLoop, count: int = 20):
    """View recent events."""
    print_header(f"EVENT LOG (Last {count})")
    
    events = sim_loop.dispatcher.get_recent_events(count)
    
    if not events:
        print("No events in history")
        return
    
    for event in events:
        print(f"[{event.event_type.value:25s}] {event.data}")


def save_snapshot(sim_loop: SimulationLoop, filename: str):
    """Save simulation state snapshot."""
    print_header(f"SAVE SNAPSHOT: {filename}")
    
    state = sim_loop.to_dict()
    
    with open(filename, 'w') as f:
        json.dump(state, f, indent=2)
    
    print(f"Snapshot saved to: {filename}")


def load_snapshot(filename: str) -> Optional[SimulationLoop]:
    """Load simulation state snapshot."""
    print_header(f"LOAD SNAPSHOT: {filename}")
    
    try:
        with open(filename, 'r') as f:
            state = json.load(f)
        
        sim_loop = SimulationLoop.from_dict(state)
        print(f"Snapshot loaded from: {filename}")
        return sim_loop
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return None
    except Exception as e:
        print(f"Error loading snapshot: {e}")
        return None


def main():
    """Main debug tool entry point."""
    parser = argparse.ArgumentParser(description='World Simulation Debug Tool')
    
    parser.add_argument('--session', type=str, default='debug',
                        help='Session ID (default: debug)')
    parser.add_argument('--region', type=str, default='frontier_haven',
                        help='Initialize from region (default: frontier_haven)')
    
    # Visualization commands
    parser.add_argument('--heatmap', type=str, choices=['suspicion', 'traffic', 'wildlife'],
                        help='Display heatmap visualization')
    parser.add_argument('--inspect', action='store_true',
                        help='Inspect system state')
    parser.add_argument('--events', type=int, metavar='COUNT',
                        help='View recent events (default: 20)')
    
    # Manipulation commands
    parser.add_argument('--fast-forward', type=float, metavar='HOURS',
                        help='Fast-forward simulation time')
    parser.add_argument('--set-weather', type=str, metavar='STATE',
                        help='Set weather state')
    parser.add_argument('--sector', type=str, default='test_sector',
                        help='Target sector for weather commands')
    
    # Snapshot commands
    parser.add_argument('--save', type=str, metavar='FILE',
                        help='Save simulation snapshot')
    parser.add_argument('--load', type=str, metavar='FILE',
                        help='Load simulation snapshot')
    
    args = parser.parse_args()
    
    # Initialize or load simulation
    if args.load:
        sim_loop = load_snapshot(args.load)
        if not sim_loop:
            return 1
    else:
        print_header(f"INITIALIZING SIMULATION: {args.session}")
        sim_loop = SimulationLoop()
        sim_loop.initialize_from_region(args.region)
        print(f"Initialized from region: {args.region}")
    
    # Execute commands
    if args.heatmap == 'suspicion':
        visualize_suspicion_heatmap(sim_loop)
    elif args.heatmap == 'traffic':
        visualize_traffic_heatmap(sim_loop)
    elif args.heatmap == 'wildlife':
        visualize_wildlife_density(sim_loop)
    
    if args.inspect:
        inspect_system_state(sim_loop)
    
    if args.events is not None:
        view_event_log(sim_loop, args.events or 20)
    
    if args.fast_forward:
        fast_forward_time(sim_loop, args.fast_forward)
    
    if args.set_weather:
        set_weather(sim_loop, args.sector, args.set_weather)
    
    if args.save:
        save_snapshot(sim_loop, args.save)
    
    # If no commands, show help
    if not any([args.heatmap, args.inspect, args.events is not None, 
                args.fast_forward, args.set_weather, args.save]):
        print_header("WORLD SIMULATION DEBUG TOOL")
        print("No commands specified. Use --help for usage information.")
        print("\nQuick examples:")
        print("  python scripts/sim_debug.py --heatmap suspicion")
        print("  python scripts/sim_debug.py --inspect")
        print("  python scripts/sim_debug.py --fast-forward 10")
        print("  python scripts/sim_debug.py --set-weather ion_storm --sector core_nexus")
        print("  python scripts/sim_debug.py --save snapshot.json")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
