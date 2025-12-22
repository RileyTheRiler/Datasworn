"""
Configuration Loader for World Simulation Systems.
Loads and validates simulation.yml and regions.yaml with type-safe access.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import yaml
from pathlib import Path


# =============================================================================
# Configuration Data Classes
# =============================================================================

@dataclass
class TrafficConfig:
    """Traffic system configuration."""
    congestion_threshold_low: float = 0.3
    congestion_threshold_high: float = 0.7
    max_ships_per_sector: int = 50
    trade_route_density: float = 0.6
    convoy_size_min: int = 2
    convoy_size_max: int = 5
    trade_ship_speed: float = 1.0
    patrol_frequency_multiplier: float = 1.0
    patrol_route_variance: float = 0.2
    patrol_scan_range: float = 2.0
    avoidance_distance: float = 1.5
    emergency_stop_distance: float = 0.5


@dataclass
class LawConfig:
    """Law enforcement system configuration."""
    suspicion_decay_rate: float = 0.1
    suspicion_threshold_investigation: float = 0.3
    suspicion_threshold_pursuit: float = 0.6
    suspicion_threshold_lethal: float = 0.9
    crime_severity_multipliers: Dict[str, float] = field(default_factory=dict)
    witness_report_chance: float = 0.7
    witness_memory_duration: float = 24.0
    investigation_duration: float = 2.0
    scan_detection_chance: float = 0.8
    pursuit_ship_speed_multiplier: float = 1.3
    pursuit_duration_max: float = 6.0
    blockade_threshold: float = 0.8
    escalation_warning_duration: float = 0.5
    escalation_fine_duration: float = 1.0
    escalation_arrest_duration: float = 2.0
    bounty_base_amount: int = 1000
    bounty_multiplier_per_severity: int = 500
    bounty_decay_rate: float = 0.05


@dataclass
class WildlifeConfig:
    """Wildlife system configuration."""
    population_cap_multiplier: float = 1.0
    spawn_density_multiplier: float = 1.0
    despawn_distance: float = 5.0
    behavior_idle_to_hunting: float = 0.1
    behavior_hunting_to_idle: float = 0.05
    behavior_flee_duration: float = 3.0
    behavior_territorial_radius: float = 2.0
    predator_detection_range: float = 1.5
    predator_chase_speed_multiplier: float = 1.5
    prey_flee_speed_multiplier: float = 1.2
    predator_hunt_success_chance: float = 0.3
    migration_trigger_chance: float = 0.01
    migration_distance_min: int = 3
    migration_distance_max: int = 8
    species_caps: Dict[str, int] = field(default_factory=dict)


@dataclass
class WeatherConfig:
    """Weather system configuration."""
    transition_probabilities: Dict[str, Dict[str, float]] = field(default_factory=dict)
    weather_change_interval_min: float = 2.0
    weather_change_interval_max: float = 8.0
    modifiers: Dict[str, Dict[str, float]] = field(default_factory=dict)
    hazard_duration_min: float = 1.0
    hazard_duration_max: float = 4.0
    forecast_steps: int = 3
    forecast_accuracy: float = 0.7


@dataclass
class GlobalConfig:
    """Global simulation settings."""
    tick_rate: float = 1.0
    time_scale: float = 1.0
    event_history_max: int = 100
    enable_cross_system_events: bool = True
    debug_mode: bool = False


@dataclass
class SimulationConfig:
    """Complete simulation configuration."""
    traffic: TrafficConfig
    law: LawConfig
    wildlife: WildlifeConfig
    weather: WeatherConfig
    global_settings: GlobalConfig


# =============================================================================
# Regional Data Classes
# =============================================================================

@dataclass
class LawPresence:
    """Law enforcement presence in a region."""
    patrol_density: float
    response_time: Optional[float]
    escalation_speed: float
    bounty_enforcement: str


@dataclass
class TrafficData:
    """Traffic patterns in a region."""
    trade_route_density: float
    congestion_baseline: float
    patrol_routes: int


@dataclass
class WildlifeData:
    """Wildlife configuration for a region."""
    spawn_enabled: bool
    species_present: List[str]
    density_multiplier: float = 1.0


@dataclass
class WeatherData:
    """Weather patterns for a region."""
    default_state: str
    hazard_frequency: float
    common_states: List[str]


@dataclass
class Region:
    """Regional metadata."""
    id: str
    name: str
    biome: str
    description: str
    settlement_density: float
    population_tier: str
    infrastructure_level: str
    faction_ownership: Optional[str]
    faction_influence: Dict[str, float]
    law_presence: LawPresence
    traffic: TrafficData
    wildlife: WildlifeData
    weather: WeatherData


@dataclass
class Biome:
    """Biome definition."""
    description: str
    base_visibility: float
    base_danger: float


# =============================================================================
# Config Loader
# =============================================================================

class ConfigLoader:
    """Loads and validates simulation configuration files."""
    
    def __init__(self, config_dir: str = "config", data_dir: str = "data"):
        self.config_dir = Path(config_dir)
        self.data_dir = Path(data_dir)
        self._simulation_config: Optional[SimulationConfig] = None
        self._regions: Optional[Dict[str, Region]] = None
        self._biomes: Optional[Dict[str, Biome]] = None
    
    def load_simulation_config(self) -> SimulationConfig:
        """Load simulation.yml configuration."""
        if self._simulation_config is not None:
            return self._simulation_config
        
        config_path = self.config_dir / "simulation.yml"
        if not config_path.exists():
            raise FileNotFoundError(f"Simulation config not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Parse traffic config
        traffic_data = data.get('traffic', {})
        traffic = TrafficConfig(
            congestion_threshold_low=traffic_data.get('congestion_threshold_low', 0.3),
            congestion_threshold_high=traffic_data.get('congestion_threshold_high', 0.7),
            max_ships_per_sector=traffic_data.get('max_ships_per_sector', 50),
            trade_route_density=traffic_data.get('trade_route_density', 0.6),
            convoy_size_min=traffic_data.get('convoy_size_min', 2),
            convoy_size_max=traffic_data.get('convoy_size_max', 5),
            trade_ship_speed=traffic_data.get('trade_ship_speed', 1.0),
            patrol_frequency_multiplier=traffic_data.get('patrol_frequency_multiplier', 1.0),
            patrol_route_variance=traffic_data.get('patrol_route_variance', 0.2),
            patrol_scan_range=traffic_data.get('patrol_scan_range', 2.0),
            avoidance_distance=traffic_data.get('avoidance_distance', 1.5),
            emergency_stop_distance=traffic_data.get('emergency_stop_distance', 0.5),
        )
        
        # Parse law config
        law_data = data.get('law', {})
        law = LawConfig(
            suspicion_decay_rate=law_data.get('suspicion_decay_rate', 0.1),
            suspicion_threshold_investigation=law_data.get('suspicion_threshold_investigation', 0.3),
            suspicion_threshold_pursuit=law_data.get('suspicion_threshold_pursuit', 0.6),
            suspicion_threshold_lethal=law_data.get('suspicion_threshold_lethal', 0.9),
            crime_severity_multipliers=law_data.get('crime_severity_multipliers', {}),
            witness_report_chance=law_data.get('witness_report_chance', 0.7),
            witness_memory_duration=law_data.get('witness_memory_duration', 24.0),
            investigation_duration=law_data.get('investigation_duration', 2.0),
            scan_detection_chance=law_data.get('scan_detection_chance', 0.8),
            pursuit_ship_speed_multiplier=law_data.get('pursuit_ship_speed_multiplier', 1.3),
            pursuit_duration_max=law_data.get('pursuit_duration_max', 6.0),
            blockade_threshold=law_data.get('blockade_threshold', 0.8),
            escalation_warning_duration=law_data.get('escalation_warning_duration', 0.5),
            escalation_fine_duration=law_data.get('escalation_fine_duration', 1.0),
            escalation_arrest_duration=law_data.get('escalation_arrest_duration', 2.0),
            bounty_base_amount=law_data.get('bounty_base_amount', 1000),
            bounty_multiplier_per_severity=law_data.get('bounty_multiplier_per_severity', 500),
            bounty_decay_rate=law_data.get('bounty_decay_rate', 0.05),
        )
        
        # Parse wildlife config
        wildlife_data = data.get('wildlife', {})
        wildlife = WildlifeConfig(
            population_cap_multiplier=wildlife_data.get('population_cap_multiplier', 1.0),
            spawn_density_multiplier=wildlife_data.get('spawn_density_multiplier', 1.0),
            despawn_distance=wildlife_data.get('despawn_distance', 5.0),
            behavior_idle_to_hunting=wildlife_data.get('behavior_idle_to_hunting', 0.1),
            behavior_hunting_to_idle=wildlife_data.get('behavior_hunting_to_idle', 0.05),
            behavior_flee_duration=wildlife_data.get('behavior_flee_duration', 3.0),
            behavior_territorial_radius=wildlife_data.get('behavior_territorial_radius', 2.0),
            predator_detection_range=wildlife_data.get('predator_detection_range', 1.5),
            predator_chase_speed_multiplier=wildlife_data.get('predator_chase_speed_multiplier', 1.5),
            prey_flee_speed_multiplier=wildlife_data.get('prey_flee_speed_multiplier', 1.2),
            predator_hunt_success_chance=wildlife_data.get('predator_hunt_success_chance', 0.3),
            migration_trigger_chance=wildlife_data.get('migration_trigger_chance', 0.01),
            migration_distance_min=wildlife_data.get('migration_distance_min', 3),
            migration_distance_max=wildlife_data.get('migration_distance_max', 8),
            species_caps=wildlife_data.get('species_caps', {}),
        )
        
        # Parse weather config
        weather_data = data.get('weather', {})
        weather = WeatherConfig(
            transition_probabilities=weather_data.get('transition_probabilities', {}),
            weather_change_interval_min=weather_data.get('weather_change_interval_min', 2.0),
            weather_change_interval_max=weather_data.get('weather_change_interval_max', 8.0),
            modifiers=weather_data.get('modifiers', {}),
            hazard_duration_min=weather_data.get('hazard_duration_min', 1.0),
            hazard_duration_max=weather_data.get('hazard_duration_max', 4.0),
            forecast_steps=weather_data.get('forecast_steps', 3),
            forecast_accuracy=weather_data.get('forecast_accuracy', 0.7),
        )
        
        # Parse global config
        global_data = data.get('global', {})
        global_settings = GlobalConfig(
            tick_rate=global_data.get('tick_rate', 1.0),
            time_scale=global_data.get('time_scale', 1.0),
            event_history_max=global_data.get('event_history_max', 100),
            enable_cross_system_events=global_data.get('enable_cross_system_events', True),
            debug_mode=global_data.get('debug_mode', False),
        )
        
        self._simulation_config = SimulationConfig(
            traffic=traffic,
            law=law,
            wildlife=wildlife,
            weather=weather,
            global_settings=global_settings
        )
        
        return self._simulation_config
    
    def load_regions(self) -> Dict[str, Region]:
        """Load regions.yaml regional metadata."""
        if self._regions is not None:
            return self._regions
        
        regions_path = self.data_dir / "world" / "regions.yaml"
        if not regions_path.exists():
            raise FileNotFoundError(f"Regions file not found: {regions_path}")
        
        with open(regions_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        regions = {}
        for region_data in data.get('regions', []):
            # Parse law presence
            law_data = region_data.get('law_presence', {})
            law_presence = LawPresence(
                patrol_density=law_data.get('patrol_density', 0.0),
                response_time=law_data.get('response_time'),
                escalation_speed=law_data.get('escalation_speed', 1.0),
                bounty_enforcement=law_data.get('bounty_enforcement', 'none'),
            )
            
            # Parse traffic
            traffic_data = region_data.get('traffic', {})
            traffic = TrafficData(
                trade_route_density=traffic_data.get('trade_route_density', 0.0),
                congestion_baseline=traffic_data.get('congestion_baseline', 0.0),
                patrol_routes=traffic_data.get('patrol_routes', 0),
            )
            
            # Parse wildlife
            wildlife_data = region_data.get('wildlife', {})
            wildlife = WildlifeData(
                spawn_enabled=wildlife_data.get('spawn_enabled', False),
                species_present=wildlife_data.get('species_present', []),
                density_multiplier=wildlife_data.get('density_multiplier', 1.0),
            )
            
            # Parse weather
            weather_data = region_data.get('weather', {})
            weather = WeatherData(
                default_state=weather_data.get('default_state', 'clear'),
                hazard_frequency=weather_data.get('hazard_frequency', 0.0),
                common_states=weather_data.get('common_states', ['clear']),
            )
            
            region = Region(
                id=region_data['id'],
                name=region_data['name'],
                biome=region_data['biome'],
                description=region_data['description'],
                settlement_density=region_data.get('settlement_density', 0.0),
                population_tier=region_data.get('population_tier', 'none'),
                infrastructure_level=region_data.get('infrastructure_level', 'none'),
                faction_ownership=region_data.get('faction_ownership'),
                faction_influence=region_data.get('faction_influence', {}),
                law_presence=law_presence,
                traffic=traffic,
                wildlife=wildlife,
                weather=weather,
            )
            
            regions[region.id] = region
        
        # Load biomes
        biomes = {}
        for biome_id, biome_data in data.get('biomes', {}).items():
            biomes[biome_id] = Biome(
                description=biome_data.get('description', ''),
                base_visibility=biome_data.get('base_visibility', 1.0),
                base_danger=biome_data.get('base_danger', 0.0),
            )
        
        self._regions = regions
        self._biomes = biomes
        
        return regions
    
    def get_region(self, region_id: str) -> Optional[Region]:
        """Get a specific region by ID."""
        if self._regions is None:
            self.load_regions()
        return self._regions.get(region_id)
    
    def get_biome(self, biome_id: str) -> Optional[Biome]:
        """Get a specific biome by ID."""
        if self._biomes is None:
            self.load_regions()
        return self._biomes.get(biome_id)
    
    def reload(self):
        """Reload all configuration (for hot-reload during development)."""
        self._simulation_config = None
        self._regions = None
        self._biomes = None
        return self.load_simulation_config(), self.load_regions()


# =============================================================================
# Global Instance
# =============================================================================

# Singleton instance for easy access
_config_loader: Optional[ConfigLoader] = None

def get_config_loader() -> ConfigLoader:
    """Get the global config loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader
