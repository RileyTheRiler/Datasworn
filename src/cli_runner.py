"""
Command-line game flow for Starforged.

Ties user input to Datasworn moves and the core rules engine so
rolling, progress, and status commands work outside the UI.
"""
from __future__ import annotations

import re
from pathlib import Path
from src.datasworn import DataswornData, Move
from src.game_state import Character, CharacterCondition, CharacterStats, MomentumState, VowState, create_initial_state
from src.intent_predictor import INTENT_KEYWORDS, IntentCategory
from src.persistence import PersistenceLayer
from src.rules_engine import ProgressTrack, RollResult, action_roll

DEFAULT_DATA_PATH = Path("data/starforged/dataforged.json")

DEFAULT_MOVE_BY_INTENT: dict[str, str] = {
    IntentCategory.COMBAT: "Strike",
    IntentCategory.EXPLORATION: "Face Danger",
    IntentCategory.SOCIAL: "Compel",
    IntentCategory.INVESTIGATION: "Gather Information",
    IntentCategory.MOVEMENT: "Undertake an Expedition",
    IntentCategory.STEALTH: "Face Danger",
    IntentCategory.REST: "Sojourn",
    IntentCategory.QUEST: "Fulfill Your Vow",
    IntentCategory.CRAFTING: "Secure an Advantage",
    IntentCategory.INVENTORY: "Secure an Advantage",
}

STAT_BY_INTENT: dict[str, str] = {
    IntentCategory.COMBAT: "iron",
    IntentCategory.EXPLORATION: "wits",
    IntentCategory.SOCIAL: "heart",
    IntentCategory.INVESTIGATION: "wits",
    IntentCategory.MOVEMENT: "edge",
    IntentCategory.STEALTH: "shadow",
    IntentCategory.REST: "heart",
    IntentCategory.QUEST: "heart",
    IntentCategory.CRAFTING: "wits",
    IntentCategory.INVENTORY: "wits",
}


