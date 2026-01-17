"""
Photo Album Manager Module.
Handles the capture and organization of cinematic moments.
"""

from typing import List, Optional
import time
import uuid
from src.game_state import PhotoEntry, PhotoAlbumState

class PhotoAlbumManager:
    """Manages the photo album state and image generation triggers."""
    
    def __init__(self, state: PhotoAlbumState):
        self.state = state

    def capture_moment(
        self,
        image_url: str,
        caption: str,
        tags: List[str],
        scene_id: str = "",
        timestamp: Optional[str] = None,
    ) -> PhotoEntry:
        """
        Creates a new photo entry and adds it to the album.
        """
        entry = PhotoEntry(
            id=str(uuid.uuid4()),
            image_url=image_url,
            caption=caption,
            timestamp=timestamp or datetime.now().isoformat(),
            tags=tags,
            scene_id=scene_id
        )
        self.state.photos.append(entry)
        return entry

    def get_photos(self, tag_filter: Optional[str] = None) -> List[PhotoEntry]:
        """Returns photos, optionally filtered by tag."""
        if tag_filter:
            return [p for p in self.state.photos if tag_filter in p.tags]
        return self.state.photos

    def get_latest_photo(self) -> Optional[PhotoEntry]:
        """Returns the most recent photo."""
        if not self.state.photos:
            return None
        return self.state.photos[-1]

    def get_recent_highlights(self, limit: int = 3) -> List[dict]:
        """Return the most recent photo entries as dictionaries."""
        if not self.state.photos:
            return []

        photos = sorted(self.state.photos, key=lambda p: p.timestamp)
        recent = photos[-limit:][::-1]

        highlights: List[dict] = []
        for entry in recent:
            highlights.append(
                {
                    "id": entry.id,
                    "caption": entry.caption,
                    "timestamp": entry.timestamp,
                    "tags": entry.tags,
                    "scene_id": entry.scene_id,
                    "image_url": entry.image_url,
                }
            )
        return highlights

# Fix missing import
from datetime import datetime
