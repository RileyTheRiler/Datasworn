"""NPC perception module for normalizing raw scene data into a world state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable
import math


@dataclass
class SensoryFilters:
    """Configuration for perceptual limits and falloff behavior."""

    sight_range: float = 25.0
    hearing_range: float = 15.0
    field_of_view: float = math.pi * 0.85  # radians
    min_confidence: float = 0.2
    distance_decay: float = 0.04


@dataclass
class NoiseModel:
    """Simple environmental noise model for sensory uncertainty."""

    visual_noise: float = 0.1
    auditory_noise: float = 0.05


@dataclass
class PerceivedFact:
    """A discrete observation with an attached confidence score."""

    category: str
    identifier: str
    details: dict[str, Any]
    confidence: float


@dataclass
class WorldState:
    """Normalized state of the local world from the NPC's perspective."""

    actors: list[PerceivedFact] = field(default_factory=list)
    objects: list[PerceivedFact] = field(default_factory=list)
    lighting: float = 1.0
    time_of_day: str | None = None
    sounds: list[PerceivedFact] = field(default_factory=list)


class PerceptionSystem:
    """Collects and filters sensory data into a usable world state."""

    def __init__(self, filters: SensoryFilters | None = None, noise: NoiseModel | None = None, debug: bool = False):
        self.filters = filters or SensoryFilters()
        self.noise = noise or NoiseModel()
        self.debug = debug

    def perceive(self, scene_graph: dict[str, Any]) -> WorldState:
        actors = self._perceive_entities(scene_graph.get("actors", []), category="actor")
        objects = self._perceive_entities(scene_graph.get("objects", []), category="object")
        sounds = self._perceive_sounds(scene_graph.get("sounds", []))

        lighting = float(scene_graph.get("lighting", 1.0))
        time_of_day = scene_graph.get("time_of_day")

        world_state = WorldState(
            actors=actors,
            objects=objects,
            lighting=lighting,
            time_of_day=time_of_day,
            sounds=sounds,
        )

        if self.debug:
            self._debug_log_world_state(world_state)

        return world_state

    def _perceive_entities(self, entities: Iterable[dict[str, Any]], category: str) -> list[PerceivedFact]:
        perceived: list[PerceivedFact] = []
        for entry in entities:
            if not self._has_line_of_sight(entry):
                continue

            distance = float(entry.get("distance", self.filters.sight_range))
            if distance > self.filters.sight_range:
                continue

            base_confidence = self._base_visual_confidence(distance, entry.get("occluded", False))
            confidence = max(self.filters.min_confidence, base_confidence - self.noise.visual_noise)

            if confidence < self.filters.min_confidence:
                continue

            perceived.append(
                PerceivedFact(
                    category=category,
                    identifier=str(entry.get("id", "unknown")),
                    details={
                        "name": entry.get("name"),
                        "distance": distance,
                        "bearing": entry.get("bearing"),
                        "state": entry.get("state"),
                        "visible": entry.get("occluded", False) is False,
                    },
                    confidence=min(1.0, confidence),
                )
            )
        return perceived

    def _perceive_sounds(self, sounds: Iterable[dict[str, Any]]) -> list[PerceivedFact]:
        perceived: list[PerceivedFact] = []
        for cue in sounds:
            distance = float(cue.get("distance", self.filters.hearing_range))
            if distance > self.filters.hearing_range:
                continue

            confidence = self._auditory_confidence(distance)
            if confidence < self.filters.min_confidence:
                continue

            perceived.append(
                PerceivedFact(
                    category="sound",
                    identifier=str(cue.get("id", cue.get("source", "sound"))),
                    details={
                        "source": cue.get("source"),
                        "intensity": cue.get("intensity", 1.0),
                        "distance": distance,
                        "description": cue.get("description"),
                    },
                    confidence=min(1.0, confidence),
                )
            )
        return perceived

    def _has_line_of_sight(self, entity: dict[str, Any]) -> bool:
        if entity.get("occluded"):
            return False
        bearing = entity.get("bearing")
        if bearing is None:
            return True
        return abs(float(bearing)) <= self.filters.field_of_view / 2

    def _base_visual_confidence(self, distance: float, occluded: bool) -> float:
        if occluded:
            return 0.0
        decay = 1.0 - distance * self.filters.distance_decay
        return max(0.0, decay)

    def _auditory_confidence(self, distance: float) -> float:
        decay = 1.0 - (distance / max(self.filters.hearing_range, 1.0))
        return max(0.0, decay - self.noise.auditory_noise)

    def _debug_log_world_state(self, world_state: WorldState) -> None:
        print("[Perception] Actors:", [(a.identifier, f"{a.confidence:.2f}") for a in world_state.actors])
        print("[Perception] Objects:", [(o.identifier, f"{o.confidence:.2f}") for o in world_state.objects])
        print("[Perception] Sounds:", [(s.identifier, f"{s.confidence:.2f}") for s in world_state.sounds])
        print("[Perception] Lighting:", world_state.lighting)
        print("[Perception] Time of day:", world_state.time_of_day)
