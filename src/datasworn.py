"""
Datasworn JSON Parser for Ironsworn: Starforged.
Loads moves, oracles, and assets from the dataforged.json file.
"""

from __future__ import annotations
import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from pydantic import BaseModel

from src.game_director import GamePhase, PhaseController


class MoveOutcome(BaseModel):
    """Represents one outcome (Strong Hit, Weak Hit, Miss) of a move."""
    text: str


class Move(BaseModel):
    """Represents a Starforged Move."""
    id: str
    name: str
    category: str
    trigger_text: str
    strong_hit: str
    weak_hit: str
    miss: str
    roll_type: str  # "Action Roll" or "Progress Roll" or "No Roll"


class OracleEntry(BaseModel):
    """A single entry in an oracle table."""
    floor: int
    ceiling: int
    result: str


class OracleTable(BaseModel):
    """Represents an Oracle table."""
    id: str
    name: str
    entries: list[OracleEntry]


class Asset(BaseModel):
    """Represents a character asset (e.g., Path, Companion)."""
    id: str
    name: str
    asset_type: str
    abilities: list[str]


class DataswornData:
    """Container for all loaded Starforged game data."""

    def __init__(self, json_path: str | Path):
        self.json_path = Path(json_path)
        self._data: dict[str, Any] = {}
        self._moves: dict[str, Move] = {}
        self._oracles: dict[str, OracleTable] = {}
        self._assets: dict[str, Asset] = {}
        self._load()

    def _load(self) -> None:
        """Load and parse the JSON file."""
        with open(self.json_path, "r", encoding="utf-8") as f:
            self._data = json.load(f)
        self._parse_moves()
        self._parse_oracles()
        self._parse_assets()

    def _parse_moves(self) -> None:
        """Parse all moves from the data."""
        move_categories = self._data.get("Move Categories", [])
        for category in move_categories:
            cat_name = category.get("Name", "Unknown")
            for move_data in category.get("Moves", []):
                move_id = move_data.get("$id", move_data.get("Name", "unknown"))
                name = move_data.get("Name", "Unknown Move")

                trigger = move_data.get("Trigger", {})
                trigger_text = trigger.get("Text", "")

                # Determine roll type
                options = trigger.get("Options", [])
                roll_type = "No Roll"
                if options:
                    roll_type = options[0].get("Method", "No Roll")

                outcomes = move_data.get("Outcomes", {})
                strong_hit = outcomes.get("Strong Hit", {}).get("Text", "")
                weak_hit = outcomes.get("Weak Hit", {}).get("Text", "")
                miss = outcomes.get("Miss", {}).get("Text", "")

                self._moves[name.lower()] = Move(
                    id=move_id,
                    name=name,
                    category=cat_name,
                    trigger_text=trigger_text,
                    strong_hit=strong_hit,
                    weak_hit=weak_hit,
                    miss=miss,
                    roll_type=roll_type,
                )

    def _parse_oracles(self) -> None:
        """Parse all oracle tables from the data."""
        oracle_categories = self._data.get("Oracle Categories", [])
        self._parse_oracle_category(oracle_categories)

    def _parse_oracle_category(self, categories: list[dict], prefix: str = "") -> None:
        """Recursively parse oracle categories."""
        for cat in categories:
            cat_name = cat.get("Name", "")
            full_name = f"{prefix}/{cat_name}" if prefix else cat_name

            # Parse tables in this category
            for table_data in cat.get("Oracles", []):
                self._parse_oracle_table(table_data, full_name)

            # Recurse into subcategories
            subcats = cat.get("Categories", [])
            if subcats:
                self._parse_oracle_category(subcats, full_name)

    def _parse_oracle_table(self, table_data: dict, category: str) -> None:
        """Parse a single oracle table."""
        table_name = table_data.get("Name", "Unknown")
        table_id = table_data.get("$id", table_name)
        entries: list[OracleEntry] = []

        for entry in table_data.get("Table", []):
            floor = entry.get("Floor", 0)
            ceiling = entry.get("Ceiling", 0)
            result = entry.get("Result", "")
            if floor and ceiling and result:
                entries.append(OracleEntry(floor=floor, ceiling=ceiling, result=result))

        if entries:
            key = f"{category}/{table_name}".lower()
            self._oracles[key] = OracleTable(id=table_id, name=table_name, entries=entries)

    def _parse_assets(self) -> None:
        """Parse all assets from the data."""
        asset_types = self._data.get("Asset Types", [])
        for asset_type in asset_types:
            type_name = asset_type.get("Name", "Unknown")
            for asset_data in asset_type.get("Assets", []):
                asset_id = asset_data.get("$id", asset_data.get("Name", "unknown"))
                name = asset_data.get("Name", "Unknown Asset")
                abilities = []
                for ability in asset_data.get("Abilities", []):
                    text = ability.get("Text", "")
                    if text:
                        abilities.append(text)

                self._assets[name.lower()] = Asset(
                    id=asset_id,
                    name=name,
                    asset_type=type_name,
                    abilities=abilities,
                )

    def get_move(self, name: str) -> Move | None:
        """Get a move by name (case-insensitive)."""
        return self._moves.get(name.lower())

    def get_all_moves(self) -> list[Move]:
        """Get all moves."""
        return list(self._moves.values())

    def get_oracle(self, path: str) -> OracleTable | None:
        """Get an oracle table by path (case-insensitive)."""
        return self._oracles.get(path.lower())

    def search_oracles(self, keyword: str) -> list[OracleTable]:
        """Search oracles by keyword."""
        keyword = keyword.lower()
        return [o for k, o in self._oracles.items() if keyword in k]

    def roll_oracle(self, path: str) -> str | None:
        """Roll on an oracle table and return the result."""
        oracle = self.get_oracle(path)
        if not oracle:
            return None
        roll = random.randint(1, 100)
        for entry in oracle.entries:
            if entry.floor <= roll <= entry.ceiling:
                return entry.result
        return None

    def get_asset(self, name: str) -> Asset | None:
        """Get an asset by name (case-insensitive)."""
        return self._assets.get(name.lower())

    def get_all_assets(self) -> list[Asset]:
        """Get all assets."""
        return list(self._assets.values())

    def get_oracle_keys(self) -> list[str]:
        """Return the keys for all oracle tables."""
        return list(self._oracles.keys())

    def get_oracle_key(self, oracle: OracleTable) -> str | None:
        """Find the key used to store a specific oracle table."""
        for key, table in self._oracles.items():
            if table is oracle:
                return key
        return None

    def get_assets_by_type(self, asset_type: str) -> list[Asset]:
        """Get assets by type (e.g., 'Path', 'Companion')."""
        asset_type_lower = asset_type.lower()
        return [a for a in self._assets.values() if a.asset_type.lower() == asset_type_lower]


