"""
Final Systems - Encounter Generation, Voice Consistency, Memory Consolidation

This module provides the final three systems to complete the AI Game Master:
1. Procedural Encounter Generator - On-demand random content
2. Voice/Tone Consistency Checker - Maintain narrator style
3. Long-term Memory Consolidation - Compress old memories
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, Any
import random
from collections import defaultdict


# =============================================================================
# PROCEDURAL ENCOUNTER GENERATOR
# =============================================================================

class EncounterType(Enum):
    """Types of encounters."""
    COMBAT = "combat"
    SOCIAL = "social"
    ENVIRONMENTAL = "environmental"
    MYSTERY = "mystery"
    MORAL = "moral"
    OPPORTUNITY = "opportunity"
    COMPLICATION = "complication"
    REVELATION = "revelation"


class EncounterScale(Enum):
    """Scale/importance of encounter."""
    MINOR = "minor"          # Brief, low stakes
    MODERATE = "moderate"    # Meaningful but not critical
    MAJOR = "major"          # Significant consequences
    CRITICAL = "critical"    # Story-changing


@dataclass
class EncounterTemplate:
    """A template for generating encounters."""
    encounter_type: EncounterType
    scale: EncounterScale
    premise: str
    elements: List[str]
    complications: List[str]
    stakes: str
    resolution_paths: List[str]


@dataclass
class ProceduralEncounterGenerator:
    """
    Generates random encounters on demand.
    
    Creates meaningful content that fits the current
    narrative context while feeling fresh.
    """
    
    recent_types: List[EncounterType] = field(default_factory=list)
    encounter_count: int = 0
    
    # Templates organized by type
    TEMPLATES: Dict[EncounterType, List[Dict[str, Any]]] = field(default_factory=lambda: {
        EncounterType.COMBAT: [
            {
                "premise": "Ambush by hostile forces",
                "elements": ["Multiple enemies", "Terrain advantage/disadvantage", "Escape route"],
                "complications": ["Hostage present", "Valuable equipment at risk", "Time pressure"],
                "stakes": "Survival and mission continuation",
                "resolutions": ["Fight through", "Negotiate", "Escape", "Surrender"]
            },
            {
                "premise": "Interrupted standoff between factions",
                "elements": ["Two hostile groups", "Valuable objective", "Cover positions"],
                "complications": ["Both sides blame player", "Innocents in crossfire", "Hidden party"],
                "stakes": "Faction relationships and immediate safety",
                "resolutions": ["Side with one", "Play both", "Third option", "Wait it out"]
            }
        ],
        EncounterType.SOCIAL: [
            {
                "premise": "Someone recognizes the player",
                "elements": ["Shared history", "Public setting", "Witnesses"],
                "complications": ["Wrong identity", "Old grudge", "Inconvenient timing"],
                "stakes": "Reputation and cover integrity",
                "resolutions": ["Embrace it", "Deny it", "Silencing", "Bargain"]
            },
            {
                "premise": "Request for help from a stranger",
                "elements": ["Desperate situation", "Limited information", "Time pressure"],
                "complications": ["Help requires sacrifice", "Story doesn't add up", "Involves enemies"],
                "stakes": "Character definition and resource expenditure",
                "resolutions": ["Help fully", "Help conditionally", "Refuse", "Investigate first"]
            }
        ],
        EncounterType.ENVIRONMENTAL: [
            {
                "premise": "Sudden environmental hazard",
                "elements": ["Immediate danger", "Limited resources", "Escape window"],
                "complications": ["Someone trapped", "Equipment damaged", "Path blocked"],
                "stakes": "Health and mission equipment",
                "resolutions": ["Push through", "Wait it out", "Find alternate route", "Sacrifice something"]
            },
            {
                "premise": "Discovery of hidden location",
                "elements": ["Concealed entrance", "Signs of activity", "Risk/reward balance"],
                "complications": ["Trapped", "Occupied", "Cursed/contaminated"],
                "stakes": "Knowledge and resources vs. time and danger",
                "resolutions": ["Full exploration", "Quick look", "Mark for later", "Avoid"]
            }
        ],
        EncounterType.MYSTERY: [
            {
                "premise": "Strange anomaly defies explanation",
                "elements": ["Unexplainable phenomenon", "Witnesses disagree", "Partial evidence"],
                "complications": ["Getting worse", "Authority denies it", "Someone profiting"],
                "stakes": "Understanding and potential danger",
                "resolutions": ["Investigate deeply", "Consult expert", "Exploit it", "Report and move on"]
            },
            {
                "premise": "Message from unknown source",
                "elements": ["Cryptic content", "Urgent tone", "Impossible knowledge"],
                "complications": ["Could be trap", "Time-sensitive", "Contradicts known facts"],
                "stakes": "Trust and mission direction",
                "resolutions": ["Follow it", "Investigate source", "Ignore", "Set counter-trap"]
            }
        ],
        EncounterType.MORAL: [
            {
                "premise": "Opportunity to benefit at someone's expense",
                "elements": ["Easy gain", "Distant victim", "No witnesses"],
                "complications": ["Victim is sympathetic", "Gain is significant", "Consequences delayed"],
                "stakes": "Character soul and practical benefit",
                "resolutions": ["Take it", "Refuse", "Find third option", "Partial exploitation"]
            },
            {
                "premise": "Forced to choose who to help",
                "elements": ["Two sympathetic parties", "Only one can be saved", "Time pressure"],
                "complications": ["Both have valid claims", "Choice reveals values", "Unknown factors"],
                "stakes": "Lives and self-definition",
                "resolutions": ["Choose A", "Choose B", "Risky both attempt", "Refuse to choose"]
            }
        ],
        EncounterType.OPPORTUNITY: [
            {
                "premise": "Unexpected windfall or advantage",
                "elements": ["Valuable resource", "Limited window", "Unclear source"],
                "complications": ["Strings attached", "Competition", "Too good to be true"],
                "stakes": "Resources vs. hidden cost",
                "resolutions": ["Accept fully", "Accept cautiously", "Investigate", "Decline"]
            }
        ],
        EncounterType.REVELATION: [
            {
                "premise": "Overheard information changes everything",
                "elements": ["Critical secret", "Unreliable source", "Personal implications"],
                "complications": ["Can't verify", "Acting on it exposes source", "Changes priorities"],
                "stakes": "Knowledge that can't be unknown",
                "resolutions": ["Act on it", "Verify first", "Confront source", "Pretend not to know"]
            }
        ]
    })
    
    def generate_encounter(self, 
                            preferred_type: EncounterType = None,
                            scale: EncounterScale = EncounterScale.MODERATE,
                            context_hints: List[str] = None) -> Dict[str, Any]:
        """Generate a random encounter."""
        
        # Avoid recent types if possible
        available_types = list(EncounterType)
        if len(self.recent_types) >= 3:
            for t in self.recent_types[-3:]:
                if t in available_types and len(available_types) > 1:
                    available_types.remove(t)
        
        # Select type
        enc_type = preferred_type if preferred_type else random.choice(available_types)
        
        # Get templates for this type
        templates = self.TEMPLATES.get(enc_type, [])
        if not templates:
            templates = self.TEMPLATES[EncounterType.SOCIAL]
        
        template = random.choice(templates)
        
        # Track history
        self.recent_types.append(enc_type)
        if len(self.recent_types) > 10:
            self.recent_types = self.recent_types[-10:]
        self.encounter_count += 1
        
        # Select random complication
        complication = random.choice(template["complications"]) if template["complications"] else None
        
        return {
            "type": enc_type.value,
            "scale": scale.value,
            "premise": template["premise"],
            "elements": template["elements"],
            "complication": complication,
            "stakes": template["stakes"],
            "resolution_options": template["resolutions"]
        }
    
    def get_encounter_guidance(self, current_tension: float = 0.5) -> str:
        """Generate encounter generation guidance."""
        
        # Generate a sample encounter
        scale = EncounterScale.MINOR if current_tension > 0.7 else \
                EncounterScale.MAJOR if current_tension < 0.3 else \
                EncounterScale.MODERATE
        
        sample = self.generate_encounter(scale=scale)
        
        # Avoid suggesting same type repeatedly
        recent_text = ""
        if self.recent_types:
            recent = set(t.value for t in self.recent_types[-3:])
            recent_text = f"\n  Recent types (vary these): {', '.join(recent)}"
        
        return f"""<encounter_generator>
