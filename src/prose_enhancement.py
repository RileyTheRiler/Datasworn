"""
Prose Enhancement System - Advanced Narrative Quality Systems

This module provides runtime analysis and enhancement for generated prose,
ensuring consistency, quality, and literary depth.

Key Systems:
1. Sensory Consistency Tracker - Track and callback introduced sensory details
2. Prose Rhythm Analyzer - Detect monotony and suggest improvements
3. Voice Consistency Checker - Ensure NPCs maintain distinctive voices
4. Metaphor/Simile Engine - Generate contextual figurative language
5. Word Choice Enhancer - Replace weak words with precise alternatives
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple
import random
import re
from collections import defaultdict


# =============================================================================
# SENSORY CONSISTENCY TRACKER
# =============================================================================

class SenseCategory(Enum):
    """Categories of sensory details to track."""
    VISUAL = "visual"
    AUDITORY = "auditory"
    OLFACTORY = "olfactory"
    TACTILE = "tactile"
    GUSTATORY = "gustatory"
    TEMPERATURE = "temperature"
    KINESTHETIC = "kinesthetic"


@dataclass
class SensoryDetail:
    """A specific sensory detail introduced in narrative."""
    sense: SenseCategory
    description: str
    location: str
    scene_introduced: int
    times_referenced: int = 0
    is_ambient: bool = False  # Ongoing vs momentary


@dataclass
class SensoryConsistencyTracker:
    """
    Tracks sensory details introduced in narrative for consistency callbacks.
    
    When you describe the "acrid smell of recycled air" in scene 1,
    this tracker reminds the narrator to reference it again when appropriate,
    creating a cohesive sensory world.
    """
    
    active_details: Dict[str, SensoryDetail] = field(default_factory=dict)
    current_scene: int = 0
    current_location: str = ""
    
    # Keywords that suggest sensory details
    SENSE_KEYWORDS: Dict[SenseCategory, List[str]] = field(default_factory=lambda: {
        SenseCategory.VISUAL: ["light", "shadow", "glow", "flicker", "color", "bright", "dark", "shimmer"],
        SenseCategory.AUDITORY: ["hum", "buzz", "whisper", "echo", "silence", "creak", "beep", "roar"],
        SenseCategory.OLFACTORY: ["smell", "scent", "stench", "aroma", "odor", "whiff", "reek"],
        SenseCategory.TACTILE: ["rough", "smooth", "cold", "warm", "sharp", "soft", "vibration"],
        SenseCategory.GUSTATORY: ["taste", "bitter", "sweet", "metallic", "sour", "salty"],
        SenseCategory.TEMPERATURE: ["hot", "cold", "freezing", "warm", "chill", "heat"],
        SenseCategory.KINESTHETIC: ["balance", "gravity", "weight", "floating", "pressure"]
    })
    
    def extract_sensory_details(self, narrative: str, location: str) -> List[SensoryDetail]:
        """Extract sensory details from narrative text."""
        found_details = []
        narrative_lower = narrative.lower()
        
        for sense, keywords in self.SENSE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in narrative_lower:
                    # Extract the surrounding context (simple approach)
                    pattern = rf'\b\w*{keyword}\w*\b.{{0,50}}'
                    matches = re.findall(pattern, narrative_lower)
                    for match in matches[:1]:  # Take first match per keyword
                        detail = SensoryDetail(
                            sense=sense,
                            description=match.strip(),
                            location=location,
                            scene_introduced=self.current_scene,
                            is_ambient=any(amb in match for amb in ["constant", "always", "continuous", "ambient"])
                        )
                        found_details.append(detail)
        
        return found_details
    
    def register_details(self, narrative: str, location: str):
        """Register new sensory details from narrative."""
        self.current_location = location
        details = self.extract_sensory_details(narrative, location)
        
        for detail in details:
            key = f"{detail.sense.value}:{detail.description[:20]}"
            if key not in self.active_details:
                self.active_details[key] = detail
    
    def get_callback_suggestions(self) -> str:
        """Generate suggestions for sensory callbacks."""
        if not self.active_details:
            return ""
        
        # Find details that could be referenced again
        callbacks = []
        for key, detail in self.active_details.items():
            if detail.location == self.current_location:
                if detail.is_ambient or detail.times_referenced < 2:
                    callbacks.append(f"- {detail.sense.value}: \"{detail.description}\"")
        
        if not callbacks:
            return ""
        
        return f"""<sensory_callbacks>
