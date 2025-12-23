"""Session persistence and isolation tests for the Gradio UI layer."""

from __future__ import annotations

from pathlib import Path

import pytest

import src.ui as ui


def _drain(generator):
    """Exhaust a generator and return its final yielded value."""

    last = None
    for last in generator:
        pass
    return last


def _stub_stream(*_, **__):
    yield "First chunk. "
    yield "Second chunk."


@pytest.fixture()
def session_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Provide an isolated session store for each test."""

    store = ui.SessionStore(tmp_path / "sessions.json")
    monkeypatch.setattr(ui, "SESSION_STORE", store)
    monkeypatch.setattr(ui, "generate_narrative_stream", _stub_stream)
    monkeypatch.setattr(ui, "check_provider_availability", lambda _config: (True, ""))
    return store


def test_sessions_are_isolated(session_store: ui.SessionStore):
    """Ensure two sessions keep independent chat and metadata."""

    # Create two separate sessions and characters.
    ui.create_character("Alpha", 2, 2, 2, 2, 2, session_id="session_alpha")
    ui.create_character("Beta", 2, 2, 2, 2, 2, session_id="session_beta")

    # Run interleaved interactions.
    alpha_history = session_store.load_session("session_alpha").chat_history
    beta_history = session_store.load_session("session_beta").chat_history

    _drain(ui.process_player_input("Explore derelict station", alpha_history, "session_alpha"))
    _drain(ui.process_player_input("Scan for signals", beta_history, "session_beta"))

    # Reload persisted sessions and verify isolation.
    alpha_session = session_store.load_session("session_alpha")
    beta_session = session_store.load_session("session_beta")

    assert len(alpha_session.chat_history) == 2
    assert len(beta_session.chat_history) == 2
    assert alpha_session.chat_history[0][0] == "System"
    assert beta_session.chat_history[0][0] == "System"
    assert alpha_session.chat_history[1][0] == "Explore derelict station"
    assert beta_session.chat_history[1][0] == "Scan for signals"

    data = session_store.path.read_text()
    assert "session_alpha" in data and "session_beta" in data


def test_approval_state_persists(session_store: ui.SessionStore):
    """Pending narrative and approval flags should survive reloads."""

    ui.create_character("Gamma", 2, 2, 2, 2, 2, session_id="session_gamma")
    history = session_store.load_session("session_gamma").chat_history

    # Produce a pending narrative that requires approval.
    _drain(ui.process_player_input("Chart a new course", history, "session_gamma"))
    pending_session = session_store.load_session("session_gamma")

    assert pending_session.awaiting_approval is True
    assert pending_session.pending_narrative.endswith("Second chunk.")

    # Accept and ensure the cleared state persists.
    ui.accept_narrative("session_gamma")
    cleared_session = session_store.load_session("session_gamma")

    assert cleared_session.awaiting_approval is False
    assert cleared_session.pending_narrative == ""
