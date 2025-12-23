import pytest

from src.starmap import PlanetType, StarmapGenerator, StarClass


@pytest.mark.parametrize("num_systems", [1, 3])
def test_small_sector_generation_has_valid_structures(num_systems):
    generator = StarmapGenerator(seed=1234)
    sector = generator.generate_sector("Tiny Sector", num_systems=num_systems)

    assert len(sector.systems) == num_systems
    assert set(sector.connections.keys()) == set(sector.systems.keys())

    for system_id, system in sector.systems.items():
        assert isinstance(system.star_class, StarClass)
        assert isinstance(system.position, tuple) and len(system.position) == 2
        assert isinstance(sector.connections.get(system_id), list)
        assert sector.connections[system_id], "Each system should have at least one connection"

        for neighbor in sector.connections[system_id]:
            assert system_id in sector.connections.get(neighbor, [])

        for planet in system.planets:
            assert isinstance(planet.planet_type, PlanetType)
            assert planet.description
            assert planet.atmosphere in {"none", "breathable", "toxic", "crushing"}
