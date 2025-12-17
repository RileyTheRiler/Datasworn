"""
Advanced Narrative Systems - Scene-Level Narrative Control

This module provides sophisticated narrative management systems for
controlling the flow, rhythm, and thematic coherence of storytelling.

Key Systems:
1. Tension Arc Manager - Track and shape narrative tension across scenes
2. Dialogue Tag Optimizer - Generate invisible dialogue attribution
3. Scene Transition Crafter - Create compelling scene openings/closings
4. Thematic Echo System - Weave motifs through narrative at key moments
5. Cliffhanger Engine - Create compelling scene breaks
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple
import random
import math


# =============================================================================
# TENSION ARC MANAGER
# =============================================================================

class TensionPhase(Enum):
    """Phases in a tension arc."""
    BASELINE = "baseline"          # Normal operating tension
    RISING = "rising"              # Building toward peak
    PEAK = "peak"                  # Maximum tension
    FALLING = "falling"           # Release after peak
    RESOLUTION = "resolution"      # Return to new baseline
    PLATEAU = "plateau"           # Sustained high tension


@dataclass
class TensionPoint:
    """A recorded tension point in the narrative."""
    scene_number: int
    tension_level: float  # 0.0 - 1.0
    cause: str  # What caused this tension level
    phase: TensionPhase


@dataclass
class TensionArcManager:
    """
    Tracks and shapes narrative tension across scenes.
    
    Ensures proper rise/fall of tension, prevents tension fatigue,
    and suggests when to escalate or release.
    """
    
    tension_history: List[TensionPoint] = field(default_factory=list)
    current_tension: float = 0.3
    current_phase: TensionPhase = TensionPhase.BASELINE
    scenes_at_current_phase: int = 0
    last_peak_scene: int = 0
    current_scene: int = 0
    
    # Pacing rules
    MIN_SCENES_BETWEEN_PEAKS: int = 4
    MAX_SCENES_AT_HIGH_TENSION: int = 3
    TENSION_DECAY_RATE: float = 0.1
    
    # Optimal tension ranges for narrative satisfaction
    PHASE_TARGETS: Dict[TensionPhase, Tuple[float, float]] = field(default_factory=lambda: {
        TensionPhase.BASELINE: (0.2, 0.4),
        TensionPhase.RISING: (0.4, 0.7),
        TensionPhase.PEAK: (0.8, 1.0),
        TensionPhase.FALLING: (0.5, 0.7),
        TensionPhase.RESOLUTION: (0.1, 0.3),
        TensionPhase.PLATEAU: (0.6, 0.8)
    })
    
    def record_tension(self, tension: float, cause: str = ""):
        """Record current scene's tension level."""
        point = TensionPoint(
            scene_number=self.current_scene,
            tension_level=tension,
            cause=cause,
            phase=self.current_phase
        )
        self.tension_history.append(point)
        self.current_tension = tension
        
        # Auto-detect phase transitions
        self._update_phase(tension)
        self.current_scene += 1
    
    def _update_phase(self, tension: float):
        """Update tension phase based on current level."""
        old_phase = self.current_phase
        
        if tension >= 0.8:
            self.current_phase = TensionPhase.PEAK
            self.last_peak_scene = self.current_scene
        elif tension >= 0.6 and self.current_tension < tension:
            self.current_phase = TensionPhase.RISING
        elif tension >= 0.6 and self.current_tension >= tension:
            self.current_phase = TensionPhase.PLATEAU
        elif tension <= 0.3 and len(self.tension_history) > 0:
            if self.tension_history[-1].tension_level > 0.5:
                self.current_phase = TensionPhase.RESOLUTION
            else:
                self.current_phase = TensionPhase.BASELINE
        elif self.current_tension > tension:
            self.current_phase = TensionPhase.FALLING
        
        if old_phase == self.current_phase:
            self.scenes_at_current_phase += 1
        else:
            self.scenes_at_current_phase = 1
    
    def get_pacing_guidance(self) -> str:
        """Generate pacing guidance based on tension arc analysis."""
        guidance_parts = []
        
        # Check for tension fatigue
        if self.current_phase in [TensionPhase.PEAK, TensionPhase.PLATEAU]:
            if self.scenes_at_current_phase >= self.MAX_SCENES_AT_HIGH_TENSION:
                guidance_parts.append(
                    f"⚠️ TENSION FATIGUE: {self.scenes_at_current_phase} scenes at high tension. "
                    "Provide release! A moment of dark humor, a quiet beat, a false resolution."
                )
        
        # Check for premature peak
        scenes_since_last_peak = self.current_scene - self.last_peak_scene
        if scenes_since_last_peak < self.MIN_SCENES_BETWEEN_PEAKS and self.current_tension > 0.7:
            guidance_parts.append(
                f"⚠️ PREMATURE PEAK: Only {scenes_since_last_peak} scenes since last peak. "
                "Build slower—let tension simmer before boiling."
            )
        
        # Phase-specific guidance
        phase_guidance = {
            TensionPhase.BASELINE: [
                "Plant seeds for future tension",
                "Establish stakes through character moments",
                "Let readers breathe while foreshadowing"
            ],
            TensionPhase.RISING: [
                "Introduce complications, not resolutions",
                "Each obstacle should feel surmountable but costly",
                "Tighten the screws incrementally"
            ],
            TensionPhase.PEAK: [
                "This is the crisis—force impossible choices",
                "Time should feel compressed, urgent",
                "Maximum stakes, minimum escape routes"
            ],
            TensionPhase.FALLING: [
                "Show consequences of the peak",
                "Allow processing time for characters (and readers)",
                "This is NOT resolution—threads still dangle"
            ],
            TensionPhase.RESOLUTION: [
                "Reward the emotional investment",
                "Change should be visible in characters",
                "Plant seeds for next arc while closing this one"
            ],
            TensionPhase.PLATEAU: [
                "Sustained tension needs variety in type, not level",
                "Shift between action tension and emotional tension",
                "Find micro-releases within the sustained pressure"
            ]
        }
        
        phase_tips = phase_guidance.get(self.current_phase, [])
        if phase_tips:
            guidance_parts.append(f"PHASE [{self.current_phase.value.upper()}]: {random.choice(phase_tips)}")
        
        # Suggest next phase transition
        target_range = self.PHASE_TARGETS.get(self.current_phase, (0.3, 0.6))
        if self.current_tension < target_range[0]:
            guidance_parts.append("↑ Consider escalating—tension is low for this phase")
        elif self.current_tension > target_range[1]:
            guidance_parts.append("↓ Consider releasing—tension is high for this phase")
        
        if not guidance_parts:
            return ""
        
        return f"""<tension_arc>
TENSION: {self.current_tension:.1f}/1.0 | PHASE: {self.current_phase.value}
Scenes at phase: {self.scenes_at_current_phase} | Since last peak: {self.current_scene - self.last_peak_scene}

{chr(10).join(guidance_parts)}
</tension_arc>"""
    
    def get_visual_arc(self, last_n: int = 10) -> str:
        """Generate ASCII visualization of recent tension arc."""
        if not self.tension_history:
            return ""
        
        recent = self.tension_history[-last_n:]
        max_height = 5
        
        lines = []
        for row in range(max_height, 0, -1):
            threshold = row / max_height
            line = ""
            for point in recent:
                if point.tension_level >= threshold:
                    line += "█"
                else:
                    line += "░"
            lines.append(f"{threshold:.1f}|{line}")
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "tension_history": [
                {"scene": p.scene_number, "level": p.tension_level, 
                 "cause": p.cause, "phase": p.phase.value}
                for p in self.tension_history[-20:]  # Keep last 20
            ],
            "current_tension": self.current_tension,
            "current_phase": self.current_phase.value,
            "scenes_at_current_phase": self.scenes_at_current_phase,
            "last_peak_scene": self.last_peak_scene,
            "current_scene": self.current_scene
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "TensionArcManager":
        manager = cls()
        manager.current_tension = data.get("current_tension", 0.3)
        manager.current_phase = TensionPhase(data.get("current_phase", "baseline"))
        manager.scenes_at_current_phase = data.get("scenes_at_current_phase", 0)
        manager.last_peak_scene = data.get("last_peak_scene", 0)
        manager.current_scene = data.get("current_scene", 0)
        
        for p in data.get("tension_history", []):
            manager.tension_history.append(TensionPoint(
                scene_number=p["scene"],
                tension_level=p["level"],
                cause=p.get("cause", ""),
                phase=TensionPhase(p["phase"])
            ))
        return manager


