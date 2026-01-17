"""
Reward evaluation and loot distribution.

The system scores encounters based on difficulty and rarity, then maps
scores to XP and loot bands. It also handles streak bonuses, unique drop
unlocks, and analytics to tune fairness during playtests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import random

from src.character_progression import CharacterProgressionEngine
from src.telemetry import telemetry


class EncounterRarity(Enum):
    """Rarity of an encounter."""

    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


RARITY_WEIGHTS = {
    EncounterRarity.COMMON: 0.8,
    EncounterRarity.UNCOMMON: 1.0,
    EncounterRarity.RARE: 1.2,
    EncounterRarity.EPIC: 1.5,
    EncounterRarity.LEGENDARY: 2.0,
}


@dataclass
class EncounterContext:
    """Details used to score an encounter."""

    name: str
    difficulty_rating: float  # 0-10 scale
    rarity: EncounterRarity
    encounter_type: str = "combat"  # combat, quest, exploration, boss
    quest_completed: bool = False
    exploration_milestone: bool = False
    boss_defeated: bool = False
    streak_count: int = 0
    quest_rank: Optional[str] = None
    special_tags: List[str] = field(default_factory=list)


@dataclass
class RewardScore:
    """Score breakdown for an encounter."""

    base_difficulty: float
    rarity_bonus: float
    streak_bonus: float
    objective_bonus: float
    boss_bonus: float

    @property
    def total(self) -> float:
        return self.base_difficulty + self.rarity_bonus + self.streak_bonus + self.objective_bonus + self.boss_bonus


@dataclass
class RewardBand:
    """XP and loot band for scored encounters."""

    name: str
    score_range: Tuple[float, float]
    xp_range: Tuple[int, int]
    loot_quality: str
    unlocks_unique: bool = False
    notes: str = ""

    def choose_xp(self, score: float) -> int:
        """Pick an XP value within the band's range weighted by score."""
        low, high = self.xp_range
        span = max(high - low, 1)
        normalized = min(max(score - self.score_range[0], 0), self.score_range[1] - self.score_range[0])
        weight = normalized / max(self.score_range[1] - self.score_range[0], 1)
        return int(low + round(span * weight))


REWARD_BANDS = [
    RewardBand(
        name="Routine",
        score_range=(0, 40),
        xp_range=(1, 3),
        loot_quality="standard",
        notes="Soft rewards for warm-up encounters",
    ),
    RewardBand(
        name="Standard",
        score_range=(40, 65),
        xp_range=(3, 6),
        loot_quality="improved",
        notes="Baseline for most fights and side quests",
    ),
    RewardBand(
        name="Heroic",
        score_range=(65, 85),
        xp_range=(6, 9),
        loot_quality="rare",
        notes="Major encounters and tough objectives",
    ),
    RewardBand(
        name="Mythic",
        score_range=(85, 120),
        xp_range=(9, 12),
        loot_quality="legendary",
        unlocks_unique=True,
        notes="Bosses, epic quest finales, flawless streaks",
    ),
]


@dataclass
class LootDrop:
    """Describes a loot entry with scaling."""

    name: str
    rarity: str
    base_amount: int
    scaling_modifiers: Dict[str, float] = field(default_factory=dict)
    unique_unlock: Optional[str] = None
    requires_score: float = 0
    requires_streak: int = 0

    def scaled_amount(self, score: float, streak: int) -> int:
        """Scale the drop amount using configured modifiers."""
        amount = self.base_amount
        if "difficulty" in self.scaling_modifiers:
            amount += int(self.scaling_modifiers["difficulty"] * score / 10)
        if "streak" in self.scaling_modifiers:
            amount += int(self.scaling_modifiers["streak"] * streak)
        if "rarity" in self.scaling_modifiers:
            amount = int(amount * self.scaling_modifiers["rarity"])
        return max(1, amount)


