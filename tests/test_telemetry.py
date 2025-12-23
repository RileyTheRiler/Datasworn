import time

import src.telemetry as telemetry_module
from src.config import TelemetryConfig
from src.telemetry import (
    PrometheusTelemetryExporter,
    TelemetryAlertManager,
    TelemetryClient,
    TelemetryEvent,
)


class DummyExporter:
    def __init__(self):
        self.events = []

    def export(self, event):
        self.events.append(event)


def test_sampling_respects_probability(monkeypatch):
    config = TelemetryConfig(
        enable_stdout=False,
        enable_json=False,
        enable_otlp=False,
        enable_prometheus=False,
        sample_rate=0.5,
    )
    exporter = DummyExporter()
    client = TelemetryClient(config, exporters=[exporter])

    monkeypatch.setattr(telemetry_module.random, "random", lambda: 0.99)
    assert client.emit("session.start", session_id="abc") is False
    assert exporter.events == []

    monkeypatch.setattr(telemetry_module.random, "random", lambda: 0.01)
    assert client.emit("session.start", session_id="abc") is True
    assert len(exporter.events) == 1


def test_prometheus_formatting_produces_labeled_metrics():
    exporter = PrometheusTelemetryExporter()
    exporter.export(TelemetryEvent("session.start", time.time(), "sess", {}))
    exporter.export(
        TelemetryEvent("quest.completed", time.time(), "sess", {"label": "quest"})
    )

    metrics = exporter.format_metrics()
    assert "# HELP telemetry_events_total" in metrics
    assert 'telemetry_events_total{type="quest"} 1' in metrics
    assert 'telemetry_events_total{type="session.start"} 1' in metrics


def test_alert_manager_detects_spikes_and_dashboards():
    manager = TelemetryAlertManager(crash_threshold=2, difficulty_threshold=0.3)

    crash_event = TelemetryEvent("crash", time.time(), None, {})
    manager.observe_event(crash_event)
    manager.observe_event(crash_event)

    assert any("Crash spike" in alert for alert in manager.active_alerts)

    difficulty_event = TelemetryEvent("boss.kill", time.time(), None, {"difficulty_rating": 1.0})
    manager.observe_event(difficulty_event)
    difficulty_event_2 = TelemetryEvent("boss.kill", time.time(), None, {"difficulty_rating": 2.0})
    manager.observe_event(difficulty_event_2)

    dashboard = manager.build_dashboard()
    assert dashboard["crashes_last_minute"] >= 2
    assert dashboard["difficulty_recent"]