class CLIRunner:
    """Lightweight CLI harness around the rules engine and Datasworn data."""

    def __init__(
        self,
        character_name: str,
        data_path: Path | None = None,
        save_path: Path | None = None,
        persistence: PersistenceLayer | None = None,
    ):
        path = data_path or DEFAULT_DATA_PATH
        self.data = DataswornData(path) if path.exists() else None
        self.state = create_initial_state(character_name)
        self.persistence = persistence or PersistenceLayer(save_path or Path("saves/game_state.db"))

    # ------------------------------------------------------------------
    # High-level flow
    # ------------------------------------------------------------------
    def handle_input(self, user_text: str) -> str:
        user_text = user_text.strip()
        if not user_text:
            return ""

        if user_text.startswith("!"):
            return self._handle_command(user_text[1:])

        intent = self._detect_intent(user_text)
        move = self._match_move(user_text, intent)
        if not move:
            return "I couldn't match that action to a move. Try naming a move or use !help for commands."

        return self._resolve_move(move, user_text, intent)

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------
    def _handle_command(self, command_text: str) -> str:
        cmd = command_text.lower().strip()
        if cmd in {"status", "debug"}:
            return self._render_status()
        if cmd == "vows":
            return self._render_vows()
        if cmd.startswith("save"):
            return self._command_save()
        if cmd.startswith("load"):
            name = command_text.split(maxsplit=1)[1] if len(command_text.split()) > 1 else None
            return self._command_load(name)
        if cmd in {"help", "?"}:
            return (
                "Available commands:\n"
                "!status - Show stats, momentum, and conditions\n"
                "!vows   - List active vows and progress\n"
                "!save   - Persist the current character\n"
                "!load   - Load a saved character by name\n"
                "!help   - Show this list"
            )
        return "Unknown command. Try !help for the list."

    def _render_status(self) -> str:
        char: Character = self.state["character"]
        condition: CharacterCondition = char.condition
        stats: CharacterStats = char.stats
        return (
            f"Character: {char.name}\n"
            f"Stats - Edge {stats.edge} | Heart {stats.heart} | Iron {stats.iron} | Shadow {stats.shadow} | Wits {stats.wits}\n"
            f"Momentum: {char.momentum.value}\n"
            f"Condition - Health {condition.health}/5, Spirit {condition.spirit}/5, Supply {condition.supply}/5"
        )

    def _render_vows(self) -> str:
        char: Character = self.state["character"]
        if not char.vows:
            return "No active vows."

        lines = ["Active vows:"]
        for vow in char.vows:
            track = ProgressTrack(name=vow.name, rank=vow.rank, ticks=vow.ticks, completed=vow.completed)
            lines.append(f"- {vow.name} ({vow.rank}) {track.display}")
        return "\n".join(lines)

    def _command_save(self) -> str:
        char: Character = self.state["character"]
        self.persistence.save_character(char)
        return f"Saved character '{char.name}'."

    def _command_load(self, name: str | None) -> str:
        target = name or self.state["character"].name
        loaded = self.persistence.load_character(target)
        if not loaded:
            return f"No saved character found for '{target}'."

        self.state["character"] = loaded
        return f"Loaded character '{loaded.name}'."

    # ------------------------------------------------------------------
    # Move resolution
    # ------------------------------------------------------------------
    def _resolve_move(self, move: Move, user_text: str, intent: str) -> str:
        char: Character = self.state["character"]

        if move.roll_type.lower().startswith("progress"):
            return self._progress_move(move, char)

        stat_name = self._choose_stat(user_text, intent)
        stat_value = getattr(char.stats, stat_name, 1)
        roll = action_roll(stat_value)

        self._apply_momentum(roll.result)

        outcome_text = self._outcome_text(move, roll.result)
        progress_note = self._maybe_mark_progress(intent)

        parts = [
            f"{move.name} ({move.roll_type})",
            f"Using {stat_name.title()} {stat_value}",
            str(roll),
            outcome_text,
        ]
        if progress_note:
            parts.append(progress_note)

        return "\n".join(parts)

    def _progress_move(self, move: Move, char: Character) -> str:
        vow = self._get_active_vow(char)
        if not vow:
            return "No vow available for a progress roll. Use !vows to add one."  # type: ignore[return-value]

        track = ProgressTrack(name=vow.name, rank=vow.rank, ticks=vow.ticks, completed=vow.completed)
        roll = track.progress_roll()

        vow.completed = roll.result != RollResult.MISS
        vow.ticks = track.ticks

        parts = [
            f"{move.name} (Progress Roll)",
            str(roll),
            self._outcome_text(move, roll.result),
        ]
        if vow.completed:
            parts.append(f"{vow.name} is now fulfilled!")

        return "\n".join(parts)

    def _outcome_text(self, move: Move, result: RollResult) -> str:
        if result == RollResult.STRONG_HIT:
            return move.strong_hit or "Strong hit."
        if result == RollResult.WEAK_HIT:
            return move.weak_hit or "Weak hit."
        return move.miss or "Miss."

    def _apply_momentum(self, result: RollResult) -> None:
        char: Character = self.state["character"]
        momentum: MomentumState = char.momentum
        delta = {RollResult.STRONG_HIT: 2, RollResult.WEAK_HIT: 1, RollResult.MISS: -2}[result]
        min_value = getattr(momentum, "min_value", -6)
        momentum.value = max(min_value, min(momentum.value + delta, momentum.max_value))

    def _maybe_mark_progress(self, intent: str) -> str:
        if intent != IntentCategory.QUEST:
            return ""

        vow = self._get_active_vow(self.state["character"])
        if not vow:
            return ""

        track = ProgressTrack(name=vow.name, rank=vow.rank, ticks=vow.ticks, completed=vow.completed)
        before = track.ticks
        track.mark_progress()
        vow.ticks = track.ticks

        return f"Progress marked on {vow.name}: {before} -> {vow.ticks} ticks ({track.display})"

    # ------------------------------------------------------------------
    # Matching helpers
    # ------------------------------------------------------------------
    def _detect_intent(self, user_text: str) -> str:
        words = set(re.findall(r"\w+", user_text.lower()))
        best_intent = IntentCategory.EXPLORATION
        best_score = 0
        for intent, keywords in INTENT_KEYWORDS.items():
            score = len(words.intersection(keywords))
            if score > best_score:
                best_score = score
                best_intent = intent
        return best_intent

    def _match_move(self, user_text: str, intent: str) -> Move | None:
        if not self.data:
            return None

        text = user_text.lower()

        if "fulfill" in text and "vow" in text:
            move = self.data.get_move("Fulfill Your Vow")
            if move:
                return move
        if "swear" in text and "vow" in text:
            move = self.data.get_move("Swear an Iron Vow")
            if move:
                return move

        for move_obj in self.data.get_all_moves():
            if move_obj.name.lower() in text:
                return move_obj

        fallback_name = DEFAULT_MOVE_BY_INTENT.get(intent)
        return self.data.get_move(fallback_name) if fallback_name else None

    def _choose_stat(self, user_text: str, intent: str) -> str:
        text = user_text.lower()
        if "sneak" in text or "hide" in text or "shadow" in text:
            return "shadow"
        if "persuade" in text or "charm" in text or "talk" in text:
            return "heart"
        return STAT_BY_INTENT.get(intent, "wits")

    def _get_active_vow(self, char: Character) -> VowState | None:
        for vow in char.vows:
            if not vow.completed:
                return vow
        return None


def bootstrap_cli(character_name: str) -> "CLIRunner":
    """Create a CLI runner with minimal defaults."""
    return CLIRunner(character_name)
