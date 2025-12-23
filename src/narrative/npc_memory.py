"""
NPC Memory & Continuity System.

This module provides persistent memory for NPCs, allowing them to:
1. Recall past interactions with the player.
2. Avoid repeating themselves or contradicting past statements.
3. Make natural callbacks to previous events.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import random


@dataclass
class EpisodicMemory:
    """A single memory of an event or interaction."""

    scene: int
    topic: str
    content: str
    emotion: str  # e.g., "HIGH", "NEUTRAL", "CRITICAL"
    participants: List[str] = field(default_factory=lambda: ["player"])


@dataclass
class PromiseRecord:
    """Track promises and whether they were honored."""

    description: str
    scene_made: int
    kept: bool | None = None  # None = unresolved, True = kept, False = broken
    resolution_scene: Optional[int] = None


@dataclass
class MemoryWindow:
    """Short or long-term memory container with eviction."""

    entries: List[EpisodicMemory] = field(default_factory=list)
    max_entries: int = 8

    def add(self, memory: EpisodicMemory):
        self.entries.append(memory)
        if len(self.entries) > self.max_entries:
            self.entries.pop(0)


@dataclass
class NPCMemoryBank:
    """
    Persistent memory store for a specific NPC.
    """

    npc_id: str
    short_term: MemoryWindow = field(default_factory=lambda: MemoryWindow(max_entries=10))
    long_term: MemoryWindow = field(default_factory=lambda: MemoryWindow(max_entries=25))
    conversation_history: Dict[str, List[int]] = field(default_factory=dict)  # topic -> [scene_nums]
    promises: List[PromiseRecord] = field(default_factory=list)
    lies_told: List[str] = field(default_factory=list)
    secrets_revealed: List[str] = field(default_factory=list)
    notable_events: List[str] = field(default_factory=list)

    def record_interaction(self, scene_num: int, topic: str, content: str, emotion: str = "NEUTRAL"):
        """
        Store what happened in this conversation.
        """
        memory = EpisodicMemory(
            scene=scene_num,
            topic=topic,
            content=content,
            emotion=emotion
        )
        self.short_term.add(memory)

        if topic not in self.conversation_history:
            self.conversation_history[topic] = []
        self.conversation_history[topic].append(scene_num)

        if emotion in ["HIGH", "CRITICAL"]:
            self.promote_memory(memory)

    def record_notable_event(self, description: str, scene_num: int) -> None:
        """Persist a notable event into long-term recall."""
        self.notable_events.append(f"Scene {scene_num}: {description}")
        self.long_term.add(
            EpisodicMemory(
                scene=scene_num,
                topic="notable_event",
                content=description,
                emotion="CRITICAL",
            )
        )

    def record_promise(self, description: str, scene_num: int, kept: bool | None = None, resolution_scene: int | None = None) -> None:
        """Track promises and outcomes."""
        self.promises.append(
            PromiseRecord(
                description=description,
                scene_made=scene_num,
                kept=kept,
                resolution_scene=resolution_scene,
            )
        )

    def resolve_promise(self, description: str, kept: bool, resolution_scene: int) -> None:
        """Update status on an existing promise."""
        for promise in reversed(self.promises):
            if promise.description == description and promise.kept is None:
                promise.kept = kept
                promise.resolution_scene = resolution_scene
                if not kept:
                    self.record_notable_event(f"Promise broken: {description}", resolution_scene)
                return
        self.record_promise(description, scene_num=resolution_scene, kept=kept, resolution_scene=resolution_scene)

    def has_discussed(self, topic: str) -> bool:
        """Check if a topic has been discussed before."""
        return topic in self.conversation_history

    def get_last_discussion(self, topic: str) -> Optional[int]:
        """Get scene number of last discussion on this topic."""
        if topic in self.conversation_history:
            return self.conversation_history[topic][-1]
        return None

    def check_consistency(self, proposed_dialogue: str) -> List[str]:
        """
        Ensure NPC doesn't contradict past statements.
        Returns a list of potential contradiction warnings.
        (This is a placeholder for more advanced semantic checking)
        """
        # In a full ML implementation, this would semantically compare
        # proposed_dialogue against self.episodic_memory content.
        # For now, we return empty list as we can't easily do semantic analysis here yet.
        return []

    def generate_callback(self, current_scene: int) -> Optional[str]:
        """
        Generate a dialogue line referencing a past meaningful interaction.
        """
        significant_memories = [
            m for m in self.long_term.entries
            if m.emotion in ["HIGH", "CRITICAL"] and (current_scene - m.scene) > 1
        ]

        if significant_memories:
            memory = random.choice(significant_memories)
            return f"I haven't forgotten about {memory.topic} back when we were at scene {memory.scene}."

        return None

    def get_recent_summary(self) -> str:
        """Summarize what this NPC remembers most recently."""
        summary_lines = []
        for memory in self.short_term.entries[-3:]:
            summary_lines.append(f"Scene {memory.scene}: {memory.topic} ({memory.emotion})")

        if self.promises:
            unresolved = [p.description for p in self.promises if p.kept is None]
            kept = [p.description for p in self.promises if p.kept]
            broken = [p.description for p in self.promises if p.kept is False]
            if unresolved:
                summary_lines.append(f"Promises pending: {', '.join(unresolved)}")
            if kept:
                summary_lines.append(f"Promises kept: {', '.join(kept[-2:])}")
            if broken:
                summary_lines.append(f"Promises broken: {', '.join(broken[-2:])}")

        if self.notable_events:
            summary_lines.append(f"Notable: {self.notable_events[-1]}")

        return " | ".join(summary_lines)

    def promote_memory(self, memory: EpisodicMemory) -> None:
        """Move a memory into long-term storage for future callbacks."""
        self.long_term.add(memory)

    def to_dict(self) -> dict:
        """Serialize state."""
        return {
            "npc_id": self.npc_id,
            "short_term": [
                {
                    "scene": m.scene,
                    "topic": m.topic,
                    "content": m.content,
                    "emotion": m.emotion,
                    "participants": m.participants
                }
                for m in self.short_term.entries
            ],
            "long_term": [
                {
                    "scene": m.scene,
                    "topic": m.topic,
                    "content": m.content,
                    "emotion": m.emotion,
                    "participants": m.participants
                }
                for m in self.long_term.entries
            ],
            "conversation_history": self.conversation_history,
            "promises": [
                {
                    "description": p.description,
                    "scene_made": p.scene_made,
                    "kept": p.kept,
                    "resolution_scene": p.resolution_scene,
                }
                for p in self.promises
            ],
            "lies_told": self.lies_told,
            "secrets_revealed": self.secrets_revealed,
            "notable_events": self.notable_events,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "NPCMemoryBank":
        """Deserialize state."""
        bank = cls(npc_id=data.get("npc_id", "unknown"))

        for m_data in data.get("short_term", []):
            bank.short_term.add(EpisodicMemory(
                scene=m_data["scene"],
                topic=m_data["topic"],
                content=m_data["content"],
                emotion=m_data.get("emotion", "NEUTRAL"),
                participants=m_data.get("participants", ["player"])
            ))

        for m_data in data.get("long_term", []):
            bank.long_term.add(EpisodicMemory(
                scene=m_data["scene"],
                topic=m_data["topic"],
                content=m_data["content"],
                emotion=m_data.get("emotion", "NEUTRAL"),
                participants=m_data.get("participants", ["player"])
            ))

        bank.conversation_history = data.get("conversation_history", {})
        bank.promises = [
            PromiseRecord(
                description=p["description"],
                scene_made=p.get("scene_made", 0),
                kept=p.get("kept"),
                resolution_scene=p.get("resolution_scene"),
            )
            for p in data.get("promises", [])
        ]
        bank.lies_told = data.get("lies_told", [])
        bank.secrets_revealed = data.get("secrets_revealed", [])
        bank.notable_events = data.get("notable_events", [])

        return bank

