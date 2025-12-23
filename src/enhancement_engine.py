"""
Enhancement Engine - Unified Integration Point

Centralizes all 13 enhancement systems into a single clean interface
for integration with the LangGraph workflow.

This unifies:
- Smart Event Detection
- Deep Oracle Integration  
- Persistent World Changes
- Session Recap Generation
- Vow-Driven Complications
- Dynamic Faction System
- Asset Narrative Integration
- Auto-Save System
- Real-Time Combat Flow
- Dialogue Choice Trees
- Economic Simulation
- Character Progression
- Multi-System Support
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from src.logging_config import get_logger

logger = get_logger("enhancement_engine")


@dataclass
class EnhancementContext:
    """Context gathered from all enhancement systems for narrator injection."""
    # Narrative injections (add to system prompt)
    world_constraints: str = ""     # From persistent_world
    faction_context: str = ""       # From faction_system
    vow_complications: str = ""     # From vow_complications
    oracle_results: str = ""        # From oracle_integration
    asset_hooks: str = ""           # From asset_narrative
    economic_context: str = ""      # From economic_system
    combat_status: str = ""         # From combat_flow
    dialogue_state: str = ""        # From dialogue_system

    # Detected events for consequence tracking
    detected_events: List[Dict[str, Any]] = field(default_factory=list)

    # Session info
    session_recap: str = ""         # From session_recap
    milestones: List[str] = field(default_factory=list)  # From character_progression

    def get_narrator_injection(self) -> str:
        """Combine all context into narrator system prompt injection."""
        parts = []

        if self.world_constraints:
            parts.append(self.world_constraints)

        if self.faction_context:
            parts.append(self.faction_context)

        if self.vow_complications:
            parts.append(self.vow_complications)

        if self.oracle_results:
            parts.append(self.oracle_results)

        if self.asset_hooks:
            parts.append(self.asset_hooks)

        if self.economic_context:
            parts.append(self.economic_context)

        if self.combat_status:
            parts.append(self.combat_status)

        if not parts:
            return ""

        return "\n\n".join([
            "<enhancement_context>",
            *parts,
            "</enhancement_context>"
        ])


class EnhancementEngine:
    """
    Unified enhancement engine coordinating all 13 systems.

    Initialize once and call process_turn() each turn for full integration.
    """

    def __init__(self):
        # Lazy-loaded engines
        self._event_detector = None
        self._oracle_engine = None
        self._world_engine = None
        self._recap_engine = None
        self._vow_engine = None
        self._faction_system = None
        self._asset_engine = None
        self._save_system = None
        self._combat_engine = None
        self._dialogue_system = None
        self._economic_system = None
        self._progression_engine = None

        self._initialized = False
        self._current_scene = 0

    def _lazy_init(self):
        """Lazy initialize all engines on first use."""
        if self._initialized:
            return

        try:
            from src.smart_event_detection import SmartEventDetector
            self._event_detector = SmartEventDetector(use_llm=True)
        except Exception as e:
            logger.warning(f"Smart event detection system unavailable: {e}")

        try:
            from src.oracle_integration import OracleIntegrationEngine
            self._oracle_engine = OracleIntegrationEngine()
        except Exception as e:
            logger.warning(f"Oracle integration system unavailable: {e}")

        try:
            from src.persistent_world import PersistentWorldEngine
            self._world_engine = PersistentWorldEngine()
            try:
                from src.lore import LoreRegistry

                self._lore_registry = LoreRegistry()
                self._world_engine.attach_lore_registry(self._lore_registry)
            except Exception as e:
                logger.debug(f"Lore registry attachment failed: {e}")
                self._lore_registry = None
        except Exception as e:
            logger.warning(f"Persistent world system unavailable: {e}")

        try:
            from src.session_recap import SessionRecapEngine
            self._recap_engine = SessionRecapEngine()
        except Exception as e:
            logger.warning(f"Session recap system unavailable: {e}")

        try:
            from src.vow_complications import VowComplicationEngine
            self._vow_engine = VowComplicationEngine()
        except Exception as e:
            logger.warning(f"Vow complication system unavailable: {e}")

        try:
            from src.faction_system import FactionSystem
            self._faction_system = FactionSystem()
        except Exception as e:
            logger.warning(f"Faction system unavailable: {e}")

        try:
            from src.asset_narrative import AssetNarrativeEngine
            self._asset_engine = AssetNarrativeEngine()
        except Exception as e:
            logger.warning(f"Asset narrative system unavailable: {e}")

        try:
            from src.auto_save import AutoSaveSystem
            self._save_system = AutoSaveSystem()
        except Exception as e:
            logger.warning(f"Auto-save system unavailable: {e}")

        try:
            from src.combat_flow import CombatFlowEngine
            self._combat_engine = CombatFlowEngine()
        except Exception as e:
            logger.warning(f"Combat flow system unavailable: {e}")

        try:
            from src.dialogue_system import DialogueSystem
            self._dialogue_system = DialogueSystem()
        except Exception as e:
            logger.warning(f"Dialogue system unavailable: {e}")

        try:
            from src.economic_system import EconomicSystem
            self._economic_system = EconomicSystem()
        except Exception as e:
            logger.warning(f"Economic system unavailable: {e}")

        try:
            from src.character_progression import CharacterProgressionEngine
            self._progression_engine = CharacterProgressionEngine()
        except Exception as e:
            logger.warning(f"Character progression system unavailable: {e}")

        self._initialized = True

    def set_scene(self, scene_number: int):
        """Update scene number across all engines."""
        self._lazy_init()
        self._current_scene = scene_number

        if self._world_engine:
            self._world_engine.set_context(scene_number)
        if self._vow_engine:
            self._vow_engine.set_scene(scene_number)
        if self._faction_system:
            self._faction_system.set_scene(scene_number)
        if self._asset_engine:
            self._asset_engine.set_scene(scene_number)
        if self._progression_engine:
            self._progression_engine.set_scene(scene_number)

    def process_turn(
        self,
        player_input: str,
        narrative_output: str = "",
        location: str = "",
        active_npcs: List[str] = None,
        player_name: str = "the protagonist",
        vow_states: List[Dict] = None,
        asset_states: List[Dict] = None,
        is_session_start: bool = False,
    ) -> EnhancementContext:
        """
        Process a turn through all enhancement systems.

        Call this after director but before narrator, and again
        after narrator output for event detection.

        Returns:
            EnhancementContext with all gathered context
        """
        self._lazy_init()
        context = EnhancementContext()
        active_npcs = active_npcs or []

        # =====================================================================
        # PRE-NARRATOR: Gather context to inject
        # =====================================================================

        # 1. Session Recap (only at session start)
        if is_session_start and self._recap_engine:
            context.session_recap = self._recap_engine.get_recap_for_session_start(
                protagonist_name=player_name
            )

        # 2. Persistent World Constraints
        if self._world_engine:
            context.world_constraints = self._world_engine.get_narrator_constraints()

            # Also get location-specific context
            if location:
                loc_context = self._world_engine.get_context_for_location(location)
                if loc_context:
                    context.world_constraints += f"\n{loc_context}"

        # 3. Faction Context
        if self._faction_system:
            context.faction_context = self._faction_system.get_narrator_context()

            # Check territory status for location
            if location:
                territory = self._faction_system.get_territory_status(location)
                if territory:
                    faction_parts = [f"  {impl}" for _, _, impl in territory]
                    context.faction_context += "\n" + "\n".join(faction_parts)

        # 4. Vow Complications
        if self._vow_engine:
            # Sync vows from game state
            if vow_states:
                from src.vow_complications import sync_vows_from_game_state
                sync_vows_from_game_state(self._vow_engine, vow_states)

            # Check for due complications
            complications = self._vow_engine.get_all_pending_complications()
            context.vow_complications = self._vow_engine.get_narrator_injection(complications)

        # 5. Oracle Auto-Generation
        if self._oracle_engine:
            oracle_results = self._oracle_engine.auto_generate(player_input)
            context.oracle_results = self._oracle_engine.get_narrator_injection(oracle_results)

        # 6. Asset Narrative Hooks
        if self._asset_engine:
            # Sync assets from game state
            if asset_states:
                self._asset_engine.sync_from_game_state(asset_states)

            # Determine context type
            scene_context = "exploration"  # Could be smarter
            if self._combat_engine and self._combat_engine.is_in_combat():
                scene_context = "combat"

            context.asset_hooks = self._asset_engine.get_narrator_injection(scene_context)

        # 7. Economic Context
        if self._economic_system and location:
            context.economic_context = self._economic_system.get_narrator_context(location)

        # 8. Combat Status
        if self._combat_engine and self._combat_engine.is_in_combat():
            context.combat_status = self._combat_engine.get_narrator_context()

        # 9. Dialogue State
        if self._dialogue_system and self._dialogue_system.is_in_dialogue():
            context.dialogue_state = self._dialogue_system.get_narrator_context()

        return context

    def post_narrative(
        self,
        narrative_output: str,
        location: str = "",
        active_npcs: List[str] = None,
        player_name: str = "the protagonist",
    ):
        """
        Process after narrative generation for event detection.

        Call this after the narrator generates output.
        """
        self._lazy_init()
        active_npcs = active_npcs or []

        # Smart Event Detection
        if self._event_detector:
            events = self._event_detector.detect_events(
                narrative=narrative_output,
                location=location,
                active_npcs=active_npcs,
                player_name=player_name,
            )

            # Record world changes from detected events
            if events and self._world_engine:
                from src.smart_event_detection import EventType
                for event in events:
                    if event.event_type == EventType.KILL:
                        for entity in event.entities:
                            self._world_engine.record_npc_death(
                                entity,
                                location=location,
                                description=event.description
                            )

        # Session event tracking
        if self._recap_engine:
            self._recap_engine.record_event(
                description=narrative_output[:200],
                importance=5,
                characters=active_npcs,
                location=location,
            )

    def start_combat(self, enemies: List[Dict[str, Any]]):
        """Start a combat encounter."""
        self._lazy_init()
        if self._combat_engine:
            self._combat_engine.start_combat(enemies)
            return self._combat_engine.roll_initiative()
        return []

    def end_combat(self) -> Dict[str, Any]:
        """End combat and get summary."""
        self._lazy_init()
        if self._combat_engine:
            summary = self._combat_engine.end_combat()

            # Record milestone if won
            if self._progression_engine and summary.get("player_survived"):
                self._progression_engine.record_combat_won()

            return summary
        return {}

    def start_dialogue(self, npc_id: str):
        """Start a dialogue with an NPC."""
        self._lazy_init()
        if self._dialogue_system:
            return self._dialogue_system.start_dialogue(npc_id)
        return None

    def modify_faction_reputation(
        self,
        faction_id: str,
        change: int,
        reason: str
    ):
        """Modify reputation with a faction."""
        self._lazy_init()
        if self._faction_system:
            return self._faction_system.modify_reputation(faction_id, change, reason)
        return None

    def award_xp(self, amount: int, source: str):
        """Award XP to the player."""
        self._lazy_init()
        if self._progression_engine:
            return self._progression_engine.award_xp(amount, source)
        return None

    def start_session(self, session_number: int = None):
        """Start a new game session."""
        self._lazy_init()
        if self._recap_engine:
            self._recap_engine.start_session(session_number)
        if self._save_system:
            self._save_system.mark_session_start()

    def end_session(self, tone: str = ""):
        """End the current session."""
        self._lazy_init()
        if self._recap_engine:
            self._recap_engine.end_session(tone)

    def auto_save(self, game_state: Dict[str, Any]):
        """Perform auto-save."""
        self._lazy_init()
        if self._save_system:
            return self._save_system.auto_save(game_state)
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize all engine states."""
        self._lazy_init()
        state = {"current_scene": self._current_scene}

        if self._world_engine:
            state["persistent_world"] = self._world_engine.to_dict()
        if self._recap_engine:
            state["session_recap"] = self._recap_engine.to_dict()
        if self._vow_engine:
            state["vow_complications"] = self._vow_engine.to_dict()
        if self._faction_system:
            state["faction_system"] = self._faction_system.to_dict()
        if self._asset_engine:
            state["asset_narrative"] = self._asset_engine.to_dict()
        if self._combat_engine:
            state["combat_flow"] = self._combat_engine.to_dict()
        if self._dialogue_system:
            state["dialogue_system"] = self._dialogue_system.to_dict()
        if self._economic_system:
            state["economic_system"] = self._economic_system.to_dict()
        if self._progression_engine:
            state["character_progression"] = self._progression_engine.to_dict()
        if self._oracle_engine:
            state["oracle_integration"] = self._oracle_engine.to_dict()

        return state

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnhancementEngine":
        """Deserialize engine states."""
        engine = cls()
        engine._lazy_init()
        engine._current_scene = data.get("current_scene", 0)

        if "persistent_world" in data and engine._world_engine:
            from src.persistent_world import PersistentWorldEngine
            engine._world_engine = PersistentWorldEngine.from_dict(data["persistent_world"])

        if "session_recap" in data and engine._recap_engine:
            from src.session_recap import SessionRecapEngine
            engine._recap_engine = SessionRecapEngine.from_dict(data["session_recap"])

        if "vow_complications" in data and engine._vow_engine:
            from src.vow_complications import VowComplicationEngine
            engine._vow_engine = VowComplicationEngine.from_dict(data["vow_complications"])

        if "faction_system" in data and engine._faction_system:
            from src.faction_system import FactionSystem
            engine._faction_system = FactionSystem.from_dict(data["faction_system"])

        if "combat_flow" in data and engine._combat_engine:
            from src.combat_flow import CombatFlowEngine
            engine._combat_engine = CombatFlowEngine.from_dict(data["combat_flow"])

        if "dialogue_system" in data and engine._dialogue_system:
            from src.dialogue_system import DialogueSystem
            engine._dialogue_system = DialogueSystem.from_dict(data["dialogue_system"])

        if "character_progression" in data and engine._progression_engine:
            from src.character_progression import CharacterProgressionEngine
            engine._progression_engine = CharacterProgressionEngine.from_dict(data["character_progression"])

        if "oracle_integration" in data and engine._oracle_engine:
            from src.oracle_integration import OracleIntegrationEngine
            engine._oracle_engine = OracleIntegrationEngine.from_dict(data["oracle_integration"])

        return engine


