"""
Voice Generator for Starforged AI Game Master.
Handles TTS generation with ElevenLabs API and caching.
"""

from __future__ import annotations
import os
import hashlib
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


# ============================================================================
# Voice Profiles
# ============================================================================

# Map character archetypes to ElevenLabs voice IDs
# These are example IDs - replace with actual voice IDs from your ElevenLabs account
VOICE_PROFILES = {
    "gruff_veteran": {
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # Example: Rachel
        "description": "Deep, gravelly, authoritative"
    },
    "nervous_scholar": {
        "voice_id": "AZnzlk1XvdvUeBnXmlld",  # Example: Domi
        "description": "Higher pitch, quick speech, analytical"
    },
    "pragmatic_merchant": {
        "voice_id": "EXAVITQu4vr4xnSDxMaL",  # Example: Bella
        "description": "Smooth, persuasive, friendly"
    },
    "charismatic_rebel": {
        "voice_id": "ErXwobaYiN019PkySvjV",  # Example: Antoni
        "description": "Passionate, energetic, inspiring"
    },
    "enigmatic_oracle": {
        "voice_id": "MF3mGyEYCl7XYWbV9V6O",  # Example: Elli
        "description": "Mysterious, calm, otherworldly"
    },
    "default": {
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "description": "Default narrator voice"
    }
}


# ============================================================================
# Voice Generator
# ============================================================================

class VoiceGenerator:
    """
    Generates TTS audio using ElevenLabs API with caching.
    """
    
    def __init__(self, cache_dir: str = "data/assets/voice_cache"):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if API is available
        self.api_available = bool(self.api_key)
        if not self.api_available:
            print("Warning: ELEVENLABS_API_KEY not found. Voice synthesis disabled.")
    
    def _get_cache_key(self, text: str, voice_id: str) -> str:
        """Generate cache key from text and voice ID."""
        content = f"{text}_{voice_id}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_path(self, cache_key: str) -> Optional[Path]:
        """Check if cached audio exists."""
        cached_file = self.cache_dir / f"{cache_key}.mp3"
        if cached_file.exists():
            return cached_file
        return None
    
    def generate_speech(
        self,
        text: str,
        voice_profile: str = "default",
        use_cache: bool = True
    ) -> Optional[str]:
        """
        Generate speech audio for text.
        
        Args:
            text: Text to synthesize
            voice_profile: Voice profile key from VOICE_PROFILES
            use_cache: Whether to use cached audio if available
        
        Returns:
            Path to audio file (relative to assets) or None if failed
        """
        if not self.api_available:
            return None
        
        # Get voice ID
        profile = VOICE_PROFILES.get(voice_profile, VOICE_PROFILES["default"])
        voice_id = profile["voice_id"]
        
        # Check cache
        cache_key = self._get_cache_key(text, voice_id)
        if use_cache:
            cached_path = self._get_cached_path(cache_key)
            if cached_path:
                # Return relative path for frontend
                return f"/assets/voice_cache/{cached_path.name}"
        
        # Generate new audio
        try:
            audio_path = self._generate_with_elevenlabs(text, voice_id, cache_key)
            if audio_path:
                return f"/assets/voice_cache/{audio_path.name}"
        except Exception as e:
            print(f"Voice generation failed: {e}")
            return None
        
        return None
    
    def _generate_with_elevenlabs(
        self,
        text: str,
        voice_id: str,
        cache_key: str
    ) -> Optional[Path]:
        """
        Generate audio using ElevenLabs API.
        
        Args:
            text: Text to synthesize
            voice_id: ElevenLabs voice ID
            cache_key: Cache key for filename
        
        Returns:
            Path to generated audio file or None
        """
        try:
            import requests
        except ImportError:
            print("Error: requests library not installed")
            return None
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Save to cache
            output_path = self.cache_dir / f"{cache_key}.mp3"
            output_path.write_bytes(response.content)
            
            return output_path
            
        except requests.exceptions.RequestException as e:
            print(f"ElevenLabs API error: {e}")
            return None
    
    def get_voice_for_character(self, character_name: str, archetype: str = "default") -> str:
        """
        Get voice profile for a character.
        
        Args:
            character_name: Character name
            archetype: Character archetype from character_voice.py
        
        Returns:
            Voice profile key
        """
        # Map archetype to voice profile
        archetype_map = {
            "gruff_veteran": "gruff_veteran",
            "nervous_scholar": "nervous_scholar",
            "pragmatic_merchant": "pragmatic_merchant",
            "charismatic_rebel": "charismatic_rebel",
            "enigmatic_oracle": "enigmatic_oracle"
        }
        
        return archetype_map.get(archetype, "default")
    
    def clear_cache(self) -> int:
        """
        Clear voice cache.
        
        Returns:
            Number of files deleted
        """
        count = 0
        for file in self.cache_dir.glob("*.mp3"):
            file.unlink()
            count += 1
        return count
    
    def get_cache_size(self) -> tuple[int, int]:
        """
        Get cache statistics.
        
        Returns:
            Tuple of (file_count, total_bytes)
        """
        files = list(self.cache_dir.glob("*.mp3"))
        total_bytes = sum(f.stat().st_size for f in files)
        return len(files), total_bytes


# ============================================================================
# Convenience Functions
# ============================================================================

def create_voice_generator() -> VoiceGenerator:
    """Create a new voice generator instance."""
    return VoiceGenerator()


def generate_npc_dialogue(
    text: str,
    npc_archetype: str = "default",
    use_cache: bool = True
) -> Optional[str]:
    """
    Quick function to generate NPC dialogue.
    
    Args:
        text: Dialogue text
        npc_archetype: NPC archetype from character_voice.py
        use_cache: Whether to use cache
    
    Returns:
        Path to audio file or None
    """
    generator = VoiceGenerator()
    voice_profile = generator.get_voice_for_character("", npc_archetype)
    return generator.generate_speech(text, voice_profile, use_cache)
