"""
Weather System - Environmental conditions, state transitions, hazards.
Manages weather states, Markov chain transitions, and environmental modifiers.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import random
import time


class WeatherState(Enum):
    """Possible weather states."""
    CLEAR = "clear"
    LIGHT_NEBULA = "light_nebula"
    DENSE_NEBULA = "dense_nebula"
    ASTEROID_FIELD = "asteroid_field"
    DEBRIS_FIELD = "debris_field"
    ION_STORM = "ion_storm"
    SOLAR_FLARE = "solar_flare"


@dataclass
class WeatherCondition:
    """Current weather condition for a sector."""
    state: WeatherState
    intensity: float  # 0.0-1.0
    duration_remaining: float  # Hours
    modifiers: Dict[str, float] = field(default_factory=dict)


@dataclass
class WeatherHazard:
    """Active weather hazard."""
    hazard_id: str
    hazard_type: str
    sector: str
    severity: float
    duration_remaining: float
    damage_rate: float


class WeatherSystem:
    """Manages weather simulation and transitions."""
    
    def __init__(self, config):
        self.config = config
        self.sector_weather: Dict[str, WeatherCondition] = {}
        self.transition_timers: Dict[str, float] = {}
        self.active_hazards: List[WeatherHazard] = []
        self.forecast: Dict[str, List[WeatherState]] = {}  # sector -> [next states]
        self._hazard_counter = 0
    
    def tick(self, delta_time: float, current_sector: str) -> List[Dict]:
        """
        Update weather simulation.
        
        Args:
            delta_time: Time elapsed in hours
            current_sector: Player's current sector
            
        Returns:
            List of weather events
        """
        events = []
        
        # Initialize weather for sector if not exists
        if current_sector not in self.sector_weather:
            self._initialize_sector_weather(current_sector)
        
        # Update transition timer
        if current_sector in self.transition_timers:
            self.transition_timers[current_sector] -= delta_time
            
            if self.transition_timers[current_sector] <= 0:
                # Trigger weather transition
                old_state = self.sector_weather[current_sector].state
                new_state = self._transition_weather(current_sector)
                
                events.append({
                    "type": "weather_change",
                    "sector": current_sector,
                    "old_state": old_state.value,
                    "new_state": new_state.value
                })
                
                # Check if new state creates hazards
                if self._is_hazardous_weather(new_state):
                    hazard = self._create_hazard(current_sector, new_state)
                    events.append({
                        "type": "weather_hazard",
                        "sector": current_sector,
                        "weather_state": new_state.value,
                        "hazard_id": hazard.hazard_id
                    })
        
        # Update active hazards
        for hazard in list(self.active_hazards):
            hazard.duration_remaining -= delta_time
            
            if hazard.duration_remaining <= 0:
                self.active_hazards.remove(hazard)
                events.append({
                    "type": "hazard_ended",
                    "hazard_id": hazard.hazard_id,
                    "sector": hazard.sector
                })
        
        # Update weather condition durations
        for sector, condition in self.sector_weather.items():
            condition.duration_remaining -= delta_time
        
        return events
    
    def _initialize_sector_weather(self, sector: str, default_state: WeatherState = WeatherState.CLEAR):
        """Initialize weather for a sector."""
        modifiers = self.config.modifiers.get(default_state.value, {})
        
        self.sector_weather[sector] = WeatherCondition(
            state=default_state,
            intensity=random.uniform(0.3, 0.7),
            duration_remaining=random.uniform(
                self.config.weather_change_interval_min,
                self.config.weather_change_interval_max
            ),
            modifiers=modifiers
        )
        
        # Set transition timer
        self.transition_timers[sector] = random.uniform(
            self.config.weather_change_interval_min,
            self.config.weather_change_interval_max
        )
        
        # Generate forecast
        self._generate_forecast(sector)
    
    def _transition_weather(self, sector: str) -> WeatherState:
        """Transition weather to a new state using Markov chain."""
        current_condition = self.sector_weather[sector]
        current_state = current_condition.state
        
        # Get transition probabilities
        transitions = self.config.transition_probabilities.get(current_state.value, {})
        
        if not transitions:
            # No transitions defined, stay in current state
            return current_state
        
        # Weighted random choice
        states = list(transitions.keys())
        probabilities = list(transitions.values())
        
        # Normalize probabilities
        total = sum(probabilities)
        if total > 0:
            probabilities = [p / total for p in probabilities]
        else:
            # Equal probability if all zeros
            probabilities = [1.0 / len(states)] * len(states)
        
        new_state_str = random.choices(states, weights=probabilities)[0]
        new_state = WeatherState(new_state_str)
        
        # Update condition
        modifiers = self.config.modifiers.get(new_state.value, {})
        current_condition.state = new_state
        current_condition.intensity = random.uniform(0.3, 1.0)
        current_condition.modifiers = modifiers
        current_condition.duration_remaining = random.uniform(
            self.config.weather_change_interval_min,
            self.config.weather_change_interval_max
        )
        
        # Reset transition timer
        self.transition_timers[sector] = random.uniform(
            self.config.weather_change_interval_min,
            self.config.weather_change_interval_max
        )
        
        # Update forecast
        self._generate_forecast(sector)
        
        return new_state
    
    def _generate_forecast(self, sector: str):
        """Generate weather forecast for a sector."""
        current_state = self.sector_weather[sector].state
        forecast = []
        
        state = current_state
        for _ in range(self.config.forecast_steps):
            # Predict next state
            transitions = self.config.transition_probabilities.get(state.value, {})
            if transitions:
                # Apply forecast accuracy
                if random.random() < self.config.forecast_accuracy:
                    # Accurate prediction
                    states = list(transitions.keys())
                    probabilities = list(transitions.values())
                    total = sum(probabilities)
                    if total > 0:
                        probabilities = [p / total for p in probabilities]
                        next_state_str = random.choices(states, weights=probabilities)[0]
                        state = WeatherState(next_state_str)
                else:
                    # Inaccurate prediction - random state
                    state = random.choice(list(WeatherState))
            
            forecast.append(state)
        
        self.forecast[sector] = forecast
    
    def _is_hazardous_weather(self, state: WeatherState) -> bool:
        """Check if weather state is hazardous."""
        hazardous = [
            WeatherState.DENSE_NEBULA,
            WeatherState.DEBRIS_FIELD,
            WeatherState.ION_STORM,
            WeatherState.SOLAR_FLARE
        ]
        return state in hazardous
    
    def _create_hazard(self, sector: str, weather_state: WeatherState) -> WeatherHazard:
        """Create a weather hazard."""
        self._hazard_counter += 1
        
        modifiers = self.config.modifiers.get(weather_state.value, {})
        damage_rate = modifiers.get("ship_damage_rate", 0.0)
        
        hazard = WeatherHazard(
            hazard_id=f"hazard_{self._hazard_counter}",
            hazard_type=weather_state.value,
            sector=sector,
            severity=random.uniform(0.5, 1.0),
            duration_remaining=random.uniform(
                self.config.hazard_duration_min,
                self.config.hazard_duration_max
            ),
            damage_rate=damage_rate
        )
        
        self.active_hazards.append(hazard)
        return hazard
    
    def get_weather(self, sector: str) -> Optional[WeatherCondition]:
        """Get current weather for a sector."""
        return self.sector_weather.get(sector)
    
    def get_forecast(self, sector: str) -> List[WeatherState]:
        """Get weather forecast for a sector."""
        return self.forecast.get(sector, [])
    
    def get_modifiers(self, sector: str) -> Dict[str, float]:
        """Get environmental modifiers for current weather."""
        condition = self.sector_weather.get(sector)
        if condition:
            return condition.modifiers
        return {}
    
    def set_weather(self, sector: str, state: WeatherState):
        """Manually set weather (for testing/debug)."""
        if sector in self.sector_weather:
            self.sector_weather[sector].state = state
            self.sector_weather[sector].modifiers = self.config.modifiers.get(state.value, {})
        else:
            self._initialize_sector_weather(sector, state)
    
    def to_dict(self) -> Dict:
        """Serialize state."""
        return {
            "sector_weather": {
                sector: {
                    "state": condition.state.value,
                    "intensity": condition.intensity,
                    "duration_remaining": condition.duration_remaining
                }
                for sector, condition in self.sector_weather.items()
            },
            "transition_timers": self.transition_timers,
            "hazard_counter": self._hazard_counter
        }
    
    @classmethod
    def from_dict(cls, data: Dict, config) -> WeatherSystem:
        """Deserialize state."""
        system = cls(config)
        system.transition_timers = data.get("transition_timers", {})
        system._hazard_counter = data.get("hazard_counter", 0)
        
        # Restore weather conditions
        for sector, weather_data in data.get("sector_weather", {}).items():
            state = WeatherState(weather_data["state"])
            modifiers = config.modifiers.get(state.value, {})
            system.sector_weather[sector] = WeatherCondition(
                state=state,
                intensity=weather_data["intensity"],
                duration_remaining=weather_data["duration_remaining"],
                modifiers=modifiers
            )
        
        return system