PREVIOUSLY ESTABLISHED SENSORY DETAILS in this location:
{chr(10).join(callbacks[:5])}

Consider weaving these back into the narrative for consistency.
Readers notice when sensory details established earlier disappear.
</sensory_callbacks>"""
    
    def advance_scene(self):
        """Move to next scene, decay old details."""
        self.current_scene += 1
        # Remove very old non-ambient details
        to_remove = []
        for key, detail in self.active_details.items():
            if not detail.is_ambient and self.current_scene - detail.scene_introduced > 5:
                to_remove.append(key)
        for key in to_remove:
            del self.active_details[key]
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "active_details": {
                k: {
                    "sense": v.sense.value,
                    "description": v.description,
                    "location": v.location,
                    "scene_introduced": v.scene_introduced,
                    "times_referenced": v.times_referenced,
                    "is_ambient": v.is_ambient
                } for k, v in self.active_details.items()
            },
            "current_scene": self.current_scene,
            "current_location": self.current_location
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SensoryConsistencyTracker":
        """Deserialize from dictionary."""
        tracker = cls()
        tracker.current_scene = data.get("current_scene", 0)
        tracker.current_location = data.get("current_location", "")
        
        for k, v in data.get("active_details", {}).items():
            tracker.active_details[k] = SensoryDetail(
                sense=SenseCategory(v["sense"]),
                description=v["description"],
                location=v["location"],
                scene_introduced=v["scene_introduced"],
                times_referenced=v.get("times_referenced", 0),
                is_ambient=v.get("is_ambient", False)
            )
        return tracker


# =============================================================================
# PROSE RHYTHM ANALYZER
# =============================================================================

@dataclass
class RhythmAnalysis:
    """Analysis of prose rhythm patterns."""
    avg_sentence_length: float
    sentence_length_variance: float
    repeated_starters: List[str]
    monotony_score: float  # 0 = varied, 1 = monotonous
    suggestions: List[str]


@dataclass
class ProseRhythmAnalyzer:
    """
    Analyzes generated prose for rhythm issues and suggests improvements.
    
    Detects:
    - Monotonous sentence lengths
    - Repeated sentence starters
    - Overuse of certain structures
    - Opportunities for rhythm variation
    """
    
    SENTENCE_STARTERS_TO_AVOID: List[str] = field(default_factory=lambda: [
        "The", "He", "She", "It", "They", "There", "This", "That",
        "I", "You", "We", "A", "An"
    ])
    
    RHYTHM_SUGGESTIONS: Dict[str, List[str]] = field(default_factory=lambda: {
        "too_uniform": [
            "Vary sentence length more dramatically—short punch after long flow",
            "Try a one-word sentence for emphasis",
            "Use a fragment to break the rhythm",
        ],
        "same_starters": [
            "Vary how sentences begin—try starting with: When, After, Before, Despite",
            "Start with action: 'Running through the corridor...' instead of 'She ran'",
            "Start with sensory detail: 'Cold metal against her palm...'",
        ],
        "too_long": [
            "Break this into shorter sentences for impact",
            "Use periods where you have commas—create pause points",
            "Action sequences need shorter, punchier sentences",
        ],
        "too_short": [
            "Connect some sentences for flow during quiet moments",
            "Let descriptions breathe with longer, more immersive sentences",
            "Save staccato rhythm for high-tension moments",
        ]
    })
    
    def analyze(self, text: str) -> RhythmAnalysis:
        """Analyze prose rhythm and identify issues."""
        # Split into sentences (simple approach)
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return RhythmAnalysis(0, 0, [], 0, [])
        
        # Calculate lengths
        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths)
        
        # Calculate variance
        variance = sum((l - avg_length) ** 2 for l in lengths) / len(lengths)
        
        # Find repeated starters
        starters = [s.split()[0] if s.split() else "" for s in sentences]
        starter_counts = defaultdict(int)
        for s in starters:
            starter_counts[s] += 1
        
        repeated = [s for s, count in starter_counts.items() 
                   if count > 2 and s in self.SENTENCE_STARTERS_TO_AVOID]
        
        # Calculate monotony score
        monotony = 0.0
        if variance < 10:  # Low variance = monotonous
            monotony += 0.4
        if len(repeated) > 0:
            monotony += 0.3
        if all(15 < l < 25 for l in lengths):  # All medium length
            monotony += 0.3
        
        # Generate suggestions
        suggestions = []
        if variance < 10:
            suggestions.extend(random.sample(self.RHYTHM_SUGGESTIONS["too_uniform"], 1))
        if repeated:
            suggestions.extend(random.sample(self.RHYTHM_SUGGESTIONS["same_starters"], 1))
        if avg_length > 25:
            suggestions.extend(random.sample(self.RHYTHM_SUGGESTIONS["too_long"], 1))
        if avg_length < 8:
            suggestions.extend(random.sample(self.RHYTHM_SUGGESTIONS["too_short"], 1))
        
        return RhythmAnalysis(
            avg_sentence_length=avg_length,
            sentence_length_variance=variance,
            repeated_starters=repeated,
            monotony_score=min(1.0, monotony),
            suggestions=suggestions
        )
    
    def get_improvement_guidance(self, text: str) -> str:
        """Generate guidance based on rhythm analysis."""
        analysis = self.analyze(text)
        
        if analysis.monotony_score < 0.3:
            return ""  # No issues
        
        guidance_parts = [f"<rhythm_feedback>"]
        guidance_parts.append(f"RHYTHM ANALYSIS: Monotony score {analysis.monotony_score:.1f}/1.0")
        
        if analysis.repeated_starters:
            guidance_parts.append(f"REPEATED STARTERS: Too many sentences start with: {', '.join(analysis.repeated_starters)}")
        
        if analysis.suggestions:
            guidance_parts.append("SUGGESTIONS:")
            for s in analysis.suggestions:
                guidance_parts.append(f"  - {s}")
        
        guidance_parts.append("</rhythm_feedback>")
        return "\n".join(guidance_parts)


# =============================================================================
# VOICE CONSISTENCY CHECKER
# =============================================================================

@dataclass
class VoiceProfile:
    """Captured voice characteristics for an NPC."""
    name: str
    vocabulary_level: str  # "simple", "moderate", "sophisticated", "technical"
    sentence_style: str  # "terse", "flowing", "fragmented", "formal"
    verbal_tics: List[str]  # Repeated phrases, filler words
    topics_discussed: List[str]
    emotional_range: str  # "restrained", "expressive", "volatile"
    sample_lines: List[str]


@dataclass 
class VoiceConsistencyChecker:
    """
    Ensures NPCs maintain consistent and distinctive voices.
    
    Tracks each NPC's speech patterns and flags when dialogue
    doesn't match their established voice.
    """
    
    voice_profiles: Dict[str, VoiceProfile] = field(default_factory=dict)
    
    VOCABULARY_MARKERS: Dict[str, List[str]] = field(default_factory=lambda: {
        "simple": ["gonna", "gotta", "ain't", "yeah", "nope", "stuff", "thing"],
        "moderate": ["perhaps", "certainly", "actually", "apparently", "basically"],
        "sophisticated": ["nevertheless", "consequently", "ostensibly", "paradigm"],
        "technical": ["parameters", "protocol", "interface", "calibrate", "diagnostic"]
    })
    
    STYLE_MARKERS: Dict[str, str] = field(default_factory=lambda: {
        "terse": "Short sentences. Few words. Gets to the point.",
        "flowing": "Longer, more elaborate sentences with subclauses and detail.",
        "fragmented": "Interrupted. Trails off... Starts again. You know?",
        "formal": "Proper grammar, complete sentences, no contractions."
    })
    
    def register_dialogue(self, npc_name: str, dialogue: str):
        """Register dialogue to build/update voice profile."""
        if npc_name not in self.voice_profiles:
            self.voice_profiles[npc_name] = VoiceProfile(
                name=npc_name,
                vocabulary_level="moderate",
                sentence_style="flowing",
                verbal_tics=[],
                topics_discussed=[],
                emotional_range="expressive",
                sample_lines=[]
            )
        
        profile = self.voice_profiles[npc_name]
        profile.sample_lines.append(dialogue[:100])
        if len(profile.sample_lines) > 10:
            profile.sample_lines = profile.sample_lines[-10:]
        
        # Detect vocabulary level
        dialogue_lower = dialogue.lower()
        for level, markers in self.VOCABULARY_MARKERS.items():
            if any(m in dialogue_lower for m in markers):
                profile.vocabulary_level = level
                break
    
    def get_voice_guidance(self, npc_name: str) -> str:
        """Get guidance for maintaining NPC voice consistency."""
        if npc_name not in self.voice_profiles:
            return ""
        
        profile = self.voice_profiles[npc_name]
        
        sample_display = ""
        if profile.sample_lines:
            recent = profile.sample_lines[-3:]
            sample_display = "\n".join([f'  "{line}"' for line in recent])
        
        return f"""<voice_consistency npc="{npc_name}">
