"""
Prose Craft System - Master-Level Narrative Writing Guidance

This module provides prose-level writing guidance to elevate narration from
functional to literary. It implements principles from master storytellers
and contemporary fiction craft.

Key Systems:
1. Sentence Rhythm - Vary length/structure for musicality
2. Sensory Specificity - Engage all five senses with precision
3. Telling Details - Select evocative, specific details
4. Dialogue Craft - Subtext, voice distinction, loading
5. Pathetic Fallacy - Environment mirrors emotion
6. POV Filtering - Narrate through character lens
7. Iceberg Theory - Imply more than stated
8. Micro-Pacing - Paragraph rhythm controls tension
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple
import random


# =============================================================================
# SENTENCE RHYTHM SYSTEM
# =============================================================================

class RhythmPattern(Enum):
    """Sentence rhythm patterns for variety."""
    STACCATO = auto()      # Short, punchy sentences for tension
    LEGATO = auto()        # Long, flowing sentences for immersion
    SYNCOPATED = auto()    # Mixed lengths for dynamism
    BUILDING = auto()      # Progressively longer for anticipation
    FALLING = auto()       # Progressively shorter for resolution
    FRAGMENT_PUNCH = auto() # Full sentence. Fragment. Impact.


@dataclass
class RhythmGuide:
    """Provides sentence rhythm guidance based on scene context."""
    
    PATTERN_EXAMPLES: Dict[RhythmPattern, str] = field(default_factory=lambda: {
        RhythmPattern.STACCATO: 
            "He ran. Footsteps behind. Closer. The door. Locked. No time.",
        RhythmPattern.LEGATO:
            "The corridor stretched before him like a throat preparing to swallow, "
            "its walls pressing closer with each step he took toward the distant light "
            "that flickered with the uncertainty of a dying star.",
        RhythmPattern.SYNCOPATED:
            "She waited. The clock on the wall measured out seconds like drops of blood "
            "falling into still water. Tick. The shadows lengthened across the floor, "
            "creeping toward her chair with patient malevolence. Tick. She didn't move.",
        RhythmPattern.BUILDING:
            "He breathed. He steadied his hand. He raised the weapon toward the door. "
            "He listened to the approaching footsteps growing louder, closer, inevitable. "
            "He thought of everyone who had ever trusted him and everyone who had died for that trust.",
        RhythmPattern.FALLING:
            "The explosion tore through the station's hull like the scream of a dying god, "
            "ripping metal and flesh alike into the cold embrace of the void. "
            "Alarms screamed. Lights died. Silence.",
        RhythmPattern.FRAGMENT_PUNCH:
            "The message was simple. Three words. Your daughter lives. Everything changed."
    })
    
    @classmethod
    def get_rhythm_for_scene(cls, tension: float, pacing: str) -> Tuple[RhythmPattern, str]:
        """Select appropriate rhythm pattern based on scene context."""
        if tension > 0.8:
            pattern = RhythmPattern.STACCATO
        elif tension > 0.6:
            pattern = random.choice([RhythmPattern.BUILDING, RhythmPattern.FRAGMENT_PUNCH])
        elif tension < 0.3:
            pattern = RhythmPattern.LEGATO
        else:
            pattern = RhythmPattern.SYNCOPATED
            
        guidance = f"""<sentence_rhythm>
RHYTHM: {pattern.name}
GUIDANCE: Match sentence length to emotional intensity. 
- High tension = short, fragmented sentences that mirror racing heartbeat
- Low tension = longer, flowing sentences that let readers breathe
- Transitions = vary deliberately to signal emotional shifts

TECHNIQUE: {cls.PATTERN_EXAMPLES.get(pattern, '')}

