"""
OCEAN Personality Model & Cinematography System.
Implements Big Five personality traits and shot selection.

OCEAN = Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism
Cinematography = Wide/Medium/Close shot selection based on emotional context.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List
import random
import re


# ============================================================================
# OCEAN Personality Model (Big Five)
# ============================================================================

@dataclass
class OCEANProfile:
    """
    Big Five personality traits for an NPC.
    Each trait is 0.0 (low) to 1.0 (high).
    """
    openness: float = 0.5  # Creativity, curiosity vs. caution
    conscientiousness: float = 0.5  # Organization, dependability vs. careless
    extraversion: float = 0.5  # Outgoing, energetic vs. reserved
    agreeableness: float = 0.5  # Friendly, compassionate vs. antagonistic
    neuroticism: float = 0.5  # Sensitive, nervous vs. confident, calm
    
    def get_dialogue_style(self) -> dict:
        """Generate dialogue style guidance based on traits."""
        style = {
            "verbosity": "normal",
            "formality": "casual",
            "emotional_tone": "neutral",
            "confidence": "average",
            "friendliness": "neutral",
        }
        
        # Extraversion affects verbosity
        if self.extraversion > 0.7:
            style["verbosity"] = "talkative"
        elif self.extraversion < 0.3:
            style["verbosity"] = "terse"
        
        # Conscientiousness affects formality
        if self.conscientiousness > 0.7:
            style["formality"] = "formal"
        elif self.conscientiousness < 0.3:
            style["formality"] = "sloppy"
        
        # Neuroticism affects emotional tone
        if self.neuroticism > 0.7:
            style["emotional_tone"] = "anxious"
        elif self.neuroticism < 0.3:
            style["emotional_tone"] = "calm"
        
        # Agreeableness affects friendliness
        if self.agreeableness > 0.7:
            style["friendliness"] = "warm"
        elif self.agreeableness < 0.3:
            style["friendliness"] = "cold"
        
        # Openness affects confidence/creativity
        if self.openness > 0.7:
            style["confidence"] = "curious"
        elif self.openness < 0.3:
            style["confidence"] = "skeptical"
        
        return style
    
    def get_narrator_context(self, npc_name: str) -> str:
        """Generate narrator context for this personality."""
        style = self.get_dialogue_style()
        
        lines = [f"[PERSONALITY: {npc_name}]"]
        lines.append(f"OCEAN: O={self.openness:.1f} C={self.conscientiousness:.1f} "
                    f"E={self.extraversion:.1f} A={self.agreeableness:.1f} N={self.neuroticism:.1f}")
        
        # Generate personality description
        traits = []
        if self.openness > 0.6:
            traits.append("curious and imaginative")
        elif self.openness < 0.4:
            traits.append("practical and cautious")
        
        if self.conscientiousness > 0.6:
            traits.append("organized and reliable")
        elif self.conscientiousness < 0.4:
            traits.append("spontaneous and flexible")
        
        if self.extraversion > 0.6:
            traits.append("outgoing and energetic")
        elif self.extraversion < 0.4:
            traits.append("reserved and introspective")
        
        if self.agreeableness > 0.6:
            traits.append("kind and cooperative")
        elif self.agreeableness < 0.4:
            traits.append("competitive and skeptical")
        
        if self.neuroticism > 0.6:
            traits.append("sensitive and anxious")
        elif self.neuroticism < 0.4:
            traits.append("confident and stable")
        
        if traits:
            lines.append(f"Personality: {', '.join(traits)}")
        
        lines.append(f"Dialogue style: {style['verbosity']}, {style['formality']}, {style['friendliness']}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "openness": self.openness,
            "conscientiousness": self.conscientiousness,
            "extraversion": self.extraversion,
            "agreeableness": self.agreeableness,
            "neuroticism": self.neuroticism,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "OCEANProfile":
        return cls(
            openness=data.get("openness", 0.5),
            conscientiousness=data.get("conscientiousness", 0.5),
            extraversion=data.get("extraversion", 0.5),
            agreeableness=data.get("agreeableness", 0.5),
            neuroticism=data.get("neuroticism", 0.5),
        )


# Pre-built personality archetypes
PERSONALITY_ARCHETYPES = {
    "hero": OCEANProfile(openness=0.7, conscientiousness=0.8, extraversion=0.6, agreeableness=0.7, neuroticism=0.3),
    "villain": OCEANProfile(openness=0.5, conscientiousness=0.7, extraversion=0.6, agreeableness=0.2, neuroticism=0.4),
    "mentor": OCEANProfile(openness=0.8, conscientiousness=0.7, extraversion=0.5, agreeableness=0.8, neuroticism=0.2),
    "trickster": OCEANProfile(openness=0.9, conscientiousness=0.3, extraversion=0.8, agreeableness=0.5, neuroticism=0.4),
    "guardian": OCEANProfile(openness=0.4, conscientiousness=0.9, extraversion=0.4, agreeableness=0.6, neuroticism=0.3),
    "rebel": OCEANProfile(openness=0.7, conscientiousness=0.3, extraversion=0.7, agreeableness=0.4, neuroticism=0.5),
    "sage": OCEANProfile(openness=0.9, conscientiousness=0.6, extraversion=0.3, agreeableness=0.7, neuroticism=0.2),
    "everyman": OCEANProfile(openness=0.5, conscientiousness=0.5, extraversion=0.5, agreeableness=0.6, neuroticism=0.5),
    "outlaw": OCEANProfile(openness=0.6, conscientiousness=0.2, extraversion=0.6, agreeableness=0.3, neuroticism=0.6),
    "caregiver": OCEANProfile(openness=0.5, conscientiousness=0.7, extraversion=0.6, agreeableness=0.9, neuroticism=0.4),
}


# ============================================================================
# Character Profile & Knowledge Guardrails
# ============================================================================


class KnowledgeFilter(Enum):
    """Controls how broadly an NPC can answer questions."""

    NONE = "none"  # Knows broadly about the world
    MILD = "mild"  # Knows what is explicitly scoped and close adjacencies
    STRICT = "strict"  # Only speaks from provided knowledge


@dataclass
class CharacterProfile:
    """Describes the character's identity and speaking style."""

    player_name: str = "Alex"
    role: str = "villager"
    pronouns: str = "they/them"
    stage_of_life: str = "adult"
    hobbies: list[str] = field(default_factory=lambda: ["people watching"])
    description: str = ""  # evocative backstory and disposition
    core_description: str = ""  # magazine-style character read
    motivation: str = "keep the peace"
    motivations: list[str] = field(default_factory=list)
    flaws: list[str] = field(default_factory=lambda: ["overthinks"])
    flaw_sentence: str = ""
    adjectives: list[str] = field(default_factory=lambda: ["plainspoken"])
    colloquialisms: list[str] = field(default_factory=lambda: ["gonna", "buddy"])
    dialog_style: str = "warm but cautious"
    example_dialog: str = ""
    dialogue_examples: list[str] = field(default_factory=list)
    personality_traits: list[str] = field(default_factory=list)
    voice: str = "default"

    def summarize(self) -> str:
        hobbies = ", ".join(self.hobbies)
        flaws = ", ".join(self.flaws)
        adjectives = ", ".join(self.adjectives)
        return (
            f"Role: {self.role}; Pronouns: {self.pronouns}; Stage: {self.stage_of_life}. "
            f"Hobbies: {hobbies or 'unspecified'}; Motivation: {self.motivation}. "
            f"Flaws: {flaws or 'none noted'}; Voice: {self.dialog_style} ({adjectives})."
        )

    def detailed_sheet(self, npc_name: str) -> str:
        """Rich profile block for grounding dialogue and narration."""

        core = self.core_description or self.description or "Everyday local with little renown."
        motivations = self.motivations or ([self.motivation] if self.motivation else [])
        motivations_line = "; ".join(motivations[:4]) or "Protect their daily routine and the people nearby."
        flaws_line = self.flaw_sentence or ("; ".join(self.flaws) if self.flaws else "" )
        adjectives_line = ", ".join(self.adjectives) or "plainspoken"
        hobbies_line = ", ".join(self.hobbies) or "unspecified pastimes"
        examples = self.dialogue_examples or ([self.example_dialog] if self.example_dialog else [])
        examples_line = " | ".join(filter(None, examples[:2]))

        lines = [
            f"Core Description: {core}",
            f"Identity: {npc_name}, a {self.stage_of_life} {self.role} who uses {self.pronouns} and relaxes with {hobbies_line}.",
            f"Motivations: {motivations_line}",
            f"Flaws: {flaws_line or 'Keeps worries private but they leak into tone.'}",
            f"Personality Traits: {', '.join(self.personality_traits) or adjectives_line}",
            f"Speech: {self.dialog_style}; colloquialisms include {', '.join(self.colloquialisms)}; voice preset: {self.voice}.",
        ]

        if examples_line:
            lines.append(f"Example Dialog: {examples_line}")

        return "\n".join(lines)


