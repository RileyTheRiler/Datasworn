"""Prompt construction utilities for Datasworn narration.

This module centralizes how system, context, and user messages are
constructed so different LLM providers receive the same structure.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


SYSTEM_PROMPT = (
    "You are the Oracle, an Ironsworn: Starforged narrator."
    " Keep responses immersive, concise, and in second person."
    " Stay within the game's science-fantasy tone and avoid modern"
    " Earth pop-culture or off-topic chatter."
    " Ground narrative beats in Datasworn move text when outcomes are"
    " provided, reflecting the listed Strong Hit / Weak Hit / Miss guidance."
    " Respect safety boundaries: no graphic content, keep tension but"
    " prioritize player comfort, and defer uncertain rules to the player."
    " Do not decide player actions; end scenes with a choice or consequence."
)


@dataclass
class PromptContext:
    """Context for building a narration prompt."""

    scene_summary: str = ""
    user_intent: str = ""
    move_outcome: str | None = None
    oracle_results: List[str] = field(default_factory=list)
    prior_exchanges: List[Dict[str, str]] = field(default_factory=list)

    def formatted_context(self) -> str:
        """Render context sections for inclusion in the prompt."""

        lines: List[str] = []

        if self.scene_summary.strip():
            lines.append("[Scene]\n" + self.scene_summary.strip())

        if self.user_intent.strip():
            lines.append("[Player Intent]\n" + self.user_intent.strip())

        if self.move_outcome:
            lines.append(
                "[Move Outcome]\n"
                "Use this Datasworn result to anchor tone and stakes: "
                f"{self.move_outcome.strip()}"
            )

        if self.oracle_results:
            oracle_block = "\n".join(f"- {result.strip()}" for result in self.oracle_results if result.strip())
            if oracle_block:
                lines.append("[Oracle Insights]\n" + oracle_block)

        if self.prior_exchanges:
            transcript = []
            for exchange in self.prior_exchanges:
                role = exchange.get("role", "user").strip() or "user"
                content = exchange.get("content", "").strip()
                if content:
                    transcript.append(f"{role.capitalize()}: {content}")
            if transcript:
                lines.append("[Recent Table Chat]\n" + "\n".join(transcript))

        return "\n\n".join(lines)


def build_narrator_messages(
    user_prompt: str,
    context: PromptContext | None = None,
    *,
    provider: str | None = None,
    system_prompt: str = SYSTEM_PROMPT,
) -> List[Dict[str, str]]:
    """Create structured chat messages for any provider.

    Args:
        user_prompt: The fresh player input or directive for the narrator.
        context: Optional narrative context payload.
        provider: Provider name for telemetry (formatting is consistent).
        system_prompt: Overrideable system prompt string.
    """

    context = context or PromptContext()
    messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]

    context_block = context.formatted_context()
    if context_block:
        messages.append({"role": "user", "content": context_block})

    # Preserve any prior exchanges as explicit message history so
    # providers with distinct role handling stay aligned.
    for exchange in context.prior_exchanges:
        role = exchange.get("role", "user") or "user"
        content = exchange.get("content", "")
        if content:
            messages.append({"role": role, "content": content})

    if user_prompt.strip():
        messages.append({"role": "user", "content": user_prompt.strip()})

    # Provider is currently informational; keeping the parameter ensures
    # future provider-specific tweaks don't alter ordering unexpectedly.
    _ = provider  # explicitly unused for clarity

    return messages
