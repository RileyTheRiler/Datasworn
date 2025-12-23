"""
Auto-Save System

Automatic save system to prevent progress loss.
Saves game state after each turn with versioning.

Features:
- Auto-save after every turn
- Multiple save slots
- Crash recovery
- Save versioning (keep last N saves)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime
from pathlib import Path
import json
import shutil
import time


@dataclass
class SaveMetadata:
    """Metadata about a save file."""
    slot_name: str
    save_time: str
    session_number: int
    scene_number: int
    character_name: str
    location: str
    description: str
    version: int
    is_auto: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "slot_name": self.slot_name,
            "save_time": self.save_time,
            "session_number": self.session_number,
            "scene_number": self.scene_number,
            "character_name": self.character_name,
            "location": self.location,
            "description": self.description,
            "version": self.version,
            "is_auto": self.is_auto,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SaveMetadata":
        return cls(
            slot_name=data.get("slot_name", "unknown"),
            save_time=data.get("save_time", ""),
            session_number=data.get("session_number", 0),
            scene_number=data.get("scene_number", 0),
            character_name=data.get("character_name", "Unknown"),
            location=data.get("location", "Unknown"),
            description=data.get("description", ""),
            version=data.get("version", 1),
            is_auto=data.get("is_auto", True),
        )


class AutoSaveSystem:
    """
    Automatic save system with versioning and recovery.

    Features:
    - Configurable auto-save frequency
    - Rolling save history
    - Crash recovery detection
    - Multiple save slots
    - Quick-save/quick-load
    """

    def __init__(
        self,
        save_directory: str = "saves",
        max_versions: int = 5,
        auto_save_interval: int = 1,  # Save every N turns
        phase_controller: Any = None,
        game_state_provider: Optional[Callable[[], Dict[str, Any]]] = None,
        phase_whitelist: Optional[List[str]] = None,
    ):
        self.save_dir = Path(save_directory)
        self.save_dir.mkdir(exist_ok=True)

        self.max_versions = max_versions
        self.auto_save_interval = auto_save_interval

        self._turn_counter = 0
        self._current_slot = "autosave"
        self._crash_recovery_file = self.save_dir / ".recovery_state"
        self._metadata_cache: Dict[str, SaveMetadata] = {}
        self._phase_controller = None

        if phase_controller and game_state_provider:
            self.bind_to_phase_controller(phase_controller, game_state_provider, phase_whitelist)

    def _get_save_path(self, slot_name: str, version: int = 0) -> Path:
        """Get path for a save file."""
        if version > 0:
            return self.save_dir / f"{slot_name}_v{version}.json"
        return self.save_dir / f"{slot_name}.json"

    def _get_metadata_path(self, slot_name: str) -> Path:
        """Get path for metadata file."""
        return self.save_dir / f"{slot_name}_meta.json"

    def save_game(
        self,
        game_state: Dict[str, Any],
        slot_name: str = None,
        description: str = "",
        is_auto: bool = True,
        retry_attempts: int = 3,
        backoff_base: float = 0.05,
    ) -> SaveMetadata:
        """
        Save game state to a slot.

        Args:
            game_state: Complete game state dict
            slot_name: Save slot name (defaults to autosave)
            description: Human-readable description
            is_auto: Whether this is an automatic save

        Returns:
            SaveMetadata for the save
        """
        slot_name = slot_name or self._current_slot
        attempt = 0
        last_error: Exception | None = None

        while attempt < max(1, retry_attempts):
            try:
                metadata = self._perform_save(
                    game_state,
                    slot_name=slot_name,
                    description=description,
                    is_auto=is_auto,
                )
                return metadata
            except Exception as exc:  # pragma: no cover - logged by caller
                last_error = exc
                attempt += 1
                if attempt >= retry_attempts:
                    raise
                delay = backoff_base * (2 ** (attempt - 1))
                time.sleep(delay)

        raise last_error if last_error else RuntimeError("Save failed without exception")

    def _to_serializable(self, obj: Any) -> Any:
        """Convert object to JSON-serializable format."""
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        elif hasattr(obj, "to_dict"):
            return obj.to_dict()
        elif hasattr(obj, "__dict__"):
            return {k: self._to_serializable(v) for k, v in obj.__dict__.items()
                   if not k.startswith("_")}
        elif isinstance(obj, dict):
            return {k: self._to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._to_serializable(v) for v in obj]
        else:
            return obj

    def _rotate_saves(self, slot_name: str):
        """Rotate existing saves to maintain version history."""
        # Shift existing versions
        for v in range(self.max_versions, 0, -1):
            old_path = self._get_save_path(slot_name, v - 1 if v > 1 else 0)
            new_path = self._get_save_path(slot_name, v)

            if old_path.exists():
                if v < self.max_versions:
                    shutil.copy2(old_path, new_path)
                else:
                    # Delete oldest version
                    if new_path.exists():
                        new_path.unlink()
                    shutil.move(old_path, new_path)

    def load_game(self, slot_name: str = None, version: int = 0) -> Optional[Dict[str, Any]]:
        """
        Load game state from a slot.

        Args:
            slot_name: Save slot name
            version: Version to load (0 = latest)

        Returns:
            Game state dict or None if not found
        """
        slot_name = slot_name or self._current_slot
        save_path = self._get_save_path(slot_name, version)

        if not save_path.exists():
            return None

        with open(save_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data.get("state")

    def list_saves(self) -> List[SaveMetadata]:
        """List all available saves with metadata."""
        saves = []

        for meta_file in self.save_dir.glob("*_meta.json"):
            with open(meta_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                saves.append(SaveMetadata.from_dict(data))

        # Sort by save time, most recent first
        saves.sort(key=lambda s: s.save_time, reverse=True)
        return saves

    def delete_save(self, slot_name: str):
        """Delete a save slot and all its versions."""
        # Delete main save and versions
        for v in range(self.max_versions + 1):
            path = self._get_save_path(slot_name, v)
            if path.exists():
                path.unlink()

        # Delete metadata
        meta_path = self._get_metadata_path(slot_name)
        if meta_path.exists():
            meta_path.unlink()

        if slot_name in self._metadata_cache:
            del self._metadata_cache[slot_name]

    def auto_save(self, game_state: Dict[str, Any]) -> Optional[SaveMetadata]:
        """
        Perform auto-save if interval is met.

        Call this after each turn. Returns metadata if save occurred.
        """
        self._turn_counter += 1

        if self._turn_counter >= self.auto_save_interval:
            self._turn_counter = 0
            return self.save_game(
                game_state,
                slot_name="autosave",
                description=f"Auto-save",
                is_auto=True
            )

        return None

    def quick_save(self, game_state: Dict[str, Any]) -> SaveMetadata:
        """Perform a quick save to dedicated slot."""
        return self.save_game(
            game_state,
            slot_name="quicksave",
            description="Quick save",
            is_auto=False
        )

    def quick_load(self) -> Optional[Dict[str, Any]]:
        """Load the quick save."""
        return self.load_game("quicksave")

    # =========================================================================
    # CRASH RECOVERY
    # =========================================================================

    def mark_session_start(self):
        """Mark that a session has started (for crash detection)."""
        self._crash_recovery_file.write_text(
            datetime.now().isoformat(),
            encoding="utf-8"
        )

    def _clear_crash_marker(self):
        """Clear crash recovery marker after successful save."""
        if self._crash_recovery_file.exists():
            self._crash_recovery_file.unlink()

    def check_crash_recovery(self) -> bool:
        """Check if there's a crash recovery state available."""
        return self._crash_recovery_file.exists()

    def get_crash_recovery_state(self) -> Optional[Dict[str, Any]]:
        """Get the latest state for crash recovery."""
        return self.load_game("autosave")

    def get_recovery_info(self) -> Optional[str]:
        """Get information about available recovery."""
        if not self.check_crash_recovery():
            return None

        saves = self.list_saves()
        if not saves:
            return "Recovery detected but no saves available"

        latest = saves[0]
        return (
            f"Previous session ended unexpectedly. "
            f"Most recent save: {latest.slot_name} "
            f"({latest.character_name} at {latest.location}, {latest.description})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize system state."""
        return {
            "turn_counter": self._turn_counter,
            "current_slot": self._current_slot,
            "max_versions": self.max_versions,
            "auto_save_interval": self.auto_save_interval,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], save_directory: str = "saves") -> "AutoSaveSystem":
        """Deserialize system state."""
        system = cls(
            save_directory=save_directory,
            max_versions=data.get("max_versions", 5),
            auto_save_interval=data.get("auto_save_interval", 1),
        )
        system._turn_counter = data.get("turn_counter", 0)
        system._current_slot = data.get("current_slot", "autosave")
        return system

    # =========================================================================
    # PHASE CONTROLLER INTEGRATION
    # =========================================================================

    def bind_to_phase_controller(
        self,
        controller: Any,
        game_state_provider: Callable[[], Dict[str, Any]],
        phase_whitelist: Optional[List[str]] = None,
    ) -> None:
        """Register callbacks so autosaves occur at safe phase boundaries."""

        def _boundary_callback(phase_name: str, **_: Any) -> None:
            if phase_whitelist and phase_name not in phase_whitelist:
                return
            state = game_state_provider()
            if state is None:
                return
            self.save_game(
                state,
                slot_name="autosave",
                description=f"After phase: {phase_name}",
                is_auto=True,
            )

        if hasattr(controller, "add_boundary_listener"):
            controller.add_boundary_listener(_boundary_callback)
        elif hasattr(controller, "register_boundary_callback"):
            controller.register_boundary_callback(_boundary_callback)
        else:
            raise ValueError("Phase controller does not support boundary callbacks")

        self._phase_controller = controller

    # =========================================================================
    # INTERNALS
    # =========================================================================

    def _perform_save(
        self,
        game_state: Dict[str, Any],
        slot_name: str,
        description: str,
        is_auto: bool,
    ) -> SaveMetadata:
        # Rotate existing saves
        self._rotate_saves(slot_name)

        # Extract metadata from game state
        character = game_state.get("character", {})
        if hasattr(character, "name"):
            char_name = character.name
        else:
            char_name = character.get("name", "Unknown") if isinstance(character, dict) else "Unknown"

        world = game_state.get("world", {})
        if hasattr(world, "current_location"):
            location = world.current_location
        else:
            location = world.get("current_location", "Unknown") if isinstance(world, dict) else "Unknown"

        session = game_state.get("session", {})
        if hasattr(session, "turn_count"):
            turn_count = session.turn_count
        else:
            turn_count = session.get("turn_count", 0) if isinstance(session, dict) else 0

        metadata = SaveMetadata(
            slot_name=slot_name,
            save_time=datetime.now().isoformat(),
            session_number=1,  # Would come from session tracking
            scene_number=turn_count,
            character_name=char_name,
            location=location,
            description=description or f"Turn {turn_count}",
            version=1,
            is_auto=is_auto,
        )

        # Convert game state to serializable format
        serializable_state = self._to_serializable(game_state)

        # Save game state
        save_path = self._get_save_path(slot_name)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump({
                "metadata": metadata.to_dict(),
                "state": serializable_state,
            }, f, indent=2, default=str)

        # Save metadata separately for quick listing
        meta_path = self._get_metadata_path(slot_name)
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata.to_dict(), f, indent=2)

        self._metadata_cache[slot_name] = metadata

        # Clear crash recovery marker on successful save
        self._clear_crash_marker()
        return metadata


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    import tempfile

    print("=" * 60)
    print("AUTO-SAVE SYSTEM TEST")
    print("=" * 60)

    # Use temp directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        system = AutoSaveSystem(save_directory=temp_dir)

        # Mock game state
        mock_state = {
            "character": {"name": "Kira", "health": 5},
            "world": {"current_location": "Waystation Epsilon"},
            "session": {"turn_count": 42},
        }

        # Test save
        print("\n--- Save Test ---")
        metadata = system.save_game(mock_state, slot_name="test_save")
        print(f"Saved: {metadata.slot_name} at {metadata.save_time}")

        # Test load
        print("\n--- Load Test ---")
        loaded = system.load_game("test_save")
        if loaded:
            print(f"Loaded character: {loaded['character']['name']}")

        # Test auto-save
        print("\n--- Auto-Save Test ---")
        for i in range(3):
            result = system.auto_save(mock_state)
            if result:
                print(f"Auto-save triggered at turn {i+1}")

        # Test list saves
        print("\n--- List Saves ---")
        saves = system.list_saves()
        for save in saves:
            print(f"- {save.slot_name}: {save.character_name} at {save.location}")

        # Test crash recovery
        print("\n--- Crash Recovery Test ---")
        system.mark_session_start()
        print(f"Crash recovery available: {system.check_crash_recovery()}")
        info = system.get_recovery_info()
        if info:
            print(info)