# =============================================================================
# SINGLETON ACCESSOR
# =============================================================================

_enhancement_engine: Optional[EnhancementEngine] = None


def get_enhancement_engine() -> EnhancementEngine:
    """Get or create the singleton enhancement engine."""
    global _enhancement_engine
    if _enhancement_engine is None:
        _enhancement_engine = EnhancementEngine()
    return _enhancement_engine


def reset_enhancement_engine():
    """Reset the enhancement engine (for testing)."""
    global _enhancement_engine
    _enhancement_engine = None


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ENHANCEMENT ENGINE TEST")
    print("=" * 60)

    engine = get_enhancement_engine()
    engine.set_scene(1)

    # Process a turn
    context = engine.process_turn(
        player_input="I explore the abandoned station, looking for survivors",
        location="Waystation Epsilon",
        active_npcs=["Engineer Tanaka"],
        player_name="Kira",
    )

    print("\n--- Narrator Injection ---")
    print(context.get_narrator_injection())

    # Test combat
    print("\n--- Combat Test ---")
    engine.start_combat([
        {"name": "Raider", "threat_level": "dangerous"},
    ])
    print("Combat started")

    # Test faction
    print("\n--- Faction Test ---")
    engine.modify_faction_reputation("iron_syndicate", 15, "Helped with a job")

    # Test XP
    print("\n--- XP Test ---")
    engine.award_xp(2, "Completed objective")

    # Serialize
    print("\n--- Serialization Test ---")
    state = engine.to_dict()
    print(f"Serialized {len(state)} engine states")
