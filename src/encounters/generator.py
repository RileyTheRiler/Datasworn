from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Mapping, Tuple

BASE_LOOT_PROBABILITIES: Mapping[str, float] = {
    "common": 0.55,
    "uncommon": 0.3,
    "rare": 0.12,
    "legendary": 0.03,
}


@dataclass
class EncounterTable:
    name: str
    encounters: List[Tuple[str, float, str]]  # (id, weight, rarity)
    loot_modifiers: Mapping[str, float]

    @classmethod
    def from_file(cls, path: Path) -> "EncounterTable":
        with open(path, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        encounters = [
            (entry["id"], float(entry.get("weight", 1.0)), entry.get("rarity", "common"))
            for entry in payload.get("encounters", [])
        ]
        loot_modifiers = payload.get("loot_modifiers", {})
        return cls(name=payload.get("name", path.stem), encounters=encounters, loot_modifiers=loot_modifiers)

    def pick_encounter(self, rng: random.Random) -> Tuple[str, str]:
        ids = [enc[0] for enc in self.encounters]
        weights = [enc[1] for enc in self.encounters]
        rarities = [enc[2] for enc in self.encounters]

        total = sum(weights)
        normalized = [w / total for w in weights]
        index = rng.choices(range(len(ids)), weights=normalized, k=1)[0]
        return ids[index], rarities[index]

    def get_loot_probabilities(self) -> Dict[str, float]:
        weighted = {}
        for rarity, base in BASE_LOOT_PROBABILITIES.items():
            modifier = self.loot_modifiers.get(rarity, 1.0)
            weighted[rarity] = base * modifier

        total = sum(weighted.values())
        return {rarity: value / total for rarity, value in weighted.items()}


@dataclass
class EncounterGenerator:
    data_path: Path
    rng: random.Random = field(default_factory=random.Random)

    def __post_init__(self) -> None:
        self.tables: Dict[str, EncounterTable] = {}
        self._load_tables()

    def _load_tables(self) -> None:
        for filename in os.listdir(self.data_path):
            if not filename.endswith(".json"):
                continue
            path = self.data_path / filename
            table = EncounterTable.from_file(path)
            self.tables[table.name] = table

    def get_table(self, biome: str) -> EncounterTable:
        if biome not in self.tables:
            raise KeyError(f"No encounter table for biome '{biome}'")
        return self.tables[biome]

    def generate(self, biome: str) -> Dict[str, str]:
        table = self.get_table(biome)
        encounter_id, encounter_rarity = table.pick_encounter(self.rng)
        loot_probabilities = table.get_loot_probabilities()
        loot_roll = self.rng.random()
        cumulative = 0.0
        loot_rarity = "common"
        for rarity, probability in loot_probabilities.items():
            cumulative += probability
            if loot_roll <= cumulative:
                loot_rarity = rarity
                break

        return {
            "biome": biome,
            "encounter": encounter_id,
            "encounter_rarity": encounter_rarity,
            "loot_rarity": loot_rarity,
        }

    def generate_batch(self, biome: str, count: int) -> List[Dict[str, str]]:
        return [self.generate(biome) for _ in range(count)]
