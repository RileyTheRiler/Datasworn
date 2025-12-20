"""
Psyche Audio Engine
Maps psychological states to audio cues and visual effects.
"""

from src.psych_profile import PsychologicalProfile, EmotionalState
from typing import Dict, List


class PsycheAudioEngine:
    """Maps psychological states to audio and visual feedback."""
    
    def get_soundscape_for_state(self, profile: PsychologicalProfile) -> List[str]:
        """
        Return list of audio cue IDs to play based on psychological state.
        Audio files should be placed in frontend/public/audio/
        """
        cues = []
        
        # Base ambient (always playing)
        cues.append("ambient_ship_hum")
        
        # Stress-based layers
        if profile.stress_level > 0.7:
            cues.append("heartbeat_loop")
        
        if profile.stress_level > 0.85:
            cues.append("breathing_heavy")
        
        # Sanity-based layers
        if profile.sanity < 0.3:
            cues.append("whispers_distant")
        
        if profile.sanity < 0.15:
            cues.append("static_interference")
        
        # Emotion-based one-shots
        if profile.current_emotion == EmotionalState.AFRAID:
            cues.append("stinger_fear")
        elif profile.current_emotion == EmotionalState.ANGRY:
            cues.append("stinger_anger")
        
        return cues
    
    def get_visual_effects(self, profile: PsychologicalProfile) -> Dict[str, any]:
        """
        Return CSS filter effects based on psychological state.
        Returns a dict of effect names and their intensity values.
        """
        effects = {
            "chromatic_aberration": 0.0,
            "vignette": 0.0,
            "desaturation": 0.0,
            "shake_intensity": 0.0,
            "blur": 0.0,
        }
        
        # Sanity effects
        if profile.sanity < 0.3:
            effects["chromatic_aberration"] = (0.3 - profile.sanity) * 10  # 0-3px
            effects["desaturation"] = (0.3 - profile.sanity) * 100  # 0-30%
        
        # Trauma effects
        if profile.trauma_scars:
            scar_count = len(profile.trauma_scars)
            effects["vignette"] = min(0.5, scar_count * 0.15)  # Max 50%
        
        # Emotion effects
        if profile.current_emotion == EmotionalState.AFRAID:
            effects["shake_intensity"] = 2.0  # pixels
        
        if profile.current_emotion == EmotionalState.OVERWHELMED:
            effects["blur"] = 1.5  # pixels
        
        return effects
    
    def get_audio_volume_modifiers(self, profile: PsychologicalProfile) -> Dict[str, float]:
        """Return volume multipliers for different audio layers."""
        return {
            "ambient": 1.0,
            "heartbeat": min(1.0, profile.stress_level * 1.2),
            "whispers": min(1.0, (0.3 - profile.sanity) * 3) if profile.sanity < 0.3 else 0.0,
            "music": max(0.3, 1.0 - profile.stress_level * 0.5),  # Music fades when stressed
        }
