"""
Chapter-Based Narrative Progression System

Manages chapter state, region locking, soft locks, economy modifiers,
ambient profiles, and time/season jumps for dramatic pacing.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml


@dataclass
class SoftLock:
    """Diegetic barrier that prevents access to regions."""
    lock_id: str
    description: str
    affected_regions: List[str]
    active: bool = True


@dataclass
class AmbientProfile:
    """Ambient encounter and atmosphere settings."""
    encounters: List[str]
    weather_bias: str
    ambient_dialogue: List[str]


@dataclass
class TimeJumpOutcome:
    """Results of a chapter transition time jump."""
    days_advanced: int
    narrative_summary: str


@dataclass
class ChapterMetadata:
    """Complete metadata for a narrative chapter."""
    chapter_id: str
    name: str
    season: str
    regions_unlocked: List[str]
    critical_missions: List[str]
    soft_locks: List[SoftLock]
    law_pressure: float
    economy_modifiers: Dict[str, float]
    ambient_sets: AmbientProfile
    time_jump_outcome: TimeJumpOutcome
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChapterMetadata':
        """Create ChapterMetadata from dictionary."""
        soft_locks = [
            SoftLock(**lock_data) for lock_data in data.get('soft_locks', [])
        ]
        
        ambient_data = data.get('ambient_sets', {})
        ambient_sets = AmbientProfile(
            encounters=ambient_data.get('encounters', []),
            weather_bias=ambient_data.get('weather_bias', 'clear'),
            ambient_dialogue=ambient_data.get('ambient_dialogue', [])
        )
        
        time_jump_data = data.get('time_jump_outcome', {})
        time_jump = TimeJumpOutcome(
            days_advanced=time_jump_data.get('days_advanced', 0),
            narrative_summary=time_jump_data.get('narrative_summary', '')
        )
        
        return cls(
            chapter_id=data['chapter_id'],
            name=data['name'],
            season=data['season'],
            regions_unlocked=data.get('regions_unlocked', []),
            critical_missions=data.get('critical_missions', []),
            soft_locks=soft_locks,
            law_pressure=data.get('law_pressure', 1.0),
            economy_modifiers=data.get('economy_modifiers', {}),
            ambient_sets=ambient_sets,
            time_jump_outcome=time_jump
        )


@dataclass
class ChapterState:
    """Current chapter progression state."""
    current_chapter_id: str = "chapter_1"
    unlocked_regions: List[str] = field(default_factory=list)
    active_soft_locks: Dict[str, SoftLock] = field(default_factory=dict)
    completed_missions: List[str] = field(default_factory=list)
    current_season: str = "Winter"
    current_law_pressure: float = 1.0
    current_economy_modifiers: Dict[str, float] = field(default_factory=dict)
    total_days_elapsed: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'current_chapter_id': self.current_chapter_id,
            'unlocked_regions': self.unlocked_regions,
            'active_soft_locks': {
                lock_id: {
                    'lock_id': lock.lock_id,
                    'description': lock.description,
                    'affected_regions': lock.affected_regions,
                    'active': lock.active
                }
                for lock_id, lock in self.active_soft_locks.items()
            },
            'completed_missions': self.completed_missions,
            'current_season': self.current_season,
            'current_law_pressure': self.current_law_pressure,
            'current_economy_modifiers': self.current_economy_modifiers,
            'total_days_elapsed': self.total_days_elapsed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChapterState':
        """Deserialize from dictionary."""
        active_soft_locks = {}
        for lock_id, lock_data in data.get('active_soft_locks', {}).items():
            active_soft_locks[lock_id] = SoftLock(**lock_data)
        
        return cls(
            current_chapter_id=data.get('current_chapter_id', 'chapter_1'),
            unlocked_regions=data.get('unlocked_regions', []),
            active_soft_locks=active_soft_locks,
            completed_missions=data.get('completed_missions', []),
            current_season=data.get('current_season', 'Winter'),
            current_law_pressure=data.get('current_law_pressure', 1.0),
            current_economy_modifiers=data.get('current_economy_modifiers', {}),
            total_days_elapsed=data.get('total_days_elapsed', 0)
        )


class ProgressionManager:
    """Manages chapter progression and world state changes."""
    
    def __init__(self, chapters_file: Optional[Path] = None):
        """Initialize with chapter metadata."""
        if chapters_file is None:
            chapters_file = Path(__file__).parent.parent.parent / "data" / "story" / "chapters.yaml"
        
        self.chapters_file = chapters_file
        self.chapters: Dict[str, ChapterMetadata] = {}
        self.state = ChapterState()
        
        self._load_chapters()
        self._initialize_state()
    
    def _load_chapters(self):
        """Load chapter metadata from YAML."""
        if not self.chapters_file.exists():
            raise FileNotFoundError(f"Chapters file not found: {self.chapters_file}")
        
        with open(self.chapters_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        for chapter_data in data.get('chapters', []):
            chapter = ChapterMetadata.from_dict(chapter_data)
            self.chapters[chapter.chapter_id] = chapter
    
    def _initialize_state(self):
        """Initialize state from first chapter."""
        first_chapter = self.chapters.get('chapter_1')
        if first_chapter:
            self.state.unlocked_regions = first_chapter.regions_unlocked.copy()
            self.state.current_season = first_chapter.season
            self.state.current_law_pressure = first_chapter.law_pressure
            self.state.current_economy_modifiers = first_chapter.economy_modifiers.copy()
            
            # Initialize soft locks
            for soft_lock in first_chapter.soft_locks:
                self.state.active_soft_locks[soft_lock.lock_id] = soft_lock
    
    def get_current_chapter(self) -> ChapterMetadata:
        """Get current chapter metadata."""
        return self.chapters.get(self.state.current_chapter_id)
    
    def unlock_region(self, region_id: str):
        """Unlock a region for travel."""
        if region_id not in self.state.unlocked_regions:
            self.state.unlocked_regions.append(region_id)
    
    def lock_region(self, region_id: str):
        """Lock a region, preventing travel."""
        if region_id in self.state.unlocked_regions:
            self.state.unlocked_regions.remove(region_id)
    
    def is_region_accessible(self, region_id: str) -> bool:
        """Check if a region is accessible (unlocked and not soft-locked)."""
        if region_id not in self.state.unlocked_regions:
            return False
        
        # Check soft locks
        for soft_lock in self.state.active_soft_locks.values():
            if soft_lock.active and region_id in soft_lock.affected_regions:
                return False
        
        return True
    
    def set_soft_lock(self, lock_id: str, active: bool):
        """Toggle a soft lock on/off."""
        if lock_id in self.state.active_soft_locks:
            self.state.active_soft_locks[lock_id].active = active
    
    def apply_economy_modifiers(self, modifiers: Dict[str, float]):
        """Apply economy modifiers to prices."""
        self.state.current_economy_modifiers = modifiers.copy()
    
    def get_price_modifier(self, category: str) -> float:
        """Get price modifier for a category."""
        return self.state.current_economy_modifiers.get(category, 1.0)
    
    def set_ambient_profile(self, profile: AmbientProfile):
        """Set current ambient encounter/atmosphere profile."""
        # This would integrate with world state systems
        # For now, just store in chapter metadata
        pass
    
    def complete_mission(self, mission_id: str):
        """Mark a mission as completed."""
        if mission_id not in self.state.completed_missions:
            self.state.completed_missions.append(mission_id)
    
    def validate_chapter_completion(self, chapter_id: Optional[str] = None) -> tuple[bool, List[str]]:
        """
        Check if chapter's critical missions are complete.
        
        Returns:
            (is_complete, missing_missions)
        """
        if chapter_id is None:
            chapter_id = self.state.current_chapter_id
        
        chapter = self.chapters.get(chapter_id)
        if not chapter:
            return False, []
        
        missing = [
            mission for mission in chapter.critical_missions
            if mission not in self.state.completed_missions
        ]
        
        return len(missing) == 0, missing
    
    def advance_chapter(self, next_chapter_id: str) -> Dict[str, Any]:
        """
        Advance to the next chapter, applying all world state changes.
        
        Returns:
            Dictionary with transition details and narrative summary.
        """
        # Validate current chapter completion
        is_complete, missing = self.validate_chapter_completion()
        if not is_complete:
            return {
                'success': False,
                'error': 'Chapter not complete',
                'missing_missions': missing
            }
        
        # Get next chapter
        next_chapter = self.chapters.get(next_chapter_id)
        if not next_chapter:
            return {
                'success': False,
                'error': f'Chapter not found: {next_chapter_id}'
            }
        
        # Apply time jump
        time_jump_result = self.apply_time_jump(next_chapter.time_jump_outcome)
        
        # Update chapter state
        self.state.current_chapter_id = next_chapter_id
        self.state.current_season = next_chapter.season
        
        # Apply world state deltas
        world_state_changes = self.apply_world_state_deltas(next_chapter)
        
        return {
            'success': True,
            'chapter_id': next_chapter_id,
            'chapter_name': next_chapter.name,
            'time_jump': time_jump_result,
            'world_state_changes': world_state_changes,
            'narrative_summary': next_chapter.time_jump_outcome.narrative_summary
        }
    
    def apply_time_jump(self, outcome: TimeJumpOutcome) -> Dict[str, Any]:
        """
        Apply time/season jump effects.
        
        Updates calendar, season, and triggers environmental changes.
        """
        self.state.total_days_elapsed += outcome.days_advanced
        
        return {
            'days_advanced': outcome.days_advanced,
            'total_days': self.state.total_days_elapsed,
            'narrative': outcome.narrative_summary
        }
    
    def apply_world_state_deltas(self, chapter: ChapterMetadata) -> Dict[str, Any]:
        """
        Apply world state changes for new chapter.
        
        Updates:
        - Region access
        - Soft locks
        - Law enforcement density
        - Economy modifiers
        - Ambient encounter sets
        """
        changes = {}
        
        # Update regions
        old_regions = set(self.state.unlocked_regions)
        new_regions = set(chapter.regions_unlocked)
        
        self.state.unlocked_regions = chapter.regions_unlocked.copy()
        
        changes['regions_added'] = list(new_regions - old_regions)
        changes['regions_removed'] = list(old_regions - new_regions)
        
        # Update soft locks
        self.state.active_soft_locks.clear()
        for soft_lock in chapter.soft_locks:
            self.state.active_soft_locks[soft_lock.lock_id] = soft_lock
        
        changes['soft_locks'] = [
            {
                'id': lock.lock_id,
                'description': lock.description,
                'affected_regions': lock.affected_regions
            }
            for lock in chapter.soft_locks
        ]
        
        # Update law pressure
        old_pressure = self.state.current_law_pressure
        self.state.current_law_pressure = chapter.law_pressure
        changes['law_pressure_change'] = chapter.law_pressure - old_pressure
        
        # Update economy
        self.state.current_economy_modifiers = chapter.economy_modifiers.copy()
        changes['economy_modifiers'] = chapter.economy_modifiers
        
        # Ambient profile
        changes['ambient_profile'] = {
            'encounters': chapter.ambient_sets.encounters,
            'weather_bias': chapter.ambient_sets.weather_bias,
            'dialogue_samples': chapter.ambient_sets.ambient_dialogue[:3]
        }
        
        return changes
    
    def get_state(self) -> Dict[str, Any]:
        """Get current progression state."""
        chapter = self.get_current_chapter()
        
        return {
            'chapter': {
                'id': chapter.chapter_id,
                'name': chapter.name,
                'season': chapter.season
            },
            'state': self.state.to_dict(),
            'progress': {
                'completed_missions': len(self.state.completed_missions),
                'total_critical_missions': len(chapter.critical_missions),
                'is_complete': self.validate_chapter_completion()[0]
            }
        }
    
    def force_set_chapter(self, chapter_id: str) -> bool:
        """
        DEBUG: Force set chapter without validation.
        
        Returns:
            True if successful, False if chapter not found.
        """
        chapter = self.chapters.get(chapter_id)
        if not chapter:
            return False
        
        self.state.current_chapter_id = chapter_id
        self.state.unlocked_regions = chapter.regions_unlocked.copy()
        self.state.current_season = chapter.season
        self.state.current_law_pressure = chapter.law_pressure
        self.state.current_economy_modifiers = chapter.economy_modifiers.copy()
        
        # Update soft locks
        self.state.active_soft_locks.clear()
        for soft_lock in chapter.soft_locks:
            self.state.active_soft_locks[soft_lock.lock_id] = soft_lock
        
        return True
