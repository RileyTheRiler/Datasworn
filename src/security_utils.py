"""Security utilities for file/path handling and payload validation."""
from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

SAFE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+$")


def sanitize_filename(name: str) -> str:
    """Validate slot/file names to prevent traversal or injection."""
    cleaned = name.strip()
    if not cleaned or not SAFE_NAME_PATTERN.fullmatch(cleaned):
        raise ValueError("Names may only include alphanumerics, dashes, underscores, and periods.")
    return cleaned


def sanitize_relative_path(base: Path, candidate: str | os.PathLike[str]) -> Path:
    """Resolve a candidate path under ``base`` and block escaping."""
    base_path = Path(base).expanduser().resolve()
    candidate_path = (base_path / Path(candidate)).resolve()
    try:
        candidate_path.relative_to(base_path)
    except ValueError as exc:  # pragma: no cover - safety branch
        raise ValueError("Path traversal detected") from exc
    return candidate_path


def validate_payload_size(payload: Any, max_bytes: int) -> int:
    """Ensure payloads do not exceed ``max_bytes`` when serialized."""
    if max_bytes <= 0:
        raise ValueError("max_bytes must be positive")

    if isinstance(payload, bytes):
        size = len(payload)
    else:
        text = payload if isinstance(payload, str) else str(payload)
        size = len(text.encode("utf-8"))

    if size > max_bytes:
        raise ValueError(f"Payload exceeds maximum size of {max_bytes} bytes")
    return size
