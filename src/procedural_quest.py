"""
Procedural Quest Generation System

This module introduces a telemetry-aware quest generator that can be invoked
from existing quest hooks (region entry, resting, boredom detection, etc.).
It builds quests via a structured pipeline:
1) Player profile ingestion
2) Context selection (biome, factions, POIs)
3) Quest template selection
4) Parameter filling via rules or optional ML scoring

Debugging helpers support seeded generation and verbose logging so designers can
validate diversity and balance.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence
import logging
import random
import time

from src.quest_lore import QuestTracker, QuestType


@dataclass
class PlayerTelemetry:
    """Lightweight view of recent player behavior used for quest tuning."""

    playstyle: str = "balanced"  # e.g., "combat", "explorer", "social"
    recent_actions: List[str] = field(default_factory=list)
    favored_factions: List[str] = field(default_factory=list)
    avoided_biomes: List[str] = field(default_factory=list)
    boredom_score: float = 0.0
    time_since_last_quest: float = 0.0
    skill_levels: Dict[str, int] = field(default_factory=dict)


@dataclass
class WorldSnapshot:
    """Minimal world state snapshot consumed by the quest generator."""

    biome: str = "unknown"
    dominant_factions: List[str] = field(default_factory=list)
    nearby_pois: List[str] = field(default_factory=list)
    threat_level: str = "moderate"
    time_of_day: str = "day"
    weather: str = "clear"


@dataclass
class QuestTemplate:
    """Quest template with supported hooks and constraints."""

    template_id: str
    title_template: str
    description_template: str
    quest_type: QuestType
    supported_hooks: Sequence[str]
    tags: Sequence[str] = field(default_factory=list)
    difficulty: str = "standard"


@dataclass
class QuestGenerationResult:
    quest_id: str
    title: str
    description: str
    quest_type: QuestType
    objectives: List[str]
    debug_info: Dict[str, str]


class ProceduralQuestEngine:
    """Pipeline-based quest generator.

    The engine can be wired into existing quest hooks such as region entry,
    resting at campfires, or boredom detection to provide new content on demand.
    """

    def __init__(
        self,
        quest_tracker: Optional[QuestTracker] = None,
        templates: Optional[Sequence[QuestTemplate]] = None,
        ml_scorer: Optional[Callable[[Dict[str, str]], float]] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.quest_tracker = quest_tracker or QuestTracker()
        self.templates = list(templates) if templates else self._default_templates()
        self.ml_scorer = ml_scorer
        self.logger = logger or logging.getLogger("procedural_quest")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate_for_hook(
        self,
        hook_event: str,
        telemetry: PlayerTelemetry,
        world_state: WorldSnapshot,
        seed: Optional[int] = None,
        debug: bool = False,
    ) -> QuestGenerationResult:
        """Generate a quest tailored to a specific hook event.

        The method is deterministic when a seed is provided, enabling designers
        to debug and replay generation paths.
        """

        rng = random.Random(seed)
        debug_info = {}

        profile = self._ingest_player_profile(telemetry, rng, debug_info)
        context = self._select_context(world_state, profile, rng, debug_info)
        template = self._select_template(hook_event, context, profile, rng, debug_info)
        params = self._fill_parameters(template, context, profile, rng, debug_info)
        quest = self._build_quest(template, params, rng)

        if debug:
            debug_info["seed"] = str(seed)
            debug_info["timestamp"] = str(time.time())
            self.logger.debug("Quest generation debug: %s", debug_info)
            quest.debug_info.update(debug_info)

        return quest

    def generate_and_track(
        self,
        hook_event: str,
        telemetry: PlayerTelemetry,
        world_state: WorldSnapshot,
        seed: Optional[int] = None,
        debug: bool = False,
    ) -> QuestGenerationResult:
        """Generate a quest and register it with the QuestTracker.

        This method can be called by existing quest hooks to add the quest to
        the active tracker, returning the generation result for UI or narration.
        """

        quest = self.generate_for_hook(hook_event, telemetry, world_state, seed, debug)
        quest_obj = self.quest_tracker.add_quest(
            quest_id=quest.quest_id,
            title=quest.title,
            description=quest.description,
            quest_type=quest.quest_type,
            stakes="",  # Stakes can be derived from params in the future
        )
        for idx, objective in enumerate(quest.objectives, start=1):
            self.quest_tracker.add_objective(
                quest_id=quest_obj.quest_id,
                obj_id=f"{quest_obj.quest_id}_obj_{idx}",
                description=objective,
            )
        return quest

    # ------------------------------------------------------------------
    # Pipeline steps
    # ------------------------------------------------------------------
    def _ingest_player_profile(
        self,
        telemetry: PlayerTelemetry,
        rng: random.Random,
        debug_info: Dict[str, str],
    ) -> Dict[str, str]:
        """Transform raw telemetry into a compact profile.

        A simple heuristic favors playstyles with recent activity while gently
        nudging toward underused content when the boredom score is high.
        """

        playstyle = telemetry.playstyle
        if telemetry.boredom_score > 0.6 and telemetry.recent_actions:
            playstyle = rng.choice(["explorer", "social", "combat"])

        profile = {
            "playstyle": playstyle,
            "focal_faction": telemetry.favored_factions[0] if telemetry.favored_factions else "independent",
            "avoid_biome": telemetry.avoided_biomes[0] if telemetry.avoided_biomes else "",
            "high_skill": max(telemetry.skill_levels, key=telemetry.skill_levels.get, default="generalist"),
        }
        debug_info["profile"] = str(profile)
        return profile

    def _select_context(
        self,
        world_state: WorldSnapshot,
        profile: Dict[str, str],
        rng: random.Random,
        debug_info: Dict[str, str],
    ) -> Dict[str, str]:
        """Choose contextual anchors like biome, faction, and POIs."""

        biome = world_state.biome if world_state.biome != profile.get("avoid_biome") else "wilds"
        faction = world_state.dominant_factions[0] if world_state.dominant_factions else profile.get("focal_faction", "independent")
        poi = rng.choice(world_state.nearby_pois) if world_state.nearby_pois else "hidden cache"

        context = {
            "biome": biome,
            "faction": faction,
            "poi": poi,
            "threat": world_state.threat_level,
            "time": world_state.time_of_day,
            "weather": world_state.weather,
        }
        debug_info["context"] = str(context)
        return context

    def _select_template(
        self,
        hook_event: str,
        context: Dict[str, str],
        profile: Dict[str, str],
        rng: random.Random,
        debug_info: Dict[str, str],
    ) -> QuestTemplate:
        """Pick a quest template that matches hook, context, and profile."""

        viable = [t for t in self.templates if hook_event in t.supported_hooks]
        if not viable:
            raise ValueError(f"No quest templates registered for hook '{hook_event}'")

        # Simple scoring: template gains weight if tags match playstyle or context.
        scored_templates: List[tuple[QuestTemplate, float]] = []
        for template in viable:
            score = 1.0
            if profile["playstyle"] in template.tags:
                score += 1.5
            if context["biome"] in template.tags or context["faction"] in template.tags:
                score += 0.5
            if template.difficulty == "hard" and profile.get("high_skill") not in ["combat", "stealth"]:
                score -= 0.3
            if self.ml_scorer:
                score += float(self.ml_scorer({"template_id": template.template_id, **context, **profile}))
            scored_templates.append((template, max(score, 0.1)))

        # Weighted choice for diversity.
        total = sum(score for _, score in scored_templates)
        pick = rng.uniform(0, total)
        for template, score in scored_templates:
            pick -= score
            if pick <= 0:
                debug_info["template"] = template.template_id
                return template
        debug_info["template"] = scored_templates[-1][0].template_id
        return scored_templates[-1][0]

    def _fill_parameters(
        self,
        template: QuestTemplate,
        context: Dict[str, str],
        profile: Dict[str, str],
        rng: random.Random,
        debug_info: Dict[str, str],
    ) -> Dict[str, str]:
        """Fill template parameters using simple rules and optional ML guidance."""

        antagonist = context["faction"] if context["threat"] != "low" else "rogue artificer"
        focus_poi = context["poi"]
        activity = "sabotage" if profile["playstyle"] == "stealth" else "rescue"

        params = {
            "biome": context["biome"],
            "faction": antagonist,
            "poi": focus_poi,
            "activity": activity,
            "time": context["time"],
        }

        if template.quest_type == QuestType.EXPLORATION:
            params["activity"] = "survey"
        elif template.quest_type == QuestType.FACTION and profile.get("focal_faction"):
            params["faction"] = profile["focal_faction"]
        elif template.quest_type == QuestType.PERSONAL:
            params["activity"] = "assist"

        # Minor random variation for objectives
        params["twist"] = rng.choice([
            "unexpected ally arrives",
            "time-sensitive weather shift",
            "hidden cache complicates route",
        ])

        debug_info["parameters"] = str(params)
        return params

    def _build_quest(
        self,
        template: QuestTemplate,
        params: Dict[str, str],
        rng: random.Random,
    ) -> QuestGenerationResult:
        """Create a QuestGenerationResult from template and parameters."""

        quest_id = f"{template.template_id}-{rng.randint(1000, 9999)}"
        title = template.title_template.format(**params)
        description = template.description_template.format(**params)
        objectives = [
            f"Reach the {params['poi']} in the {params['biome']} biome",
            f"{params['activity'].capitalize()} the target linked to {params['faction']}",
            f"Adapt to the twist: {params['twist']}",
        ]

        return QuestGenerationResult(
            quest_id=quest_id,
            title=title,
            description=description,
            quest_type=template.quest_type,
            objectives=objectives,
            debug_info={},
        )

    # ------------------------------------------------------------------
    # Debugging helpers
    # ------------------------------------------------------------------
    def preview_candidates(
        self,
        hook_event: str,
        telemetry: PlayerTelemetry,
        world_state: WorldSnapshot,
    ) -> List[str]:
        """Return IDs of templates eligible for a hook to validate coverage."""

        return [t.template_id for t in self.templates if hook_event in t.supported_hooks]

    def trace_generation(
        self,
        hook_event: str,
        telemetry: PlayerTelemetry,
        world_state: WorldSnapshot,
        seed: int,
    ) -> Dict[str, str]:
        """Run generation with debug information returned."""

        result = self.generate_for_hook(hook_event, telemetry, world_state, seed=seed, debug=True)
        return result.debug_info

    # ------------------------------------------------------------------
    # Defaults
    # ------------------------------------------------------------------
    @staticmethod
    def _default_templates() -> List[QuestTemplate]:
        return [
            QuestTemplate(
                template_id="campfire_rescue",
                title_template="Rescue at the {poi}",
                description_template=(
                    "A distress signal flickers near the {poi} as night falls."
                    " Local {faction} forces might reach them first unless you act during the {time}."
                ),
                quest_type=QuestType.SIDE,
                supported_hooks=["campfire_rest", "boredom_trigger"],
                tags=["social", "explorer"],
                difficulty="standard",
            ),
            QuestTemplate(
                template_id="region_patrol",
                title_template="Secure the {biome} frontier",
                description_template=(
                    "Reports suggest the {faction} are testing defenses near {poi}."
                    " Conduct a patrol during the {time} while the weather remains {weather}."
                ),
                quest_type=QuestType.FACTION,
                supported_hooks=["region_enter", "boredom_trigger"],
                tags=["combat", "faction"],
                difficulty="hard",
            ),
            QuestTemplate(
                template_id="wanderer_mystery",
                title_template="Mystery in the {biome}",
                description_template=(
                    "A wandering scholar reports anomalies around {poi}."
                    " Investigate quietly before the {faction} claim the discovery."
                ),
                quest_type=QuestType.EXPLORATION,
                supported_hooks=["region_enter", "campfire_rest"],
                tags=["explorer", "investigation"],
                difficulty="standard",
            ),
            QuestTemplate(
                template_id="personal_favor",
                title_template="Aid an ally of the {faction}",
                description_template=(
                    "An ally asks you to {activity} a contact near {poi}."
                    " They fear reprisal from {faction} if it goes wrong."
                ),
                quest_type=QuestType.PERSONAL,
                supported_hooks=["campfire_rest", "boredom_trigger"],
                tags=["social", "stealth"],
                difficulty="standard",
            ),
        ]