SAMPLE ENCOUNTER (if scene needs content):
  Type: {sample['type'].upper()} | Scale: {sample['scale']}
  Premise: "{sample['premise']}"
  Elements: {', '.join(sample['elements'][:3])}
  Complication: {sample['complication']}
  Stakes: {sample['stakes']}
  Options: {', '.join(sample['resolution_options'])}
{recent_text}

ENCOUNTER DESIGN PRINCIPLES:
  - Every encounter should offer meaningful choice
  - Stakes should be clear before commitment
  - Multiple resolution paths reward creativity
  - Complications prevent simple solutions
  
PACING AWARENESS:
  - High tension scenes → minor encounters (don't overwhelm)
  - Low tension → opportunity for major encounters
  - After major encounter → breathing room
</encounter_generator>"""
    
    def to_dict(self) -> dict:
        return {
            "recent_types": [t.value for t in self.recent_types],
            "encounter_count": self.encounter_count
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ProceduralEncounterGenerator":
        gen = cls()
        gen.recent_types = [EncounterType(t) for t in data.get("recent_types", [])]
        gen.encounter_count = data.get("encounter_count", 0)
        return gen


# =============================================================================
# VOICE/TONE CONSISTENCY CHECKER
# =============================================================================

class NarrativeVoice(Enum):
    """Narrator voice styles."""
    LITERARY = "literary"        # Poetic, atmospheric
    PULP = "pulp"               # Fast, punchy, direct
    HARDBOILED = "hardboiled"   # Cynical, sparse
    LYRICAL = "lyrical"         # Beautiful, flowing
    CLINICAL = "clinical"       # Detached, precise
    INTIMATE = "intimate"       # Close, emotional
    MYTHIC = "mythic"           # Grand, archetypal


class ToneProfile(Enum):
    """Overall tone profiles."""
    DARK = "dark"
    HOPEFUL = "hopeful"
    GRITTY = "gritty"
    WHIMSICAL = "whimsical"
    SERIOUS = "serious"
    MELANCHOLIC = "melancholic"


@dataclass
class VoiceConsistencyChecker:
    """
    Maintains consistent narrator voice and tone.
    
    Prevents jarring shifts in writing style
    and ensures the narrative feels unified.
    """
    
    established_voice: NarrativeVoice = NarrativeVoice.LITERARY
    established_tone: ToneProfile = ToneProfile.GRITTY
    vocabulary_register: str = "elevated"  # casual, standard, elevated, archaic
    
    # Voice characteristics
    forbidden_elements: List[str] = field(default_factory=list)
    preferred_elements: List[str] = field(default_factory=list)
    
    # Voice profiles
    VOICE_PROFILES: Dict[NarrativeVoice, Dict[str, Any]] = field(default_factory=lambda: {
        NarrativeVoice.LITERARY: {
            "sentence_length": "varied, often complex",
            "imagery": "rich metaphor and symbolism",
            "pacing": "measured, atmospheric",
            "example": "The station wheezed around them, a dying thing that had forgotten how to stop breathing.",
            "avoid": ["simple declaratives only", "action verbs without context", "telling over showing"]
        },
        NarrativeVoice.PULP: {
            "sentence_length": "short, punchy",
            "imagery": "vivid, immediate",
            "pacing": "rapid, urgent",
            "example": "Gun up. Door open. Three hostiles. Time to work.",
            "avoid": ["long introspective passages", "excessive description", "slow burns"]
        },
        NarrativeVoice.HARDBOILED: {
            "sentence_length": "terse, clipped",
            "imagery": "cynical observations",
            "pacing": "steady, world-weary",
            "example": "The job was simple. They always are, until they aren't.",
            "avoid": ["optimistic language", "flowery prose", "naive character moments"]
        },
        NarrativeVoice.LYRICAL: {
            "sentence_length": "flowing, musical",
            "imagery": "beautiful even in darkness",
            "pacing": "dreamlike",
            "example": "Light fell through the broken dome like mercy, touching nothing, changing nothing.",
            "avoid": ["harsh language for shock", "purely functional prose", "rapid-fire action"]
        },
        NarrativeVoice.MYTHIC: {
            "sentence_length": "declarative, weighty",
            "imagery": "archetypal, timeless",
            "pacing": "deliberate, significant",
            "example": "And so the wanderer came to the threshold, as all wanderers must.",
            "avoid": ["casual dialogue", "modern slang", "mundane details"]
        }
    })
    
    TONE_GUIDANCE: Dict[ToneProfile, Dict[str, str]] = field(default_factory=lambda: {
        ToneProfile.DARK: {
            "success_feels": "like brief respite, not triumph",
            "failure_feels": "inevitable, costly",
            "hope": "rare and fragile",
            "humor": "black, bitter, or absent"
        },
        ToneProfile.HOPEFUL: {
            "success_feels": "earned and meaningful",
            "failure_feels": "a lesson, not an end",
            "hope": "justified, growing",
            "humor": "warm, connecting"
        },
        ToneProfile.GRITTY: {
            "success_feels": "hard-won, always costs something",
            "failure_feels": "brutal but survivable",
            "hope": "practical, tested",
            "humor": "dark, coping mechanism"
        },
        ToneProfile.MELANCHOLIC: {
            "success_feels": "tinged with loss",
            "failure_feels": "confirming sadness",
            "hope": "nostalgia for better times",
            "humor": "bittersweet, rare"
        }
    })
    
    def set_voice(self, voice: NarrativeVoice, tone: ToneProfile, 
                   register: str = "standard"):
        """Set the narrative voice profile."""
        self.established_voice = voice
        self.established_tone = tone
        self.vocabulary_register = register
    
    def add_forbidden(self, element: str):
        """Add an element to avoid."""
        if element not in self.forbidden_elements:
            self.forbidden_elements.append(element)
    
    def add_preferred(self, element: str):
        """Add a preferred element."""
        if element not in self.preferred_elements:
            self.preferred_elements.append(element)
    
    def get_voice_guidance(self) -> str:
        """Generate voice consistency guidance."""
        
        voice_profile = self.VOICE_PROFILES.get(self.established_voice, {})
        tone_guidance = self.TONE_GUIDANCE.get(self.established_tone, {})
        
        forbidden_text = ""
        if self.forbidden_elements:
            forbidden_text = f"\n  FORBIDDEN: {', '.join(self.forbidden_elements[:5])}"
        
        preferred_text = ""
        if self.preferred_elements:
            preferred_text = f"\n  PREFERRED: {', '.join(self.preferred_elements[:5])}"
        
        return f"""<voice_consistency>
ESTABLISHED VOICE: {self.established_voice.value.upper()}
TONE: {self.established_tone.value} | Register: {self.vocabulary_register}

VOICE CHARACTERISTICS:
  Sentences: {voice_profile.get('sentence_length', 'standard')}
  Imagery: {voice_profile.get('imagery', 'standard')}
  Pacing: {voice_profile.get('pacing', 'standard')}
  
EXAMPLE: "{voice_profile.get('example', 'Maintain consistent style.')}"

AVOID IN THIS VOICE:
  {', '.join(voice_profile.get('avoid', ['nothing specific']))}

TONE GUIDANCE:
  Success feels: {tone_guidance.get('success_feels', 'appropriate')}
  Failure feels: {tone_guidance.get('failure_feels', 'consequential')}
  Hope: {tone_guidance.get('hope', 'present')}
  Humor: {tone_guidance.get('humor', 'appropriate')}
{forbidden_text}{preferred_text}

CONSISTENCY RULE:
  Jarring voice shifts break immersion. The narrative should feel
  like one author wrote it, even across many sessions.
</voice_consistency>"""
    
    def to_dict(self) -> dict:
        return {
            "established_voice": self.established_voice.value,
            "established_tone": self.established_tone.value,
            "vocabulary_register": self.vocabulary_register,
            "forbidden_elements": self.forbidden_elements,
            "preferred_elements": self.preferred_elements
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "VoiceConsistencyChecker":
        checker = cls()
        checker.established_voice = NarrativeVoice(data.get("established_voice", "literary"))
        checker.established_tone = ToneProfile(data.get("established_tone", "gritty"))
        checker.vocabulary_register = data.get("vocabulary_register", "standard")
        checker.forbidden_elements = data.get("forbidden_elements", [])
        checker.preferred_elements = data.get("preferred_elements", [])
        return checker


# =============================================================================
# LONG-TERM MEMORY CONSOLIDATION
# =============================================================================

class MemoryImportance(Enum):
    """Importance levels for memories."""
    TRIVIAL = "trivial"        # Can be forgotten
    MINOR = "minor"            # Context but not critical
    SIGNIFICANT = "significant" # Important to remember
    CRITICAL = "critical"       # Must never forget
    DEFINING = "defining"       # Core to character/story


@dataclass
class ConsolidatedMemory:
    """A compressed memory entry."""
    memory_id: str
    summary: str
    importance: MemoryImportance
    scene_range: Tuple[int, int]  # Start and end scene
    key_entities: List[str]
    emotional_weight: float
    tags: List[str]


@dataclass
class LongTermMemoryConsolidation:
    """
    Compresses old memories to manage context window.
    
    Keeps important memories accessible while
    summarizing less critical ones.
    """
    
    consolidated_memories: List[ConsolidatedMemory] = field(default_factory=list)
    current_scene: int = 0
    consolidation_threshold: int = 10  # Scenes before consolidation
    
    # Importance keywords for auto-classification
    IMPORTANCE_MARKERS: Dict[MemoryImportance, List[str]] = field(default_factory=lambda: {
        MemoryImportance.CRITICAL: ["death", "killed", "betrayed", "revealed", "promise", "vow", "secret"],
        MemoryImportance.SIGNIFICANT: ["discovered", "learned", "alliance", "enemy", "saved", "wounded"],
        MemoryImportance.MINOR: ["met", "traveled", "rested", "purchased", "conversation"],
        MemoryImportance.TRIVIAL: ["routine", "uneventful", "waited", "slept"]
    })
    
    def add_memory(self, summary: str, importance: MemoryImportance = None,
                    entities: List[str] = None, emotional_weight: float = 0.5,
                    tags: List[str] = None):
        """Add a new memory to be consolidated."""
        
        # Auto-detect importance if not provided
        if importance is None:
            importance = self._detect_importance(summary)
        
        memory = ConsolidatedMemory(
            memory_id=f"mem_{self.current_scene}_{len(self.consolidated_memories)}",
            summary=summary,
            importance=importance,
            scene_range=(self.current_scene, self.current_scene),
            key_entities=entities or [],
            emotional_weight=emotional_weight,
            tags=tags or []
        )
        self.consolidated_memories.append(memory)
    
    def _detect_importance(self, text: str) -> MemoryImportance:
        """Auto-detect memory importance from text."""
        text_lower = text.lower()
        
        for importance, markers in self.IMPORTANCE_MARKERS.items():
            for marker in markers:
                if marker in text_lower:
                    return importance
        
        return MemoryImportance.MINOR
    
    def consolidate_old_memories(self, scenes_to_keep_detailed: int = 5) -> List[str]:
        """Consolidate old memories into summaries."""
        
        threshold_scene = self.current_scene - scenes_to_keep_detailed
        
        # Separate old and recent
        old_memories = [m for m in self.consolidated_memories 
                       if m.scene_range[1] < threshold_scene]
        recent_memories = [m for m in self.consolidated_memories 
                         if m.scene_range[1] >= threshold_scene]
        
        if not old_memories:
            return []
        
        # Group by importance
        by_importance: Dict[MemoryImportance, List[ConsolidatedMemory]] = defaultdict(list)
        for m in old_memories:
            by_importance[m.importance].append(m)
        
        consolidated_summaries = []
        new_consolidated = []
        
        # Keep critical/defining memories intact
        for m in by_importance.get(MemoryImportance.CRITICAL, []):
            new_consolidated.append(m)
        for m in by_importance.get(MemoryImportance.DEFINING, []):
            new_consolidated.append(m)
        
        # Summarize significant memories in groups
        significant = by_importance.get(MemoryImportance.SIGNIFICANT, [])
        if significant:
            # Group into chunks of 3
            for i in range(0, len(significant), 3):
                chunk = significant[i:i+3]
                summaries = [m.summary for m in chunk]
                combined_summary = "; ".join(summaries)
                
                # Create merged memory
                merged = ConsolidatedMemory(
                    memory_id=f"merged_{chunk[0].scene_range[0]}_{chunk[-1].scene_range[1]}",
                    summary=f"[CONSOLIDATED] {combined_summary}",
                    importance=MemoryImportance.SIGNIFICANT,
                    scene_range=(chunk[0].scene_range[0], chunk[-1].scene_range[1]),
                    key_entities=list(set(e for m in chunk for e in m.key_entities)),
                    emotional_weight=sum(m.emotional_weight for m in chunk) / len(chunk),
                    tags=list(set(t for m in chunk for t in m.tags))
                )
                new_consolidated.append(merged)
                consolidated_summaries.append(merged.summary)
        
        # Minor and trivial get super-consolidated
        minor_trivial = by_importance.get(MemoryImportance.MINOR, []) + \
                        by_importance.get(MemoryImportance.TRIVIAL, [])
        if minor_trivial:
            scene_range = (minor_trivial[0].scene_range[0], minor_trivial[-1].scene_range[1])
            overview = f"[CONSOLIDATED] Scenes {scene_range[0]}-{scene_range[1]}: Various minor events and encounters"
            
            merged = ConsolidatedMemory(
                memory_id=f"overview_{scene_range[0]}_{scene_range[1]}",
                summary=overview,
                importance=MemoryImportance.MINOR,
                scene_range=scene_range,
                key_entities=[],
                emotional_weight=0.3,
                tags=["overview"]
            )
            new_consolidated.append(merged)
            consolidated_summaries.append(overview)
        
        # Update memory list
        self.consolidated_memories = new_consolidated + recent_memories
        
        return consolidated_summaries
    
    def get_memory_guidance(self) -> str:
        """Generate memory consolidation guidance."""
        
        # Categorize memories
        critical = [m for m in self.consolidated_memories 
                   if m.importance in [MemoryImportance.CRITICAL, MemoryImportance.DEFINING]]
        recent = self.consolidated_memories[-5:] if self.consolidated_memories else []
        
        critical_text = ""
        if critical:
            crit_items = [f"  ★ {m.summary[:60]}..." for m in critical[:5]]
            critical_text = f"""
CRITICAL MEMORIES (never forget):
{chr(10).join(crit_items)}"""
        
        recent_text = ""
        if recent:
            recent_items = [f"  Scene {m.scene_range[0]}: {m.summary[:50]}..." for m in recent]
            recent_text = f"""
RECENT EVENTS:
{chr(10).join(recent_items)}"""
        
        stats = f"Total memories: {len(self.consolidated_memories)} | Current scene: {self.current_scene}"
        
        return f"""<memory_consolidation>
{stats}
{critical_text}{recent_text}

MEMORY PRINCIPLES:
  - Critical events must be referenced when relevant
  - Old details fade but emotional impact remains
  - Characters remember what mattered to them
  - "I remember when..." should feel authentic
  
CONSOLIDATION STATUS:
  Memories older than {self.consolidation_threshold} scenes are compressed.
  Critical/defining memories are preserved verbatim.
</memory_consolidation>"""
    
    def to_dict(self) -> dict:
        return {
            "consolidated_memories": [
                {
                    "memory_id": m.memory_id,
                    "summary": m.summary,
                    "importance": m.importance.value,
                    "scene_range": m.scene_range,
                    "key_entities": m.key_entities,
                    "emotional_weight": m.emotional_weight,
                    "tags": m.tags
                } for m in self.consolidated_memories[-50:]  # Keep last 50
            ],
            "current_scene": self.current_scene,
            "consolidation_threshold": self.consolidation_threshold
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "LongTermMemoryConsolidation":
        system = cls()
        system.current_scene = data.get("current_scene", 0)
        system.consolidation_threshold = data.get("consolidation_threshold", 10)
        
        for m in data.get("consolidated_memories", []):
            system.consolidated_memories.append(ConsolidatedMemory(
                memory_id=m["memory_id"],
                summary=m["summary"],
                importance=MemoryImportance(m["importance"]),
                scene_range=tuple(m["scene_range"]),
                key_entities=m.get("key_entities", []),
                emotional_weight=m.get("emotional_weight", 0.5),
                tags=m.get("tags", [])
            ))
        return system


# =============================================================================
# MASTER FINAL SYSTEMS ENGINE
# =============================================================================

@dataclass
class FinalSystemsEngine:
    """Master engine for the final three systems."""
    
    encounters: ProceduralEncounterGenerator = field(default_factory=ProceduralEncounterGenerator)
    voice: VoiceConsistencyChecker = field(default_factory=VoiceConsistencyChecker)
    memory: LongTermMemoryConsolidation = field(default_factory=LongTermMemoryConsolidation)
    
    def get_comprehensive_guidance(self, current_tension: float = 0.5) -> str:
        """Generate comprehensive guidance from all final systems."""
        
        sections = []
        
        # Voice consistency (always important)
        voice_guidance = self.voice.get_voice_guidance()
        if voice_guidance:
            sections.append(voice_guidance)
        
        # Memory consolidation
        memory_guidance = self.memory.get_memory_guidance()
        if memory_guidance:
            sections.append(memory_guidance)
        
        # Encounter generator (optional use)
        encounter_guidance = self.encounters.get_encounter_guidance(current_tension)
        if encounter_guidance:
            sections.append(encounter_guidance)
        
        if not sections:
            return ""
        
        return f"""
<final_systems>
=== VOICE, MEMORY & ENCOUNTER GUIDANCE ===
{chr(10).join(sections)}
</final_systems>
"""
    
    def to_dict(self) -> dict:
        return {
            "encounters": self.encounters.to_dict(),
            "voice": self.voice.to_dict(),
            "memory": self.memory.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "FinalSystemsEngine":
        engine = cls()
        if "encounters" in data:
            engine.encounters = ProceduralEncounterGenerator.from_dict(data["encounters"])
        if "voice" in data:
            engine.voice = VoiceConsistencyChecker.from_dict(data["voice"])
        if "memory" in data:
            engine.memory = LongTermMemoryConsolidation.from_dict(data["memory"])
        return engine


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("FINAL SYSTEMS ENGINE - TEST")
    print("=" * 60)
    
    engine = FinalSystemsEngine()
    
    # Set voice
    engine.voice.set_voice(NarrativeVoice.LITERARY, ToneProfile.GRITTY, "elevated")
    engine.voice.add_forbidden("modern slang")
    engine.voice.add_preferred("atmospheric descriptions")
    
    # Add some memories
    engine.memory.add_memory("Player killed the station commander in self-defense", 
                              importance=MemoryImportance.CRITICAL,
                              entities=["Commander Torres", "Station Omega"])
    engine.memory.add_memory("Discovered hidden cargo bay containing illegal weapons",
                              importance=MemoryImportance.SIGNIFICANT)
    engine.memory.add_memory("Rested at waystation, purchased supplies",
                              importance=MemoryImportance.TRIVIAL)
    
    print("\n--- COMPREHENSIVE GUIDANCE ---")
    guidance = engine.get_comprehensive_guidance(current_tension=0.6)
    print(guidance[:2500] + "..." if len(guidance) > 2500 else guidance)