AVOID: 
- Same sentence length repeatedly (monotonous)
- Only subject-verb-object structures (mechanical)
- Starting consecutive sentences with same word (repetitive)
</sentence_rhythm>"""
        
        return pattern, guidance


# =============================================================================
# SENSORY SPECIFICITY SYSTEM
# =============================================================================

class SenseType(Enum):
    """The five senses plus proprioception and interoception."""
    SIGHT = "visual"
    SOUND = "auditory"
    SMELL = "olfactory"
    TASTE = "gustatory"
    TOUCH = "tactile"
    PROPRIOCEPTION = "body_position"  # Where limbs are in space
    INTEROCEPTION = "internal"  # Heartbeat, breathing, gut feelings


@dataclass
class SensoryPalette:
    """Generates sensory detail prompts for immersive description."""
    
    SENSE_PROMPTS: Dict[SenseType, List[str]] = field(default_factory=lambda: {
        SenseType.SIGHT: [
            "What specific colors dominate? (Not 'blue' but 'cobalt', 'cerulean', 'the blue of old bruises')",
            "What quality of light? (harsh, diffuse, flickering, absent)",
            "What small visual detail would the character notice first?"
        ],
        SenseType.SOUND: [
            "What's the baseline sound? (hum of recycled air, distant machinery, oppressive silence)",
            "What interrupts or punctuates that baseline?",
            "What sounds are conspicuously absent?"
        ],
        SenseType.SMELL: [
            "What's the dominant scent? (Smell triggers memory—what might it remind the character of?)",
            "Is it organic, mechanical, chemical?",
            "Does it change as they move through the space?"
        ],
        SenseType.TASTE: [
            "What taste lingers in their mouth? (fear tastes like copper, grief like ash)",
            "Is the air tasted on the tongue? (metallic, sweet with decay, sterile)",
            "What did they last eat/drink, and does that memory surface?"
        ],
        SenseType.TOUCH: [
            "What textures surround them? (rough, smooth, organic, synthetic)",
            "What's the temperature? (not just hot/cold—humid, dry, changing)",
            "What are their hands touching right now?"
        ],
        SenseType.PROPRIOCEPTION: [
            "How does their body feel in space? (cramped, exposed, off-balance)",
            "What's their posture communicating?",
            "Are they braced for impact, relaxed, coiled to run?"
        ],
        SenseType.INTEROCEPTION: [
            "What's their heartbeat doing? (not 'racing'—specific: 'a fist pounding at their ribs')",
            "How's their breathing? (shallow, caught, deliberately slow)",
            "What does their gut tell them?"
        ]
    })
    
    @classmethod
    def generate_sensory_guidance(cls, location_type: str = "generic") -> str:
        """Generate prompts to enrich sensory description."""
        # Select 3-4 senses to emphasize (always include at least one unusual one)
        primary_senses = [SenseType.SIGHT, SenseType.SOUND]
        unusual_senses = [SenseType.SMELL, SenseType.TASTE, SenseType.PROPRIOCEPTION, SenseType.INTEROCEPTION]
        
        selected = primary_senses + random.sample(unusual_senses, 2)
        
        prompts = []
        for sense in selected:
            prompt = random.choice(cls.SENSE_PROMPTS.get(sense, ["Describe this sense."]))
            prompts.append(f"  - {sense.value.upper()}: {prompt}")
        
        return f"""<sensory_guidance>
ENGAGE MULTIPLE SENSES in this description. Amateur writers over-rely on sight.
Master writers make readers feel present through unexpected sensory details.

PROMPTS FOR THIS SCENE:
{chr(10).join(prompts)}

TECHNIQUE: Lead with an unexpected sense, then layer others.
BAD: "The room was dark and smelled bad."
GOOD: "The recycled air carried the ghost of old sweat and stale coffee—the smell of too many 
long nights. Emergency lights painted the corridor in bloody reds that turned every shadow suspect."

