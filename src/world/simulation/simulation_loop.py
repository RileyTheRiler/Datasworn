"""
Simulation Loop - Central coordinator for all world simulation systems.
Ticks each system, resolves inter-system events, and publishes to dispatcher.
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import time

from src.world.simulation.config_loader import SimulationConfig, get_config_loader
from src.world.simulation.traffic import TrafficSystem, Vector3, PatrolRoute
from src.world.simulation.law import LawSystem
from src.world.simulation.wildlife import WildlifeSystem
from src.world.simulation.weather import WeatherSystem, WeatherState
from src.world.simulation.event_dispatcher import WorldEventDispatcher, EventType


@dataclass
class SimulationState:
    """Complete simulation state for persistence."""
    traffic_state: Dict
    law_state: Dict
    wildlife_state: Dict
    weather_state: Dict
    dispatcher_state: Dict
    last_tick_time: float


class SimulationLoop:
    """Central simulation coordinator."""
    
    def __init__(self, config: Optional[SimulationConfig] = None):
        # Load config if not provided
        if config is None:
            loader = get_config_loader()
            config = loader.load_simulation_config()
        
        self.config = config
        
        # Initialize systems
        self.traffic = TrafficSystem(config.traffic)
        self.law = LawSystem(config.law)
        self.wildlife = WildlifeSystem(config.wildlife)
        self.weather = WeatherSystem(config.weather)
        self.dispatcher = WorldEventDispatcher(config.global_settings.event_history_max)
        
        # Timing
        self.last_tick_time = time.time()
        self.accumulated_time = 0.0
        
        # Cross-system event handlers
        self._setup_cross_system_events()
    
    def _setup_cross_system_events(self):
        """Set up cross-system event handlers."""
        if not self.config.global_settings.enable_cross_system_events:
            return
        
        # Weather affects traffic congestion
        def on_weather_hazard(event):
            sector = event.data.get('sector')
            if sector:
                # Increase congestion due to hazard
                current_congestion = self.traffic.get_congestion(sector)
                self.traffic.congestion_map[sector] = min(1.0, current_congestion + 0.2)
        
        self.dispatcher.subscribe(EventType.WEATHER_HAZARD, on_weather_hazard)
        
        # Crime triggers law response
        def on_crime_committed(event):
            # Law system handles this internally, but we can log it
            if self.config.global_settings.debug_mode:
                print(f"Crime committed: {event.data}")
        
        self.dispatcher.subscribe(EventType.CRIME_COMMITTED, on_crime_committed)
        
        # Predator near traffic could trigger distress signal
        def on_predator_stalking(event):
            # Check if any ships are nearby
            # This is a simplified cross-system interaction
            pass
        
        self.dispatcher.subscribe(EventType.PREDATOR_STALKING, on_predator_stalking)
    
    def tick(self, game_state: Dict[str, Any]) -> List[Dict]:
        """
        Run one simulation tick.
        
        Args:
            game_state: Current game state with player info
            
        Returns:
            List of all events generated this tick
        """
        current_time = time.time()
        real_delta = current_time - self.last_tick_time
        self.last_tick_time = current_time
        
        # Apply time scale
        delta_time = real_delta * self.config.global_settings.time_scale / 3600.0  # Convert to hours
        
        all_events = []
        
        # Extract player state
        player_position = self._get_player_position(game_state)
        current_sector = self._get_current_sector(game_state)
        current_biome = self._get_current_biome(game_state)
        player_state = self._extract_player_state(game_state)
        
        # Tick each system in priority order
        
        # 1. Weather (affects other systems)
        weather_events = self.weather.tick(delta_time, current_sector)
        all_events.extend(weather_events)
        
        # 2. Wildlife (can affect traffic and law)
        wildlife_events = self.wildlife.tick(delta_time, current_biome, player_position)
        all_events.extend(wildlife_events)
        
        # 3. Traffic (can trigger law events)
        traffic_events = self.traffic.tick(delta_time, current_sector, Vector3(*player_position))
        all_events.extend(traffic_events)
        
        # 4. Law (responds to all other systems)
        law_events = self.law.tick(delta_time, player_state)
        all_events.extend(law_events)
        
        # Publish all events to dispatcher
        self.dispatcher.publish_batch(all_events)
        
        # Resolve cross-system interactions
        if self.config.global_settings.enable_cross_system_events:
            cross_events = self._resolve_cross_system_events(all_events, game_state)
            all_events.extend(cross_events)
        
        return all_events
    
    def _resolve_cross_system_events(self, events: List[Dict], game_state: Dict) -> List[Dict]:
        """Resolve interactions between systems."""
        cross_events = []
        
        # Example: Storm + Traffic Congestion = Convoy Breakdown
        has_storm = any(e.get('type') == 'weather_hazard' for e in events)
        has_congestion = any(e.get('type') == 'traffic_congestion' for e in events)
        
        if has_storm and has_congestion:
            cross_events.append({
                'type': 'distress_signal',
                'source': 'convoy',
                'reason': 'storm_breakdown'
            })
        
        # Example: Predator + Trade Route = Distress Signal
        has_predator = any(e.get('type') == 'predator_stalking' for e in events)
        has_traffic = any(e.get('type') == 'traffic_spawn' and e.get('ship_type') == 'trader' for e in events)
        
        if has_predator and has_traffic:
            cross_events.append({
                'type': 'distress_signal',
                'source': 'trader',
                'reason': 'predator_attack'
            })
        
        return cross_events
    
    def _get_player_position(self, game_state: Dict) -> tuple:
        """Extract player position from game state."""
        # Default position if not found
        return (0.0, 0.0, 0.0)
    
    def _get_current_sector(self, game_state: Dict) -> str:
        """Extract current sector from game state."""
        world = game_state.get('world', {})
        if isinstance(world, dict):
            return world.get('current_location', 'unknown_sector')
        return getattr(world, 'current_location', 'unknown_sector')
    
    def _get_current_biome(self, game_state: Dict) -> str:
        """Extract current biome from game state."""
        world = game_state.get('world', {})
        if isinstance(world, dict):
            return world.get('location_type', 'neutral')
        return getattr(world, 'location_type', 'neutral')
    
    def _extract_player_state(self, game_state: Dict) -> Dict:
        """Extract relevant player state for law system."""
        character = game_state.get('character', {})
        
        # Extract or create default player state
        player_state = {
            'crimes_committed': getattr(character, 'crimes_committed', []) if hasattr(character, 'crimes_committed') else [],
            'reputation': getattr(character, 'reputation', {}) if hasattr(character, 'reputation') else {},
            'honor': getattr(character, 'honor', 0.5) if hasattr(character, 'honor') else 0.5,
            'current_posture': getattr(character, 'current_posture', 'normal') if hasattr(character, 'current_posture') else 'normal',
            'weapon_readied': getattr(character, 'weapon_readied', False) if hasattr(character, 'weapon_readied') else False,
            'intoxication_level': getattr(character, 'intoxication_level', 0.0) if hasattr(character, 'intoxication_level') else 0.0,
            'disguise_active': getattr(character, 'disguise_active', None) if hasattr(character, 'disguise_active') else None,
        }
        
        return player_state
    
    def initialize_from_region(self, region_id: str):
        """Initialize simulation systems based on regional metadata."""
        loader = get_config_loader()
        region = loader.get_region(region_id)
        
        if not region:
            print(f"Warning: Region {region_id} not found")
            return
        
        # Initialize weather for region
        default_weather = WeatherState(region.weather.default_state)
        self.weather.set_weather(region_id, default_weather)
        
        # Initialize wildlife populations
        if region.wildlife.spawn_enabled:
            for species_id in region.wildlife.species_present:
                # Get species cap from config
                cap = self.config.wildlife.species_caps.get(species_id, 10)
                
                # Determine if predator (simplified)
                is_predator = species_id in ['void_leviathan', 'plasma_eel']
                prey = ['nebula_drifter', 'asteroid_borer'] if is_predator else []
                
                self.wildlife.initialize_population(
                    species_id,
                    region.biome,
                    cap,
                    is_predator,
                    prey
                )
        
        # Initialize patrol routes based on law presence
        if region.law_presence.patrol_density > 0 and region.faction_ownership:
            # Create a simple patrol route (can be expanded)
            waypoints = [
                Vector3(0, 0, 0),
                Vector3(5, 0, 0),
                Vector3(5, 5, 0),
                Vector3(0, 5, 0),
            ]
            
            patrol = PatrolRoute(
                faction=region.faction_ownership,
                waypoints=waypoints,
                patrol_frequency=region.law_presence.patrol_density,
                scan_range=self.config.traffic.patrol_scan_range
            )
            
            self.traffic.add_patrol_route(region.faction_ownership, patrol)
    
    def get_state(self) -> SimulationState:
        """Get complete simulation state for persistence."""
        return SimulationState(
            traffic_state=self.traffic.to_dict(),
            law_state=self.law.to_dict(),
            wildlife_state=self.wildlife.to_dict(),
            weather_state=self.weather.to_dict(),
            dispatcher_state=self.dispatcher.to_dict(),
            last_tick_time=self.last_tick_time
        )
    
    def load_state(self, state: SimulationState):
        """Load simulation state from persistence."""
        self.traffic = TrafficSystem.from_dict(state.traffic_state, self.config.traffic)
        self.law = LawSystem.from_dict(state.law_state, self.config.law)
        self.wildlife = WildlifeSystem.from_dict(state.wildlife_state, self.config.wildlife)
        self.weather = WeatherSystem.from_dict(state.weather_state, self.config.weather)
        self.dispatcher = WorldEventDispatcher.from_dict(
            state.dispatcher_state,
            self.config.global_settings.event_history_max
        )
        self.last_tick_time = state.last_tick_time
    
    def to_dict(self) -> Dict:
        """Serialize complete state."""
        state = self.get_state()
        return {
            'traffic': state.traffic_state,
            'law': state.law_state,
            'wildlife': state.wildlife_state,
            'weather': state.weather_state,
            'dispatcher': state.dispatcher_state,
            'last_tick_time': state.last_tick_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict, config: Optional[SimulationConfig] = None) -> SimulationLoop:
        """Deserialize from dict."""
        loop = cls(config)
        
        state = SimulationState(
            traffic_state=data.get('traffic', {}),
            law_state=data.get('law', {}),
            wildlife_state=data.get('wildlife', {}),
            weather_state=data.get('weather', {}),
            dispatcher_state=data.get('dispatcher', {}),
            last_tick_time=data.get('last_tick_time', time.time())
        )
        
        loop.load_state(state)
        return loop
