"""
Memory Architecture for Starforged AI Game Master.
Implements three-tier memory system for maintaining narrative context.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import ollama


# ============================================================================
# Memory Tiers
# ============================================================================

@dataclass
class ActiveContext:
    """
    Tier 1: Active Context - Always present in LLM context.
    Contains immediate scene information.
    """
    current_scene: str = ""
    active_npcs: list[str] = field(default_factory=list)
    player_stats: dict[str, Any] = field(default_factory=dict)
    current_vow: str = ""
    recent_exchanges: list[dict] = field(default_factory=list)  # Last 3-5
    
    def add_exchange(self, role: str, content: str, max_exchanges: int = 5) -> None:
        """Add an exchange, keeping only the most recent."""
        self.recent_exchanges.append({"role": role, "content": content[:500]})
        if len(self.recent_exchanges) > max_exchanges:
            self.recent_exchanges.pop(0)
    
    def to_context_string(self) -> str:
        """Format for injection into LLM context."""
        parts = []
        
        if self.current_scene:
            parts.append(f"[Current Scene]\n{self.current_scene}")
        
        if self.active_npcs:
            parts.append(f"[NPCs Present: {', '.join(self.active_npcs)}]")
        
        if self.current_vow:
            parts.append(f"[Active Vow: {self.current_vow}]")
        
        return "\n\n".join(parts)


@dataclass
class SessionBuffer:
    """
    Tier 2: Session Summary - Compressed recent events.
    Contains scene summaries from current session.
    """
    scene_summaries: list[str] = field(default_factory=list)
    decisions_made: list[str] = field(default_factory=list)
    npcs_encountered: dict[str, str] = field(default_factory=dict)  # name -> last disposition
    vow_progress: dict[str, float] = field(default_factory=dict)
    
    def add_scene_summary(self, summary: str, max_scenes: int = 10) -> None:
        """Add a scene summary, keeping only recent ones."""
        self.scene_summaries.append(summary)
        if len(self.scene_summaries) > max_scenes:
            self.scene_summaries.pop(0)
    
    def record_decision(self, decision: str) -> None:
        """Record a significant player decision."""
        self.decisions_made.append(decision)
        if len(self.decisions_made) > 10:
            self.decisions_made.pop(0)
    
    def to_context_string(self) -> str:
        """Format for injection into LLM context."""
        parts = []
        
        if self.scene_summaries:
            recent = self.scene_summaries[-3:]  # Last 3 scenes
            parts.append("[Recent Events]\n" + "\n".join(f"- {s}" for s in recent))
        
        if self.decisions_made:
            recent = self.decisions_made[-3:]
            parts.append("[Key Decisions]\n" + "\n".join(f"- {d}" for d in recent))
        
        return "\n\n".join(parts)


@dataclass
class CampaignSummary:
    """
    Tier 3: Campaign Summary - Highly compressed long-term memory.
    Contains major beats and world state changes.
    """
    major_beats: list[str] = field(default_factory=list)
    key_relationships: dict[str, str] = field(default_factory=dict)  # npc -> relationship
    world_changes: list[str] = field(default_factory=list)
    themes: list[str] = field(default_factory=list)
    
    def add_major_beat(self, beat: str) -> None:
        """Record a major story beat."""
        self.major_beats.append(beat)
    
    def set_relationship(self, npc: str, relationship: str) -> None:
        """Update relationship with an NPC."""
        self.key_relationships[npc] = relationship
    
    def to_context_string(self) -> str:
        """Format for injection into LLM context."""
        parts = []
        
        if self.major_beats:
            parts.append("[Campaign History]\n" + "\n".join(f"- {b}" for b in self.major_beats[-5:]))
        
        if self.key_relationships:
            rels = [f"{npc}: {rel}" for npc, rel in list(self.key_relationships.items())[:5]]
            parts.append("[Key Relationships]\n" + "\n".join(f"- {r}" for r in rels))
        
        return "\n\n".join(parts)


# ============================================================================
# Memory Manager
# ============================================================================

@dataclass
class MemoryManager:
    """
    Manages all three tiers of memory and context building.
    """
    active: ActiveContext = field(default_factory=ActiveContext)
    session: SessionBuffer = field(default_factory=SessionBuffer)
    campaign: CampaignSummary = field(default_factory=CampaignSummary)
    model: str = "llama3.1"
    _client: ollama.Client = field(default_factory=ollama.Client, repr=False)
    
    def summarize_scene(self, scene_text: str) -> str:
        """
        Use LLM to compress a scene into 2-3 sentences.
        Falls back to truncation if LLM unavailable.
        """
        if len(scene_text) < 200:
            return scene_text
        
        try:
            response = self._client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Summarize the following scene in 2-3 sentences. Focus on key events, decisions made, and consequences. Be concise."
                    },
                    {"role": "user", "content": scene_text}
                ],
                options={"temperature": 0.3, "num_predict": 150}
            )
            return response.get("message", {}).get("content", scene_text[:200])
        except Exception:
            # Fallback to simple truncation
            return scene_text[:200] + "..."
    
    def summarize_session(self) -> str:
        """
        Compress all session scenes into a single paragraph.
        """
        if not self.session.scene_summaries:
            return ""
        
        all_scenes = "\n".join(self.session.scene_summaries)
        
        try:
            response = self._client.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Compress these scene summaries into a single paragraph capturing the session's key events. Maximum 4 sentences."
                    },
                    {"role": "user", "content": all_scenes}
                ],
                options={"temperature": 0.3, "num_predict": 200}
            )
            return response.get("message", {}).get("content", all_scenes[:300])
        except Exception:
            return all_scenes[:300]
    
    def build_narrator_context(self, token_budget: int = 3000) -> str:
        """
        Build context string for narrator with intelligent allocation.
        
        Allocation strategy:
        - 40% active context (immediate scene)
        - 30% session buffer (recent events)
        - 20% lorebook entries (if available)
        - 10% campaign summary (major beats)
        
        Args:
            token_budget: Approximate character budget (~4 chars per token)
        
        Returns:
            Formatted context string
        """
        char_budget = token_budget * 4
        
        # Calculate allocations
        active_budget = int(char_budget * 0.40)
        session_budget = int(char_budget * 0.30)
        campaign_budget = int(char_budget * 0.10)
        # Reserve 20% for lorebook (handled separately)
        
        parts = []
        
        # Active context (highest priority)
        active_str = self.active.to_context_string()
        if active_str:
            parts.append(active_str[:active_budget])
        
        # Session buffer
        session_str = self.session.to_context_string()
        if session_str:
            parts.append(session_str[:session_budget])
        
        # Campaign summary
        campaign_str = self.campaign.to_context_string()
        if campaign_str:
            parts.append(campaign_str[:campaign_budget])
        
        return "\n\n---\n\n".join(parts)
    
    def process_scene_end(self, scene_text: str, npcs: list[str] = None) -> None:
        """
        Called when a scene ends. Updates all memory tiers.
        
        Args:
            scene_text: The narrative text from the scene
            npcs: NPCs that appeared in the scene
        """
        # Summarize and add to session
        summary = self.summarize_scene(scene_text)
        self.session.add_scene_summary(summary)
        
        # Update NPC tracking
        if npcs:
            for npc in npcs:
                self.session.npcs_encountered[npc] = "appeared this session"
        
        # Update active context
        self.active.current_scene = scene_text[:500]  # Keep recent scene
    
    def end_session(self) -> None:
        """
        Called at session end. Compresses session to campaign memory.
        """
        # Summarize entire session
        session_summary = self.summarize_session()
        if session_summary:
            self.campaign.add_major_beat(f"Session: {session_summary}")
        
        # Persist important NPCs
        for npc, disposition in self.session.npcs_encountered.items():
            if npc not in self.campaign.key_relationships:
                self.campaign.set_relationship(npc, disposition)
        
        # Clear session buffer for next session
        self.session = SessionBuffer()
    
    def to_dict(self) -> dict:
        """Serialize for storage."""
        return {
            "active": {
                "current_scene": self.active.current_scene,
                "active_npcs": self.active.active_npcs,
                "current_vow": self.active.current_vow,
                "recent_exchanges": self.active.recent_exchanges,
            },
            "session": {
                "scene_summaries": self.session.scene_summaries,
                "decisions_made": self.session.decisions_made,
                "npcs_encountered": self.session.npcs_encountered,
            },
            "campaign": {
                "major_beats": self.campaign.major_beats,
                "key_relationships": self.campaign.key_relationships,
                "world_changes": self.campaign.world_changes,
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict, model: str = "llama3.1") -> "MemoryManager":
        """Deserialize from storage."""
        manager = cls(model=model)
        
        if "active" in data:
            manager.active.current_scene = data["active"].get("current_scene", "")
            manager.active.active_npcs = data["active"].get("active_npcs", [])
            manager.active.current_vow = data["active"].get("current_vow", "")
            manager.active.recent_exchanges = data["active"].get("recent_exchanges", [])
        
        if "session" in data:
            manager.session.scene_summaries = data["session"].get("scene_summaries", [])
            manager.session.decisions_made = data["session"].get("decisions_made", [])
            manager.session.npcs_encountered = data["session"].get("npcs_encountered", {})
        
        if "campaign" in data:
            manager.campaign.major_beats = data["campaign"].get("major_beats", [])
            manager.campaign.key_relationships = data["campaign"].get("key_relationships", {})
            manager.campaign.world_changes = data["campaign"].get("world_changes", [])
        
        return manager


# ============================================================================
# Entity Extraction (for Knowledge Graph integration)
# ============================================================================

def extract_entities(narrative_text: str, client: ollama.Client = None, model: str = "llama3.1") -> list[dict]:
    """
    Extract entities (NPCs, locations, items) from narrative text.
    Uses LLM for extraction.
    
    Returns:
        List of dicts with keys: type, name, description
    """
    if client is None:
        client = ollama.Client()
    
    prompt = """Extract any named entities from this narrative text.
Return a JSON array of objects with these fields:
- "type": "NPC" | "LOCATION" | "ITEM" | "FACTION"
- "name": the entity's name
- "description": brief description based on context

Only include entities that are explicitly named. Return [] if none found.
Output ONLY the JSON array, nothing else.

Text:
""" + narrative_text
    
    try:
        response = client.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.1, "num_predict": 500}
        )
        
        content = response.get("message", {}).get("content", "[]")
        
        # Parse JSON
        import json
        # Find JSON in response
        start = content.find("[")
        end = content.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(content[start:end])
    except Exception:
        pass
    
    return []


# ============================================================================
# Convenience Functions
# ============================================================================

def create_memory_manager(model: str = "llama3.1") -> MemoryManager:
    """Create a new memory manager with default settings."""
    return MemoryManager(model=model)