ESTABLISHED VOICE for {npc_name}:
- Vocabulary: {profile.vocabulary_level}
- Style: {profile.sentence_style} - {self.STYLE_MARKERS.get(profile.sentence_style, '')}
- Emotional range: {profile.emotional_range}

SAMPLE LINES (maintain this voice):
{sample_display}

CONSISTENCY CHECK: Does new dialogue match this established pattern?
If {npc_name} has always spoken tersely, don't suddenly give them flowery speeches.
</voice_consistency>"""
    
    def get_all_voices_context(self, active_npcs: List[str]) -> str:
        """Get voice context for all active NPCs."""
        contexts = []
        for npc in active_npcs:
            if npc in self.voice_profiles:
                contexts.append(self.get_voice_guidance(npc))
        
        if not contexts:
            return ""
        
        return "\n".join(contexts)
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "voice_profiles": {
                name: {
                    "name": p.name,
                    "vocabulary_level": p.vocabulary_level,
                    "sentence_style": p.sentence_style,
                    "verbal_tics": p.verbal_tics,
                    "topics_discussed": p.topics_discussed,
                    "emotional_range": p.emotional_range,
                    "sample_lines": p.sample_lines
                } for name, p in self.voice_profiles.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "VoiceConsistencyChecker":
        """Deserialize from dictionary."""
        checker = cls()
        for name, p in data.get("voice_profiles", {}).items():
            checker.voice_profiles[name] = VoiceProfile(
                name=p["name"],
                vocabulary_level=p["vocabulary_level"],
                sentence_style=p["sentence_style"],
                verbal_tics=p.get("verbal_tics", []),
                topics_discussed=p.get("topics_discussed", []),
                emotional_range=p["emotional_range"],
                sample_lines=p.get("sample_lines", [])
            )
        return checker


# =============================================================================
# METAPHOR/SIMILE ENGINE
# =============================================================================

class FigurativeType(Enum):
    """Types of figurative language."""
    SIMILE = "simile"  # Like/as comparison
    METAPHOR = "metaphor"  # Direct comparison
    PERSONIFICATION = "personification"  # Human qualities to non-human
    SYNECDOCHE = "synecdoche"  # Part for whole


@dataclass
class MetaphorEngine:
    """
    Generates contextually appropriate figurative language.
    
    Provides similes, metaphors, and other figurative devices
    matched to genre, mood, and subject matter.
    """
    
    # Domain-specific figurative language banks
    SPACE_FIGURATIVES: Dict[str, List[str]] = field(default_factory=lambda: {
        "darkness": [
            "darkness thick as engine grease",
            "the void swallowed light like a hunger",
            "shadows pooled like spilled oil",
            "night pressed against the viewport like curious fingers"
        ],
        "silence": [
            "silence heavy as radiation shielding",
            "quiet that hummed like dying circuits",
            "the kind of silence that makes your ears ring",
            "stillness that felt like held breath"
        ],
        "danger": [
            "threat crackling like static before a storm",
            "death waiting patient as a targeting computer",
            "danger coiled in the air like magnetic flux",
            "the moment before hull breach—everything suspended"
        ],
        "technology": [
            "the console glowed like a dying star's last gasp",
            "data streamed past like rain on a canopy",
            "the ship groaned, bones of metal protesting",
            "engines purring like a predator at rest"
        ],
        "emotion": [
            "hope thin as recycled atmosphere",
            "grief settling into bones like zero-g",
            "anger burning cold as interstellar space",
            "love stubborn as corrosion, spreading slow"
        ],
        "time": [
            "minutes stretched like relativistic dilation",
            "time compressed, each second a lifetime",
            "hours slid past unnoticed as drift",
            "the moment crystallized, frozen in memory"
        ]
    })
    
    NOIR_FIGURATIVES: Dict[str, List[str]] = field(default_factory=lambda: {
        "darkness": [
            "shadows stacked like old debts",
            "darkness wearing the station like a shroud",
            "black as a loan shark's heart",
            "night that had forgotten morning existed"
        ],
        "danger": [
            "trouble written in neon and blood",
            "the kind of wrong that leaves a body",
            "death tap-dancing at the edge of vision",
            "threat thick enough to choke on"
        ],
        "character": [
            "face like a map of bad decisions",
            "eyes that had seen too much and forgotten none",
            "smile that promised nothing good",
            "the kind of tired that sleep doesn't fix"
        ]
    })
    
    HORROR_FIGURATIVES: Dict[str, List[str]] = field(default_factory=lambda: {
        "fear": [
            "dread crawling up the spine on centipede legs",
            "fear with weight, settling in the stomach like stone",
            "terror that tasted like copper and bile",
            "panic clawing at the inside of the skull"
        ],
        "wrongness": [
            "angles that hurt to look at directly",
            "movement at the edge of vision, patient and wrong",
            "the feeling of being watched by something that didn't have eyes",
            "reality wearing thin like old fabric"
        ],
        "atmosphere": [
            "air thick with something that wasn't quite smell",
            "silence that listened back",
            "cold that came from inside, not out",
            "the quality of light before something breaks"
        ]
    })
    
    current_genre: str = "space_opera"
    used_recently: Set[str] = field(default_factory=set)
    
    def get_figurative(self, subject: str, genre: str = None) -> Optional[str]:
        """Get a figurative expression for the subject."""
        genre = genre or self.current_genre
        
        # Select appropriate bank
        if "noir" in genre.lower():
            bank = self.NOIR_FIGURATIVES
        elif "horror" in genre.lower():
            bank = self.HORROR_FIGURATIVES
        else:
            bank = self.SPACE_FIGURATIVES
        
        # Find matching subject
        subject_lower = subject.lower()
        matching_key = None
        for key in bank.keys():
            if key in subject_lower or subject_lower in key:
                matching_key = key
                break
        
        if not matching_key:
            # Try general emotional mapping
            for key in ["emotion", "danger", "darkness"]:
                if key in bank:
                    matching_key = key
                    break
        
        if not matching_key:
            return None
        
        options = bank[matching_key]
        # Filter out recently used
        available = [o for o in options if o not in self.used_recently]
        if not available:
            self.used_recently.clear()
            available = options
        
        chosen = random.choice(available)
        self.used_recently.add(chosen)
        
        return chosen
    
    def get_narrator_guidance(self, subjects: List[str] = None) -> str:
        """Generate figurative language suggestions for narrator."""
        subjects = subjects or ["darkness", "emotion", "time"]
        
        suggestions = []
        for subject in subjects[:3]:
            fig = self.get_figurative(subject)
            if fig:
                suggestions.append(f'  - {subject}: "{fig}"')
        
        if not suggestions:
            return ""
        
        return f"""<figurative_language>