class LootTable:
    """Loot table with scaling modifiers and unique unlocks."""

    def __init__(self):
        self.core_loot: List[LootDrop] = [
            LootDrop(
                name="Credits Cache",
                rarity="common",
                base_amount=50,
                scaling_modifiers={"difficulty": 1.5},
            ),
            LootDrop(
                name="Weapon Components",
                rarity="uncommon",
                base_amount=2,
                scaling_modifiers={"difficulty": 0.3, "rarity": 1.1},
            ),
            LootDrop(
                name="Ship Spare Parts",
                rarity="uncommon",
                base_amount=3,
                scaling_modifiers={"difficulty": 0.4},
            ),
            LootDrop(
                name="Faction Intel",
                rarity="rare",
                base_amount=1,
                scaling_modifiers={"difficulty": 0.2, "streak": 0.5},
            ),
        ]

        self.unique_loot: List[LootDrop] = [
            LootDrop(
                name="Eclipsed Relic",
                rarity="legendary",
                base_amount=1,
                scaling_modifiers={"rarity": 1.0},
                unique_unlock="mythic_relic",
                requires_score=90,
            ),
            LootDrop(
                name="Streak Champion's Badge",
                rarity="epic",
                base_amount=1,
                scaling_modifiers={"streak": 1.0},
                unique_unlock="streak_badge",
                requires_streak=3,
            ),
            LootDrop(
                name="Boss Core Fragment",
                rarity="legendary",
                base_amount=1,
                scaling_modifiers={"difficulty": 0.5},
                unique_unlock="boss_fragment",
                requires_score=85,
            ),
        ]

    def generate_loot(self, score: float, band: RewardBand, streak: int) -> List[Dict[str, Any]]:
        """Generate loot drops based on score, band, and streak."""
        drops: List[Dict[str, Any]] = []
        quality_gate = band.loot_quality

        for drop in self.core_loot:
            # Weight drop chance by loot quality
            chance = self._quality_chance(quality_gate, drop.rarity)
            if random.random() <= chance:
                drops.append({
                    "name": drop.name,
                    "rarity": drop.rarity,
                    "amount": drop.scaled_amount(score, streak),
                })

        # Unique drops unlocked by score/streak thresholds
        for drop in self.unique_loot:
            if score >= drop.requires_score and streak >= drop.requires_streak:
                drops.append({
                    "name": drop.name,
                    "rarity": drop.rarity,
                    "amount": drop.scaled_amount(score, streak),
                    "unique_unlock": drop.unique_unlock,
                })

        return drops

    @staticmethod
    def _quality_chance(band_quality: str, drop_rarity: str) -> float:
        """Basic mapping of band loot quality to drop odds."""
        base = {
            "standard": 0.45,
            "improved": 0.65,
            "rare": 0.8,
            "legendary": 0.95,
        }.get(band_quality, 0.5)

        rarity_penalty = {
            "common": 0.0,
            "uncommon": -0.05,
            "rare": -0.1,
            "epic": -0.2,
            "legendary": -0.3,
        }.get(drop_rarity, 0.0)

        return max(0.1, min(1.0, base + rarity_penalty))


@dataclass
class RewardOutcome:
    """Results of evaluating an encounter."""

    context: EncounterContext
    score: RewardScore
    band: RewardBand
    xp_awarded: int
    loot: List[Dict[str, Any]]
    unique_unlocks: List[str]
    fairness_index: float
    breakdown: Dict[str, Any]

    def apply_to_progression(self, progression: CharacterProgressionEngine):
        """Propagate XP awards into the progression engine."""
        progression.award_xp(self.xp_awarded, f"Encounter: {self.context.name} ({self.band.name})")

        # Bonus XP for connected objectives
        if self.context.quest_completed:
            progression.award_xp(2, "Quest completion bonus")
        if self.context.exploration_milestone:
            progression.award_xp(1, "Exploration milestone")
        if self.context.boss_defeated:
            progression.award_xp(3, "Boss defeated")


class RewardAnalytics:
    """Simple analytics for reward fairness and tuning."""

    def __init__(self):
        self._history: List[Dict[str, Any]] = []
        self._band_counts: Dict[str, int] = {band.name: 0 for band in REWARD_BANDS}

    def record(self, outcome: RewardOutcome):
        """Record a reward result for later analysis."""
        self._history.append({
            "score": outcome.score.total,
            "band": outcome.band.name,
            "xp": outcome.xp_awarded,
            "loot_count": len(outcome.loot),
            "streak": outcome.context.streak_count,
            "fairness_index": outcome.fairness_index,
        })
        self._band_counts[outcome.band.name] += 1

    def fairness_snapshot(self) -> Dict[str, Any]:
        """Compute fairness metrics for the current playtest session."""
        if not self._history:
            return {"fairness_index": 1.0, "mean_xp": 0, "band_mix": self._band_counts}

        mean_xp = sum(h["xp"] for h in self._history) / len(self._history)
        mean_score = sum(h["score"] for h in self._history) / len(self._history)
        fairness_index = mean_xp / max(mean_score, 1)
        return {
            "fairness_index": round(fairness_index, 2),
            "mean_xp": round(mean_xp, 2),
            "band_mix": dict(self._band_counts),
        }

    def tuning_recommendations(self) -> List[str]:
        """Suggest tuning actions based on fairness."""
        snapshot = self.fairness_snapshot()
        recommendations = []

        if snapshot["fairness_index"] < 0.6:
            recommendations.append("XP feels stingy; consider widening Heroic/Mythic XP ranges.")
        elif snapshot["fairness_index"] > 1.2:
            recommendations.append("XP feels generous; tighten Mythic XP or reduce streak bonuses.")

        band_mix = snapshot.get("band_mix", {})
        if band_mix.get("Mythic", 0) == 0:
            recommendations.append("No Mythic rewards seen; verify boss and streak scoring thresholds.")
        if band_mix.get("Routine", 0) > band_mix.get("Heroic", 0):
            recommendations.append("Players are stuck in Routine bands; ease rarity bonuses or quest hooks.")

        if not recommendations:
            recommendations.append("Rewards look balanced. Continue current tuning.")

        return recommendations


