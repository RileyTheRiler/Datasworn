import pytest

from src.cache import PromptResultCache
from src.llm_provider import LLMCapabilities, LLMProvider
from src.prompting import CapabilityRequest, PromptContext, execute_prompt_with_fallback, reset_circuit_breakers


class FailingProvider(LLMProvider):
    def __init__(self, name="failing"):
        self._name = name

    def chat(self, messages, temperature=0.7, max_tokens=1024, stream=False):
        raise ConnectionError("network unreachable")

    def is_available(self) -> bool:
        return False

    def capabilities(self) -> LLMCapabilities:
        return LLMCapabilities(
            max_output_tokens=1024, safety_features=["none"], cost_per_1k_tokens=0.0, supports_streaming=False
        )

    @property
    def name(self) -> str:
        return self._name


class EchoProvider(LLMProvider):
    def __init__(self, name="echo"):
        self._name = name

    def chat(self, messages, temperature=0.7, max_tokens=1024, stream=False):
        return "|".join(m["content"] for m in messages if m.get("content"))

    def is_available(self) -> bool:
        return True

    def capabilities(self) -> LLMCapabilities:
        return LLMCapabilities(
            max_output_tokens=1024, safety_features=["none"], cost_per_1k_tokens=0.0, supports_streaming=False
        )

    @property
    def name(self) -> str:
        return self._name


@pytest.fixture(autouse=True)
def reset_breakers():
    reset_circuit_breakers()
    yield
    reset_circuit_breakers()


def test_offline_fallback_avoids_crash(tmp_path):
    context = PromptContext(scene_summary="Silent ship")
    cache = PromptResultCache(directory=tmp_path)
    response = execute_prompt_with_fallback(
        "Proceed cautiously",
        context=context,
        providers=[FailingProvider()],
        capability_request=CapabilityRequest(min_output_tokens=128, allow_streaming=False),
        prompt_cache=cache,
        connectivity_check=lambda: False,
    )

    assert "offline narrator" in response
    assert "Proceed cautiously" in response


def test_cached_response_used_when_available(tmp_path):
    context = PromptContext(scene_summary="Reactor core")
    cache = PromptResultCache(directory=tmp_path)
    response = execute_prompt_with_fallback(
        "Stabilize output",
        context=context,
        providers=[FailingProvider()],
        capability_request=CapabilityRequest(min_output_tokens=128, allow_streaming=False),
        prompt_cache=cache,
        connectivity_check=lambda: False,
    )

    # Second call should return identical cached value even if connectivity is restored
    second = execute_prompt_with_fallback(
        "Stabilize output",
        context=context,
        providers=[EchoProvider()],
        capability_request=CapabilityRequest(min_output_tokens=128, allow_streaming=False),
        prompt_cache=cache,
        connectivity_check=lambda: True,
    )

    assert response == second


def test_provider_success_stores_cache(tmp_path):
    context = PromptContext(scene_summary="Airlock")
    cache = PromptResultCache(directory=tmp_path)
    result = execute_prompt_with_fallback(
        "Cycle the chamber",
        context=context,
        providers=[EchoProvider()],
        capability_request=CapabilityRequest(min_output_tokens=64, allow_streaming=False),
        prompt_cache=cache,
        connectivity_check=lambda: True,
    )

    assert "Cycle the chamber" in result
    # Verify cached retrieval
    again = execute_prompt_with_fallback(
        "Cycle the chamber",
        context=context,
        providers=[EchoProvider()],
        capability_request=CapabilityRequest(min_output_tokens=64, allow_streaming=False),
        prompt_cache=cache,
        connectivity_check=lambda: True,
    )
    assert result == again
