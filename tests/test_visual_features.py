"""
Test Visual Features - Environmental Landscapes, Weather, and Time of Day
"""

import pytest
from src.game_state import WorldState
from src.image_gen import generate_landscape_prompt, TimeOfDay, WeatherCondition


def test_world_state_environmental_fields():
    """Test that WorldState has environmental tracking fields."""
    world = WorldState()
    
    assert hasattr(world, 'current_time')
    assert hasattr(world, 'current_weather')
    assert hasattr(world, 'location_visuals')
    
    assert world.current_time == "Day"
    assert world.current_weather == "Clear"
    assert isinstance(world.location_visuals, dict)


def test_time_of_day_enum():
    """Test TimeOfDay enum values."""
    assert TimeOfDay.DAY.value == "Day"
    assert TimeOfDay.NIGHT.value == "Night"
    assert TimeOfDay.TWILIGHT.value == "Twilight"
    assert TimeOfDay.DAWN.value == "Dawn"


def test_weather_condition_enum():
    """Test WeatherCondition enum values."""
    assert WeatherCondition.CLEAR.value == "Clear"
    assert WeatherCondition.RAIN.value == "Rain"
    assert WeatherCondition.DUST_STORM.value == "Dust Storm"
    assert WeatherCondition.FOG.value == "Fog"
    assert WeatherCondition.SNOW.value == "Snow"
    assert WeatherCondition.STORM.value == "Storm"


def test_generate_landscape_prompt_day_clear():
    """Test landscape prompt generation for day/clear conditions."""
    prompt = generate_landscape_prompt(
        location_name="Iron Plains",
        description="A vast expanse of rust-colored terrain",
        time_of_day="Day",
        weather="Clear"
    )
    
    assert "Iron Plains" in prompt
    assert "rust-colored terrain" in prompt
    assert "bright daylight" in prompt
    assert "crisp atmosphere" in prompt
    # "Plains" doesn't trigger planetary detection, so it uses generic sci-fi environment
    assert "sci-fi environment" in prompt


def test_generate_landscape_prompt_night_rain():
    """Test landscape prompt generation for night/rain conditions."""
    prompt = generate_landscape_prompt(
        location_name="Orbital Station Gamma",
        description="A massive space station",
        time_of_day="Night",
        weather="Rain"
    )
    
    assert "Orbital Station Gamma" in prompt
    assert "dark starlit sky" in prompt
    assert "falling rain" in prompt
    assert "space station" in prompt  # Should detect "Station" as space station


def test_generate_landscape_prompt_derelict():
    """Test landscape prompt generation for derelict locations."""
    prompt = generate_landscape_prompt(
        location_name="Derelict Freighter",
        description="An abandoned cargo vessel",
        time_of_day="Twilight",
        weather="Fog"
    )
    
    assert "Derelict Freighter" in prompt
    assert "golden hour lighting" in prompt
    assert "thick fog banks" in prompt
    assert "derelict spacecraft" in prompt  # Should detect "Derelict"


def test_location_visuals_caching():
    """Test that location visuals can be cached."""
    world = WorldState()
    
    world.location_visuals["Iron Plains"] = {
        "time": "Day",
        "weather": "Clear",
        "image_url": "/assets/generated/loc_12345.png"
    }
    
    assert "Iron Plains" in world.location_visuals
    assert world.location_visuals["Iron Plains"]["time"] == "Day"
    assert world.location_visuals["Iron Plains"]["weather"] == "Clear"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