@dataclass
class RelationState:
    """Relationship attributes toward the player."""

    trust: int = 0
    respect: int = 0
    familiar: int = 0
    flirtatious: int = 0
    attraction: int = 0

    def label(self) -> str:
        if self.trust >= 10 and self.respect >= 5 and self.familiar >= 10 and self.flirtatious <= 5 and self.attraction >= 5:
            return "friend"
        if self.trust <= 0 and self.respect <= -20 and self.flirtatious <= 5 and self.attraction <= -20:
            return "archenemy"
        if self.trust > 5 and self.respect > 0:
            return "ally"
        if self.trust < -5 and self.respect < -5:
            return "rival"
        return "neutral"


@dataclass
class KnowledgeProfile:
    """Defines what an NPC is allowed to know or recall."""

    filter_level: KnowledgeFilter = KnowledgeFilter.MILD
    domains: list[str] = field(default_factory=lambda: ["local history", "trade", "weather"])
    expertise_period: str = "current era"
    known_entities: list[str] = field(default_factory=list)
    forbidden_topics: list[str] = field(default_factory=lambda: ["modern celebrities", "player hardware"])

    def allows_topic(self, prompt: str) -> bool:
        lowered = prompt.lower()
        tokens = set(re.findall(r"[a-zA-Z][a-zA-Z']+", lowered))
        domain_tokens = {d.lower() for d in self.domains}
        known_entities = {e.lower() for e in self.known_entities}

        if self.filter_level == KnowledgeFilter.NONE:
            return True

        if self.filter_level == KnowledgeFilter.STRICT:
            return bool(tokens & domain_tokens or tokens & known_entities)

        # Mild: block obvious out-of-era or forbidden topics
        forbidden_keywords = {"internet", "smartphone", "blockchain", "michael", "jackson", "youtube"}
        if any(keyword in tokens for keyword in forbidden_keywords):
            return False

        return True

