"""Telemetry and monitoring utilities.

The module centralizes structured event emission, sampling, and export to a
variety of sinks so that instrumentation can be added without coupling game
logic to specific backends.
"""
from __future__ import annotations

import json
import random
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Protocol

from src.config import TelemetryConfig, config
from src.logging_config import get_logger

logger = get_logger("telemetry")


@dataclass
class TelemetryEvent:
    """A normalized telemetry envelope."""

    event_type: str
    timestamp: float
    session_id: Optional[str] = None
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload = {
            "event_type": self.event_type,
            "timestamp": datetime.fromtimestamp(self.timestamp).isoformat(),
            "session_id": self.session_id,
            "attributes": self.attributes,
        }
        return payload

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"))


class TelemetryExporter(Protocol):
    """Exporter interface used by telemetry sinks."""

    def export(self, event: TelemetryEvent) -> None:  # pragma: no cover - interface
        ...


class StdoutTelemetryExporter:
    """Emit telemetry as JSON to stdout for local debugging."""

    def export(self, event: TelemetryEvent) -> None:
        print(event.to_json())


class JsonTelemetryExporter:
    """Append telemetry events to a JSONL file."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def export(self, event: TelemetryEvent) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(event.to_json() + "\n")


class OtlpTelemetryExporter:
    """Prepare telemetry payloads for OTLP collectors.

    Network transmission is intentionally stubbed for offline testing while
    keeping the formatting consistent with OTLP expectations.
    """

    def __init__(self, endpoint: str) -> None:
        self.endpoint = endpoint
        self.buffer: list[Dict[str, Any]] = []

    def export(self, event: TelemetryEvent) -> None:
        payload = {
            "resource": {"service.name": "datasworn"},
            "endpoint": self.endpoint,
            "record": event.to_dict(),
        }
        self.buffer.append(payload)
        logger.debug("Prepared OTLP payload: %s", payload)


class PrometheusTelemetryExporter:
    """Track counters suitable for Prometheus scraping."""

    def __init__(self) -> None:
        self.counters: dict[str, int] = defaultdict(int)

    def export(self, event: TelemetryEvent) -> None:
        label = event.attributes.get("label", event.event_type)
        self.counters[label] += 1

    def format_metrics(self) -> str:
        lines = ["# HELP telemetry_events_total Count of emitted telemetry events",
                 "# TYPE telemetry_events_total counter"]
        for label, value in sorted(self.counters.items()):
            lines.append(f'telemetry_events_total{{type="{label}"}} {value}')
        return "\n".join(lines) + "\n"


class TelemetryAlertManager:
    """Simple alerting checks for crash spikes and difficulty anomalies."""

    def __init__(self, crash_threshold: int, difficulty_threshold: float) -> None:
        self.crash_threshold = crash_threshold
        self.difficulty_threshold = difficulty_threshold
        self.crash_window: deque[datetime] = deque()
        self.difficulty_samples: deque[float] = deque(maxlen=20)
        self.active_alerts: list[str] = []

    def observe_event(self, event: TelemetryEvent) -> None:
        now = datetime.utcnow()
        if event.event_type == "crash":
            self.crash_window.append(now)
            while self.crash_window and now - self.crash_window[0] > timedelta(minutes=1):
                self.crash_window.popleft()
            if len(self.crash_window) >= self.crash_threshold:
                self.active_alerts.append(
                    f"Crash spike detected: {len(self.crash_window)} crashes in the last minute"
                )

        if "difficulty_rating" in event.attributes:
            try:
                rating = float(event.attributes["difficulty_rating"])
            except (TypeError, ValueError):
                rating = None
            if rating is not None:
                self.difficulty_samples.append(rating)
                if len(self.difficulty_samples) >= 4:
                    recent = list(self.difficulty_samples)[-4:]
                    drift = max(recent) - min(recent)
                    if drift >= self.difficulty_threshold:
                        self.active_alerts.append(
                            f"Difficulty curve anomaly: drift {drift:.2f} over last {len(recent)} events"
                        )

    def build_dashboard(self) -> Dict[str, Any]:
        return {
            "active_alerts": list(self.active_alerts),
            "crashes_last_minute": len(self.crash_window),
            "difficulty_recent": list(self.difficulty_samples),
        }


class TelemetryClient:
    """Central telemetry dispatcher with sampling support."""

    def __init__(
        self,
        telemetry_config: Optional[TelemetryConfig] = None,
        exporters: Optional[Iterable[TelemetryExporter]] = None,
        alert_manager: Optional[TelemetryAlertManager] = None,
    ) -> None:
        self.config = telemetry_config or config.telemetry
        self.exporters: List[TelemetryExporter] = list(exporters) if exporters is not None else self._build_exporters()
        self.alert_manager = alert_manager or TelemetryAlertManager(
            self.config.crash_alert_threshold, self.config.difficulty_anomaly_threshold
        )

    def _build_exporters(self) -> List[TelemetryExporter]:
        exporters: List[TelemetryExporter] = []
        if self.config.enable_stdout:
            exporters.append(StdoutTelemetryExporter())
        if self.config.enable_json:
            exporters.append(JsonTelemetryExporter(self.config.json_path))
        if self.config.enable_otlp and self.config.otlp_endpoint:
            exporters.append(OtlpTelemetryExporter(self.config.otlp_endpoint))
        if self.config.enable_prometheus:
            exporters.append(PrometheusTelemetryExporter())
        return exporters

    def emit(
        self,
        event_type: str,
        *,
        session_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        sample_rate: Optional[float] = None,
    ) -> bool:
        rate = sample_rate if sample_rate is not None else self.config.sample_rate
        if rate <= 0:
            return False
        if rate < 1.0 and random.random() > rate:
            return False

        event = TelemetryEvent(
            event_type=event_type,
            timestamp=time.time(),
            session_id=session_id,
            attributes=attributes or {},
        )
        for exporter in self.exporters:
            exporter.export(event)
        if self.alert_manager:
            self.alert_manager.observe_event(event)
        return True

    # Convenience emitters -------------------------------------------------
    def emit_session_start(self, session_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        return self.emit("session.start", session_id=session_id, attributes=metadata or {})

    def emit_session_end(self, session_id: str, summary: Dict[str, Any]) -> bool:
        return self.emit("session.end", session_id=session_id, attributes=summary)

    def emit_quest_completion(self, quest_id: str, quest_type: str, difficulty: str, session_id: Optional[str]) -> bool:
        return self.emit(
            "quest.completed",
            session_id=session_id,
            attributes={"quest_id": quest_id, "quest_type": quest_type, "difficulty": difficulty},
        )

    def emit_wipe(self, cause: str, session_id: Optional[str], difficulty_rating: Optional[float] = None) -> bool:
        attributes = {"cause": cause}
        if difficulty_rating is not None:
            attributes["difficulty_rating"] = difficulty_rating
        return self.emit("party.wipe", session_id=session_id, attributes=attributes)

    def emit_boss_kill(
        self,
        boss_name: str,
        difficulty_rating: float,
        session_id: Optional[str],
        rewards: Optional[Dict[str, Any]] = None,
    ) -> bool:
        attributes = {"boss": boss_name, "difficulty_rating": difficulty_rating}
        attributes.update(rewards or {})
        return self.emit("boss.kill", session_id=session_id, attributes=attributes)


telemetry = TelemetryClient()