# =============================================================================
# DIALOGUE TAG OPTIMIZER
# =============================================================================

class DialogueTagStyle(Enum):
    """Styles for dialogue attribution."""
    INVISIBLE = "invisible"      # "said" - disappears in reading
    ACTION_BEAT = "action_beat"  # Action replaces tag entirely
    DESCRIPTIVE = "descriptive"  # "whispered", "snarled" - for emphasis
    NONE = "none"               # No tag needed (clear speaker)


@dataclass
class DialogueTagOptimizer:
    """
    Generates optimal dialogue attribution strategies.
    
    Minimizes intrusive tags while maintaining clarity.
    Uses action beats and invisible tags strategically.
    """
    
    # Tags that "disappear" during reading
    INVISIBLE_TAGS: List[str] = field(default_factory=lambda: [
        "said", "asked", "replied", "answered"
    ])
    
    # Descriptive tags for specific emotional contexts
    DESCRIPTIVE_TAGS: Dict[str, List[str]] = field(default_factory=lambda: {
        "anger": ["snapped", "snarled", "spat", "bit out", "growled"],
        "fear": ["whispered", "stammered", "breathed", "managed"],
        "joy": ["laughed", "chirped", "beamed", "exclaimed"],
        "sadness": ["murmured", "sighed", "choked out", "managed"],
        "suspicion": ["muttered", "observed", "noted", "pointed out"],
        "urgency": ["barked", "shouted", "called", "warned"],
        "calm": ["said quietly", "observed", "remarked", "noted"]
    })
    
    # Action beats that replace tags entirely
    ACTION_BEAT_TEMPLATES: Dict[str, List[str]] = field(default_factory=lambda: {
        "nervous": [
            "{name} picked at the seam of their sleeve.",
            "{name}'s eyes darted to the exit.",
            "A muscle jumped in {name}'s jaw."
        ],
        "confident": [
            "{name} leaned back, arms crossed.",
            "{name} held their gaze without blinking.",
            "{name} smiled without warmth."
        ],
        "thinking": [
            "{name} was quiet for a long moment.",
            "{name} turned to look out the viewport.",
            "{name}'s fingers drummed against the console."
        ],
        "emotional": [
            "{name} looked away.",
            "{name}'s hands tightened into fists.",
            "Something shifted in {name}'s expression."
        ],
        "dismissive": [
            "{name} waved a hand.",
            "{name} didn't look up.",
            "{name} continued working."
        ]
    })
    
    def get_attribution_strategy(
        self, 
        speaker: str,
        emotional_context: str = "neutral",
        previous_speaker: Optional[str] = None,
        lines_since_last_tag: int = 0
    ) -> Tuple[DialogueTagStyle, str]:
        """Determine optimal attribution strategy."""
        
        # Rule 1: If same speaker continues, often no tag needed
        if previous_speaker == speaker and lines_since_last_tag < 3:
            return DialogueTagStyle.NONE, ""
        
        # Rule 2: Two-person conversation with clear back-and-forth
        if lines_since_last_tag == 1 and previous_speaker is not None:
            # Maybe no tag, maybe a brief action beat
            if random.random() < 0.5:
                return DialogueTagStyle.NONE, ""
            else:
                return DialogueTagStyle.ACTION_BEAT, self._get_action_beat(speaker, emotional_context)
        
        # Rule 3: Strong emotion warrants descriptive tag
        if emotional_context in self.DESCRIPTIVE_TAGS:
            if random.random() < 0.3:  # Don't overuse
                tag = random.choice(self.DESCRIPTIVE_TAGS[emotional_context])
                return DialogueTagStyle.DESCRIPTIVE, f'{speaker} {tag}'
        
        # Rule 4: Default to action beat or invisible tag
        if random.random() < 0.6:
            return DialogueTagStyle.ACTION_BEAT, self._get_action_beat(speaker, emotional_context)
        else:
            return DialogueTagStyle.INVISIBLE, f'{speaker} said'
    
    def _get_action_beat(self, speaker: str, context: str) -> str:
        """Generate an action beat for the speaker."""
        context_map = {
            "anger": "confident",
            "fear": "nervous",
            "neutral": "thinking",
            "suspicion": "thinking",
            "sadness": "emotional",
            "calm": "dismissive"
        }
        
        beat_context = context_map.get(context, "thinking")
        templates = self.ACTION_BEAT_TEMPLATES.get(beat_context, self.ACTION_BEAT_TEMPLATES["thinking"])
        
        return random.choice(templates).format(name=speaker)
    
    def get_narrator_guidance(self) -> str:
        """Generate dialogue tagging guidance for narrator."""
        return """<dialogue_tags>
DIALOGUE ATTRIBUTION STRATEGY:

HIERARCHY OF PREFERENCE:
1. NO TAG — When speaker is obvious from context/alternation
2. ACTION BEAT — "She turned away. 'I can't do this.'" (Best of both worlds)
3. INVISIBLE TAG — "said/asked" — disappears during reading
4. DESCRIPTIVE TAG — "snarled/whispered" — ONLY when HOW matters deeply

RHYTHM RULE:
In rapid back-and-forth, drop most tags. Reader tracks the volleys.
Every 4-5 lines, a brief action beat grounds us without slowing pace.

EXAMPLE:
  BAD:  "I didn't do it," he said defensively. "You always accuse me," he said angrily.
  GOOD: "I didn't do it." He spread his hands. "You always—" A breath. "You always accuse me."

ACTION BEATS vs TAGS:
Action beats > Tags when you want to:
  - Show character state through physicality
  - Create a beat/pause in the dialogue
  - Reveal what character WON'T say directly
</dialogue_tags>"""


