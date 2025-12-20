"""
Psychological Difficulty Scaling
Adjusts game difficulty based on character's mental state.
"""

from src.psych_profile import PsychologicalProfile


class PsychologicalDifficultyScaler:
    """Scales difficulty based on trauma and mental state."""
    
    def get_difficulty_modifier(self, profile: PsychologicalProfile) -> float:
        """
        Calculate a global difficulty modifier based on psychological state.
        Returns a value from 0.0 (easier) to 1.0+ (harder).
        """
        modifier = 0.0
        
        # Trauma makes everything harder
        trauma_count = len(profile.trauma_scars)
        modifier += trauma_count * 0.1  # +10% per scar
        
        # Low sanity increases difficulty
        if profile.sanity < 0.5:
            modifier += (0.5 - profile.sanity) * 0.4  # Up to +20%
        
        # High stress increases difficulty
        if profile.stress_level > 0.7:
            modifier += (profile.stress_level - 0.7) * 0.3  # Up to +9%
        
        # Addiction/withdrawal
        if profile.addiction_level > 0.5:
            modifier += profile.addiction_level * 0.2  # Up to +20%
        
        return min(1.0, modifier)  # Cap at +100%
    
    def apply_withdrawal_penalty(self, profile: PsychologicalProfile) -> int:
        """
        Return penalty to apply to rolls if character is addicted and not using.
        """
        if profile.addiction_level >= 0.5:
            return -1
        elif profile.addiction_level >= 0.8:
            return -2
        return 0
    
    def check_permadeath(self, profile: PsychologicalProfile) -> dict:
        """
        Check if character has reached permanent psychotic break.
        """
        if profile.sanity <= 0.0:
            return {
                "permadeath": True,
                "message": "Your mind shatters. The void claims you. This character is lost.",
                "cause": "Complete sanity loss"
            }
        
        # Alternative: Too many unintegrated traumas
        unintegrated = [s for s in profile.trauma_scars if s.arc_stage == "fresh"]
        if len(unintegrated) >= 5:
            return {
                "permadeath": True,
                "message": "Too many wounds. Your psyche fractures beyond repair.",
                "cause": "Excessive unhealed trauma"
            }
        
        return {"permadeath": False}