AVOID: Generic descriptors (beautiful, nice, bad, strange)
USE: Specific, evocative details that only THIS place would have
</sensory_guidance>"""


# =============================================================================
# TELLING DETAILS SYSTEM
# =============================================================================

@dataclass
class TellingDetailGuide:
    """Guidance for selecting details that do narrative work."""
    
    DETAIL_PRINCIPLES: List[str] = field(default_factory=lambda: [
        "One perfect detail > ten generic descriptions",
        "Details should reveal character, advance plot, or establish mood (ideally all three)",
        "What would THIS character notice that another wouldn't?",
        "What's slightly wrong or off about the scene?",
        "What detail, if removed, would the reader miss most?",
        "What's the detail the character is trying NOT to notice?",
        "What do worn edges, scratches, and repairs reveal about history?"
    ])
    
    DETAIL_EXAMPLES: Dict[str, str] = field(default_factory=lambda: {
        "character_revealing":
            "She noticed his hands first—clean nails, soft palms. "
            "A man who'd never worked a day in his life. Or one who ensured others did the dirty work.",
        "mood_setting":
            "The photograph on his desk faced the wall.",
        "plot_advancing":
            "Three coffee cups on the table. Two still steaming. But only one chair.",
        "world_building":
            "The shop's prices were listed in three currencies, two of which no longer existed.",
        "tension_building":
            "Everything in the apartment was perfectly in place. Too perfect. "
            "As if someone had cleaned thoroughly before leaving. Or after."
    })
    
    @classmethod
    def generate_detail_guidance(cls) -> str:
        """Generate guidance for selecting telling details."""
        principle = random.choice(cls.DETAIL_PRINCIPLES)
        example_type = random.choice(list(cls.DETAIL_EXAMPLES.keys()))
        example = cls.DETAIL_EXAMPLES[example_type]
        
        return f"""<telling_details>
PRINCIPLE: {principle}

The right detail does more work than paragraphs of description.
Ask: What single object or observation would tell this story if I could only choose one?

EXAMPLE ({example_type.replace('_', ' ')}):
"{example}"

TECHNIQUE: The "Camera Lingers" test
If this were a film, what would the camera hold on for an extra beat?
That's your telling detail. Describe THAT.

AVOID:
- Exhaustive inventories of room contents
- Details that any character would notice equally
- Decorative description that does no narrative work
</telling_details>"""


# =============================================================================
# DIALOGUE CRAFT SYSTEM
# =============================================================================

class DialogueTechnique(Enum):
    """Advanced dialogue techniques."""
    SUBTEXT = "Characters rarely say exactly what they mean"
    COMPRESSION = "Cut small talk—enter late, leave early"
    DISTINCTIVE_VOICE = "Each character should sound unique"
    LOADING = "Every line should carry weight"
    MISDIRECTION = "What characters don't say matters"
    POWER_DYNAMICS = "Status is negotiated through speech"
    INTERRUPTION = "Break patterns to show emotion"


@dataclass
class DialogueCraftGuide:
    """Advanced dialogue writing guidance."""
    
    VOICE_MARKERS: Dict[str, List[str]] = field(default_factory=lambda: {
        "educated": ["complex sentences", "precise vocabulary", "conditional phrasing"],
        "street": ["contractions", "interrupted thoughts", "slang", "code-switching"],
        "military": ["clipped", "acronyms", "passive voice for accountability avoidance"],
        "nervous": ["filler words", "trailing off", "questions answered with questions"],
        "powerful": ["declarative statements", "comfortable silence", "others' names used"],
        "manipulative": ["questions that assume answers", "we not I", "flattery-wrapped demands"]
    })
    
    SUBTEXT_EXAMPLES: List[Tuple[str, str, str]] = field(default_factory=lambda: [
        (
            "I'm not angry.",
            "She set the glass down with exquisite care.",
            "What's NOT said (she's furious) is revealed by action, not words."
        ),
        (
            "'How's Sarah?' 'She's fine.'",
            "The conversation stopped. Started. Stopped again.",
            "The awkwardness around the topic is the real information."
        ),
        (
            "'Interesting plan.'",
            "He didn't look up from his datapad.",
            "'Interesting' is the word people use when they can't say what they think."
        )
    ])
    
    @classmethod
    def generate_dialogue_guidance(cls, speaking_character: Optional[str] = None) -> str:
        """Generate dialogue craft guidance."""
        example = random.choice(cls.SUBTEXT_EXAMPLES)
        
        techniques = random.sample(list(DialogueTechnique), 3)
        technique_list = "\n".join([f"  - {t.name}: {t.value}" for t in techniques])
        
        return f"""<dialogue_craft>
