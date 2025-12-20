"""
Tests for Star Map and Rumor Systems.
"""

import pytest
from src.starmap import (
    StarmapGenerator, Sector, StarSystem, Planet,
    PlanetType, StarClass, RoutePlanner, generate_default_sector
)
from src.rumor_system import (
    RumorNetwork, Rumor, RumorType, RumorSource,
    RumorGenerator
)


# ============================================================================
# Star Map Tests
# ============================================================================

def test_starmap_generation():
    """Test procedural sector generation."""
    generator = StarmapGenerator(seed=42)
    sector = generator.generate_sector("Test Sector", num_systems=10)
    
    assert sector.name == "Test Sector"
    assert len(sector.systems) == 10
    assert len(sector.connections) == 10
    
    # Check that systems have valid data
    for system in sector.systems.values():
        assert system.name
        assert system.star_class in StarClass
        assert len(system.position) == 2
        assert 0 <= system.position[0] <= 100
        assert 0 <= system.position[1] <= 100
        assert len(system.planets) >= 1


def test_planet_generation():
    """Test planet generation."""
    generator = StarmapGenerator(seed=42)
    planet = generator._generate_planet("TestStar", 0)
    
    assert planet.name
    assert planet.planet_type in PlanetType
    assert planet.description
    assert planet.atmosphere in ["none", "breathable", "toxic", "crushing"]


def test_route_planning():
    """Test route finding between systems."""
    sector = generate_default_sector()
    planner = RoutePlanner(sector)
    
    # Get two systems
    system_ids = list(sector.systems.keys())
    if len(system_ids) >= 2:
        start = system_ids[0]
        end = system_ids[1]
        
        route = planner.find_route(start, end)
        
        # Route should exist or be None
        if route:
            assert route[0] == start
            assert route[-1] == end
            assert len(route) >= 2


def test_reachable_systems():
    """Test finding reachable systems within jump range."""
    sector = generate_default_sector()
    planner = RoutePlanner(sector)
    
    system_ids = list(sector.systems.keys())
    if system_ids:
        start = system_ids[0]
        reachable = planner.get_reachable_systems(start, max_jumps=2)
        
        # Should find at least some systems
        assert isinstance(reachable, list)


def test_sector_serialization():
    """Test sector to_dict and from_dict."""
    sector = generate_default_sector()
    
    # Serialize
    data = sector.to_dict()
    
    # Deserialize
    restored = Sector.from_dict(data)
    
    assert restored.name == sector.name
    assert len(restored.systems) == len(sector.systems)
    assert len(restored.connections) == len(sector.connections)


# ============================================================================
# Rumor System Tests
# ============================================================================

def test_rumor_creation():
    """Test creating rumors."""
    network = RumorNetwork()
    
    rumor = network.create_rumor(
        content="Pirates spotted near Beacon",
        rumor_type=RumorType.THREAT,
        location="Forge Station",
        source_reliability=RumorSource.CREDIBLE,
        accuracy=0.8
    )
    
    assert rumor.id
    assert rumor.content == "Pirates spotted near Beacon"
    assert rumor.rumor_type == RumorType.THREAT
    assert rumor.location_origin == "Forge Station"
    assert "Forge Station" in rumor.current_locations


def test_rumor_spread():
    """Test rumor propagation between locations."""
    network = RumorNetwork()
    
    # Create rumor at location A
    rumor = network.create_rumor(
        content="Test rumor",
        rumor_type=RumorType.OPPORTUNITY,
        location="Location A"
    )
    
    # Spread to location B
    spread = network.spread_rumors("Location A", "Location B", spread_chance=1.0)
    
    assert len(spread) >= 1
    assert "Location B" in rumor.current_locations


def test_rumor_aging():
    """Test rumor decay over time."""
    network = RumorNetwork()
    
    rumor = network.create_rumor(
        content="Old news",
        rumor_type=RumorType.NPC_GOSSIP,
        location="Station",
        decay_rate=1.0  # Always becomes outdated
    )
    
    assert not rumor.is_outdated
    
    # Age the rumor
    rumor.age()
    
    assert rumor.age_scenes == 1
    assert rumor.is_outdated


def test_rumor_accuracy():
    """Test rumor accuracy based on source reliability."""
    network = RumorNetwork()
    
    # Verified source should be very accurate
    verified = network.create_rumor(
        content="Verified info",
        rumor_type=RumorType.LOCATION_INFO,
        location="Hub",
        source_reliability=RumorSource.VERIFIED,
        accuracy=1.0
    )
    
    assert verified.get_reliability_modifier() == 0.9
    
    # Unreliable source should be less accurate
    unreliable = network.create_rumor(
        content="Dubious claim",
        rumor_type=RumorType.NPC_GOSSIP,
        location="Hub",
        source_reliability=RumorSource.UNRELIABLE,
        accuracy=0.5
    )
    
    assert unreliable.get_reliability_modifier() == 0.3


def test_disinformation():
    """Test planting false information."""
    network = RumorNetwork()
    
    disinfo = network.plant_disinformation(
        content="The enemy has retreated",
        location="Frontline"
    )
    
    assert disinfo.accuracy == 0.0
    assert disinfo.source_reliability == RumorSource.CREDIBLE  # Seems credible but is false


def test_rumor_filtering():
    """Test filtering rumors by type and location."""
    network = RumorNetwork()
    
    # Create various rumors
    network.create_rumor("Threat 1", RumorType.THREAT, "Station A")
    network.create_rumor("Threat 2", RumorType.THREAT, "Station B")
    network.create_rumor("Opportunity", RumorType.OPPORTUNITY, "Station A")
    
    # Filter by type
    threats = network.get_rumors_by_type(RumorType.THREAT)
    assert len(threats) == 2
    
    # Filter by location
    station_a_rumors = network.get_rumors_at_location("Station A")
    assert len(station_a_rumors) == 2


def test_rumor_generator():
    """Test procedural rumor generation."""
    generator = RumorGenerator()
    
    threat = generator.generate_threat_rumor("Beacon System", "Iron Syndicate")
    assert "Beacon System" in threat or "Iron Syndicate" in threat
    
    opportunity = generator.generate_opportunity_rumor("Nexus", "Nexus Prime")
    assert "Nexus" in opportunity
    
    faction_rumor = generator.generate_faction_rumor("Free Traders", "Stellar Navy")
    assert "Free Traders" in faction_rumor


def test_rumor_serialization():
    """Test rumor network serialization."""
    network = RumorNetwork()
    
    network.create_rumor("Test 1", RumorType.THREAT, "Loc A")
    network.create_rumor("Test 2", RumorType.OPPORTUNITY, "Loc B")
    
    # Serialize
    data = network.to_dict()
    
    # Deserialize
    restored = RumorNetwork.from_dict(data)
    
    assert len(restored.rumors) == 2
    assert restored._rumor_counter == network._rumor_counter


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
