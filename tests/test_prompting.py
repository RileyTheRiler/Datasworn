import pytest

from src.prompting import (
    PromptContext,
    SYSTEM_PROMPT,
    build_narrator_messages,
)


def test_context_format_includes_hooks():
    context = PromptContext(
        scene_summary="Derelict station shudders under half-power.",
        user_intent="Patch the torn hull and calm the crew.",
        move_outcome="Weak Hit on Face Danger (Edge)",
        oracle_results=["Space Sighting: Drifting wreck", "Action + Theme: Secure / Echo"],
        prior_exchanges=[{"role": "assistant", "content": "The bulkhead is failing."}],
    )

    messages = build_narrator_messages("Seal the breach before it vents.", context)

    # System + context + prior exchange + user prompt
    assert messages[0]["role"] == "system"
    assert SYSTEM_PROMPT in messages[0]["content"]

    context_message = messages[1]["content"]
    assert "[Scene]" in context_message
    assert "[Move Outcome]" in context_message
    assert "Datasworn" in context_message
    assert "[Oracle Insights]" in context_message
    assert "Recent Table Chat" in context_message

    assert messages[-2] == {"role": "assistant", "content": "The bulkhead is failing."}
    assert messages[-1]["content"].startswith("Seal the breach")


def test_provider_format_consistency():
    context = PromptContext(scene_summary="Calm corridor.")
    user_prompt = "Advance cautiously."

    providers = [None, "ollama", "Gemini", "custom"]
    outputs = [build_narrator_messages(user_prompt, context, provider=p) for p in providers]

    # All providers should receive the same structure and ordering.
    first_shape = [msg["role"] for msg in outputs[0]]
    for output in outputs[1:]:
        assert [msg["role"] for msg in output] == first_shape
        assert output[0]["content"] == SYSTEM_PROMPT
        assert "Calm corridor." in output[1]["content"]
        assert output[-1]["content"] == user_prompt.strip()


def test_context_handles_empty_sections():
    context = PromptContext()
    messages = build_narrator_messages("Describe the void.", context)

    # Only system and user messages should be present when context is empty.
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["content"] == "Describe the void."
