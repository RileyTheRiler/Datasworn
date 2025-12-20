"""
Character Voice System for Starforged AI Game Master.
Maintains NPC voice consistency across interactions.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import re


# ============================================================================
# Character Profile
# ============================================================================

@dataclass
class CharacterProfile:
    """
    Defines an NPC's unique voice characteristics.
    Used to maintain consistency across interactions.
    """
    name: str
    
    # Speech patterns
    speech_patterns: list[str] = field(default_factory=list)
    
    # Emotional states and how they manifest
    emotional_range: dict[str, str] = field(default_factory=dict)
    
    # Phrases this character uses
    signature_phrases: list[str] = field(default_factory=list)
    
    # Things this character would never say
    forbidden_expressions: list[str] = field(default_factory=list)
    
    # Physical mannerisms (for action descriptions)
    physical_mannerisms: list[str] = field(default_factory=list)
    
    # Current state
    current_disposition: str = "neutral"
    relationship_to_player: str = "stranger"
    
    # Secret the player doesn't know (for dramatic irony)
    secret: str = ""
    
    # ElevenLabs Voice ID
    voice_id: str | None = None
    
    def get_voice_injection(self) -> str:
        """
        Generate text to inject into narrator prompt for this character.
        """
        lines = [f"\n[CHARACTER VOICE: {self.name}]"]
        
        if self.speech_patterns:
            lines.append(f"Speech: {'; '.join(self.speech_patterns)}")
        
        if self.current_disposition in self.emotional_range:
            lines.append(f"Current mood: {self.emotional_range[self.current_disposition]}")
        
        if self.signature_phrases:
            lines.append(f"May use phrases like: \"{self.signature_phrases[0]}\"")
        
        if self.forbidden_expressions:
            lines.append(f"Will NOT say: {', '.join(self.forbidden_expressions[:3])}")
        
        if self.physical_mannerisms:
            lines.append(f"Mannerisms: {self.physical_mannerisms[0]}")
        
        lines.append(f"Relationship to player: {self.relationship_to_player}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        """Serialize for storage."""
        return {
            "name": self.name,
            "speech_patterns": self.speech_patterns,
            "emotional_range": self.emotional_range,
            "signature_phrases": self.signature_phrases,
            "forbidden_expressions": self.forbidden_expressions,
            "physical_mannerisms": self.physical_mannerisms,
            "current_disposition": self.current_disposition,
            "relationship_to_player": self.relationship_to_player,
            "secret": self.secret,
            "voice_id": self.voice_id,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CharacterProfile":
        """Deserialize from storage."""
        return cls(
            name=data.get("name", "Unknown"),
            speech_patterns=data.get("speech_patterns", []),
            emotional_range=data.get("emotional_range", {}),
            signature_phrases=data.get("signature_phrases", []),
            forbidden_expressions=data.get("forbidden_expressions", []),
            physical_mannerisms=data.get("physical_mannerisms", []),
            current_disposition=data.get("current_disposition", "neutral"),
            relationship_to_player=data.get("relationship_to_player", "stranger"),
            secret=data.get("secret", ""),
            voice_id=data.get("voice_id"),
        )


# ============================================================================
# Preset Archetypes
# ============================================================================

ARCHETYPE_PROFILES = {
    "gruff_veteran": CharacterProfile(
        name="Veteran Template",
        speech_patterns=[
            "Clipped, military cadence",
            "Drops articles when tense ('Check perimeter' not 'Check the perimeter')",
            "Uses ship/military terminology as metaphor",
            "Rarely asks questions—makes statements or gives orders",
        ],
        emotional_range={
            "default": "Guarded professionalism",
            "under_pressure": "Colder, more precise, fewer words",
            "rare_vulnerability": "Speaks slower, looks away, voice drops",
            "angry": "Goes quiet, not loud. Dangerous stillness.",
        },
        signature_phrases=[
            "That's not how this works.",
            "Check your six.",
            "Fuel's burning.",
            "We've got a situation.",
        ],
        forbidden_expressions=[
            "please",
            "I'm sorry",
            "I need help",
            "I'm scared",
        ],
        physical_mannerisms=[
            "Flexes scarred hands when thinking",
            "Checks exits when entering rooms",
            "Stands with weight on back foot, ready to move",
        ],
        voice_id="21m00Tcm4TlvDq8ikWAM"
    ),
    
    "nervous_scholar": CharacterProfile(
        name="Scholar Template",
        speech_patterns=[
            "Longer sentences with qualifications and caveats",
            "Technical jargon that they then explain",
            "Trails off mid-thought when distracted",
            "Speaks faster when excited about their subject",
        ],
        emotional_range={
            "default": "Distracted, focused on data",
            "excited": "Rapid speech, forgets social cues",
            "frightened": "Freezes, speaks in whispers, seeks facts to anchor to",
            "defensive": "Retreats into technical language as shield",
        },
        signature_phrases=[
            "Well, technically speaking...",
            "The data suggests—",
            "That's... that's not what the research indicates.",
            "Give me a moment to think.",
        ],
        forbidden_expressions=[
            "I don't know",
            "violence is the answer",
            "gut feeling",
        ],
        physical_mannerisms=[
            "Adjusts glasses or equivalent constantly",
            "Takes notes on everything",
            "Mumbles calculations under breath",
        ],
        voice_id="AZnzlk1XvdvUeBnXmlld"
    ),
    
    "pragmatic_merchant": CharacterProfile(
        name="Merchant Template",
        speech_patterns=[
            "Every sentence implies a transaction",
            "Friendly surface with calculating undertone",
            "Uses 'we' to imply partnership",
            "Deflects personal questions with humor",
        ],
        emotional_range={
            "default": "Professionally warm, always selling",
            "threatened": "Drops the act, cold and transactional",
            "genuine": "Rare moments of real connection, quickly covered",
            "greedy": "Eyes go sharp, smile widens",
        },
        signature_phrases=[
            "I think we can work something out.",
            "Let's talk numbers.",
            "Everyone's got a price.",
            "Nothing personal—just business.",
        ],
        forbidden_expressions=[
            "for free",
            "I trust you",
            "money doesn't matter",
        ],
        physical_mannerisms=[
            "Weighs objects in hand habitually",
            "Counts things (people, exits, valuables)",
            "Always positioned near the exit",
        ],
        voice_id="EXAVITQu4vr4xnSDxMaL"
    ),
    
    "charismatic_rebel": CharacterProfile(
        name="Rebel Template",
        speech_patterns=[
            "Passionate, uses 'we' for the cause",
            "Mixes poetry with profanity",
            "Interrupts when excited",
            "Speaks in manifestos when pushed",
        ],
        emotional_range={
            "default": "Burning conviction barely contained",
            "inspired": "Eyes bright, gestures wide, voice rising",
            "betrayed": "Cold fury, clipped words, no forgiveness",
            "doubtful": "Arguments with self, pacing",
        },
        signature_phrases=[
            "The Forge wasn't meant to be ruled.",
            "Someone has to stand up.",
            "Are you in, or are you part of the problem?",
            "They want us afraid. I refuse.",
        ],
        forbidden_expressions=[
            "the authorities are right",
            "it's not my fight",
            "some things can't be changed",
        ],
        physical_mannerisms=[
            "Can't sit still during meetings",
            "Touches scars from past protests",
            "Makes eye contact too intensely",
        ],
        voice_id="ErXwobaYiN019PkySvjV"
    ),
    
    "enigmatic_oracle": CharacterProfile(
        name="Oracle Template",
        speech_patterns=[
            "Speaks in questions that are really statements",
            "Long pauses before responding",
            "Metaphors drawn from the Forge itself",
            "Refers to things the player hasn't told them",
        ],
        emotional_range={
            "default": "Serene detachment, seeing beyond the moment",
            "concerned": "Cryptic warnings, refuses to be direct",
            "amused": "Knowing smile, as if watching a play unfold",
            "urgent": "Drops the mystery, speaks plain—which is terrifying",
        },
        signature_phrases=[
            "The stars remember what you've forgotten.",
            "Is that what you truly want to know?",
            "The path is already chosen. You simply haven't walked it yet.",
            "Interesting.",
        ],
        forbidden_expressions=[
            "I don't know",
            "that's random",
            "let me explain clearly",
        ],
        physical_mannerisms=[
            "Eyes focus on something no one else can see",
            "Touches things as if reading them",
            "Moves in ways that seem unhurried but cover ground quickly",
        ],
        voice_id="MF3mGyEYCl7XYWbV9V6O"
    ),
}


# ============================================================================
# Voice Manager
# ============================================================================

@dataclass
class VoiceManager:
    """
    Manages character voices across the campaign.
    """
    profiles: dict[str, CharacterProfile] = field(default_factory=dict)
    active_characters: list[str] = field(default_factory=list)  # Characters in current scene
    
    def add_character(self, profile: CharacterProfile) -> None:
        """Add or update a character profile."""
        self.profiles[profile.name.lower()] = profile
    
    def get_character(self, name: str) -> CharacterProfile | None:
        """Get a character by name (case-insensitive)."""
        return self.profiles.get(name.lower())
    
    def create_from_archetype(self, name: str, archetype: str) -> CharacterProfile:
        """
        Create a new character based on an archetype.
        
        Args:
            name: The character's actual name
            archetype: One of the archetype keys (gruff_veteran, etc.)
        
        Returns:
            New CharacterProfile based on archetype
        """
        template = ARCHETYPE_PROFILES.get(archetype)
        if not template:
            # Default to a neutral template
            return CharacterProfile(name=name)
        
        # Create new profile based on template
        profile = CharacterProfile(
            name=name,
            speech_patterns=template.speech_patterns.copy(),
            emotional_range=template.emotional_range.copy(),
            signature_phrases=template.signature_phrases.copy(),
            forbidden_expressions=template.forbidden_expressions.copy(),
            physical_mannerisms=template.physical_mannerisms.copy(),
            voice_id=template.voice_id
        )
        
        self.add_character(profile)
        return profile
    
    def set_active_characters(self, names: list[str]) -> None:
        """Set which characters are in the current scene."""
        self.active_characters = [n.lower() for n in names]
    
    def get_voice_prompt(self) -> str:
        """
        Generate voice injection text for all active characters.
        """
        parts = []
        for name in self.active_characters:
            profile = self.get_character(name)
            if profile:
                parts.append(profile.get_voice_injection())
        
        return "\n".join(parts) if parts else ""
    
    def validate_dialogue(self, text: str, character_name: str) -> tuple[bool, list[str]]:
        """
        Check if dialogue is consistent with a character's voice.
        
        Returns:
            Tuple of (is_valid, list of issues)
        """
        profile = self.get_character(character_name)
        if not profile:
            return True, []  # Can't validate unknown character
        
        issues = []
        text_lower = text.lower()
        
        # Check forbidden expressions
        for expr in profile.forbidden_expressions:
            if expr.lower() in text_lower:
                issues.append(f"{character_name} would not say: '{expr}'")
        
        return len(issues) == 0, issues
    
    def update_disposition(self, name: str, disposition: str) -> None:
        """Update a character's current emotional state."""
        profile = self.get_character(name)
        if profile:
            profile.current_disposition = disposition
    
    def update_relationship(self, name: str, relationship: str) -> None:
        """Update a character's relationship to the player."""
        profile = self.get_character(name)
        if profile:
            profile.relationship_to_player = relationship
    
    def to_dict(self) -> dict:
        """Serialize for storage."""
        return {
            "profiles": {k: v.to_dict() for k, v in self.profiles.items()},
            "active_characters": self.active_characters,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "VoiceManager":
        """Deserialize from storage."""
        manager = cls()
        
        for name, profile_data in data.get("profiles", {}).items():
            manager.profiles[name] = CharacterProfile.from_dict(profile_data)
        
        manager.active_characters = data.get("active_characters", [])
        
        return manager


# ============================================================================
# Convenience Functions
# ============================================================================

def create_voice_manager() -> VoiceManager:
    """Create a new voice manager."""
    return VoiceManager()


def get_archetype_names() -> list[str]:
    """Get available archetype names."""
    return list(ARCHETYPE_PROFILES.keys())


# ============================================================================
# NPC Knowledge Model (Beliefs & Rumors)
# ============================================================================

@dataclass
class BeliefEntry:
    """A single belief an NPC holds about the world."""
    subject: str  # What/who the belief is about
    belief: str  # What they believe
    confidence: float = 0.8  # 0-1 how sure they are
    source: str = "observation"  # Where they learned this
    scene_learned: int = 0  # When they learned it
    is_accurate: bool = True  # Does this match reality?


@dataclass
class Rumor:
    """A rumor that can propagate between NPCs."""
    content: str
    origin_npc: str
    credibility: float = 0.5  # 0-1 how believable
    spread_count: int = 0  # How many NPCs have heard it
    scene_created: int = 0


@dataclass 
class NPCKnowledge:
    """
    Tracks what an NPC knows, believes, and has heard.
    Prevents "god knowledge" - NPCs only know what they've learned.
    """
    npc_name: str
    
    # What they believe to be true
    beliefs: dict[str, BeliefEntry] = field(default_factory=dict)
    
    # Rumors they've heard
    rumors: list[Rumor] = field(default_factory=list)
    
    # Last known player location/status
    last_known_player_location: str = ""
    last_seen_player_scene: int = 0
    
    # What triggers they're aware of
    known_events: list[str] = field(default_factory=list)
    
    def add_belief(
        self,
        subject: str,
        belief: str,
        confidence: float = 0.8,
        source: str = "observation",
        scene: int = 0,
        is_accurate: bool = True,
    ) -> None:
        """Add or update a belief about something."""
        self.beliefs[subject.lower()] = BeliefEntry(
            subject=subject,
            belief=belief,
            confidence=min(1.0, max(0.0, confidence)),
            source=source,
            scene_learned=scene,
            is_accurate=is_accurate,
        )
    
    def get_belief(self, subject: str) -> BeliefEntry | None:
        """Get what the NPC believes about a subject."""
        return self.beliefs.get(subject.lower())
    
    def has_outdated_info(self, subject: str, current_scene: int, staleness_threshold: int = 5) -> bool:
        """Check if NPC's knowledge about a subject is outdated."""
        belief = self.beliefs.get(subject.lower())
        if not belief:
            return False
        return (current_scene - belief.scene_learned) > staleness_threshold
    
    def hear_rumor(self, rumor: Rumor, trust_source: float = 0.5) -> bool:
        """
        NPC hears a rumor. Returns True if they believe it.
        """
        # Check if already heard this rumor
        for existing in self.rumors:
            if existing.content == rumor.content:
                return False
        
        # Decide to believe based on credibility and trust
        import random
        believe_chance = rumor.credibility * trust_source
        
        if random.random() < believe_chance:
            self.rumors.append(rumor)
            rumor.spread_count += 1
            return True
        return False
    
    def spread_rumor(self, content: str, scene: int) -> Rumor:
        """Create a new rumor from this NPC."""
        rumor = Rumor(
            content=content,
            origin_npc=self.npc_name,
            credibility=0.5,
            spread_count=0,
            scene_created=scene,
        )
        self.rumors.append(rumor)
        return rumor
    
    def update_player_location(self, location: str, scene: int) -> None:
        """Update where NPC last saw/heard the player was."""
        self.last_known_player_location = location
        self.last_seen_player_scene = scene
    
    def get_knowledge_context(self, current_scene: int) -> str:
        """
        Generate context string about what this NPC knows.
        Used for narrator guidance.
        """
        lines = [f"[{self.npc_name}'s KNOWLEDGE]"]
        
        # Player location knowledge
        if self.last_known_player_location:
            scenes_ago = current_scene - self.last_seen_player_scene
            if scenes_ago == 0:
                lines.append(f"Knows player is at: {self.last_known_player_location}")
            elif scenes_ago <= 3:
                lines.append(f"Last knew player was at: {self.last_known_player_location} ({scenes_ago} scenes ago)")
            else:
                lines.append(f"Has outdated info - still thinks player at: {self.last_known_player_location}")
        
        # Key beliefs
        relevant_beliefs = [
            b for b in self.beliefs.values() 
            if b.confidence > 0.5
        ][:3]
        if relevant_beliefs:
            for belief in relevant_beliefs:
                accuracy = "WRONG" if not belief.is_accurate else "accurate"
                lines.append(f"Believes ({accuracy}): {belief.subject} - {belief.belief}")
        
        # Active rumors
        if self.rumors:
            lines.append(f"Has heard {len(self.rumors)} rumors")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "npc_name": self.npc_name,
            "beliefs": {k: {
                "subject": v.subject,
                "belief": v.belief,
                "confidence": v.confidence,
                "source": v.source,
                "scene_learned": v.scene_learned,
                "is_accurate": v.is_accurate,
            } for k, v in self.beliefs.items()},
            "rumors": [{
                "content": r.content,
                "origin_npc": r.origin_npc,
                "credibility": r.credibility,
                "spread_count": r.spread_count,
                "scene_created": r.scene_created,
            } for r in self.rumors],
            "last_known_player_location": self.last_known_player_location,
            "last_seen_player_scene": self.last_seen_player_scene,
            "known_events": self.known_events,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "NPCKnowledge":
        knowledge = cls(npc_name=data.get("npc_name", "Unknown"))
        
        for key, bdata in data.get("beliefs", {}).items():
            knowledge.beliefs[key] = BeliefEntry(
                subject=bdata.get("subject", ""),
                belief=bdata.get("belief", ""),
                confidence=bdata.get("confidence", 0.8),
                source=bdata.get("source", "unknown"),
                scene_learned=bdata.get("scene_learned", 0),
                is_accurate=bdata.get("is_accurate", True),
            )
        
        for rdata in data.get("rumors", []):
            knowledge.rumors.append(Rumor(
                content=rdata.get("content", ""),
                origin_npc=rdata.get("origin_npc", ""),
                credibility=rdata.get("credibility", 0.5),
                spread_count=rdata.get("spread_count", 0),
                scene_created=rdata.get("scene_created", 0),
            ))
        
        knowledge.last_known_player_location = data.get("last_known_player_location", "")
        knowledge.last_seen_player_scene = data.get("last_seen_player_scene", 0)
        knowledge.known_events = data.get("known_events", [])
        
        return knowledge


class KnowledgeNetwork:
    """
    Manages knowledge across all NPCs.
    Handles rumor propagation between connected NPCs.
    """
    
    def __init__(self):
        self.npc_knowledge: dict[str, NPCKnowledge] = {}
    
    def get_or_create(self, npc_name: str) -> NPCKnowledge:
        """Get NPC knowledge, creating if needed."""
        key = npc_name.lower()
        if key not in self.npc_knowledge:
            self.npc_knowledge[key] = NPCKnowledge(npc_name=npc_name)
        return self.npc_knowledge[key]
    
    def propagate_rumor(
        self,
        rumor: Rumor,
        from_npc: str,
        to_npcs: list[str],
        trust_levels: dict[str, float] | None = None,
    ) -> list[str]:
        """
        Spread a rumor from one NPC to others.
        
        Returns:
            List of NPCs who believed the rumor
        """
        believers = []
        trust_levels = trust_levels or {}
        
        for npc_name in to_npcs:
            if npc_name.lower() == from_npc.lower():
                continue
            
            knowledge = self.get_or_create(npc_name)
            trust = trust_levels.get(npc_name.lower(), 0.5)
            
            if knowledge.hear_rumor(rumor, trust):
                believers.append(npc_name)
        
        return believers
    
    def broadcast_event(self, event: str, witnesses: list[str], scene: int) -> None:
        """All witness NPCs learn about an event."""
        for npc_name in witnesses:
            knowledge = self.get_or_create(npc_name)
            knowledge.known_events.append(event)
            knowledge.add_belief(
                subject=f"event_{len(knowledge.known_events)}",
                belief=event,
                confidence=0.9,
                source="witnessed",
                scene=scene,
                is_accurate=True,
            )
    
    def to_dict(self) -> dict:
        return {
            "npc_knowledge": {k: v.to_dict() for k, v in self.npc_knowledge.items()}
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeNetwork":
        network = cls()
        for key, kdata in data.get("npc_knowledge", {}).items():
            network.npc_knowledge[key] = NPCKnowledge.from_dict(kdata)
        return network

