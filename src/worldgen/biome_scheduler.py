from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Optional


@dataclass
class BiomeCurve:
    """Represents a soft progression curve for a biome.

    The curve uses a triangular profile between ``start`` and ``end`` with a
    configurable ``peak``. Scarcity reduces the effective weight, allowing the
    scheduler to dial down rare or protected biomes without removing them
    entirely.
    """

    name: str
    start: float
    peak: float
    end: float
    scarcity: float = 0.0
    softness: float = 0.2

    def weight_at(self, position: float) -> float:
        """Return a smooth weight for this biome at a given position.

        The triangular shape is smoothed by a cosine ramp to avoid sharp edges
        while still emphasizing the peak region. Scarcity scales the result
        downward but never removes the biome completely.
        """

        if position < self.start or position > self.end:
            return 0.0

        # Normalized location between start and peak/end.
        if position <= self.peak:
            span = max(self.peak - self.start, 1e-6)
            t = (position - self.start) / span
        else:
            span = max(self.end - self.peak, 1e-6)
            t = 1.0 - (position - self.peak) / span

        # Apply cosine easing for softer transitions.
        eased = (1 - math.cos(math.pi * t)) / 2
        eased = max(eased, self.softness * 0.1)
        scarcity_scale = max(0.05, 1.0 - self.scarcity)
        return eased * scarcity_scale


@dataclass
class BiomeScheduler:
    """Chooses biomes along a route using progression curves.

    The scheduler supports global scarcity knobs and reproducible selection via
    an injected random state.
    """

    curves: List[BiomeCurve]
    global_scarcity: float = 0.0
    rng: random.Random = field(default_factory=random.Random)

    def __post_init__(self) -> None:
        self.curves_by_name: Dict[str, BiomeCurve] = {curve.name: curve for curve in self.curves}

    def get_weights(self, position: float) -> Dict[str, float]:
        """Compute biome weights at a given position."""

        weights: Dict[str, float] = {}
        for curve in self.curves:
            base_weight = curve.weight_at(position)
            scarcity_scale = max(0.05, 1.0 - self.global_scarcity)
            weight = base_weight * scarcity_scale
            if weight > 0:
                weights[curve.name] = weight
        return weights

    def pick_biome(self, position: float) -> str:
        """Choose a biome at the given position using weighted randomness."""

        weights = self.get_weights(position)
        if not weights:
            raise ValueError("No biome weights available at this position")

        choices: List[str] = []
        values: List[float] = []
        for name, weight in weights.items():
            choices.append(name)
            values.append(weight)

        total = sum(values)
        normalized = [w / total for w in values]
        return self.rng.choices(choices, weights=normalized, k=1)[0]

    def walk(self, positions: Iterable[float]) -> List[str]:
        """Return the biome choices for a series of positions."""

        return [self.pick_biome(pos) for pos in positions]

    def scarcity_adjusted(self, overrides: Optional[Mapping[str, float]] = None) -> "BiomeScheduler":
        """Return a new scheduler with per-biome scarcity overrides.

        ``overrides`` is a mapping of biome name to scarcity value between 0 and
        1, where larger values reduce the biome's prevalence.
        """

        updated: List[BiomeCurve] = []
        overrides = overrides or {}
        for curve in self.curves:
            scarcity = overrides.get(curve.name, curve.scarcity)
            updated.append(
                BiomeCurve(
                    name=curve.name,
                    start=curve.start,
                    peak=curve.peak,
                    end=curve.end,
                    scarcity=scarcity,
                    softness=curve.softness,
                )
            )

        return BiomeScheduler(curves=updated, global_scarcity=self.global_scarcity, rng=self.rng)
