"""Prompt construction utilities for Datasworn narration.

This module centralizes how system, context, and user messages are
constructed so different LLM providers receive the same structure.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
import socket
from typing import Callable, Dict, List, Iterable, Optional

from src.cache import PromptResultCache
from src.feedback_learning import record_prompt_metric
from src.llm_provider import LLMCapabilities, LLMProvider


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
class CapabilityRequest:
    """Request describing the prompt needs for provider selection."""

    min_output_tokens: int
    required_safety: Iterable[str] = field(default_factory=list)
    max_cost_per_1k_tokens: Optional[float] = None
    allow_streaming: bool = True

    def is_satisfied_by(self, capabilities: LLMCapabilities) -> bool:
        if capabilities.max_output_tokens < self.min_output_tokens:
            return False
        if self.max_cost_per_1k_tokens is not None and capabilities.cost_per_1k_tokens > self.max_cost_per_1k_tokens:
            return False
        if self.allow_streaming and not capabilities.supports_streaming:
            return False

        required = set(self.required_safety)
        if required and not required.issubset(set(capabilities.safety_features)):
            return False
        return True


@dataclass
class CircuitBreaker:
    """Simple circuit breaker that also reacts to high latency."""

    max_failures: int = 2
    reset_timeout: float = 30.0
    high_latency_threshold: float = 3.0
    failures: int = 0
    last_failure_time: float = 0.0

    def allow_request(self) -> bool:
        if self.failures < self.max_failures:
            return True

        if (time.time() - self.last_failure_time) > self.reset_timeout:
            self.failures = 0
            return True
        return False

    def record_success(self):
        self.failures = 0

    def record_failure(self, latency: float, reason: str):
        self.failures += 1
        self.last_failure_time = time.time()
        record_prompt_metric(
            "provider_failure",
            provider=None,
            metadata={"latency_ms": int(latency * 1000), "reason": reason},
        )


_CIRCUIT_BREAKERS: Dict[str, CircuitBreaker] = {}


def reset_circuit_breakers():
    """Clear breaker state (primarily for tests)."""

    _CIRCUIT_BREAKERS.clear()


def _get_breaker(name: str, *, config: CircuitBreaker | None = None) -> CircuitBreaker:
    breaker = _CIRCUIT_BREAKERS.get(name)
    if breaker is None:
        breaker = CircuitBreaker()
        _CIRCUIT_BREAKERS[name] = breaker

    if config:
        breaker.max_failures = config.max_failures
        breaker.reset_timeout = config.reset_timeout
        breaker.high_latency_threshold = config.high_latency_threshold
    return breaker


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


def detect_connectivity(timeout: float = 1.5) -> bool:
    """Return True when outbound connectivity appears available."""

    try:
        with socket.create_connection(("8.8.8.8", 53), timeout=timeout):
            return True
    except OSError:
        return False


def _deterministic_local_response(user_prompt: str, context: PromptContext) -> str:
    context_block = context.formatted_context()
    stitched_context = context_block.replace("\n\n", " | ") if context_block else "no recent context"
    return (
        "[offline narrator] Using local guidance based on recent notes. "
        f"Context: {stitched_context}. "
        f"Player prompt: {user_prompt.strip()}"
    )


def execute_prompt_with_fallback(
    user_prompt: str,
    *,
    context: PromptContext | None = None,
    providers: List[LLMProvider],
    capability_request: CapabilityRequest,
    temperature: float = 0.7,
    max_tokens: int = 512,
    stream: bool = False,
    max_retries: int = 2,
    breaker_config: CircuitBreaker | None = None,
    prompt_cache: PromptResultCache | None = None,
    connectivity_check: Callable[[], bool] | None = None,
) -> str:
    """Execute a prompt with retries and capability-aware fallback."""

    if not providers:
        raise ValueError("At least one provider is required")

    eligible: List[LLMProvider] = [
        provider for provider in providers if capability_request.is_satisfied_by(provider.capabilities())
    ]
    if not eligible:
        raise RuntimeError("No providers satisfy the requested capabilities")

    context = context or PromptContext()
    messages = build_narrator_messages(user_prompt, context)
    cache = prompt_cache or PromptResultCache()
    cached = cache.get_prompt(user_prompt, context)
    if cached:
        record_prompt_metric("prompt_cache_hit", provider=None, metadata={"source": "prompt"})
        return cached

    checker = connectivity_check or detect_connectivity
    if not checker():
        fallback = _deterministic_local_response(user_prompt, context)
        cache.store_prompt(user_prompt, context, fallback)
        record_prompt_metric("connectivity_offline", provider=None, metadata={"source": "local_fallback"})
        return fallback

    last_error: Exception | None = None

    for provider in eligible:
        breaker = _get_breaker(provider.name, config=breaker_config)
        if not breaker.allow_request():
            record_prompt_metric("circuit_open", provider.name, metadata={"provider": provider.name})
            continue

        for attempt in range(max_retries):
            start = time.perf_counter()
            try:
                response = provider.chat(
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream,
                )
                latency = time.perf_counter() - start

                if latency > breaker.high_latency_threshold:
                    breaker.record_failure(latency, "high_latency")
                    record_prompt_metric(
                        "fallback_due_to_latency",
                        provider.name,
                        metadata={"latency_ms": int(latency * 1000)},
                    )
                    break

                breaker.record_success()
                record_prompt_metric(
                    "provider_success",
                    provider.name,
                    metadata={"latency_ms": int(latency * 1000)},
                )
                final_response = _coerce_response(response)
                cache.store_prompt(user_prompt, context, final_response)
                return final_response
            except Exception as exc:  # noqa: PERF203 - controlled retries
                latency = time.perf_counter() - start
                breaker.record_failure(latency, str(exc))
                record_prompt_metric(
                    "provider_retry",
                    provider.name,
                    metadata={"attempt": attempt + 1, "error": str(exc)},
                )
                last_error = exc

        record_prompt_metric("provider_fallback", provider.name, metadata={"provider": provider.name})

    fallback = _deterministic_local_response(user_prompt, context)
    cache.store_prompt(user_prompt, context, fallback)
    record_prompt_metric(
        "provider_failure_fallback", provider=None, metadata={"error": str(last_error) if last_error else "unknown"}
    )
    return fallback


def _coerce_response(response: str | Iterable[str]) -> str:
    if isinstance(response, str):
        return response
    return "".join(response)
