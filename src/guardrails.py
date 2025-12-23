"""
Guardrail utilities for narrative generation.

This module provides lightweight safety layers:
- Context packet assembly from known facts.
- Prompt guardrails that constrain content to verified information.
- Post-generation verification to flag unsupported statements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List
import re


DEFAULT_WHITELIST = {
    "forge",
    "ironsworn",
    "starforged",
    "ship",
    "station",
    "sector",
    "crew",
    "void",
    "drift",
    "hull",
    "airlock",
}

DEFAULT_BANNED_TOPICS = {
    "language model",
    "llm",
    "artificial intelligence",
    "computer program",
    "out-of-character",
    "fourth wall",
    "breaking character",
}


@dataclass
class GuardrailFactStore:
    """Holds high-confidence facts used to constrain generation."""

    high_confidence_facts: List[str] = field(default_factory=list)
    current_goal: str = ""
    emotional_state: str = ""
    personality_tone: str = ""
    whitelist_concepts: set[str] = field(default_factory=lambda: set(DEFAULT_WHITELIST))
    banned_topics: set[str] = field(default_factory=lambda: set(DEFAULT_BANNED_TOPICS))

    def build_context_packet(self) -> str:
        """Assemble a structured context packet for prompts."""
        lines = ["[Context packet]", "High-confidence facts:"]

        facts = [f for f in self.high_confidence_facts if f]
        if facts:
            for fact in facts:
                lines.append(f"- {fact}")
        else:
            lines.append("- No stored facts. Keep responses minimal and cautious.")

        if self.current_goal:
            lines.append(f"Current goal: {self.current_goal}")
        if self.emotional_state:
            lines.append(f"Emotional state: {self.emotional_state}")
        if self.personality_tone:
            lines.append(f"Personality tone: {self.personality_tone}")

        return "\n".join(lines)

    def guardrail_rules(self) -> str:
        """Guardrail instructions for LLM prompts."""
        rules = [
            "[Guardrails]",
            "- Refuse to mention unseen or unverified information.",
            "- If unsure, express uncertainty rather than inventing details.",
            "- Stay fully in-universe; block meta/4th-wall or out-of-setting references.",
            "- Content whitelist: " + ", ".join(sorted(self.whitelist_concepts)),
        ]
        return "\n".join(rules)

    def apply_content_filter(self, text: str) -> str:
        """Remove sentences that break immersion or use banned topics."""
        sentences = _split_sentences(text)
        filtered: List[str] = []

        for sentence in sentences:
            lowered = sentence.lower()
            if any(topic in lowered for topic in self.banned_topics):
                continue
            filtered.append(sentence.strip())

        return " ".join(filtered).strip()

    def is_sentence_supported(self, sentence: str) -> bool:
        """Check if a sentence is backed by a fact or whitelisted concept."""
        lowered = sentence.lower()
        for fact in self.high_confidence_facts:
            if fact and fact.lower() in lowered:
                return True

        return any(concept in lowered for concept in self.whitelist_concepts)

    def verify_output(self, text: str) -> str:
        """Flag sentences that lack support in the fact store."""
        filtered = self.apply_content_filter(text)
        if not filtered:
            return "[All content removed by guardrails. Provide a cautious, in-universe summary.]"

        sentences = _split_sentences(filtered)
        verified: List[str] = []

        for sentence in sentences:
            if not sentence.strip():
                continue
            if self.is_sentence_supported(sentence):
                verified.append(sentence.strip())
            else:
                verified.append(f"[Unverified—express uncertainty] {sentence.strip()}")

        return " ".join(verified).strip()


def _split_sentences(text: str) -> List[str]:
    """Lightweight sentence splitter for narrative prose."""
    return [s for s in re.split(r"(?<=[.!?])\s+", text) if s]


def build_guardrail_prompt(fact_store: GuardrailFactStore) -> str:
    """Combine the context packet and guardrail rules for prompt injection."""
    return f"{fact_store.build_context_packet()}\n\n{fact_store.guardrail_rules()}"


def sanitize_and_verify(text: str, fact_store: GuardrailFactStore) -> str:
    """Apply filtering and verification in a single helper."""
    return fact_store.verify_output(text)
