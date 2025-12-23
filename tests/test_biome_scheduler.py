import random
from collections import Counter
from pathlib import Path

from src.encounters.generator import EncounterGenerator
from src.worldgen.biome_scheduler import BiomeCurve, BiomeScheduler


def dominant_biome(samples):
    counts = Counter(samples)
    return counts.most_common(1)[0][0]


def test_progression_and_scarcity_curves():
    rng = random.Random(7)
    scheduler = BiomeScheduler(
        curves=[
            BiomeCurve("verdant_forest", start=0, peak=100, end=320, scarcity=0.05),
            BiomeCurve("scorched_dunes", start=220, peak=520, end=950, scarcity=0.2),
            BiomeCurve("glacial_expanse", start=650, peak=900, end=1200, scarcity=0.3),
        ],
        rng=rng,
    )

    early = scheduler.walk(range(0, 150, 10))
    middle = scheduler.walk(range(350, 650, 10))
    late = scheduler.walk(range(850, 1050, 10))

    assert dominant_biome(early) == "verdant_forest"
    assert dominant_biome(middle) == "scorched_dunes"
    assert dominant_biome(late) == "glacial_expanse"

    adjusted = scheduler.scarcity_adjusted({"glacial_expanse": 0.9})
    late_adjusted = adjusted.walk(range(850, 1050, 10))
    assert late_adjusted.count("glacial_expanse") < late.count("glacial_expanse")


def test_encounter_tables_and_loot_envelopes():
    rng = random.Random(11)
    scheduler = BiomeScheduler(
        curves=[
            BiomeCurve("verdant_forest", start=0, peak=100, end=320, scarcity=0.05),
            BiomeCurve("scorched_dunes", start=220, peak=520, end=950, scarcity=0.2),
            BiomeCurve("glacial_expanse", start=650, peak=900, end=1200, scarcity=0.3),
        ],
        rng=rng,
    )
    generator = EncounterGenerator(Path("data/biomes"), rng=rng)

    loot_counts = Counter()
    seen_biomes = set()
    for position in range(0, 1000, 20):
        biome = scheduler.pick_biome(position)
        seen_biomes.add(biome)
        outcome = generator.generate(biome)
        loot_counts[outcome["loot_rarity"]] += 1

    assert {"verdant_forest", "scorched_dunes", "glacial_expanse"}.issubset(seen_biomes)
    total = sum(loot_counts.values())
    exotic_ratio = (loot_counts["rare"] + loot_counts["legendary"]) / total
    assert 0.15 <= exotic_ratio <= 0.35