MASTER DIALOGUE PRINCIPLES:

{technique_list}

SUBTEXT EXAMPLE:
  Dialogue: "{example[0]}"
  Action beat: {example[1]}
  Why it works: {example[2]}

TECHNIQUE: Dialogue Iceberg
  - The surface: what they say
  - Below surface: what they mean
  - Deep below: what they're afraid to admit

VOICE DISTINCTION:
Every character should be identifiable by speech alone. Consider:
  - Sentence length (curt vs. elaborate)
  - Vocabulary (educated, technical, profane)
  - Rhythm (staccato, flowing, halting)
  - What topics they avoid

AVOID:
  - "As you know, Bob" exposition
  - Characters explaining their emotions ("I feel angry")
  - Perfectly articulate emotional speeches (people struggle to express deep feelings)
  - Dialogue that could be said by any character
</dialogue_craft>"""


# =============================================================================
# PATHETIC FALLACY SYSTEM
# =============================================================================

@dataclass
class PatheticFallacyGuide:
    """Environment-emotion mirroring guidance."""
    
    EMOTION_ENVIRONMENTS: Dict[str, List[str]] = field(default_factory=lambda: {
        "grief": [
            "rain on windows like the room itself is weeping",
            "gray light that flattens everything",
            "the distant sound of something winding down",
            "objects that used to belong to someone"
        ],
        "tension": [
            "flickering lights that refuse to stay steady",
            "sounds that almost resolve into words",
            "shadows that seem to move when not directly observed",
            "stuck doors, jammed drawers, things that don't work"
        ],
        "hope": [
            "light breaking through where it shouldn't",
            "the first growth in desolate places",
            "machines that unexpectedly spring to life",
            "warmth in a cold place"
        ],
        "dread": [
            "the hum of something vast and patient",
            "architecture that seems designed to disorient",
            "the smell of something wrong but unidentifiable",
            "silence where there should be sound"
        ],
        "rage": [
            "sharp edges and harsh angles",
            "red warning lights, alarm sounds",
            "things breaking, systems failing",
            "heat building toward release"
        ],
        "peace": [
            "systems running smoothly, everything in place",
            "natural light, organic curves",
            "distant sounds that don't demand attention",
            "the smell of something clean or alive"
        ]
    })
    
    @classmethod
    def generate_fallacy_guidance(cls, emotional_state: str = "tension") -> str:
        """Generate environment-emotion mirroring guidance."""
        # Find closest match or default
        matched_emotion = emotional_state.lower()
        if matched_emotion not in cls.EMOTION_ENVIRONMENTS:
            matched_emotion = "tension"  # Default
            
        examples = cls.EMOTION_ENVIRONMENTS[matched_emotion]
        
        return f"""<pathetic_fallacy>
ENVIRONMENT-EMOTION MIRRORING for: {matched_emotion.upper()}

The environment should FEEL like the emotional state without stating it.
The world becomes a reflection of inner experience.

ENVIRONMENTAL SUGGESTIONS:
{chr(10).join([f"  - {ex}" for ex in examples])}

TECHNIQUE: Transferred Epithets
Instead of "She felt anxious in the room," try:
"The room felt anxious—every surface too sharp, every shadow too deep."

SUBTLETY SCALE:
  1. Heavy-handed: "Storm clouds gathered as she received the bad news"
  5. Balanced: Environmental details that could be coincidence... but feel connected
  10. Subtle: The reader feels the emotion from environment without consciously noting why

AIM: 5-7 on the subtlety scale. Let environment suggest, not declare.