# =============================================================================
# SCENE TRANSITION CRAFTER
# =============================================================================

class TransitionType(Enum):
    """Types of scene transitions."""
    CUT = "cut"                    # Hard cut to new scene
    DISSOLVE = "dissolve"          # Smooth time/location transition
    MATCH_CUT = "match_cut"        # Visual/thematic link between scenes
    SMASH_CUT = "smash_cut"        # Jarring tonal shift
    FADE_OUT = "fade_out"          # Gradual end scene
    COLD_OPEN = "cold_open"        # Jump into action
    HOOK = "hook"                  # End on question/cliffhanger


@dataclass
class SceneTransitionCrafter:
    """
    Generates compelling scene openings and closings.
    
    Ensures scenes start with momentum and end with hooks.
    Provides templates for various transition types.
    """
    
    # Scene opening strategies
    OPENING_STRATEGIES: Dict[str, List[str]] = field(default_factory=lambda: {
        "action": [
            "Start mid-action. The reader catches up.",
            "First line should be MOVEMENT or IMPACT.",
            "Enter the scene as late as possible—skip the walking-through-door."
        ],
        "mystery": [
            "Open with a question (explicit or implied).",
            "Show something wrong before explaining what.",
            "Start with observation that doesn't quite add up."
        ],
        "character": [
            "First line reveals character through specific choice or observation.",
            "Open on character DOING something characteristic.",
            "Begin with a telling detail about their current state."
        ],
        "atmosphere": [
            "Establish location through ONE dominant sensory detail.",
            "Let the environment suggest the emotional landscape.",
            "Open on what makes THIS moment different from ordinary."
        ],
        "dialogue": [
            "Start mid-conversation. Context emerges from content.",
            "First line should be provocative/intriguing.",
            "Open on response, not the question that prompted it."
        ]
    })
    
    # Scene closing strategies
    CLOSING_STRATEGIES: Dict[str, List[str]] = field(default_factory=lambda: {
        "hook": [
            "End on a revelation that recontextualizes everything.",
            "Last line should raise a question.",
            "Close on a choice the character must make—but don't show the choice."
        ],
        "resonance": [
            "Echo an earlier moment with new meaning.",
            "End on image that encapsulates the scene's emotional truth.",
            "Close on sensory detail that lingers."
        ],
        "momentum": [
            "End on motion toward the next thing.",
            "Last line should be GOING somewhere (physically or emotionally).",
            "Close on decision, not completion."
        ],
        "quiet": [
            "End on small human moment after intensity.",
            "Close on what's NOT said.",
            "Let silence be the final beat."
        ],
        "ominous": [
            "End on detail that's wrong but unexplained.",
            "Close on character not seeing what reader sees.",
            "Last line should feel like a held breath."
        ]
    })
    
    # Match cut suggestions
    MATCH_CUT_EXAMPLES: List[Tuple[str, str]] = field(default_factory=lambda: [
        ("Close-up on eyes opening", "Opening on viewport/screen coming online"),
        ("Fist slamming table", "Ship docking with a thud"),
        ("Flame dying", "Sun setting through window"),
        ("Door closing", "Airlock cycling"),
        ("Heart monitor beeping", "Radar ping"),
        ("Tears falling", "Rain on window")
    ])
    
    def get_opening_guidance(self, scene_type: str = "action", 
                             previous_scene_end: str = "") -> str:
        """Generate scene opening guidance."""
        strategies = self.OPENING_STRATEGIES.get(scene_type, self.OPENING_STRATEGIES["action"])
        
        opening_strats = "\n".join([f"  - {s}" for s in strategies])
        
        match_cut = ""
        if previous_scene_end:
            match_cut = f"""
POTENTIAL MATCH CUT from previous scene ending: "{previous_scene_end[:50]}..."
Consider visual/thematic echoes that link scenes."""
        
        return f"""<scene_opening>
SCENE START GUIDANCE ({scene_type.upper()}):

{opening_strats}
{match_cut}

IN MEDIAS RES PRINCIPLE:
"Enter late, leave early." Skip setup. Trust readers.
First sentence should make them NEED the second sentence.

AVOID:
  - Weather openings (unless weather IS the story)
  - Character waking up (unless nightmare is plot-relevant)
  - Describing the room before something happens in it
  - Lengthy establishing before the point
</scene_opening>"""
    
    def get_closing_guidance(self, desired_effect: str = "hook",
                             next_scene_tension: float = 0.5) -> str:
        """Generate scene closing guidance."""
        strategies = self.CLOSING_STRATEGIES.get(desired_effect, self.CLOSING_STRATEGIES["hook"])
        
        closing_strats = "\n".join([f"  - {s}" for s in strategies])
        
        # Match cut suggestions
        match_example = random.choice(self.MATCH_CUT_EXAMPLES)
        
        return f"""<scene_closing>
SCENE END GUIDANCE ({desired_effect.upper()}):

{closing_strats}

MATCH CUT TECHNIQUE:
  Scene A ends: "{match_example[0]}"
  Scene B opens: "{match_example[1]}"
(Visual rhyme creates subconscious connection)

LAST LINE TEST:
Read your final line alone. Does it:
  ✓ Create questions, not answers?
  ✓ Have rhythm that feels like an ending?
  ✓ Carry emotional weight beyond its literal meaning?

NEXT SCENE TENSION: {next_scene_tension:.1f}
{"Build to cliffhanger—next scene is high intensity" if next_scene_tension > 0.6 else "Allow softer landing—next scene needs room to build"}
</scene_closing>"""
    
    def get_narrator_guidance(self, scene_position: str = "middle") -> str:
        """Generate comprehensive transition guidance."""
        if scene_position == "opening":
            return self.get_opening_guidance()
        elif scene_position == "closing":
            return self.get_closing_guidance()
        else:
            return ""


