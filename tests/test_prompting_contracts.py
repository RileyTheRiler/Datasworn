import time

import pytest

from src.feedback_learning import clear_prompt_metrics, recent_prompt_metrics
from src.llm_provider import LLMCapabilities, LLMProvider
from src.prompting import (
    CapabilityRequest,
    CircuitBreaker,
    PromptContext,
    build_narrator_messages,
    execute_prompt_with_fallback,
    reset_circuit_breakers,
)


class StubProvider(LLMProvider):
    def __init__(self, name: str, capabilities: LLMCapabilities, delay: float = 0.0, fail_first: int = 0):
        self._name = name
        self._capabilities = capabilities
        self._delay = delay
        self._fail_first = fail_first
        self.calls = 0
        self.messages = None

    def chat(self, messages, temperature=0.7, max_tokens=1024, stream=False):  # noqa: ARG002
        self.calls += 1
        self.messages = messages
        if self.calls <= self._fail_first:
            raise RuntimeError(f"{self._name} failed intentionally")
        if self._delay:
            time.sleep(self._delay)
        return f"{self._name}:{messages[-1]['content']}"

    def is_available(self) -> bool:
        return True

    @property
    def name(self) -> str:
        return self._name

    def capabilities(self) -> LLMCapabilities:
        return self._capabilities


def setup_function(_function):
    reset_circuit_breakers()
    clear_prompt_metrics()


def test_prompt_construction_deterministic():
    capability = LLMCapabilities(max_output_tokens=512, safety_features=["local_execution"], cost_per_1k_tokens=0)
    provider = StubProvider("deterministic", capability)
    context = PromptContext(scene_summary="Steady corridors", prior_exchanges=[{"role": "assistant", "content": "Echo."}])
    request = CapabilityRequest(min_output_tokens=128, required_safety=["local_execution"])

    response = execute_prompt_with_fallback(
        "Proceed.",
        context=context,
        providers=[provider],
        capability_request=request,
        breaker_config=CircuitBreaker(high_latency_threshold=1.0),
    )

    expected_messages = build_narrator_messages("Proceed.", context)
    assert provider.messages == expected_messages
    assert response.startswith("deterministic:Proceed.")


def test_latency_triggers_fallback_selection():
    slow_capability = LLMCapabilities(max_output_tokens=1024, safety_features=["moderation"], cost_per_1k_tokens=0.02)
    fast_capability = LLMCapabilities(max_output_tokens=1024, safety_features=["moderation"], cost_per_1k_tokens=0.02)

    slow_provider = StubProvider("slow", slow_capability, delay=0.05)
    fast_provider = StubProvider("fast", fast_capability)
    request = CapabilityRequest(min_output_tokens=256, required_safety=["moderation"])

    response = execute_prompt_with_fallback(
        "Rush the blockade.",
        providers=[slow_provider, fast_provider],
        capability_request=request,
        breaker_config=CircuitBreaker(max_failures=1, high_latency_threshold=0.01),
    )

    assert response.startswith("fast:")
    metrics = recent_prompt_metrics()
    assert any(m["event"] == "fallback_due_to_latency" and m["provider"] == "slow" for m in metrics)


def test_capability_filtering_prefers_suitable_provider():
    weak_capability = LLMCapabilities(max_output_tokens=64, safety_features=[], cost_per_1k_tokens=0)
    strong_capability = LLMCapabilities(max_output_tokens=2048, safety_features=["local_execution"], cost_per_1k_tokens=0)

    weak = StubProvider("weak", weak_capability)
    strong = StubProvider("strong", strong_capability)
    request = CapabilityRequest(min_output_tokens=128, required_safety=["local_execution"])

    response = execute_prompt_with_fallback(
        "Chart a safe path.",
        providers=[weak, strong],
        capability_request=request,
    )

    assert response.startswith("strong:")
    assert weak.calls == 0
