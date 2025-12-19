"""
Asset Narrative Integration

Connects character assets (equipment, companions, vehicles) to
narrative content, making them feel alive in the story.

Assets aren't just mechanical bonuses - they're story elements.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
import random


class AssetCategory(Enum):
    """Categories of assets."""
    COMPANION = "companion"
    PATH = "path"
    COMMAND_VEHICLE = "command_vehicle"
    SUPPORT_VEHICLE = "support_vehicle"
    MODULE = "module"
    DEED = "deed"


@dataclass
class AssetNarrativeHook:
    """A narrative hook for an asset."""
    trigger: str  # e.g., "combat", "exploration", "social"
    template: str  # Narrative template with {asset_name}
    probability: float = 0.3
    conditions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trigger": self.trigger,
            "template": self.template,
            "probability": self.probability,
            "conditions": self.conditions,
        }


@dataclass
class TrackedAsset:
    """An asset being tracked for narrative integration."""
    id: str
    name: str
    category: AssetCategory
    abilities_enabled: List[bool]
    description: str = ""
    personality: str = ""  # For companions
    relationship: str = ""  # Player's relationship with companion
    narrative_weight: float = 0.5  # How often to feature in narrative

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category.value,
            "abilities_enabled": self.abilities_enabled,
            "description": self.description,
            "personality": self.personality,
            "relationship": self.relationship,
            "narrative_weight": self.narrative_weight,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TrackedAsset":
        return cls(
            id=data["id"],
            name=data["name"],
            category=AssetCategory(data.get("category", "path")),
            abilities_enabled=data.get("abilities_enabled", [True, False, False]),
            description=data.get("description", ""),
            personality=data.get("personality", ""),
            relationship=data.get("relationship", ""),
            narrative_weight=data.get("narrative_weight", 0.5),
        )


# Pre-defined narrative hooks by category
CATEGORY_HOOKS: Dict[AssetCategory, List[AssetNarrativeHook]] = {
    AssetCategory.COMPANION: [
        AssetNarrativeHook(
            trigger="exploration",
            template="{asset_name} notices something you missed",
            probability=0.3,
        ),
        AssetNarrativeHook(
            trigger="combat",
            template="{asset_name} moves to cover your flank",
            probability=0.4,
        ),
        AssetNarrativeHook(
            trigger="social",
            template="{asset_name}'s presence adds weight to your words",
            probability=0.25,
        ),
        AssetNarrativeHook(
            trigger="rest",
            template="You share a quiet moment with {asset_name}",
            probability=0.4,
        ),
        AssetNarrativeHook(
            trigger="danger",
            template="{asset_name} senses the danger before you do",
            probability=0.35,
        ),
    ],
    AssetCategory.COMMAND_VEHICLE: [
        AssetNarrativeHook(
            trigger="travel",
            template="The {asset_name} hums beneath you as you plot the course",
            probability=0.4,
        ),
        AssetNarrativeHook(
            trigger="arrival",
            template="The {asset_name} settles into its berth",
            probability=0.3,
        ),
        AssetNarrativeHook(
            trigger="combat",
            template="The {asset_name}'s weapons come online",
            probability=0.35,
        ),
        AssetNarrativeHook(
            trigger="exploration",
            template="Sensors aboard the {asset_name} ping with data",
            probability=0.3,
        ),
    ],
    AssetCategory.PATH: [
        AssetNarrativeHook(
            trigger="skill_use",
            template="Your training as a {asset_name} guides your actions",
            probability=0.25,
        ),
        AssetNarrativeHook(
            trigger="social",
            template="Your reputation as a {asset_name} precedes you",
            probability=0.2,
        ),
    ],
    AssetCategory.MODULE: [
        AssetNarrativeHook(
            trigger="ship_action",
            template="The {asset_name} module activates",
            probability=0.3,
        ),
    ],
}

# Companion personality interjections
COMPANION_INTERJECTIONS = {
    "brave": [
        "{name} steps forward, ready for anything",
        "{name} stands their ground",
        "{name} doesn't flinch",
    ],
    "cautious": [
        "{name} hangs back, assessing the situation",
        "{name} suggests caution",
        "{name} eyes the exits",
    ],
    "loyal": [
        "{name} stays close, watching your back",
        "{name} awaits your command",
        "{name} stands by your side",
    ],
    "curious": [
        "{name} examines something with interest",
        "{name} investigates the surroundings",
        "{name} asks questions you hadn't considered",
    ],
    "protective": [
        "{name} positions themselves between you and danger",
        "{name} watches for threats",
        "{name} bristles at any sign of hostility toward you",
    ],
}


class AssetNarrativeEngine:
    """
    Engine for integrating assets into narrative.

    Features:
    - Context-aware asset mentions
    - Companion personality integration
    - Ship/vehicle ambient descriptions
    - Ability trigger narratives
    """

    def __init__(self):
        self._assets: Dict[str, TrackedAsset] = {}
        self._last_featured: Dict[str, int] = {}  # asset_id -> scene count
        self._current_scene: int = 0

    def add_asset(
        self,
        asset_id: str,
        name: str,
        category: AssetCategory,
        abilities: List[bool] = None,
        personality: str = "",
        description: str = ""
    ):
        """Register an asset for narrative tracking."""
        self._assets[asset_id] = TrackedAsset(
            id=asset_id,
            name=name,
            category=category,
            abilities_enabled=abilities or [True, False, False],
            personality=personality,
            description=description,
        )

    def remove_asset(self, asset_id: str):
        """Remove an asset from tracking."""
        if asset_id in self._assets:
            del self._assets[asset_id]

    def set_scene(self, scene_number: int):
        """Set current scene for cooldown tracking."""
        self._current_scene = scene_number

    def get_narrative_hooks(
        self,
        context: str,
        max_hooks: int = 2
    ) -> List[str]:
        """
        Get narrative hooks for the current context.

        Args:
            context: Scene context (combat, exploration, social, etc.)
            max_hooks: Maximum hooks to return

        Returns:
            List of narrative snippets
        """
        hooks = []

        for asset in self._assets.values():
            # Check cooldown
            scenes_since = self._current_scene - self._last_featured.get(asset.id, 0)
            if scenes_since < 2 and self._last_featured.get(asset.id, 0) > 0:
                continue

            category_hooks = CATEGORY_HOOKS.get(asset.category, [])

            for hook in category_hooks:
                if hook.trigger != context:
                    continue

                # Weight by narrative importance
                adjusted_prob = hook.probability * asset.narrative_weight

                if random.random() < adjusted_prob:
                    narrative = hook.template.format(asset_name=asset.name)
                    hooks.append(narrative)
                    self._last_featured[asset.id] = self._current_scene

                    if len(hooks) >= max_hooks:
                        return hooks

        return hooks

    def get_companion_interjection(
        self,
        companion_id: str,
        situation: str = "general"
    ) -> Optional[str]:
        """
        Get an interjection from a companion.

        Args:
            companion_id: ID of the companion asset
            situation: Type of situation

        Returns:
            Interjection text or None
        """
        asset = self._assets.get(companion_id)
        if not asset or asset.category != AssetCategory.COMPANION:
            return None

        personality = asset.personality or "loyal"
        interjections = COMPANION_INTERJECTIONS.get(personality, COMPANION_INTERJECTIONS["loyal"])

        if random.random() < 0.4:  # 40% chance
            template = random.choice(interjections)
            return template.format(name=asset.name)

        return None

    def get_ship_ambient(self, ship_id: str = None) -> Optional[str]:
        """Get ambient description of ship/vehicle."""
        # Find command vehicle if not specified
        ship = None
        if ship_id:
            ship = self._assets.get(ship_id)
        else:
            for asset in self._assets.values():
                if asset.category == AssetCategory.COMMAND_VEHICLE:
                    ship = asset
                    break

        if not ship:
            return None

        ambients = [
            f"The {ship.name}'s engines hum in the background",
            f"Soft lights illuminate the {ship.name}'s interior",
            f"The familiar creaks of the {ship.name} surround you",
            f"The {ship.name} feels like home",
            f"Status lights blink on the {ship.name}'s console",
        ]

        if random.random() < 0.3:
            return random.choice(ambients)
        return None

    def get_ability_narrative(
        self,
        asset_id: str,
        ability_index: int
    ) -> Optional[str]:
        """Get narrative for using an asset ability."""
        asset = self._assets.get(asset_id)
        if not asset:
            return None

        if ability_index >= len(asset.abilities_enabled):
            return None

        if not asset.abilities_enabled[ability_index]:
            return None

        # Generic ability use narratives
        if asset.category == AssetCategory.COMPANION:
            return f"{asset.name} lends their skills to the task"
        elif asset.category == AssetCategory.PATH:
            return f"You draw on your training as a {asset.name}"
        elif asset.category == AssetCategory.COMMAND_VEHICLE:
            return f"The {asset.name}'s systems respond to your command"
        else:
            return f"The {asset.name} proves its worth"

    def get_narrator_injection(self, context: str = "general") -> str:
        """Generate narrator injection for assets."""
        injections = []

        # Get context-appropriate hooks
        hooks = self.get_narrative_hooks(context, max_hooks=2)
        for hook in hooks:
            injections.append(f"• {hook}")

        # Check for companion interjection
        for asset in self._assets.values():
            if asset.category == AssetCategory.COMPANION:
                interjection = self.get_companion_interjection(asset.id)
                if interjection:
                    injections.append(f"• COMPANION: {interjection}")
                break

        # Check for ship ambient
        ambient = self.get_ship_ambient()
        if ambient:
            injections.append(f"• AMBIANCE: {ambient}")

        if not injections:
            return ""

        return "\n".join([
            "[ASSET INTEGRATION - weave naturally]",
            *injections,
            "[END ASSET INTEGRATION]",
        ])

    def sync_from_game_state(self, asset_states: List[Dict[str, Any]]):
        """Sync assets from game state."""
        current_ids = set(self._assets.keys())
        state_ids = set()

        for state in asset_states:
            asset_id = state.get("id", "")
            name = state.get("name", "Unknown")
            state_ids.add(asset_id)

            # Determine category from data or default
            category = AssetCategory.PATH  # Default

            if asset_id in self._assets:
                # Update existing
                self._assets[asset_id].abilities_enabled = state.get(
                    "abilities_enabled", [True, False, False]
                )
            else:
                # Add new
                self.add_asset(
                    asset_id=asset_id,
                    name=name,
                    category=category,
                    abilities=state.get("abilities_enabled", [True, False, False]),
                )

        # Remove assets no longer in state
        for old_id in current_ids - state_ids:
            self.remove_asset(old_id)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize engine state."""
        return {
            "assets": {k: v.to_dict() for k, v in self._assets.items()},
            "last_featured": self._last_featured,
            "current_scene": self._current_scene,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AssetNarrativeEngine":
        """Deserialize engine state."""
        engine = cls()
        engine._assets = {
            k: TrackedAsset.from_dict(v)
            for k, v in data.get("assets", {}).items()
        }
        engine._last_featured = data.get("last_featured", {})
        engine._current_scene = data.get("current_scene", 0)
        return engine


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ASSET NARRATIVE ENGINE TEST")
    print("=" * 60)

    engine = AssetNarrativeEngine()

    # Add test assets
    engine.add_asset(
        "comp_rover",
        "Rover",
        AssetCategory.COMPANION,
        personality="loyal",
        description="A robotic canine companion",
    )

    engine.add_asset(
        "ship_wayfinder",
        "Wayfinder",
        AssetCategory.COMMAND_VEHICLE,
        description="A reliable cargo hauler",
    )

    engine.add_asset(
        "path_scavenger",
        "Scavenger",
        AssetCategory.PATH,
        description="Expert at finding value in ruins",
    )

    # Test narrative hooks
    print("\n--- Combat Hooks ---")
    hooks = engine.get_narrative_hooks("combat", max_hooks=3)
    for hook in hooks:
        print(f"• {hook}")

    print("\n--- Exploration Hooks ---")
    hooks = engine.get_narrative_hooks("exploration", max_hooks=3)
    for hook in hooks:
        print(f"• {hook}")

    # Test companion interjection
    print("\n--- Companion Interjection ---")
    for _ in range(3):
        interjection = engine.get_companion_interjection("comp_rover")
        if interjection:
            print(f"• {interjection}")

    # Test ship ambient
    print("\n--- Ship Ambient ---")
    for _ in range(3):
        ambient = engine.get_ship_ambient()
        if ambient:
            print(f"• {ambient}")

    # Test narrator injection
    print("\n--- Narrator Injection ---")
    print(engine.get_narrator_injection("exploration"))
