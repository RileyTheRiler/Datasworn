"""
Centralized Configuration for Starforged AI Game Master.
All configurable values should be defined here rather than hardcoded in modules.
"""

from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PathConfig:
    """File and directory paths."""
    saves_dir: str = "saves"
    feedback_db: str = "saves/feedback_learning.db"
    style_profiles_dir: str = "data/style_profiles"
    datasworn_dir: str = "data/datasworn"

    def __post_init__(self):
        # Allow environment variable overrides
        self.saves_dir = os.environ.get("STARFORGED_SAVES_DIR", self.saves_dir)
        self.feedback_db = os.environ.get("STARFORGED_FEEDBACK_DB", self.feedback_db)


@dataclass
class LLMConfig:
    """LLM provider configuration."""
    default_provider: str = "gemini"
    default_model: str = "gemini-2.0-flash"
    ollama_model: str = "llama3.1"

    # Generation parameters
    temperature: float = 0.85
    top_p: float = 0.90
    top_k: int = 50
    repeat_penalty: float = 1.15
    max_tokens: int = 2000

    def __post_init__(self):
        self.default_provider = os.environ.get("LLM_PROVIDER", self.default_provider)
        self.default_model = os.environ.get("LLM_MODEL", self.default_model)
        self.ollama_model = os.environ.get("OLLAMA_MODEL", self.ollama_model)


@dataclass
class DirectorConfig:
    """Director/pacing thresholds."""
    tension_threshold_high: float = 0.8
    tension_threshold_medium: float = 0.5
    tension_threshold_low: float = 0.2

    # Pacing controls
    max_fast_scenes_before_breather: int = 3
    climax_tension_threshold: float = 0.8

    # Vow-based escalation
    vow_escalation_threshold: float = 0.6


@dataclass
class NarrativeConfig:
    """Narrative system configuration."""
    max_npcs_in_scene: int = 3
    max_active_beats: int = 5
    max_due_beats_per_scene: int = 2
    max_foreshadowing_items: int = 5

    # Memory limits
    max_recent_scene_summaries: int = 3
    max_key_relationships: int = 5
    max_major_beats: int = 3

    # Few-shot examples
    few_shot_example_count: int = 2
    max_example_length: int = 400


@dataclass
class FeedbackConfig:
    """Feedback learning configuration."""
    min_paragraphs_for_analysis: int = 20
    reanalysis_threshold: int = 10

    # Retrieval settings
    positive_examples: int = 2
    negative_examples: int = 1


@dataclass
class UIConfig:
    """UI-related configuration."""
    typewriter_speed_ms: int = 30
    auto_save_interval_seconds: int = 60
    max_message_history: int = 100

    # Audio defaults
    ambient_volume: float = 0.5
    music_volume: float = 0.6
    voice_volume: float = 0.8


@dataclass
class GameConfig:
    """Master configuration containing all sub-configs."""
    paths: PathConfig = field(default_factory=PathConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    director: DirectorConfig = field(default_factory=DirectorConfig)
    narrative: NarrativeConfig = field(default_factory=NarrativeConfig)
    feedback: FeedbackConfig = field(default_factory=FeedbackConfig)
    ui: UIConfig = field(default_factory=UIConfig)

    # Debug mode
    debug: bool = False
    phase_tracing: bool = False

    def __post_init__(self):
        self.debug = os.environ.get("STARFORGED_DEBUG", "").lower() in ("1", "true", "yes")
        self.phase_tracing = (
            os.environ.get("STARFORGED_PHASE_TRACING", "").lower() in ("1", "true", "yes")
        )


# Global config instance - import this in other modules
config = GameConfig()


def get_config() -> GameConfig:
    """Get the global configuration instance."""
    return config


def reload_config() -> GameConfig:
    """Reload configuration (useful for testing or runtime updates)."""
    global config
    config = GameConfig()
    return config