AVOID: Weather clichés (storms for conflict, rain for sadness, sunshine for joy)
</pathetic_fallacy>"""


# =============================================================================
# POV FILTERING SYSTEM
# =============================================================================

@dataclass
class POVFilter:
    """Point-of-view filtering guidance."""
    
    POV_PRINCIPLES: List[str] = field(default_factory=lambda: [
        "Everything is filtered through the POV character's perceptions and biases",
        "What they notice reveals who they are",
        "What they DON'T notice is equally revealing",
        "Their vocabulary affects how the world is described",
        "Their emotional state colors their perceptions",
        "Unreliable narration is more interesting than omniscient truth"
    ])
    
    @classmethod
    def generate_pov_guidance(cls, character_name: str = "the protagonist", 
                              character_traits: List[str] = None) -> str:
        """Generate POV filtering guidance."""
        traits = character_traits or ["observant", "guarded"]
        traits_str = ", ".join(traits)
        
        principles = random.sample(cls.POV_PRINCIPLES, 3)
        
        return f"""<pov_filtering>
NARRATE THROUGH: {character_name} (traits: {traits_str})

Everything in the narration should feel filtered through this character's unique consciousness.

PRINCIPLES:
{chr(10).join([f"  - {p}" for p in principles])}

TECHNIQUE: The Perception Test
For every description, ask: "Would THIS character notice/think/phrase it this way?"
  - A soldier notices exits and sight lines
  - A medic notices signs of stress in faces
  - A mechanic notices what's about to break
  - A con artist notices what people are trying to hide

EMOTIONAL COLORING:
The same room described by someone grieving feels different than by someone in love.
Let {character_name}'s current emotional state tint every observation.

VOCABULARY CHECK:
Use words this character would actually know/use.
A street kid doesn't describe things in technical jargon.
A scientist doesn't use vague, flowery language.

