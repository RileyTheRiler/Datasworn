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

    def capture_moment(self, image_url: str, caption: str, tags: List[str], scene_id: str = "") -> PhotoEntry:
        """
        Creates a new photo entry and adds it to the album.
        """
        entry = PhotoEntry(
            id=str(uuid.uuid4()),
            image_url=image_url,
            caption=caption,
            timestamp=datetime.now().isoformat(), # Use datetime.now() but need import
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

# Fix missing import
from datetime import datetime