# ============================================================================
# Maslow's Hierarchy of Needs
# ============================================================================

class MaslowLevel(Enum):
    """Maslow's hierarchy levels."""
    PHYSIOLOGICAL = 1  # Food, water, shelter
    SAFETY = 2  # Security, stability
    LOVE_BELONGING = 3  # Friendship, family
    ESTEEM = 4  # Respect, recognition
    SELF_ACTUALIZATION = 5  # Purpose, meaning


@dataclass
class MaslowNeeds:
    """Tracks an NPC's needs hierarchy."""
    physiological: float = 1.0  # 0-1, 1 = fully satisfied
    safety: float = 1.0
    love_belonging: float = 0.5
    esteem: float = 0.5
    self_actualization: float = 0.3
    
    def get_dominant_need(self) -> MaslowLevel:
        """Get the most pressing unsatisfied need."""
        # Maslow's principle: lower needs must be met first
        if self.physiological < 0.3:
            return MaslowLevel.PHYSIOLOGICAL
        if self.safety < 0.3:
            return MaslowLevel.SAFETY
        if self.love_belonging < 0.3:
            return MaslowLevel.LOVE_BELONGING
        if self.esteem < 0.3:
            return MaslowLevel.ESTEEM
        return MaslowLevel.SELF_ACTUALIZATION
    
    def get_motivation_context(self) -> str:
        """Generate motivation context for narrator."""
        need = self.get_dominant_need()
        
        motivations = {
            MaslowLevel.PHYSIOLOGICAL: "Driven by hunger, thirst, or exhaustion. Will trade anything for basics.",
            MaslowLevel.SAFETY: "Desperate for security. Avoids risks, seeks protection.",
            MaslowLevel.LOVE_BELONGING: "Lonely. Seeks connection, acceptance, loyalty.",
            MaslowLevel.ESTEEM: "Craves recognition and respect. Prideful.",
            MaslowLevel.SELF_ACTUALIZATION: "Pursuing meaning and purpose. Idealistic.",
        }
        
        return f"[MOTIVATION: {need.name}]\n{motivations[need]}"
    
    def to_dict(self) -> dict:
        return {
            "physiological": self.physiological,
            "safety": self.safety,
            "love_belonging": self.love_belonging,
            "esteem": self.esteem,
            "self_actualization": self.self_actualization,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "MaslowNeeds":
        return cls(**{k: data.get(k, 0.5) for k in ["physiological", "safety", "love_belonging", "esteem", "self_actualization"]})


@dataclass
class NPCIdentity:
    """NPC personality container with memory, backstory, and mood hooks."""

    name: str
    profile: CharacterProfile = field(default_factory=CharacterProfile)
    personality: OCEANProfile = field(default_factory=OCEANProfile)
    needs: MaslowNeeds = field(default_factory=MaslowNeeds)
    relations: RelationState = field(default_factory=RelationState)
    knowledge: KnowledgeProfile = field(default_factory=KnowledgeProfile)
    traits: List[PersonalityTrait] = field(default_factory=list)
    backstory: Backstory = field(default_factory=Backstory)
    memories: List[MemoryFragment] = field(default_factory=list)
    mood: MoodState = field(default_factory=MoodState)

    def update_mood_from_situation(
        self,
        threat: float = 0.0,
        crowd_hostility: float = 0.0,
        cover_available: bool = True,
        social_support: float = 0.5,
        is_wounded: bool = False,
        recent_victory: bool = False,
        recent_loss: bool = False,
    ) -> None:
        """Update mood using immediate situational cues."""

        fatigue = 0.6 if is_wounded else 0.3 if not cover_available else 0.1
        perceived_threat = min(1.0, threat + crowd_hostility * 0.5)
        self.mood.update(
            threat_level=perceived_threat,
            social_support=social_support,
            fatigue=fatigue,
            recent_victory=recent_victory,
            recent_loss=recent_loss,
        )

    def add_memory(
        self,
        description: str,
        significance: float = 0.5,
        tags: list[str] | None = None,
        max_memories: int = 8,
    ) -> None:
        """Record a personal memory and keep a bounded log."""

        fragment = MemoryFragment(description=description, significance=significance, tags=tags or [])
        self.memories.append(fragment)
        self.memories = sorted(self.memories, key=lambda m: m.significance, reverse=True)[:max_memories]

    def narrator_context(self) -> str:
        """Blend traits, mood, and backstory into a narrator-friendly context."""

        trait_line = "; ".join(t.to_descriptor() for t in self.traits[:3]) or "no notable quirks"
        memory_line = "; ".join(m.to_descriptor() for m in self.memories[:3]) or "no memorable incidents yet"
        backstory_line = self.backstory.summary()
        mood_line = self.mood.describe()
        maslow_line = self.needs.get_motivation_context()
        personality_line = self.personality.get_narrator_context(self.name)
        relation_line = f"Relation to {self.profile.player_name}: {self.relations.label()}"
        profile_line = self.profile.summarize()
        detailed_profile = self.profile.detailed_sheet(self.name)

        return "\n".join([
            f"[NPC: {self.name}]",
            personality_line,
            f"Traits: {trait_line}",
            backstory_line,
            f"Memories: {memory_line}",
            mood_line,
            maslow_line,
            relation_line,
            profile_line,
            detailed_profile,
        ])

    def grounded_reply(self, player_prompt: str, fallback: str | None = None) -> str:
        """Return an in-world, non-hallucinatory reply scaffold for dialogue generation."""

        return DialogueGuardrails(self).respond(player_prompt, fallback=fallback)


# ============================================================================
# Dialogue guardrails to keep NPCs grounded and in-character
# ============================================================================


class DialogueGuardrails:
    """Detects absurd or out-of-world prompts and steers NPC responses."""

    OUT_OF_WORLD_KEYWORDS = {
        "michael jackson",
        "elon musk",
        "youtube",
        "smartphone",
        "blockchain",
        "internet",
        "android phone",
    }
    IMPOSSIBLE_PHRASES = ["turn into", "transform into", "become a", "shape shift into"]
    IMPOSSIBLE_OBJECTS = {"watermelon", "fruit", "rock", "chair"}

    def __init__(self, npc: NPCIdentity):
        self.npc = npc

    def _tone_prefix(self) -> str:
        style = self.npc.personality.get_dialogue_style()
        friendliness = style.get("friendliness", "neutral")
        tone = "gently" if friendliness == "warm" else "flatly" if friendliness == "cold" else "steadily"
        relation = self.npc.relations.label()
        return f"{self.npc.name} ({self.npc.profile.role}, views {self.npc.profile.player_name} as {relation}) {tone}"

    def _focus_topics(self) -> str:
        """Provide grounded topics to steer absurd prompts back in-world."""

        domains = ", ".join(self.npc.knowledge.domains[:2]) or "the market stalls"
        anchors = ", ".join(self.npc.backstory.anchors[:1])
        hobbies = ", ".join(self.npc.profile.hobbies[:1])
        focus_bits = [domains]

        if anchors:
            focus_bits.append(f"memories of {anchors}")
        if hobbies:
            focus_bits.append(f"their hobby of {hobbies}")

        return ", ".join(focus_bits)

    def _knowledge_limit_reason(self) -> str:
        level = self.npc.knowledge.filter_level
        if level == KnowledgeFilter.STRICT:
            return "their world is small and they only trust firsthand trade gossip"
        if level == KnowledgeFilter.MILD:
            return "they only speak about their trade, era, and familiar faces"
        return "they stick to what they truly know"

    def _is_impossible_request(self, prompt: str) -> bool:
        lowered = prompt.lower()
        return any(phrase in lowered for phrase in self.IMPOSSIBLE_PHRASES) and any(obj in lowered for obj in self.IMPOSSIBLE_OBJECTS)

    def _is_out_of_world(self, prompt: str) -> bool:
        lowered = prompt.lower()
        for keyword in self.OUT_OF_WORLD_KEYWORDS:
            if keyword in lowered:
                return True
        return not self.npc.knowledge.allows_topic(prompt)

    def _refusal(self, reason: str) -> str:
        mood = self.npc.mood.current.value
        return f"{self._tone_prefix()} declines: {reason} (mood: {mood})."

    def _impossible_reason(self) -> str:
        return (
            "they cannot twist bone and flesh into fruit; instead they suggest something useful within reach"
        )

    def respond(self, prompt: str, fallback: str | None = None) -> str:
        """Return an NPC-safe reply that avoids 4th-wall breaks and hallucinations."""

        if self._is_impossible_request(prompt):
            return self._refusal(
                f"{self._impossible_reason()}; they pivot toward {self._focus_topics()}"
            )

        if self._is_out_of_world(prompt):
            return self._refusal(
                f"they do not recognize that name or idea—{self._knowledge_limit_reason()}—and steer the talk back to {self._focus_topics()}"
            )

        if not self.npc.knowledge.allows_topic(prompt):
            return self._refusal(
                f"their knowledge is limited because {self._knowledge_limit_reason()}; they prefer discussing {self._focus_topics()}"
            )

        if fallback:
            return fallback

        focus_domains = ", ".join(self.npc.knowledge.domains[:2]) or "their daily work"
        return (
            f"{self._tone_prefix()} answers from lived experience about {focus_domains}, "
            "avoiding speculation or out-of-character topics."
        )


# ============================================================================
# Cinematography System
# ============================================================================

class ShotType(Enum):
    """Types of cinematographic shots."""
    ESTABLISHING = "establishing"  # Wide - show environment
    WIDE = "wide"  # Full scene, multiple characters
    MEDIUM = "medium"  # Upper body, conversational
    CLOSE = "close"  # Face, emotional detail
    EXTREME_CLOSE = "extreme_close"  # Eyes, hands, specific detail
    OVER_SHOULDER = "over_shoulder"  # Dialogue framing
    POV = "pov"  # Player's direct view


@dataclass
class CinematographyDirector:
    """
    Selects appropriate "shot" framing for narrative descriptions.
    Based on emotional intensity and tactical complexity.
    """
    
    def select_shot(
        self,
        emotional_intensity: float,  # 0-1
        tactical_complexity: float,  # 0-1
        is_dialogue: bool = False,
        is_action: bool = False,
    ) -> ShotType:
        """Select the appropriate shot type."""
        # High emotion = zoom in
        if emotional_intensity > 0.8:
            return ShotType.EXTREME_CLOSE
        elif emotional_intensity > 0.6:
            return ShotType.CLOSE
        
        # High tactical = zoom out
        if tactical_complexity > 0.7:
            return ShotType.WIDE
        elif tactical_complexity > 0.5:
            return ShotType.ESTABLISHING
        
        # Dialogue defaults
        if is_dialogue:
            return ShotType.OVER_SHOULDER if emotional_intensity > 0.4 else ShotType.MEDIUM
        
        # Action defaults
        if is_action:
            return ShotType.MEDIUM
        
        return ShotType.MEDIUM
    
    def get_shot_guidance(self, shot: ShotType) -> str:
        """Generate narrator guidance for the selected shot."""
        guidance = {
            ShotType.ESTABLISHING: (
                "WIDE SHOT: Describe the environment first. Set the stage. "
                "Weather, lighting, scale. Characters are small in the frame."
            ),
            ShotType.WIDE: (
                "WIDE SHOT: Show the full scene. Multiple characters, their positions relative "
                "to each other. Tactical layout visible."
            ),
            ShotType.MEDIUM: (
                "MEDIUM SHOT: Focus on upper body. Gestures, posture, general demeanor. "
                "Some environment visible for context."
            ),
            ShotType.CLOSE: (
                "CLOSE-UP: Focus on the face. Micro-expressions matter. "
                "What do their eyes betray? The twitch of a lip?"
            ),
            ShotType.EXTREME_CLOSE: (
                "EXTREME CLOSE-UP: A single detail fills the frame. "
                "The white knuckles. The tear track. The trembling hand."
            ),
            ShotType.OVER_SHOULDER: (
                "OVER-SHOULDER: Frame the dialogue through one character's perspective. "
                "We see who they're talking to, their reaction."
            ),
            ShotType.POV: (
                "POV SHOT: We see exactly what the player sees. First-person immediacy. "
                "Describe through their senses directly."
            ),
        }
        return guidance.get(shot, guidance[ShotType.MEDIUM])
    
    def get_narrator_context(
        self,
        emotional_intensity: float,
        tactical_complexity: float,
        is_dialogue: bool = False,
        is_action: bool = False,
    ) -> str:
        """Generate full cinematography context for narrator."""
        shot = self.select_shot(emotional_intensity, tactical_complexity, is_dialogue, is_action)
        guidance = self.get_shot_guidance(shot)
        
        return f"[CINEMATOGRAPHY: {shot.value.upper()}]\n{guidance}"


# ============================================================================
# Convenience Functions
# ============================================================================

def create_personality(archetype: str = "everyman") -> OCEANProfile:
    """Create a personality from archetype."""
    return PERSONALITY_ARCHETYPES.get(archetype, PERSONALITY_ARCHETYPES["everyman"])


def create_random_personality() -> OCEANProfile:
    """Create a randomized personality."""
    return OCEANProfile(
        openness=random.uniform(0.2, 0.8),
        conscientiousness=random.uniform(0.2, 0.8),
        extraversion=random.uniform(0.2, 0.8),
        agreeableness=random.uniform(0.2, 0.8),
        neuroticism=random.uniform(0.2, 0.8),
    )


def create_npc_identity(
    name: str,
    archetype: str = "everyman",
    trait_notes: list[str] | None = None,
    backstory: Backstory | None = None,
    profile: CharacterProfile | None = None,
    knowledge: KnowledgeProfile | None = None,
    relations: RelationState | None = None,
) -> NPCIdentity:
    """Helper to spin up an NPCIdentity with traits, backstory, and baseline mood."""

    trait_notes = trait_notes or ["observant", "keeps old promises", "hides frustration"]
    traits = [PersonalityTrait(note, description=note, intensity=random.uniform(0.3, 0.8)) for note in trait_notes]
    backstory = backstory or Backstory(origin="frontier colony", formative_events=["survived a station fire"], ideals=["loyalty", "self-reliance"], anchors=["old captain", "family keepsake"])
    return NPCIdentity(
        name=name,
        personality=create_personality(archetype),
        traits=traits,
        backstory=backstory,
        profile=profile or CharacterProfile(),
        knowledge=knowledge or KnowledgeProfile(),
        relations=relations or RelationState(),
    )


def get_cinematography_context(
    emotional_intensity: float,
    tactical_complexity: float = 0.0,
) -> str:
    """Quick cinematography context generation."""
    director = CinematographyDirector()
    return director.get_narrator_context(
        emotional_intensity=emotional_intensity,
        tactical_complexity=tactical_complexity,
    )
class Mood(Enum):
    """High-level mood buckets for quick narration hooks."""

    NEUTRAL = "neutral"
    CALM = "calm"
    FOCUSED = "focused"
    ANXIOUS = "anxious"
    ANGRY = "angry"
    HOPEFUL = "hopeful"
    MELANCHOLIC = "melancholic"
    ELATED = "elated"
    GUARDED = "guarded"


@dataclass
class PersonalityTrait:
    """A distinctive trait with a short description and intensity."""

    name: str
    description: str
    intensity: float = 0.5  # 0-1

    def to_descriptor(self) -> str:
        weight = "strong" if self.intensity > 0.7 else "subtle" if self.intensity < 0.3 else "present"
        return f"{self.name} ({weight}; {self.description})"


@dataclass
class Backstory:
    """Stores an NPC's origin, formative events, and enduring hooks."""

    origin: str = ""
    upbringing: str = ""
    formative_events: list[str] = field(default_factory=list)
    secrets: list[str] = field(default_factory=list)
    ideals: list[str] = field(default_factory=list)
    anchors: list[str] = field(default_factory=list)  # People or places that matter

    def summary(self, max_events: int = 2) -> str:
        events = ", ".join(self.formative_events[:max_events]) if self.formative_events else "mysterious past"
        ideals = ", ".join(self.ideals[:2]) if self.ideals else "personal code"
        return f"From {self.origin or 'an unknown place'}, shaped by {events}, guided by {ideals}."


@dataclass
class MemoryFragment:
    """Personal memory snippets that anchor behavior and mood."""

    description: str
    significance: float = 0.5  # 0-1 importance
    tags: list[str] = field(default_factory=list)

    def to_descriptor(self) -> str:
        highlight = "defining" if self.significance > 0.7 else "minor" if self.significance < 0.3 else "notable"
        return f"{highlight} memory: {self.description}"


@dataclass
class MoodState:
    """Dynamic mood that reacts to immediate situation and memories."""

    current: Mood = Mood.NEUTRAL
    intensity: float = 0.5  # 0-1 arousal level
    outlook: str = "balanced"  # optimistic / pessimistic / balanced

    def update(self, threat_level: float = 0.0, social_support: float = 0.5, fatigue: float = 0.0,
               recent_victory: bool = False, recent_loss: bool = False) -> None:
        """Blend situational factors into a current mood."""

        # Arousal rises with threat or victory, drops with support and rest
        self.intensity = max(0.0, min(1.0, 0.5 + threat_level * 0.4 - fatigue * 0.2 + (0.15 if recent_victory else 0)
                                      - (0.1 if social_support > 0.7 else 0)))

        if threat_level > 0.6 or fatigue > 0.6:
            self.current = Mood.ANXIOUS if social_support < 0.4 else Mood.GUARDED
        elif recent_victory and self.intensity > 0.5:
            self.current = Mood.ELATED if social_support > 0.5 else Mood.FOCUSED
        elif recent_loss:
            self.current = Mood.MELANCHOLIC if social_support < 0.5 else Mood.GUARDED
        elif social_support > 0.7 and threat_level < 0.3:
            self.current = Mood.CALM
        else:
            self.current = Mood.FOCUSED if self.intensity > 0.6 else Mood.NEUTRAL

        self.outlook = "optimistic" if social_support > 0.6 or recent_victory else "pessimistic" if recent_loss else "balanced"

    def describe(self) -> str:
        return f"Mood: {self.current.value} ({self.outlook}, intensity {self.intensity:.2f})"

