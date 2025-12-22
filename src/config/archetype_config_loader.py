"""
Configuration loader for the archetype system.

Loads and validates archetype definitions from YAML configuration.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class ArchetypeDefinition:
    """Definition of a single archetype from configuration."""
    name: str
    cluster: str
    psychological_wound: str
    psychological_need: str
    moral_corruption: str
    moral_need: str
    signals: Dict[str, Dict[str, float]]
    stress_modifiers: Dict[str, float]
    seeds: Dict[str, List[str]]
    revelation_triggers: Dict[str, str]


@dataclass
class InferenceConfig:
    """Configuration for the inference engine."""
    decay_rate: float
    confidence_threshold: float
    shift_threshold: float
    min_observations: int


@dataclass
class RevelationConfig:
    """Configuration for revelation triggers."""
    mirror_moment_threshold: float
    cost_revealed_threshold: float
    origin_glimpsed_threshold: float
    choice_crystallized_threshold: float
    final_revelation_threshold: float
    min_scenes_between_revelations: int


class ArchetypeConfigLoader:
    """Loads and provides access to archetype configuration."""
    
    def __init__(self, config_path: str = None):
        """
        Initialize the config loader.
        
        Args:
            config_path: Path to the archetype_config.yaml file.
                        If None, uses default location.
        """
        if config_path is None:
            # Default to config/archetype_config.yaml relative to project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "archetype_config.yaml"
        
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self._archetypes: Dict[str, ArchetypeDefinition] = {}
        self._load_config()
    
    def _load_config(self):
        """Load the YAML configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Archetype configuration not found: {self.config_path}"
            )
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)
        
        # Parse archetype definitions
        archetypes_data = self._config.get('archetypes', {})
        for name, data in archetypes_data.items():
            self._archetypes[name] = ArchetypeDefinition(
                name=name,
                cluster=data['cluster'],
                psychological_wound=data['psychological_wound'],
                psychological_need=data['psychological_need'],
                moral_corruption=data['moral_corruption'],
                moral_need=data['moral_need'],
                signals=data.get('signals', {}),
                stress_modifiers=data.get('stress_modifiers', {}),
                seeds=data.get('seeds', {}),
                revelation_triggers=data.get('revelation_triggers', {}),
            )
    
    def get_archetype(self, name: str) -> ArchetypeDefinition:
        """Get definition for a specific archetype."""
        if name not in self._archetypes:
            raise ValueError(f"Unknown archetype: {name}")
        return self._archetypes[name]
    
    def get_all_archetypes(self) -> Dict[str, ArchetypeDefinition]:
        """Get all archetype definitions."""
        return self._archetypes.copy()
    
    def get_archetype_names(self) -> List[str]:
        """Get list of all archetype names."""
        return list(self._archetypes.keys())
    
    def get_archetypes_by_cluster(self, cluster: str) -> List[str]:
        """Get all archetypes in a specific cluster."""
        return [
            name for name, defn in self._archetypes.items()
            if defn.cluster == cluster
        ]
    
    def get_inference_config(self) -> InferenceConfig:
        """Get inference engine configuration."""
        inference_data = self._config.get('inference', {})
        return InferenceConfig(
            decay_rate=inference_data.get('decay_rate', 0.95),
            confidence_threshold=inference_data.get('confidence_threshold', 0.6),
            shift_threshold=inference_data.get('shift_threshold', 0.15),
            min_observations=inference_data.get('min_observations', 5),
        )
    
    def get_revelation_config(self) -> RevelationConfig:
        """Get revelation configuration."""
        revelation_data = self._config.get('revelation', {})
        return RevelationConfig(
            mirror_moment_threshold=revelation_data.get('mirror_moment_threshold', 0.25),
            cost_revealed_threshold=revelation_data.get('cost_revealed_threshold', 0.40),
            origin_glimpsed_threshold=revelation_data.get('origin_glimpsed_threshold', 0.55),
            choice_crystallized_threshold=revelation_data.get('choice_crystallized_threshold', 0.70),
            final_revelation_threshold=revelation_data.get('final_revelation_threshold', 0.85),
            min_scenes_between_revelations=revelation_data.get('min_scenes_between_revelations', 3),
        )
    
    def get_signal_weight(
        self, 
        archetype: str, 
        behavior_type: str, 
        signal_name: str
    ) -> float:
        """
        Get the signal weight for a specific behavior.
        
        Args:
            archetype: Name of the archetype
            behavior_type: Type of behavior (dialogue, action, interrogation, crisis)
            signal_name: Specific signal within that behavior type
            
        Returns:
            Signal weight (0.0 if not found)
        """
        archetype_def = self.get_archetype(archetype)
        return archetype_def.signals.get(behavior_type, {}).get(signal_name, 0.0)
    
    def get_stress_modifier(self, archetype: str, stress_type: str) -> float:
        """
        Get the stress modifier for a specific stress type.
        
        Args:
            archetype: Name of the archetype
            stress_type: Type of stress
            
        Returns:
            Stress modifier (1.0 if not found, meaning no modification)
        """
        archetype_def = self.get_archetype(archetype)
        return archetype_def.stress_modifiers.get(stress_type, 1.0)
    
    def get_seeds(self, archetype: str, seed_type: str = None) -> List[str]:
        """
        Get foreshadowing seeds for an archetype.
        
        Args:
            archetype: Name of the archetype
            seed_type: Type of seed (environmental, dialogue, symbolic).
                      If None, returns all seeds.
            
        Returns:
            List of seed strings
        """
        archetype_def = self.get_archetype(archetype)
        if seed_type is None:
            # Return all seeds
            all_seeds = []
            for seeds_list in archetype_def.seeds.values():
                all_seeds.extend(seeds_list)
            return all_seeds
        else:
            return archetype_def.seeds.get(seed_type, [])
    
    def get_revelation_trigger(self, archetype: str, trigger_type: str) -> str:
        """
        Get the revelation trigger condition for an archetype.
        
        Args:
            archetype: Name of the archetype
            trigger_type: Type of trigger (mirror_moment, cost_revealed, etc.)
            
        Returns:
            Trigger condition string
        """
        archetype_def = self.get_archetype(archetype)
        return archetype_def.revelation_triggers.get(trigger_type, "")


# Global singleton instance
_config_loader: ArchetypeConfigLoader = None


def get_config_loader() -> ArchetypeConfigLoader:
    """Get the global configuration loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ArchetypeConfigLoader()
    return _config_loader


def reload_config():
    """Reload the configuration from disk."""
    global _config_loader
    _config_loader = ArchetypeConfigLoader()