METAPHOR/SIMILE SUGGESTIONS for this scene:
{chr(10).join(suggestions)}

USAGE GUIDANCE:
- Use sparingly—one strong metaphor per paragraph maximum
- Match intensity to emotional weight of scene
- Avoid clichés (avoid: "cold as ice", "black as night", "fast as lightning")
- Best metaphors feel fresh yet inevitable

TECHNIQUE: Extended Metaphor
Pick one metaphor and thread it through a passage:
"The station was a body, and they were in its gut—pipes for veins, 
conduits for nerves, and somewhere above them, the brain that ran it all."
</figurative_language>"""
    
    def to_dict(self) -> dict:
        return {
            "current_genre": self.current_genre,
            "used_recently": list(self.used_recently)
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "MetaphorEngine":
        engine = cls()
        engine.current_genre = data.get("current_genre", "space_opera")
        engine.used_recently = set(data.get("used_recently", []))
        return engine


# =============================================================================
# WORD CHOICE ENHANCER
# =============================================================================

@dataclass
class WordChoiceEnhancer:
    """
    Suggests stronger word choices for common weak words.
    
    Replaces vague or overused words with precise alternatives
    matched to context and mood.
    """
    
    WEAK_TO_STRONG: Dict[str, Dict[str, List[str]]] = field(default_factory=lambda: {
        "walked": {
            "confident": ["strode", "marched", "stalked"],
            "nervous": ["crept", "edged", "skulked"],
            "tired": ["trudged", "shuffled", "dragged"],
            "fast": ["hurried", "rushed", "bolted"],
            "casual": ["ambled", "wandered", "drifted"]
        },
        "said": {
            "angry": ["snapped", "snarled", "spat"],
            "quiet": ["murmured", "whispered", "breathed"],
            "uncertain": ["hedged", "ventured", "offered"],
            "confident": ["declared", "announced", "stated"],
            "sad": ["sighed", "managed", "choked out"]
        },
        "looked": {
            "quick": ["glanced", "flicked", "darted"],
            "intense": ["stared", "fixed on", "scrutinized"],
            "searching": ["scanned", "swept", "examined"],
            "furtive": ["peeked", "peered", "spied"]
        },
        "very": {
            "default": ["extremely", "remarkably", "utterly", "absolutely"]
        },
        "big": {
            "default": ["massive", "vast", "enormous", "imposing", "hulking"]
        },
        "small": {
            "default": ["tiny", "minuscule", "cramped", "compact", "diminutive"]
        },
        "good": {
            "default": ["excellent", "superb", "exceptional", "outstanding"]
        },
        "bad": {
            "default": ["terrible", "awful", "dire", "grim", "catastrophic"]
        },
        "nice": {
            "default": ["pleasant", "agreeable", "charming", "delightful"]
        },
        "thing": {
            "default": ["object", "device", "artifact", "mechanism", "entity"]
        }
    })
    
    def get_enhancement_guidance(self) -> str:
        """Generate word choice guidance for narrator."""
        # Select a few examples to highlight
        examples = []
        sample_words = random.sample(list(self.WEAK_TO_STRONG.keys()), 4)
        
        for word in sample_words:
            contexts = self.WEAK_TO_STRONG[word]
            context = random.choice(list(contexts.keys()))
            alternatives = contexts[context][:3]
            examples.append(f'  - "{word}" ({context}) → {", ".join(alternatives)}')
        
        return f"""<word_choice>
