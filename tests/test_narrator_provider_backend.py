import builtins

from src.llm_provider import LLMProvider
from src.narrator import NarratorConfig, _get_provider


class DummyProvider(LLMProvider):
    def chat(self, messages, temperature=0.7, max_tokens=1024, stream=False):
        return "stub"

    def is_available(self) -> bool:  # pragma: no cover - trivial
        return True

    @property
    def name(self) -> str:  # pragma: no cover - trivial
        return "dummy"


def test_provider_selection_respects_config_backend(monkeypatch):
    calls = []

    def guarded_import(name, *args, **kwargs):
        if name == "ollama":
            raise AssertionError("Ollama import attempted despite using Gemini backend")
        return original_import(name, *args, **kwargs)

    def fake_get_llm_provider(provider_type=None, model=None, api_key=None):
        calls.append((provider_type, model, api_key))
        return DummyProvider()

    original_import = builtins.__import__
    monkeypatch.setattr(builtins, "__import__", guarded_import)
    monkeypatch.setattr("src.narrator.get_llm_provider", fake_get_llm_provider)

    config = NarratorConfig(backend="gemini", model="custom-model")
    provider = _get_provider(config)

    assert isinstance(provider, DummyProvider)
    assert calls == [("gemini", "custom-model", None)]
