from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import json
import os
from pathlib import Path

@dataclass
class PracticeCard:
    id: str
    text: str
    difficulty: str  # 'beginner', 'intermediate', 'advanced'
    metadata: Dict[str, any] = field(default_factory=dict)

@dataclass
class PracticeSet:
    id: str
    title: str
    difficulty: str
    cards: List[PracticeCard] = field(default_factory=list)
    is_default: bool = False
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "difficulty": self.difficulty,
            "cards": [vars(c) for c in self.cards],
            "is_default": self.is_default,
            "card_count": len(self.cards)
        }

@dataclass
class UserProgress:
    practice_counts: Dict[str, int] = field(default_factory=dict)  # card_id -> count
    recording_counts: Dict[str, int] = field(default_factory=dict) # card_id -> count
    total_time_ms: Dict[str, int] = field(default_factory=dict)    # card_id -> ms
    
    def to_dict(self):
        return {
            "practice_counts": self.practice_counts,
            "recording_counts": self.recording_counts,
            "total_time_ms": self.total_time_ms
        }

DEFAULT_CARD_SETS = [
    PracticeSet(
        id="beginner_words",
        title="Simple words starting",
        difficulty="beginner",
        is_default=True,
        cards=[
            PracticeCard("b1", "Alpha", "beginner"),
            PracticeCard("b2", "Bravo", "beginner"),
            PracticeCard("b3", "Charlie", "beginner"),
            PracticeCard("b4", "Delta", "beginner"),
            PracticeCard("b5", "Echo", "beginner"),
        ]
    ),
    PracticeSet(
        id="beginner_calendar",
        title="Months, days, and seasons",
        difficulty="beginner",
        is_default=True,
        cards=[
            PracticeCard("b6", "January", "beginner"),
            PracticeCard("b7", "Monday", "beginner"),
            PracticeCard("b8", "Summer", "beginner"),
        ]
    ),
    PracticeSet(
        id="intermediate_phrases",
        title="Simple phrases",
        difficulty="intermediate",
        is_default=True,
        cards=[
            PracticeCard("i1", "The quick brown fox jumps over the lazy dog.", "intermediate"),
            PracticeCard("i2", "She sells seashells by the seashore.", "intermediate"),
        ]
    ),
    PracticeSet(
        id="advanced_excerpts",
        title="Book excerpts",
        difficulty="advanced",
        is_default=True,
        cards=[
            PracticeCard("a1", "Call me Ishmael. Some years ago—never mind how long precisely—having little or no money in my purse, and nothing particular to interest me on shore, I thought I would sail about a little and see the watery part of the world.", "advanced"),
        ]
    )
]

class PracticeManager:
    def __init__(self, data_dir: str = "data/practice"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.custom_sets_path = self.data_dir / "custom_sets.json"
        self.progress_path = self.data_dir / "progress.json"
        
        self.custom_sets = self._load_custom_sets()
        self.progress = self._load_progress()

    def _load_custom_sets(self) -> List[PracticeSet]:
        if not self.custom_sets_path.exists():
            return []
        try:
            with open(self.custom_sets_path, 'r') as f:
                data = json.load(f)
                return [PracticeSet(
                    id=s['id'],
                    title=s['title'],
                    difficulty=s['difficulty'],
                    is_default=False,
                    cards=[PracticeCard(**c) for c in s['cards']]
                ) for s in data]
        except Exception:
            return []

    def _load_progress(self) -> UserProgress:
        if not self.progress_path.exists():
            return UserProgress()
        try:
            with open(self.progress_path, 'r') as f:
                data = json.load(f)
                return UserProgress(
                    practice_counts=data.get('practice_counts', {}),
                    recording_counts=data.get('recording_counts', {}),
                    total_time_ms=data.get('total_time_ms', {})
                )
        except Exception:
            return UserProgress()

    def save_custom_sets(self):
        with open(self.custom_sets_path, 'w') as f:
            json.dump([s.to_dict() for s in self.custom_sets], f, indent=2)

    def save_progress(self):
        with open(self.progress_path, 'w') as f:
            json.dump(self.progress.to_dict(), f, indent=2)

    def get_all_sets(self) -> List[PracticeSet]:
        return DEFAULT_CARD_SETS + self.custom_sets

    def get_set(self, set_id: str) -> Optional[PracticeSet]:
        all_sets = self.get_all_sets()
        return next((s for s in all_sets if s.id == set_id), None)

    def add_custom_set(self, title: str, difficulty: str, cards: List[str]):
        import uuid
        set_id = str(uuid.uuid4())
        new_cards = [PracticeCard(str(uuid.uuid4()), text, difficulty) for text in cards]
        new_set = PracticeSet(set_id, title, difficulty, new_cards, False)
        self.custom_sets.append(new_set)
        self.save_custom_sets()
        return new_set

    def track_usage(self, card_id: str, is_recording: bool, time_ms: int):
        self.progress.practice_counts[card_id] = self.progress.practice_counts.get(card_id, 0) + 1
        if is_recording:
            self.progress.recording_counts[card_id] = self.progress.recording_counts.get(card_id, 0) + 1
        self.progress.total_time_ms[card_id] = self.progress.total_time_ms.get(card_id, 0) + time_ms
        self.save_progress()