AVOID WEAK WORDS - Replace with precise alternatives:
{chr(10).join(examples)}

PRECISION PRINCIPLE:
Every word should be the RIGHT word, not just a word that works.
"She walked into the room" tells us nothing.
"She stalked into the room" tells us everything.

THE ONE-WORD TEST:
Before using a word, ask: "Can I find a single word that does more work?"
"Very angry" → "furious"
"Walked quickly" → "hurried"
"Said loudly" → "shouted"

SAID IS (SOMETIMES) FINE:
Don't replace every "said" with creative tags. 
Use vivid alternatives when the HOW matters.
Use "said" when it should disappear.
</word_choice>"""


# =============================================================================
# MASTER PROSE ENHANCEMENT ENGINE
# =============================================================================

@dataclass
class ProseEnhancementEngine:
    """Master engine coordinating all prose enhancement systems."""
    
    sensory_tracker: SensoryConsistencyTracker = field(default_factory=SensoryConsistencyTracker)
    rhythm_analyzer: ProseRhythmAnalyzer = field(default_factory=ProseRhythmAnalyzer)
    voice_checker: VoiceConsistencyChecker = field(default_factory=VoiceConsistencyChecker)
    metaphor_engine: MetaphorEngine = field(default_factory=MetaphorEngine)
    word_enhancer: WordChoiceEnhancer = field(default_factory=WordChoiceEnhancer)
    
    def process_narrative(self, narrative: str, location: str, active_npcs: List[str] = None):
        """Process generated narrative to update all trackers."""
        # Update sensory tracker
        self.sensory_tracker.register_details(narrative, location)
        
        # Extract and register NPC dialogue
        if active_npcs:
            for npc in active_npcs:
                # Simple dialogue extraction (look for quotes after name)
                pattern = rf'{npc}[^"]*"([^"]+)"'
                matches = re.findall(pattern, narrative, re.IGNORECASE)
                for dialogue in matches:
                    self.voice_checker.register_dialogue(npc, dialogue)
    
    def get_comprehensive_guidance(
        self,
        location: str = "",
        active_npcs: List[str] = None,
        genre: str = "space_opera",
        subjects: List[str] = None
    ) -> str:
        """Generate comprehensive prose enhancement guidance."""
        
        sections = []
        
        # Sensory callbacks
        if location:
            self.sensory_tracker.current_location = location
            sensory = self.sensory_tracker.get_callback_suggestions()
            if sensory:
                sections.append(sensory)
        
        # Voice consistency for active NPCs
        if active_npcs:
            voice_context = self.voice_checker.get_all_voices_context(active_npcs)
            if voice_context:
                sections.append(voice_context)
        
        # Metaphor suggestions
        self.metaphor_engine.current_genre = genre
        metaphors = self.metaphor_engine.get_narrator_guidance(subjects)
        if metaphors:
            sections.append(metaphors)
        
        # Word choice guidance
        sections.append(self.word_enhancer.get_enhancement_guidance())
        
        if not sections:
            return ""
        
        return f"""
