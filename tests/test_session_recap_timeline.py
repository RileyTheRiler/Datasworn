from datetime import datetime, timedelta
import json

from src.session_recap import MilestoneCategory, SessionRecapEngine


def test_timeline_ordering_and_filters():
    engine = SessionRecapEngine()
    base_time = datetime(2024, 1, 1, 12, 0, 0)

    engine.start_session(1)
    engine.record_milestone(
        description="Accepted the iron vow",
        category=MilestoneCategory.QUEST,
        importance=6,
        timestamp=base_time,
    )
    engine.record_milestone(
        description="Bartered for ship fuel",
        category=MilestoneCategory.ECONOMY,
        importance=4,
        timestamp=base_time + timedelta(minutes=3),
    )
    engine.record_milestone(
        description="Clashed with raiders",
        category=MilestoneCategory.COMBAT,
        importance=9,
        timestamp=base_time + timedelta(minutes=5),
    )

    ordered = engine.get_timeline()
    assert [entry.description for entry in ordered] == [
        "Accepted the iron vow",
        "Bartered for ship fuel",
        "Clashed with raiders",
    ]

    combat_only = engine.get_timeline([MilestoneCategory.COMBAT.value])
    assert len(combat_only) == 1
    assert combat_only[0].category is MilestoneCategory.COMBAT

    economy_and_narrative = engine.get_timeline(["economy", "narrative"])
    assert all(entry.category in {MilestoneCategory.ECONOMY, MilestoneCategory.NARRATIVE} for entry in economy_and_narrative)


def test_timeline_export_integrity():
    engine = SessionRecapEngine()
    engine.start_session(1)
    engine.record_milestone(
        description="Skirmished with pirates",
        category=MilestoneCategory.COMBAT,
        importance=8,
        timestamp=datetime(2024, 1, 2, 8, 0, 0),
    )
    engine.record_milestone(
        description="Negotiated a ceasefire",
        category=MilestoneCategory.NARRATIVE,
        importance=7,
        timestamp=datetime(2024, 1, 2, 8, 30, 0),
    )

    exported = engine.export_timeline_json([MilestoneCategory.COMBAT.value, MilestoneCategory.NARRATIVE.value])
    payload = json.loads(exported)

    assert payload["total_entries"] == 2
    assert payload["timeline"][0]["category"] == "combat"
    assert payload["timeline"][1]["description"] == "Negotiated a ceasefire"
    assert payload["timeline"][0]["timestamp"] < payload["timeline"][1]["timestamp"]
