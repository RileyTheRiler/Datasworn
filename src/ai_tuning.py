"""
Designer-facing AI tuning controls.

This module surfaces perception ranges, confidence thresholds,
hallucination guardrails, and personality presets that other systems can
consume without digging through internal classes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from .personality import OCEANProfile


@dataclass
class PerceptionConfig:
    """How far and how confidently actors notice things."""

    sight_range_meters: float = 18.0
    hearing_range_meters: float = 12.0
    peripheral_awareness: float = 0.4  # 0-1 sensitivity to side threats
    evidence_persistence_minutes: int = 8

    def to_context(self) -> dict:
        """Return a lightweight context blob for utility AI or director hooks."""
        return {
            "perception": {
                "sight": self.sight_range_meters,
                "hearing": self.hearing_range_meters,
                "peripheral_awareness": self.peripheral_awareness,
                "evidence_persistence_minutes": self.evidence_persistence_minutes,
            }
        }


@dataclass
class ConfidenceThresholds:
    """Decision gates for what the AI will act on or surface to players."""

    accept_environmental_fact: float = 0.35
    act_on_goal: float = 0.6
    warn_party: float = 0.5
    escalate_security: float = 0.75

    def gate(self, confidence: float, action: str) -> bool:
        """Simple policy check for a requested action string."""
        thresholds = {
            "accept_fact": self.accept_environmental_fact,
            "share": self.warn_party,
            "pursue_goal": self.act_on_goal,
            "escalate": self.escalate_security,
        }
        required = thresholds.get(action, self.accept_environmental_fact)
        return confidence >= required


@dataclass
class HallucinationPolicy:
    """Controls when hallucinations may be injected into play."""

    min_sanity: float = 0.15
    reject_below_confidence: float = 0.55
    max_per_scene: int = 1
    require_director_approval: bool = True

    def allows(
        self,
        *,
        sanity: float,
        hallucinations_this_scene: int,
        hallucination_confidence: float,
        director_approved: bool = False,
    ) -> bool:
        """Return whether a hallucination should be allowed to surface."""
        if sanity > self.min_sanity and not self.require_director_approval:
            # Stable enough that hallucinations are optional; allow if confidence passes.
            return hallucination_confidence >= self.reject_below_confidence

        if sanity < self.min_sanity:
            if hallucinations_this_scene >= self.max_per_scene:
                return False
            if hallucination_confidence < self.reject_below_confidence:
                return False
            if self.require_director_approval and not director_approved:
                return False
            return True

        return False


@dataclass
class DesignerProfile:
    """Bundle of personality traits with reasoning weights."""

    id: str
    label: str
    description: str
    ocean: OCEANProfile
    reasoning_weights: Dict[str, float] = field(default_factory=dict)

    def as_prompt(self) -> str:
        """Format as a concise tag for downstream LLM prompts."""
        weights = ", ".join(
            f"{k}: {v:.1f}" for k, v in sorted(self.reasoning_weights.items())
        )
        return (
            f"[{self.label}] {self.description}\n"
            f"OCEAN: {self.ocean.to_dict()}\n"
            f"Reasoning weights → {weights}"
        )


DESIGNER_PRESETS: dict[str, DesignerProfile] = {
    "stealthy_guard": DesignerProfile(
        id="stealthy_guard",
        label="Stealthy Guard",
        description="Disciplined lookout who favors shadows and pattern recognition.",
        ocean=OCEANProfile(
            openness=0.35,
            conscientiousness=0.8,
            extraversion=0.25,
            agreeableness=0.45,
            neuroticism=0.35,
        ),
        reasoning_weights={
            "caution": 0.9,
            "pattern_matching": 0.85,
            "empathy": 0.2,
            "initiative": 0.55,
        },
    ),
    "friendly_merchant": DesignerProfile(
        id="friendly_merchant",
        label="Friendly Merchant",
        description="Talkative dealmaker who trusts social proof over threats.",
        ocean=OCEANProfile(
            openness=0.65,
            conscientiousness=0.55,
            extraversion=0.8,
            agreeableness=0.85,
            neuroticism=0.25,
        ),
        reasoning_weights={
            "empathy": 0.85,
            "risk_tolerance": 0.35,
            "greed": 0.65,
            "relationship_weight": 0.75,
        },
    ),
    "anxious_survivor": DesignerProfile(
        id="anxious_survivor",
        label="Anxious Survivor",
        description="Jittery loner who double-checks every corridor and rumor.",
        ocean=OCEANProfile(
            openness=0.45,
            conscientiousness=0.6,
            extraversion=0.2,
            agreeableness=0.4,
            neuroticism=0.8,
        ),
        reasoning_weights={
            "caution": 0.95,
            "resource_hoarding": 0.7,
            "trust": 0.2,
            "escape_bias": 0.8,
        },
    ),
}
