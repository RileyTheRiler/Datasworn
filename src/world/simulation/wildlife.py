"""
Wildlife System - Alien ecosystem simulation with populations, behaviors, predator/prey.
Manages creature spawning, behaviors, and ecological interactions.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import random


class BehaviorState(Enum):
    """Creature behavior states."""
    IDLE = "idle"
    HUNTING = "hunting"
    FLEEING = "fleeing"
    TERRITORIAL = "territorial"
    MIGRATING = "migrating"


@dataclass
class SpeciesPopulation:
    """Population data for a species in a biome."""
    species_id: str
    biome: str
    current_count: int
    population_cap: int
    is_predator: bool
    prey_species: List[str] = field(default_factory=list)


@dataclass
class Creature:
    """Individual creature instance."""
    creature_id: str
    species_id: str
    position: tuple  # (x, y, z)
    behavior_state: BehaviorState
    health: float = 1.0
    target_position: Optional[tuple] = None
    flee_timer: float = 0.0


class WildlifeSystem:
    """Manages alien ecosystem simulation."""
    
    def __init__(self, config):
        self.config = config
        self.populations: Dict[str, SpeciesPopulation] = {}
        self.active_creatures: Dict[str, Creature] = {}
        self.biome_densities: Dict[str, Dict[str, int]] = {}  # biome -> {species -> count}
        self.predator_prey_map: Dict[str, List[str]] = {}
        self._creature_counter = 0
    
    def tick(self, delta_time: float, current_biome: str, player_position: tuple) -> List[Dict]:
        """
        Update wildlife simulation.
        
        Args:
            delta_time: Time elapsed in hours
            current_biome: Player's current biome
            player_position: Player's position (x, y, z)
            
        Returns:
            List of wildlife events
        """
        events = []
        
        # Update existing creatures
        for creature_id, creature in list(self.active_creatures.items()):
            # Check despawn distance
            dist = self._calculate_distance(creature.position, player_position)
            if dist > self.config.despawn_distance:
                del self.active_creatures[creature_id]
                continue
            
            # Update behavior
            behavior_events = self._update_creature_behavior(creature, delta_time, player_position)
            events.extend(behavior_events)
            
            # Decay flee timer
            if creature.flee_timer > 0:
                creature.flee_timer -= delta_time
                if creature.flee_timer <= 0:
                    creature.behavior_state = BehaviorState.IDLE
        
        # Spawn new creatures based on density
        if current_biome in self.biome_densities:
            for species_id, current_count in self.biome_densities[current_biome].items():
                population = self.populations.get(f"{species_id}_{current_biome}")
                if population and current_count < population.population_cap:
                    # Chance to spawn
                    spawn_chance = self.config.spawn_density_multiplier * delta_time * 0.1
                    if random.random() < spawn_chance:
                        new_creature = self._spawn_creature(species_id, current_biome, player_position)
                        if new_creature:
                            self.active_creatures[new_creature.creature_id] = new_creature
                            events.append({
                                "type": "wildlife_spawn",
                                "species": species_id,
                                "biome": current_biome
                            })
        
        # Check for predator/prey interactions
        predator_events = self._process_predator_prey_interactions(player_position)
        events.extend(predator_events)
        
        # Check for migration triggers
        if random.random() < self.config.migration_trigger_chance * delta_time:
            migration_event = self._trigger_migration(current_biome)
            if migration_event:
                events.append(migration_event)
        
        # Check for player proximity events
        for creature in self.active_creatures.values():
            dist = self._calculate_distance(creature.position, player_position)
            
            # Predator stalking player
            if creature.behavior_state == BehaviorState.HUNTING and dist < self.config.predator_detection_range:
                population = self.populations.get(f"{creature.species_id}_{current_biome}")
                if population and population.is_predator:
                    events.append({
                        "type": "predator_stalking",
                        "species": creature.species_id,
                        "creature_id": creature.creature_id,
                        "distance": dist
                    })
        
        return events
    
    def _update_creature_behavior(self, creature: Creature, delta_time: float, player_position: tuple) -> List[Dict]:
        """Update individual creature behavior."""
        events = []
        
        if creature.behavior_state == BehaviorState.IDLE:
            # Chance to start hunting
            if random.random() < self.config.behavior_idle_to_hunting * delta_time:
                creature.behavior_state = BehaviorState.HUNTING
                events.append({
                    "type": "behavior_change",
                    "creature_id": creature.creature_id,
                    "new_state": "hunting"
                })
        
        elif creature.behavior_state == BehaviorState.HUNTING:
            # Chance to return to idle
            if random.random() < self.config.behavior_hunting_to_idle * delta_time:
                creature.behavior_state = BehaviorState.IDLE
        
        elif creature.behavior_state == BehaviorState.FLEEING:
            # Move away from player
            if creature.flee_timer <= 0:
                creature.behavior_state = BehaviorState.IDLE
        
        return events
    
    def _process_predator_prey_interactions(self, player_position: tuple) -> List[Dict]:
        """Process predator hunting prey."""
        events = []
        
        for predator in self.active_creatures.values():
            if predator.behavior_state != BehaviorState.HUNTING:
                continue
            
            # Find nearby prey
            for prey in self.active_creatures.values():
                if prey.creature_id == predator.creature_id:
                    continue
                
                # Check if prey species is in predator's diet
                if prey.species_id not in self.predator_prey_map.get(predator.species_id, []):
                    continue
                
                dist = self._calculate_distance(predator.position, prey.position)
                if dist < self.config.predator_detection_range:
                    # Predator chases prey
                    if random.random() < self.config.predator_hunt_success_chance:
                        # Successful hunt
                        del self.active_creatures[prey.creature_id]
                        events.append({
                            "type": "predator_kill",
                            "predator": predator.species_id,
                            "prey": prey.species_id
                        })
                    else:
                        # Prey escapes
                        prey.behavior_state = BehaviorState.FLEEING
                        prey.flee_timer = self.config.behavior_flee_duration
                        events.append({
                            "type": "prey_escape",
                            "predator": predator.species_id,
                            "prey": prey.species_id
                        })
                    break  # Predator focuses on one prey at a time
        
        return events
    
    def _spawn_creature(self, species_id: str, biome: str, player_position: tuple) -> Optional[Creature]:
        """Spawn a new creature."""
        self._creature_counter += 1
        
        # Random position near player but not too close
        offset_x = random.uniform(-5, 5)
        offset_y = random.uniform(-5, 5)
        offset_z = random.uniform(-5, 5)
        
        position = (
            player_position[0] + offset_x,
            player_position[1] + offset_y,
            player_position[2] + offset_z
        )
        
        creature = Creature(
            creature_id=f"{species_id}_{self._creature_counter}",
            species_id=species_id,
            position=position,
            behavior_state=BehaviorState.IDLE
        )
        
        # Update density
        if biome not in self.biome_densities:
            self.biome_densities[biome] = {}
        self.biome_densities[biome][species_id] = self.biome_densities[biome].get(species_id, 0) + 1
        
        return creature
    
    def _trigger_migration(self, current_biome: str) -> Optional[Dict]:
        """Trigger a migration event."""
        # Pick a random species in the biome
        if current_biome not in self.biome_densities or not self.biome_densities[current_biome]:
            return None
        
        species_id = random.choice(list(self.biome_densities[current_biome].keys()))
        
        # Remove some creatures (they migrated away)
        count = self.biome_densities[current_biome][species_id]
        migrated = int(count * 0.5)  # 50% migrate
        
        self.biome_densities[current_biome][species_id] -= migrated
        
        return {
            "type": "wildlife_migration",
            "species": species_id,
            "count": migrated,
            "from_biome": current_biome
        }
    
    def _calculate_distance(self, pos1: tuple, pos2: tuple) -> float:
        """Calculate 3D distance between positions."""
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        dz = pos1[2] - pos2[2]
        return (dx**2 + dy**2 + dz**2) ** 0.5
    
    def initialize_population(self, species_id: str, biome: str, cap: int, is_predator: bool, prey: List[str] = None):
        """Initialize a species population for a biome."""
        pop_id = f"{species_id}_{biome}"
        self.populations[pop_id] = SpeciesPopulation(
            species_id=species_id,
            biome=biome,
            current_count=0,
            population_cap=int(cap * self.config.population_cap_multiplier),
            is_predator=is_predator,
            prey_species=prey or []
        )
        
        if is_predator and prey:
            self.predator_prey_map[species_id] = prey
        
        # Initialize density tracking
        if biome not in self.biome_densities:
            self.biome_densities[biome] = {}
        self.biome_densities[biome][species_id] = 0
    
    def get_population_count(self, species_id: str, biome: str) -> int:
        """Get current population count for a species in a biome."""
        return self.biome_densities.get(biome, {}).get(species_id, 0)
    
    def to_dict(self) -> Dict:
        """Serialize state."""
        return {
            "biome_densities": self.biome_densities,
            "creature_counter": self._creature_counter
        }
    
    @classmethod
    def from_dict(cls, data: Dict, config) -> WildlifeSystem:
        """Deserialize state."""
        system = cls(config)
        system.biome_densities = data.get("biome_densities", {})
        system._creature_counter = data.get("creature_counter", 0)
        return system
