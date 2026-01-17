import unittest
from datetime import datetime

from src.session_recap import SessionRecapEngine
from src.photo_album import PhotoAlbumManager
from src.game_state import PhotoAlbumState, MemoryStateModel, VowState


class TestRecapDigest(unittest.TestCase):
    def test_digest_includes_album_memory_and_vows(self):
        engine = SessionRecapEngine()
        engine.start_session(1)
        engine.record_event("Breached the derelict station", importance=8, location="Shadow Spire")

        album = PhotoAlbumState()
        manager = PhotoAlbumManager(album)
        manager.capture_moment(
            image_url="/static/test.png",
            caption="Recovered the lost fragment",
            tags=["Discovery", "Mystery"],
            scene_id="scene-1",
            timestamp=datetime(2024, 1, 1, 12, 0).isoformat(),
        )

        memory = MemoryStateModel(
            scene_summaries=["Docked with the derelict", "Triggered ancient defenses"],
            decisions_made=["Trusted the rogue AI"],
            npcs_encountered={"Rogue AI": "Offered cryptic warnings"},
        )
        vows = [VowState(name="Recover the relic", rank="dangerous", ticks=8)]

        digest = engine.build_digest(
            protagonist_name="Ash",
            album_state=album,
            memory_state=memory,
            vow_state=vows,
            current_location="Shadow Spire",
        )

        self.assertIn("Ash", digest["recap"])
        self.assertEqual(digest["highlights"][0]["caption"], "Recovered the lost fragment")
        self.assertIn("Docked with the derelict", digest["memory"]["recent_summaries"])
        self.assertEqual(digest["vows"][0]["name"], "Recover the relic")


if __name__ == "__main__":
    unittest.main()
