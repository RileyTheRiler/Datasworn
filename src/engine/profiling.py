"""Lightweight profiling helpers for engine update loops.

These helpers are intentionally allocation-friendly so they can wrap tight
per-frame loops without introducing noticeable overhead. They are used by
engine systems to track per-section timing and to emit summaries for perf
tests and flamegraph generation.
"""

from __future__ import annotations

from collections import deque
from contextlib import contextmanager, nullcontext
from statistics import mean
from time import perf_counter
from typing import Deque, Iterable


class FrameProfiler:
    """Aggregates spans from frame/update loops.

    The profiler stores a bounded history of span durations (in seconds) per
    label to keep memory growth under control.
    """

    def __init__(self, max_samples: int = 240) -> None:
        self.max_samples = max_samples
        self._samples: dict[str, Deque[float]] = {}

    @contextmanager
    def span(self, label: str):
        """Context manager that records a timed span for the given label."""

        start = perf_counter()
        try:
            yield
        finally:
            duration = perf_counter() - start
            bucket = self._samples.setdefault(label, deque(maxlen=self.max_samples))
            bucket.append(duration)

    def maybe_span(self, label: str | None):
        """Return a span context if a label is provided, else a no-op."""

        if label is None:
            return nullcontext()
        return self.span(label)

    def _percentile(self, values: list[float], percentile: float) -> float:
        if not values:
            return 0.0
        values = sorted(values)
        k = max(0, min(len(values) - 1, int(len(values) * percentile)))
        return values[k]

    def summary(self) -> dict[str, dict[str, float]]:
        """Return aggregate metrics in milliseconds for each recorded label."""

        results: dict[str, dict[str, float]] = {}
        for label, samples in self._samples.items():
            if not samples:
                continue
            values_ms = [s * 1000.0 for s in samples]
            results[label] = {
                "count": float(len(values_ms)),
                "avg_ms": mean(values_ms),
                "max_ms": max(values_ms),
                "p95_ms": self._percentile(values_ms, 0.95),
            }
        return results

    def flatten_spans(self) -> Iterable[tuple[str, float]]:
        """Iterate through recorded spans as (label, duration_seconds)."""

        for label, samples in self._samples.items():
            for sample in samples:
                yield label, sample