# =============================================================================
# THEMATIC ECHO SYSTEM
# =============================================================================

@dataclass
class ThematicElement:
    """A tracked thematic element for echoing."""
    name: str
    description: str
    first_appearance: int  # Scene number
    appearances: List[int] = field(default_factory=list)
    emotional_contexts: List[str] = field(default_factory=list)
    transformation_arc: str = ""  # How meaning changes


@dataclass
class ThematicEchoSystem:
    """
    Tracks and weaves motifs through narrative at key moments.
    
    Manages recurring images, phrases, and themes for
    resonance and payoff.
    """
    
    themes: Dict[str, ThematicElement] = field(default_factory=dict)
    current_scene: int = 0
    pending_echoes: List[str] = field(default_factory=list)  # Themes due for echo
    
    # Template motifs by category
    MOTIF_CATEGORIES: Dict[str, List[Dict[str, str]]] = field(default_factory=lambda: {
        "visual": [
            {"name": "light_dark", "desc": "Contrast between light and darkness"},
            {"name": "reflection", "desc": "Mirrors, windows, reflective surfaces"},
            {"name": "threshold", "desc": "Doors, airlocks, points of no return"},
            {"name": "falling", "desc": "Descent, gravity, loss of control"}
        ],
        "object": [
            {"name": "inherited_item", "desc": "Object passed between characters"},
            {"name": "broken_thing", "desc": "Something damaged that reflects character state"},
            {"name": "photograph", "desc": "Image of the past/lost people"},
            {"name": "tool_of_trade", "desc": "Item that defines character's identity"}
        ],
        "phrase": [
            {"name": "repeated_words", "desc": "Specific phrase echoed by different characters"},
            {"name": "promise", "desc": "A vow made early that must be kept/broken"},
            {"name": "lie", "desc": "Untruth that gains weight through repetition"},
            {"name": "question", "desc": "Question asked early, answered late"}
        ],
        "sensory": [
            {"name": "signature_smell", "desc": "Scent associated with memory/person"},
            {"name": "recurring_sound", "desc": "Sound that triggers association"},
            {"name": "texture", "desc": "Tactile sensation linked to emotion"}
        ]
    })
    
    def register_theme(self, name: str, description: str, 
                       transformation: str = "") -> ThematicElement:
        """Register a new thematic element to track."""
        theme = ThematicElement(
            name=name,
            description=description,
            first_appearance=self.current_scene,
            appearances=[self.current_scene],
            transformation_arc=transformation
        )
        self.themes[name] = theme
        return theme
    
    def record_echo(self, theme_name: str, emotional_context: str = ""):
        """Record an appearance of a theme."""
        if theme_name in self.themes:
            theme = self.themes[theme_name]
            theme.appearances.append(self.current_scene)
            if emotional_context:
                theme.emotional_contexts.append(emotional_context)
    
    def get_echo_suggestions(self, emotional_intensity: float = 0.5,
                              is_climactic: bool = False) -> str:
        """Suggest themes that could be echoed in current scene."""
        if not self.themes:
            return ""
        
        suggestions = []
        
        for name, theme in self.themes.items():
            scenes_since = self.current_scene - theme.appearances[-1]
            
            # Themes are ripe for echo after some distance
            if scenes_since >= 3 or is_climactic:
                suggestions.append({
                    "name": name,
                    "desc": theme.description,
                    "distance": scenes_since,
                    "times_used": len(theme.appearances),
                    "transformation": theme.transformation_arc
                })
        
        if not suggestions:
            # Suggest new motifs to establish
            category = random.choice(list(self.MOTIF_CATEGORIES.keys()))
            motif = random.choice(self.MOTIF_CATEGORIES[category])
            return f"""<thematic_opportunity>
No established motifs ready for echo. Consider PLANTING:
  Category: {category}
  Motif: "{motif['name']}" - {motif['desc']}
  
Introduce this element naturally now. It will resonate when echoed later.
</thematic_opportunity>"""
        
        # Sort by ripeness for echo
        suggestions.sort(key=lambda x: x["distance"], reverse=True)
        
        echo_text = []
        for s in suggestions[:3]:
            transform = f" | Arc: {s['transformation']}" if s['transformation'] else ""
            echo_text.append(f"  - {s['name']}: {s['desc']} (unused for {s['distance']} scenes){transform}")
        
        climactic_note = ""
        if is_climactic:
            climactic_note = """
⭐ CLIMACTIC MOMENT: Maximum resonance opportunity.
   Echo established motifs for emotional payoff.
   Invert or transform their meaning for devastating effect."""
        
        return f"""<thematic_echoes>
MOTIFS READY FOR CALLBACK:
{chr(10).join(echo_text)}
{climactic_note}

ECHO TECHNIQUE:
First appearance: Establish the motif naturally
Middle appearances: Reinforce, add associations
Climax: Transform or invert for maximum impact

EXAMPLE ARC:
  Scene 3: "She always checked her reflection before a job."
  Scene 8: "The broken mirror showed her in fragments."
  Scene 15: "She passed the mirror without looking. She knew who she was now."
</thematic_echoes>"""
    
    def advance_scene(self):
        """Move to next scene."""
        self.current_scene += 1
    
    def to_dict(self) -> dict:
        return {
            "themes": {
                name: {
                    "name": t.name,
                    "description": t.description,
                    "first_appearance": t.first_appearance,
                    "appearances": t.appearances,
                    "emotional_contexts": t.emotional_contexts,
                    "transformation_arc": t.transformation_arc
                } for name, t in self.themes.items()
            },
            "current_scene": self.current_scene
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ThematicEchoSystem":
        system = cls()
        system.current_scene = data.get("current_scene", 0)
        
        for name, t in data.get("themes", {}).items():
            system.themes[name] = ThematicElement(
                name=t["name"],
                description=t["description"],
                first_appearance=t["first_appearance"],
                appearances=t.get("appearances", []),
                emotional_contexts=t.get("emotional_contexts", []),
                transformation_arc=t.get("transformation_arc", "")
            )
        return system


# =============================================================================
# CLIFFHANGER ENGINE
# =============================================================================

class CliffhangerType(Enum):
    """Types of cliffhangers."""
    REVELATION = "revelation"      # Truth changes everything
    DANGER = "danger"              # Immediate threat
    CHOICE = "choice"              # Decision point, outcome unknown
    ARRIVAL = "arrival"            # Someone/something appears
    DEPARTURE = "departure"        # Someone leaves/is taken
    BETRAYAL = "betrayal"          # Trust broken
    MYSTERY = "mystery"            # Question posed, answer withheld


@dataclass
class CliffhangerEngine:
    """
    Creates compelling scene breaks and act endings.
    
    Ensures readers feel compelled to continue.
    """
    
    CLIFFHANGER_TEMPLATES: Dict[CliffhangerType, List[str]] = field(default_factory=lambda: {
        CliffhangerType.REVELATION: [
            "End on character's realization—but not what they realized.",
            "\"Oh,\" {name} said, very quietly. \"Oh no.\"",
            "The truth was written in {detail}. And it changed everything.",
            "They had been looking at this all wrong."
        ],
        CliffhangerType.DANGER: [
            "End on the moment BEFORE impact/attack/disaster.",
            "The sound of {threat} grew closer.",
            "They had thirty seconds. Maybe less.",
            "The {warning} began to flash. The kind that only flashed once."
        ],
        CliffhangerType.CHOICE: [
            "End on the choice presented, not the decision made.",
            "Two doors. One truth. No time.",
            "\"You have until I reach zero,\" {antagonist} said. \"Ten. Nine...\"",
            "It would cost them everything. But it might be worth it."
        ],
        CliffhangerType.ARRIVAL: [
            "End on the door opening—but not what's behind it.",
            "The recognition hit like a physical blow. It was {person/thing}.",
            "Of all the people who could have walked through that door...",
            "\"Hello,\" said the last voice they expected to hear."
        ],
        CliffhangerType.MYSTERY: [
            "End on the question, not the answer.",
            "But if {assumption} was wrong, then what was actually happening?",
            "Three people knew the truth. Two were dead. The third was missing.",
            "The message contained only coordinates. And a time. Tomorrow."
        ]
    })
    
    recent_types: List[CliffhangerType] = field(default_factory=list)
    
    def get_cliffhanger_guidance(self, preferred_type: CliffhangerType = None,
                                   scene_context: str = "") -> str:
        """Generate cliffhanger guidance."""
        # Avoid repeating recent types
        available = [t for t in CliffhangerType if t not in self.recent_types[-2:]]
        if not available:
            available = list(CliffhangerType)
        
        if preferred_type and preferred_type in available:
            chosen = preferred_type
        else:
            chosen = random.choice(available)
        
        templates = self.CLIFFHANGER_TEMPLATES.get(chosen, [])
        examples = "\n".join([f"  - {t}" for t in templates[:3]])
        
        return f"""<cliffhanger_guidance>
CLIFFHANGER TYPE: {chosen.value.upper()}

TEMPLATES:
{examples}

CORE PRINCIPLE: End on the QUESTION, not the ANSWER.
The reader's imagination during the gap is more powerful than your prose.

MICRO-CLIFFHANGERS (for chapter/scene ends):
  - The unfinished sentence
  - The half-opened door  
  - The ringing communicator
  - The look that means something
  - The detail that doesn't fit

TIMING: The cliffhanger IS the ending. Don't explain, don't soften.
Last line should feel like stepping off a cliff.
</cliffhanger_guidance>"""
    
    def record_cliffhanger(self, cliff_type: CliffhangerType):
        """Record used cliffhanger for variety tracking."""
        self.recent_types.append(cliff_type)
        if len(self.recent_types) > 5:
            self.recent_types = self.recent_types[-5:]


# =============================================================================
# MASTER NARRATIVE SYSTEMS ENGINE
# =============================================================================

@dataclass
class NarrativeSystemsEngine:
    """Master engine coordinating all narrative systems."""
    
    tension_manager: TensionArcManager = field(default_factory=TensionArcManager)
    dialogue_optimizer: DialogueTagOptimizer = field(default_factory=DialogueTagOptimizer)
    transition_crafter: SceneTransitionCrafter = field(default_factory=SceneTransitionCrafter)
    thematic_system: ThematicEchoSystem = field(default_factory=ThematicEchoSystem)
    cliffhanger_engine: CliffhangerEngine = field(default_factory=CliffhangerEngine)
    
    def get_comprehensive_guidance(
        self,
        tension_level: float = 0.5,
        scene_position: str = "middle",  # "opening", "middle", "closing"
        is_climactic: bool = False,
        include_themes: bool = True
    ) -> str:
        """Generate comprehensive narrative systems guidance."""
        
        sections = []
        
        # Tension arc
        self.tension_manager.record_tension(tension_level, f"Scene {self.tension_manager.current_scene}")
        tension_guidance = self.tension_manager.get_pacing_guidance()
        if tension_guidance:
            sections.append(tension_guidance)
        
        # Scene transitions
        if scene_position == "opening":
            sections.append(self.transition_crafter.get_opening_guidance())
        elif scene_position == "closing":
            sections.append(self.transition_crafter.get_closing_guidance(
                next_scene_tension=tension_level + 0.1
            ))
            sections.append(self.cliffhanger_engine.get_cliffhanger_guidance())
        
        # Thematic echoes
        if include_themes:
            theme_guidance = self.thematic_system.get_echo_suggestions(
                emotional_intensity=tension_level,
                is_climactic=is_climactic
            )
            if theme_guidance:
                sections.append(theme_guidance)
        
        # Dialogue guidance (always helpful)
        sections.append(self.dialogue_optimizer.get_narrator_guidance())
        
        if not sections:
            return ""
        
        return f"""
<narrative_systems>
=== NARRATIVE STRUCTURE GUIDANCE ===
{chr(10).join(sections)}
</narrative_systems>
"""
    
    def advance_scene(self):
        """Move all systems to next scene."""
        self.thematic_system.advance_scene()
    
    def to_dict(self) -> dict:
        return {
            "tension_manager": self.tension_manager.to_dict(),
            "thematic_system": self.thematic_system.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "NarrativeSystemsEngine":
        engine = cls()
        if "tension_manager" in data:
            engine.tension_manager = TensionArcManager.from_dict(data["tension_manager"])
        if "thematic_system" in data:
            engine.thematic_system = ThematicEchoSystem.from_dict(data["thematic_system"])
        return engine


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("NARRATIVE SYSTEMS ENGINE - TEST")
    print("=" * 60)
    
    engine = NarrativeSystemsEngine()
    
    # Simulate a few scenes
    tensions = [0.3, 0.4, 0.5, 0.7, 0.85, 0.9, 0.6, 0.4, 0.3]
    
    for i, t in enumerate(tensions):
        print(f"\n--- Scene {i+1} (tension: {t}) ---")
        position = "opening" if i == 0 else ("closing" if i == len(tensions)-1 else "middle")
        is_climax = t >= 0.85
        
        guidance = engine.get_comprehensive_guidance(
            tension_level=t,
            scene_position=position,
            is_climactic=is_climax
        )
        print(guidance[:1500] + "..." if len(guidance) > 1500 else guidance)
        engine.advance_scene()
    
    print("\n--- TENSION ARC VISUALIZATION ---")
    print(engine.tension_manager.get_visual_arc())
