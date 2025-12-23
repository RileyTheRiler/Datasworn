import sys
import os
import unittest

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.consequence_tracker import ConsequenceTracker, ConsequenceSeverity
from src.narrative_memory import NarrativeSnapshot
from src.story_graph import StoryDAG
from src.narrative_orchestrator import NarrativeOrchestrator


class TestNarrativeSnapshots(unittest.TestCase):
    def test_consequence_events_feed_snapshot(self):
        tracker = ConsequenceTracker()
        snapshot = NarrativeSnapshot(scene_index=1)

        consequence = tracker.add_consequence(
            description="Owes a debt to the merchant guild",
            severity=ConsequenceSeverity.MAJOR,
            snapshot=snapshot,
        )

        tracker.escalate_consequence(consequence.id, snapshot=snapshot)
        self.assertTrue(any(evt.event_type == "consequence_added" for evt in snapshot.recent_events))
        self.assertTrue(any(evt.event_type == "consequence_escalated" for evt in snapshot.recent_events))

    def test_story_graph_persists_snapshots(self):
        graph = StoryDAG()
        snapshot = NarrativeSnapshot(scene_index=3)
        snapshot.active_vows.append("Protect the village")
        snapshot.unresolved_threads.append("Stop the raiders")

        graph.record_snapshot(snapshot)
        restored = StoryDAG.from_dict(graph.to_dict())

        self.assertEqual(len(restored.snapshots), 1)
        restored_snapshot = restored.snapshots[0]
        self.assertIn("Protect the village", restored_snapshot.active_vows)
        self.assertIn("Stop the raiders", restored_snapshot.unresolved_threads)

    def test_orchestrator_uses_snapshot_for_beats(self):
        orchestrator = NarrativeOrchestrator()
        orchestrator.current_scene = 2
        orchestrator.latest_snapshot = NarrativeSnapshot(scene_index=2)
        orchestrator.latest_snapshot.unresolved_threads.append("Who sabotaged the drive core")
        orchestrator.story_graph.record_snapshot(orchestrator.latest_snapshot)

        guidance = orchestrator.get_comprehensive_guidance(location="Hangar", active_npcs=[])

        self.assertIn("SUGGESTED BEAT: REVELATION", guidance)


if __name__ == "__main__":
    unittest.main()