@dataclass
class PhaseOrchestratedState:
    """Lightweight state container to demonstrate a phased turn loop."""

    turn_counter: int = 0
    combat_log: list[str] = field(default_factory=list)
    narrative_log: list[str] = field(default_factory=list)
    economy_balance: int = 0
    render_queue: list[dict[str, Any]] = field(default_factory=list)


class DataswornTurnEngine:
    """Coordinates simple combat/narrative/economy updates through the phase controller."""

    def __init__(self, phase_controller: PhaseController | None = None):
        self.phase_controller = phase_controller or PhaseController()
        self.state = PhaseOrchestratedState()

    def tick(self, player_action: str, ai_summary: str) -> PhaseOrchestratedState:
        """Run a single turn using the configured phase ordering."""

        def _player_input() -> str:
            self.state.combat_log.append(f"player:{player_action}")
            return player_action

        def _ai_responses() -> str:
            self.state.combat_log.append(f"ai:{ai_summary}")
            return ai_summary

        def _world_update() -> int:
            self.state.turn_counter += 1
            self.state.economy_balance += 5
            return self.state.turn_counter

        def _narrative_update() -> str:
            beat = f"Turn {self.state.turn_counter}: {player_action} / {ai_summary}"
            self.state.narrative_log.append(beat)
            return beat

        def _render_hook() -> dict[str, Any]:
            frame = {
                "turn": self.state.turn_counter,
                "last_beat": self.state.narrative_log[-1] if self.state.narrative_log else None,
                "economy": self.state.economy_balance,
            }
            self.state.render_queue.append(frame)
            return frame

        self.phase_controller.execute_phase(GamePhase.PLAYER_INPUT, _player_input)
        self.phase_controller.execute_phase(GamePhase.AI_RESPONSE, _ai_responses)
        self.phase_controller.execute_phase(GamePhase.WORLD_UPDATE, _world_update)
        self.phase_controller.execute_phase(GamePhase.NARRATIVE_UPDATE, _narrative_update)
        self.phase_controller.execute_phase(GamePhase.RENDER_HOOK, _render_hook)

        return self.state


def load_starforged_data(json_path: str | Path = "data/starforged/dataforged.json") -> DataswornData:
    """Load Starforged game data from JSON."""
    return DataswornData(json_path)
