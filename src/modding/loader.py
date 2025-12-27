"""Sandboxed loader for third-party mods/plugins.

Plugins are executed in a subprocess with a restricted set of builtins
and whitelisted imports to reduce the risk of malicious behavior.
"""
from __future__ import annotations

import ast
import builtins
import multiprocessing as mp
try:  # Unix-only resource controls
    import resource
except ImportError:  # pragma: no cover - non-POSIX environments
    resource = None
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from src.security_utils import sanitize_relative_path, validate_payload_size


ALLOWED_IMPORTS = {"math", "random", "statistics"}
SAFE_BUILTINS = {
    "abs",
    "all",
    "any",
    "bool",
    "dict",
    "enumerate",
    "float",
    "int",
    "len",
    "list",
    "max",
    "min",
    "pow",
    "range",
    "round",
    "set",
    "sorted",
    "str",
    "sum",
    "tuple",
    "zip",
}


class SandboxError(RuntimeError):
    """Base error for sandbox failures."""


class PluginTimeout(SandboxError):
    """Raised when plugin execution exceeds the configured timeout."""


@dataclass
class SandboxedResult:
    """Result from sandboxed execution."""

    output: Any
    logs: list[str]


class SandboxedModLoader:
    """Load and execute plugins with strict guards."""

    def __init__(
        self,
        base_dir: Path,
        allowed_imports: Iterable[str] | None = None,
        timeout_s: float = 1.0,
        memory_limit_mb: int = 128,
    ):
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.allowed_imports = set(allowed_imports) if allowed_imports else set(ALLOWED_IMPORTS)
        self.timeout_s = timeout_s
        self.memory_limit_mb = memory_limit_mb

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def execute(self, relative_path: str, entrypoint: str, payload: dict[str, Any] | None = None) -> SandboxedResult:
        payload = payload or {}
        source = self._load_and_validate(relative_path)
        return self._execute_source(source, entrypoint, payload)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _load_and_validate(self, relative_path: str) -> str:
        plugin_path = sanitize_relative_path(self.base_dir, relative_path)
        if not plugin_path.exists():
            raise FileNotFoundError(f"Plugin not found: {plugin_path}")

        source = plugin_path.read_text(encoding="utf-8")
        validate_payload_size(source, self.memory_limit_mb * 1024 * 1024)
        self._validate_imports(source)
        return source

    def _validate_imports(self, source: str) -> None:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root not in self.allowed_imports:
                        raise SandboxError(f"Import of '{alias.name}' is not permitted")

    def _execute_source(self, source: str, entrypoint: str, payload: dict[str, Any]) -> SandboxedResult:
        queue: mp.Queue = mp.Queue()
        proc = mp.Process(
            target=_sandbox_worker,
            args=(source, entrypoint, payload, self.allowed_imports, self.memory_limit_mb, queue),
        )
        proc.start()
        proc.join(self.timeout_s)

        if proc.is_alive():
            proc.terminate()
            proc.join()
            raise PluginTimeout(f"Plugin '{entrypoint}' exceeded {self.timeout_s} seconds")

        if queue.empty():
            raise SandboxError("Plugin did not return a result")

        success, content = queue.get_nowait()
        if not success:
            raise SandboxError(content)
        return SandboxedResult(output=content["result"], logs=content.get("logs", []))


def _sandbox_worker(
    source: str,
    entrypoint: str,
    payload: dict[str, Any],
    allowed_imports: set[str],
    memory_limit_mb: int,
    queue: mp.Queue,
) -> None:
    """Execute plugin code inside a constrained subprocess."""

    def limited_import(name: str, globals=None, locals=None, fromlist=None, level=0):  # type: ignore[override]
        root = name.split(".")[0]
        if root not in allowed_imports:
            raise ImportError(f"Import of '{name}' is not allowed")
        return __import__(name, globals, locals, fromlist, level)

    safe_builtins = {key: getattr(builtins, key) for key in SAFE_BUILTINS if hasattr(builtins, key)}
    safe_builtins["__import__"] = limited_import

    if resource is not None:
        try:
            memory_bytes = memory_limit_mb * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        except (AttributeError, ValueError, resource.error):
            pass

    sandbox_globals: dict[str, Any] = {"__builtins__": safe_builtins, "logs": []}

    try:
        exec(compile(source, "<plugin>", "exec"), sandbox_globals)
        func = sandbox_globals.get(entrypoint)
        if not callable(func):
            raise SandboxError(f"Entrypoint '{entrypoint}' not found or not callable")
        result = func(payload)
        queue.put((True, {"result": result, "logs": sandbox_globals.get("logs", [])}))
    except Exception as exc:  # pragma: no cover - propagated to parent
        queue.put((False, str(exc)))
