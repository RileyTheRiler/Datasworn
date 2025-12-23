import os
import sys
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.cognition_loop import (
    CognitionLoop,
    DialogueEngine,
    PerceptionSystem,
    SceneContext,
    Stimulus,
    WorkingMemory,
)


class TestPerception(unittest.TestCase):
    def test_filters_and_confidence(self):
        system = PerceptionSystem(vision_range=10.0, hearing_range=6.0)
        observer = (0.0, 0.0)

        visible = Stimulus("visible", (5.0, 0.0), fact="open crate")
        occluded = Stimulus("occluded", (5.0, 0.0), occluded=True, fact="hidden stash")
        audible = Stimulus("audible", (0.0, 5.5), volume=1.0, occluded=True, fact="footsteps")

        filtered = system.filter(observer, [visible, occluded, audible])
        self.assertIn(visible, filtered)
        self.assertIn(audible, filtered)
        self.assertNotIn(occluded, filtered)

        self.assertGreater(system.confidence(observer, visible), 0.6)
        self.assertAlmostEqual(system.confidence(observer, audible), 0.35)
        self.assertEqual(system.confidence(observer, occluded), 0.0)


class TestMemory(unittest.TestCase):
    def test_memory_ttl_and_reordering(self):
        memory = WorkingMemory(decay_rate=0.2)
        base_time = 100.0

        # Add a batch of stimuli with staggered TTLs and relevance
        for i in range(15):
            memory.remember(
                Stimulus(f"s{i}", (i, i)),
                ttl=1.0 if i % 2 == 0 else 5.0,
                relevance=1.0 - (i * 0.03),
                now=base_time,
            )

        # Advance time so short-TTL entries expire and relevance decays
        memory.advance_time(base_time + 2.0)
        self.assertLess(memory.count, 15)  # Expired short-lived traces

        ordered = memory.ordered_traces()
        self.assertTrue(all(ordered[i].relevance >= ordered[i + 1].relevance for i in range(len(ordered) - 1)))

        # Add a highly relevant recent trace and ensure it bubbles to the top
        memory.remember(Stimulus("critical", (0, 0)), ttl=5.0, relevance=1.0, now=base_time + 2.0)
        top = memory.ordered_traces()[0]
        self.assertEqual(top.stimulus.id, "critical")


class FakeClock:
    def __init__(self, advance_per_call: float = 0.0):
        self.now = 0.0
        self.advance_per_call = advance_per_call

    def __call__(self):
        self.now += self.advance_per_call
        return self.now

    def advance(self, delta: float):
        self.now += delta
        return self.now


class TestCognitionLoop(unittest.TestCase):
    def test_tick_loop_respects_reachability_and_knowledge(self):
        clock = FakeClock()
        loop = CognitionLoop(observer=(0.0, 0.0), frame_budget_ms=5.0, time_provider=clock)
        context = SceneContext(reachable_tiles={(1.0, 0.0)}, known_facts={"reachable fact"})

        stimuli = [
            Stimulus("reachable", (1.0, 0.0), fact="reachable fact"),
            Stimulus("unreachable", (20.0, 0.0), fact="far target"),
            Stimulus("heard", (0.0, 4.0), volume=1.0, occluded=True, fact="rustling"),
        ]

        result = loop.tick(stimuli, context)
        self.assertIn("investigate:reachable", result["actions"])
        self.assertNotIn("investigate:unreachable", result["actions"])
        self.assertTrue(all("far target" not in line for line in result["dialogue"]))
        # Occluded/heard fact should not generate dialogue
        self.assertTrue(all("rustling" not in line for line in result["dialogue"]))

    def test_tick_frequency_and_lod_controls(self):
        clock = FakeClock(advance_per_call=0.0)
        loop = CognitionLoop(observer=(0.0, 0.0), frame_budget_ms=3.0, time_provider=clock)
        loop.update_lod(3)

        context = SceneContext(reachable_tiles={(i, 0.0) for i in range(10)}, known_facts={f"s{i}" for i in range(10)})
        stimuli = [Stimulus(f"s{i}", (i, 0.0), fact=f"s{i}") for i in range(10)]

        first_tick = loop.tick(stimuli, context)
        self.assertLessEqual(len(first_tick["actions"]), 4)  # LOD throttles workload
        self.assertTrue(first_tick["within_budget"])

        # Second tick without advancing time should be skipped by frequency gate
        second_tick = loop.tick(stimuli, context)
        self.assertEqual(second_tick["actions"], [])

        # Simulate a slow frame by advancing clock during measurement
        slow_clock = FakeClock(advance_per_call=0.01)
        slow_loop = CognitionLoop(observer=(0.0, 0.0), frame_budget_ms=1.0, time_provider=slow_clock)
        slow_result = slow_loop.tick(stimuli, context)
        self.assertFalse(slow_result["within_budget"])


class TestDialogue(unittest.TestCase):
    def test_tone_and_hallucination_suppression(self):
        engine = DialogueEngine(tone="cheerful")
        line = engine.compose("The reactor hums softly.")
        self.assertTrue(line.startswith("(warm)"))
        self.assertNotIn("player", line.lower())

        meta_line = engine.compose("Breaking the fourth wall is not allowed.")
        self.assertNotIn("fourth wall", meta_line.lower())

        suppressed = engine.compose("phantom vision", hallucination=True)
        self.assertEqual(suppressed, "")


if __name__ == "__main__":
    unittest.main()