AVOID:
  - Describing anything the POV character can't perceive
  - Neutral, objective description (that's documentary, not fiction)
  - Knowing what other characters are thinking (only observable behavior)
</pov_filtering>"""


# =============================================================================
# ICEBERG THEORY SYSTEM
# =============================================================================

@dataclass
class IcebergGuide:
    """Hemingway's iceberg theory - show 1/8, imply 7/8."""
    
    ICEBERG_TECHNIQUES: List[Tuple[str, str]] = field(default_factory=lambda: [
        (
            "The gesture that replaces explanation",
            "Instead of 'She was nervous about seeing him again,' show: "
            "'She checked her reflection in the dark screen three times before the door opened.'"
        ),
        (
            "The question that makes readers ask their own",
            "Instead of explaining the history, have a character say: "
            "'I see you're still wearing that ring.' Let readers imagine what happened."
        ),
        (
            "The conspicuous absence",
            "Don't describe what's missing—describe everything else's reaction to it. "
            "'The dinner table was set for four. Only two chairs were used.'"
        ),
        (
            "The loaded object",
            "An object carries weight without explanation. "
            "She found the music box in his quarters. She didn't wind it."
        ),
        (
            "The interrupted moment",
            "Cut before the expected reaction. "
            "'I have something to tell you,' she said. She looked at the stars. "
            "The stars didn't look back. End scene. Let readers feel what comes next."
        )
    ])
    
    @classmethod
    def generate_iceberg_guidance(cls) -> str:
        """Generate iceberg theory guidance."""
        techniques = random.sample(cls.ICEBERG_TECHNIQUES, 3)
        
        return f"""<iceberg_theory>
HEMINGWAY'S ICEBERG: Show 1/8, imply 7/8

The goal is resonance—that feeling when a reader senses depth beneath the surface.
Trust your audience. They want to work for meaning.

TECHNIQUES:
{chr(10).join([f"  - {t[0]}: {t[1]}" for t in techniques])}

THE SILENCE TEST:
After writing a paragraph, ask: "What can I delete and still have the meaning land?"
The best version is often the shortest version that still echoes.

EMOTIONAL RESTRAINT:
The deeper the emotion, the more restrained the prose should be.
Melodrama diminishes tragedy. Understatement amplifies it.

MOMENTS TO UNDERSTATE:
  - Death (don't milk it—let the fact speak)
  - Betrayal (the quiet devastation hits harder than shouting)
  - Love (actions over declarations)
  - Sacrifice (don't explain the nobility—show the cost)

AVOID:
  - Explaining the metaphor after presenting it
  - Characters articulating exactly what they've learned
  - Narrator commenting on the significance of moments
  - "She didn't know it yet, but this would change everything"
</iceberg_theory>"""


# =============================================================================
# MICRO-PACING SYSTEM
# =============================================================================

class ParagraphPace(Enum):
    """Paragraph length for pacing control."""
    DENSE = "Long paragraphs slow pace, build immersion, suit contemplation"
    RAPID = "Short paragraphs accelerate pace, suit action/tension"
    STAGGERED = "Varied lengths create rhythm, suit dynamic scenes"
    WHITE_SPACE = "Single sentences as paragraphs create emphasis and pause"


@dataclass
class MicroPacingGuide:
    """Paragraph-level pacing control."""
    
    @classmethod
    def generate_pacing_guidance(cls, tension_level: float, 
                                  scene_type: str = "action") -> str:
        """Generate paragraph pacing guidance."""
        if tension_level > 0.8:
            pace = ParagraphPace.RAPID
            example = """He ran.
            
The corridor stretched. Endless.

Behind him, the sound of systematic searching. Closer.

Door. Another door. Another.

Locked. All locked."""
        elif tension_level > 0.5:
            pace = ParagraphPace.STAGGERED
            example = """She studied the console, her fingers hovering over controls she didn't 
fully understand. The schematics made sense in theory. In practice, one wrong sequence 
could decompress the entire module.

A sound behind her.

She didn't turn. Kept her breathing steady. Someone was watching, and they wanted 
her to know it."""
        else:
            pace = ParagraphPace.DENSE
            example = """The observation deck had been her favorite place since she first 
arrived at the station, back when everything had seemed possible and the darkness 
between the stars was just distance, not metaphor. She came here when she needed 
to remember that the universe was larger than her problems, that somewhere out 
there, light was still moving toward worlds that wouldn't see it for centuries, 
carrying messages no one had sent to receivers that didn't exist yet."""
            
        return f"""<micro_pacing>
TENSION LEVEL: {tension_level:.1f} → {pace.name}
{pace.value}

PARAGRAPH LENGTH CONTROL:
  - Fast/tense: 1-2 sentences per paragraph. White space = held breath.
  - Moderate: 3-4 sentences. Room to breathe but momentum maintained.
  - Slow/contemplative: 5+ sentences. Immersive, meditative, interior.

CURRENT SCENE PACE EXAMPLE:
{example}

RHYTHM BREAKS:
A single-sentence paragraph after longer ones = emphasis
A long paragraph after short ones = shift in intensity
Use this deliberately.

LINE BREAK = BEAT
Every paragraph break is a pause. Use them like a drummer uses silence.

AVOID:
  - Same paragraph length throughout (monotonous)
  - Changing pace without narrative reason
  - Action scenes with long paragraphs (prevents urgency)
  - Quiet moments with choppy paragraphs (prevents immersion)
</micro_pacing>"""


# =============================================================================
# PROSE CRAFT MASTER GENERATOR
# =============================================================================

@dataclass
class ProseCraftEngine:
    """Master engine for generating comprehensive prose guidance."""
    
    rhythm_guide: RhythmGuide = field(default_factory=RhythmGuide)
    sensory_palette: SensoryPalette = field(default_factory=SensoryPalette)
    detail_guide: TellingDetailGuide = field(default_factory=TellingDetailGuide)
    dialogue_guide: DialogueCraftGuide = field(default_factory=DialogueCraftGuide)
    fallacy_guide: PatheticFallacyGuide = field(default_factory=PatheticFallacyGuide)
    pov_filter: POVFilter = field(default_factory=POVFilter)
    iceberg_guide: IcebergGuide = field(default_factory=IcebergGuide)
    pacing_guide: MicroPacingGuide = field(default_factory=MicroPacingGuide)
    
    def generate_comprehensive_guidance(
        self,
        tension_level: float = 0.5,
        emotional_state: str = "neutral",
        pov_character: str = "the protagonist",
        character_traits: List[str] = None,
        scene_type: str = "general",
        location_type: str = "generic"
    ) -> str:
        """Generate comprehensive prose guidance for narrator."""
        
        sections = []
        
        # Get rhythm guidance
        _, rhythm = RhythmGuide.get_rhythm_for_scene(tension_level, scene_type)
        sections.append(rhythm)
        
        # Sensory guidance
        sections.append(SensoryPalette.generate_sensory_guidance(location_type))
        
        # Telling details
        sections.append(TellingDetailGuide.generate_detail_guidance())
        
        # Dialogue craft
        sections.append(DialogueCraftGuide.generate_dialogue_guidance(pov_character))
        
        # Pathetic fallacy
        sections.append(PatheticFallacyGuide.generate_fallacy_guidance(emotional_state))
        
        # POV filtering
        sections.append(POVFilter.generate_pov_guidance(pov_character, character_traits))
        
        # Iceberg theory
        sections.append(IcebergGuide.generate_iceberg_guidance())
        
        # Micro-pacing
        sections.append(MicroPacingGuide.generate_pacing_guidance(tension_level, scene_type))
        
        master_guidance = f"""
<prose_craft_mastery>
=== PROSE-LEVEL WRITING GUIDANCE ===

Your narration should read like literary fiction, not game text.
Every sentence should earn its place. Every word should carry weight.

THE THREE TESTS FOR EVERY PARAGRAPH:
1. MUSIC: Does it sound good read aloud? Is there rhythm and variety?
2. PRECISION: Is every word the right word? (Not good—the RIGHT one?)
3. RESONANCE: Does it suggest more than it states? Does it echo?

{chr(10).join(sections)}

FINAL PRINCIPLE: Write the sentence you would want to read.
Not the obvious one. The true one.
</prose_craft_mastery>
"""
        return master_guidance
    
    def generate_quick_guidance(self, focus: str = "general") -> str:
        """Generate focused guidance on a single prose element."""
        focus_map = {
            "rhythm": lambda: RhythmGuide.get_rhythm_for_scene(0.5, "general")[1],
            "senses": lambda: SensoryPalette.generate_sensory_guidance(),
            "details": lambda: TellingDetailGuide.generate_detail_guidance(),
            "dialogue": lambda: DialogueCraftGuide.generate_dialogue_guidance(),
            "environment": lambda: PatheticFallacyGuide.generate_fallacy_guidance(),
            "pov": lambda: POVFilter.generate_pov_guidance(),
            "iceberg": lambda: IcebergGuide.generate_iceberg_guidance(),
            "pacing": lambda: MicroPacingGuide.generate_pacing_guidance(0.5)
        }
        
        if focus in focus_map:
            return focus_map[focus]()
        
        # Default: random selection
        return random.choice(list(focus_map.values()))()


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    engine = ProseCraftEngine()
    
    print("=" * 60)
    print("PROSE CRAFT ENGINE - COMPREHENSIVE GUIDANCE TEST")
    print("=" * 60)
    
    guidance = engine.generate_comprehensive_guidance(
        tension_level=0.7,
        emotional_state="tension",
        pov_character="Commander Thane",
        character_traits=["suspicious", "calculating", "haunted"],
        scene_type="confrontation",
        location_type="station"
    )
    
    print(guidance)
    
    print("\n" + "=" * 60)
    print("QUICK GUIDANCE TEST - DIALOGUE")
    print("=" * 60)
    
    print(engine.generate_quick_guidance("dialogue"))
