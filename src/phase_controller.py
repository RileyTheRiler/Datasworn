"""Simple phase controller used to emit safe boundary callbacks."""

from __future__ import annotations

from typing import Callable, List, Any


class PhaseController:
    """Dispatches notifications when narrative/game phases complete."""

    def __init__(self) -> None:
        self._boundary_listeners: List[Callable[[str], Any]] = []

    def add_boundary_listener(self, callback: Callable[[str], Any]) -> None:
        self._boundary_listeners.append(callback)

    def complete_phase(self, phase_name: str, **kwargs: Any) -> None:
        """Notify listeners that a phase boundary has been reached."""
        for listener in list(self._boundary_listeners):
            listener(phase_name, **kwargs)