class RewardEngine:
    """Orchestrates encounter scoring and rewards."""

    def __init__(self, progression: Optional[CharacterProgressionEngine] = None):
        self.progression = progression
        self.loot_table = LootTable()
        self.analytics = RewardAnalytics()

    def score_encounter(self, context: EncounterContext) -> RewardScore:
        """Score an encounter based on difficulty, rarity, and objectives."""
        base = max(0.0, min(context.difficulty_rating, 10)) * 8
        rarity = 10 * RARITY_WEIGHTS.get(context.rarity, 1.0)
        streak = min(context.streak_count * 2.5, 15)
        objective = 0.0
        if context.quest_completed:
            objective += 8 if context.quest_rank == "epic" else 5
        if context.exploration_milestone:
            objective += 4
        boss = 12 if context.boss_defeated or context.encounter_type == "boss" else 0

        return RewardScore(
            base_difficulty=round(base, 2),
            rarity_bonus=round(rarity, 2),
            streak_bonus=round(streak, 2),
            objective_bonus=round(objective, 2),
            boss_bonus=round(boss, 2),
        )

    def map_to_band(self, score: float) -> RewardBand:
        """Map a numeric score to the configured reward band."""
        for band in REWARD_BANDS:
            if band.score_range[0] <= score < band.score_range[1]:
                return band
        return REWARD_BANDS[-1]

    def evaluate(self, context: EncounterContext) -> RewardOutcome:
        """Evaluate rewards for an encounter."""
        score = self.score_encounter(context)
        band = self.map_to_band(score.total)
        xp_award = band.choose_xp(score.total)
        loot = self.loot_table.generate_loot(score.total, band, context.streak_count)
        unique_unlocks = [drop["unique_unlock"] for drop in loot if "unique_unlock" in drop]

        fairness = xp_award / max(score.total, 1)
        breakdown = {
            "base": score.base_difficulty,
            "rarity": score.rarity_bonus,
            "streak": score.streak_bonus,
            "objective": score.objective_bonus,
            "boss": score.boss_bonus,
        }

        outcome = RewardOutcome(
            context=context,
            score=score,
            band=band,
            xp_awarded=xp_award,
            loot=loot,
            unique_unlocks=unique_unlocks,
            fairness_index=round(fairness, 2),
            breakdown=breakdown,
        )

        if self.progression:
            outcome.apply_to_progression(self.progression)

        self.analytics.record(outcome)
        return outcome

    def quest_completion_reward(self, quest_name: str, quest_rank: str = "dangerous") -> RewardOutcome:
        """Shortcut for resolving rewards when a quest is finished."""
        context = EncounterContext(
            name=f"Quest: {quest_name}",
            difficulty_rating=8 if quest_rank in {"extreme", "epic"} else 6,
            rarity=EncounterRarity.RARE if quest_rank in {"formidable", "extreme"} else EncounterRarity.UNCOMMON,
            encounter_type="quest",
            quest_completed=True,
            quest_rank=quest_rank,
        )
        return self.evaluate(context)

    def exploration_milestone_reward(self, location_name: str, streak: int = 0) -> RewardOutcome:
        """Reward for significant exploration progress."""
        context = EncounterContext(
            name=f"Discovery: {location_name}",
            difficulty_rating=5,
            rarity=EncounterRarity.UNCOMMON,
            encounter_type="exploration",
            exploration_milestone=True,
            streak_count=streak,
        )
        return self.evaluate(context)

    def boss_defeat_reward(self, boss_name: str, difficulty_rating: float = 9.5, streak: int = 0) -> RewardOutcome:
        """Reward for defeating a boss encounter."""
        context = EncounterContext(
            name=f"Boss: {boss_name}",
            difficulty_rating=difficulty_rating,
            rarity=EncounterRarity.LEGENDARY,
            encounter_type="boss",
            boss_defeated=True,
            streak_count=streak,
        )
        outcome = self.evaluate(context)
        telemetry.emit_boss_kill(
            boss_name,
            difficulty_rating,
            session_id=None,
            rewards={"xp": outcome.xp_awarded, "band": outcome.band.name},
        )
        return outcome
