import pathlib

import pytest

from scripts.content_lint import lint_paths


FIXTURES = pathlib.Path(__file__).parent / "fixtures" / "content_lint"


@pytest.fixture(scope="module")
def lint_results():
    return lint_paths([FIXTURES])


def _messages_for(filename: str, issues):
    target = FIXTURES / filename
    return [issue for issue in issues if issue.path == target]


def test_flags_banned_phrases(lint_results):
    issues = _messages_for("banned_phrase.txt", lint_results)
    assert any("Banned phrase" in issue.message for issue in issues), "Expected banned phrase to be reported"


def test_flags_placeholders(lint_results):
    issues = _messages_for("placeholder.txt", lint_results)
    assert any("placeholder" in issue.message.lower() for issue in issues), "Expected placeholder to be reported"


def test_flags_mixed_voice(lint_results):
    issues = _messages_for("voice_mix.txt", lint_results)
    assert any("Mixed first- and second-person voice" == issue.message for issue in issues)


def test_flags_low_readability(lint_results):
    issues = _messages_for("readability.txt", lint_results)
    assert any("Low readability" in issue.message for issue in issues)
