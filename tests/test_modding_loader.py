import textwrap

import pytest

from src.modding.loader import PluginTimeout, SandboxError, SandboxedModLoader


def test_rejects_disallowed_import(tmp_path):
    plugin = tmp_path / "unsafe.py"
    plugin.write_text(
        textwrap.dedent(
            """
            import os

            def run(payload):
                return os.listdir("/")
            """
        )
    )
    loader = SandboxedModLoader(tmp_path, timeout_s=0.5)

    with pytest.raises(SandboxError):
        loader.execute("unsafe.py", "run", {})


def test_executes_allowed_plugin(tmp_path):
    plugin = tmp_path / "safe.py"
    plugin.write_text(
        textwrap.dedent(
            """
            import math

            def run(payload):
                return math.sqrt(payload.get("value", 0))
            """
        )
    )
    loader = SandboxedModLoader(tmp_path)

    result = loader.execute("safe.py", "run", {"value": 16})
    assert result.output == 4


def test_plugin_timeout(tmp_path):
    plugin = tmp_path / "hang.py"
    plugin.write_text(
        textwrap.dedent(
            """
            def run(payload):
                while True:
                    pass
            """
        )
    )
    loader = SandboxedModLoader(tmp_path, timeout_s=0.2)

    with pytest.raises(PluginTimeout):
        loader.execute("hang.py", "run", {})
