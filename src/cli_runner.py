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
from src.photo_album import PhotoAlbumManager
from src.session_recap import SessionRecapEngine
from src.config import config
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
        self.recap_engine = SessionRecapEngine()
        self.album_manager = PhotoAlbumManager(self.state["album"])
        self.recap_engine.start_session()

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
        """Dispatch CLI bang-commands."""

        cmd = command_text.strip()
        if not cmd:
            return "Unknown command. Try !help for the list."

        name, *rest = cmd.split(maxsplit=1)
        name = name.lower()
        arg = rest[0].strip() if rest else ""

        if name in {"status", "debug"}:
            return self._render_status()
        if name == "assets":
            return self._render_assets()
        if name == "vows":
            return self._render_vows()
        if name in {"review", "reviewvows"}:
            return self._render_vows(include_header=True)
        if name in {"memory", "memories"}:
            return self._render_memory()
        if name == "oracle":
            return self._roll_oracle(arg)
        if name in {"rest", "sojourn"}:
            return self._command_rest()
        if name in {"recap", "what", "digest"}:
            return self._render_recap_digest()
        if name == "save":
            return self._command_save()
        if name == "load":
            load_name = rest[0].strip() if rest else None
            return self._command_load(load_name)
        if name in {"help", "?"}:
            if arg == "moves":
                return self._render_move_help()
            return (
                "Available commands:\n"
                "!status       - Show stats, momentum, and conditions\n"
                "!assets       - List equipped assets and abilities\n"
                "!vows         - List active vows and progress\n"
                "!review vows  - Highlight sworn oaths and progress\n"
                "!memory       - Summarize recent scenes, choices, and NPCs\n"
                "!rest         - Take a breather and regain condition\n"
                "!recap        - Show 'What happened?' digest with highlights\n"
                "!oracle NAME  - Roll an oracle by path or keyword\n"
                "!save         - Persist the current character\n"
                "!load [NAME]  - Load a saved character by name\n"
                "!help moves   - List move prompts and examples\n"
                "!help         - Show this list"
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

    def _render_assets(self) -> str:
        char: Character = self.state["character"]
        if not char.assets:
            return "No assets equipped."

        lines = ["Equipped assets:"]
        for asset_state in char.assets:
            asset_details = self.data.get_asset(asset_state.name) if self.data else None
            type_label = f" ({asset_details.asset_type})" if asset_details else ""
            lines.append(f"- {asset_state.name}{type_label}")

            if asset_details and asset_details.abilities:
                for idx, ability_text in enumerate(asset_details.abilities):
                    enabled = asset_state.abilities_enabled[idx] if idx < len(asset_state.abilities_enabled) else False
                    checkbox = "[x]" if enabled else "[ ]"
                    lines.append(f"  {checkbox} {ability_text}")
            elif asset_details:
                lines.append("  No abilities listed.")
            else:
                lines.append("  (Asset details unavailable without Datasworn data.)")

        return "\n".join(lines)

    def _render_vows(self) -> str:
        char: Character = self.state["character"]
        if not char.vows:
            return "No active vows."

        lines = ["Active vows:"]
        for vow in char.vows:
            track = ProgressTrack(name=vow.name, rank=vow.rank, ticks=vow.ticks, completed=vow.completed)
            lines.append(f"- {vow.name} ({vow.rank}) {track.display}")
        return "\n".join(lines)

    def _render_memory(self) -> str:
        memory = self.state.get("memory")
        if not memory:
            return "No memories recorded yet."

        lines = ["Recent memory log:"]
        if memory.scene_summaries:
            lines.append("Scenes:")
            for summary in memory.scene_summaries[-3:]:
                lines.append(f"  - {summary}")
        if memory.decisions_made:
            lines.append("Decisions:")
            for decision in memory.decisions_made[-3:]:
                lines.append(f"  - {decision}")
        if memory.npcs_encountered:
            lines.append("NPCs encountered:")
            for name, note in list(memory.npcs_encountered.items())[-3:]:
                lines.append(f"  - {name}: {note}")

        return "\n".join(lines)

    def _command_rest(self) -> str:
        char: Character = self.state["character"]
        condition: CharacterCondition = char.condition
        before = (condition.health, condition.spirit, condition.supply)

        condition.health = min(5, condition.health + 1)
        condition.spirit = min(5, condition.spirit + 1)
        condition.supply = min(5, condition.supply + 1)

        self.album_manager.capture_moment(
            image_url="cli://rest",
            caption=f"{char.name} caught their breath at {self.state['world'].current_location}",
            tags=["Rest", "Recovery"],
            scene_id=self.state["world"].current_location or "camp",
        )
        self.recap_engine.record_event(
            description="Took time to rest and regroup",
            importance=4,
            characters=[char.name],
            location=self.state["world"].current_location,
            emotional_tone="relief",
        )

        after = (condition.health, condition.spirit, condition.supply)
        return (
            "Rested and regrouped."
            f"\nHealth: {before[0]} → {after[0]}"
            f"\nSpirit: {before[1]} → {after[1]}"
            f"\nSupply: {before[2]} → {after[2]}"
            "\nUse the recap panel for highlights and vows."
        )

    def _render_recap_digest(self) -> str:
        char: Character = self.state["character"]
        digest = self.recap_engine.build_digest(
            protagonist_name=char.name,
            album_state=self.state.get("album"),
            memory_state=self.state.get("memory"),
            vow_state=char.vows,
            current_location=self.state.get("world").current_location,
        )

        lines = [digest.get("title", "What happened?"), ""]
        lines.append(digest.get("recap", ""))

        if digest.get("highlights"):
            lines.append("\nHighlights:")
            for photo in digest["highlights"]:
                lines.append(f"- {photo.get('caption')} ({', '.join(photo.get('tags', []))})")

        memory = digest.get("memory") or {}
        if memory:
            lines.append("\nMemory anchors:")
            for summary in memory.get("recent_summaries", []):
                lines.append(f"- {summary}")
            for decision in memory.get("recent_decisions", []):
                lines.append(f"- Decision: {decision}")

        if digest.get("vows"):
            lines.append("\nVows:")
            for vow in digest["vows"]:
                lines.append(f"- {vow['name']} ({vow['rank']}) {vow['progress']}")

        tooltip = config.ui.mechanic_tooltips.get("recap", {})
        if tooltip:
            lines.append(f"\nTip: {tooltip.get('summary', '')}")

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

        self.recap_engine.record_event(
            description=f"{move.name}: {roll.result.value}",
            importance=6,
            characters=[char.name],
            location=self.state.get("world").current_location,
            emotional_tone=roll.result.value,
        )

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

    def _render_move_help(self) -> str:
        if not self.data:
            return "Move reference is unavailable until Datasworn data is loaded."

        moves = sorted({move.name for move in self.data.get_all_moves()})
        examples = ", ".join(moves[:8])
        return (
            f"{len(moves)} moves loaded. Name a move in your action to roll it (e.g., 'Secure an Advantage').\n"
            "If you just describe intent, I'll pick a fitting move for you.\n"
            f"Examples: {examples}..."
        )

    def _roll_oracle(self, oracle_query: str) -> str:
        if not self.data:
            return "No Datasworn data loaded. Place dataforged.json to use oracles."

        if not oracle_query:
            return (
                "Usage: !oracle <category/table>. Examples:\n"
                "!oracle Space/Planets\n"
                "!oracle Derelicts/Zone Form\n"
                "!oracle character"  # keyword search
            )

        # Try an exact path first
        direct = self.data.roll_oracle(oracle_query)
        if direct:
            return f"{oracle_query}: {direct}"

        # Fallback to keyword search
        matches = self.data.search_oracles(oracle_query)
        if not matches:
            return "No matching oracle found. Try a broader keyword."

        if len(matches) > 1:
            names: list[str] = []
            for table in matches[:5]:
                key = self.data.get_oracle_key(table)
                label = f"{table.name} ({key})" if key else table.name
                names.append(label)
            return f"Multiple oracles match '{oracle_query}'. Narrow it down: {', '.join(names)}"

        oracle = matches[0]
        key = self.data.get_oracle_key(oracle)
        result = self.data.roll_oracle(key or oracle_query)
        return f"{oracle.name}: {result}"

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