<prose_enhancement>
=== PROSE ENHANCEMENT GUIDANCE ===
{chr(10).join(sections)}
</prose_enhancement>
"""
    
    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "sensory_tracker": self.sensory_tracker.to_dict(),
            "voice_checker": self.voice_checker.to_dict(),
            "metaphor_engine": self.metaphor_engine.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ProseEnhancementEngine":
        """Deserialize from dictionary."""
        engine = cls()
        if "sensory_tracker" in data:
            engine.sensory_tracker = SensoryConsistencyTracker.from_dict(data["sensory_tracker"])
        if "voice_checker" in data:
            engine.voice_checker = VoiceConsistencyChecker.from_dict(data["voice_checker"])
        if "metaphor_engine" in data:
            engine.metaphor_engine = MetaphorEngine.from_dict(data["metaphor_engine"])
        return engine


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("PROSE ENHANCEMENT ENGINE - TEST")
    print("=" * 60)
    
    engine = ProseEnhancementEngine()
    
    # Test sensory tracking
    test_narrative = """
    The recycled air carried a faint metallic taste, like old blood. 
    Emergency lighting cast everything in deep red shadows. 
    Somewhere in the distance, a generator hummed its endless song.
    """
    
    engine.process_narrative(test_narrative, "Engine Room", ["Torres", "Chen"])
    
    # Test voice registration
    engine.voice_checker.register_dialogue("Torres", "Ain't got time for this. Move it.")
    engine.voice_checker.register_dialogue("Torres", "Yeah? Well stuff happens. Deal with it.")
    engine.voice_checker.register_dialogue("Chen", "The diagnostic parameters indicate systemic failure.")
    
    print("\n--- COMPREHENSIVE GUIDANCE ---")
    guidance = engine.get_comprehensive_guidance(
        location="Engine Room",
        active_npcs=["Torres", "Chen"],
        genre="space_opera",
        subjects=["danger", "technology", "silence"]
    )
    print(guidance)
    
    print("\n--- RHYTHM ANALYSIS ---")
    analyzer = ProseRhythmAnalyzer()
    monotonous = "He walked. He stopped. He looked. He moved. He waited. He left."
    print(analyzer.get_improvement_guidance(monotonous))
