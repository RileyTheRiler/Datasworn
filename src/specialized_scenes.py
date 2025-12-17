"""
Specialized Scene Systems - Scene-Type Specific Narration Enhancement

This module provides specialized narration systems for specific scene types,
ensuring each type of scene gets the focused guidance it needs.

Key Systems:
1. Combat Narration System - Cinematic action sequences
2. Investigation Scene System - Mystery and discovery
3. Social Encounter System - Dialogue and intrigue
4. Exploration Scene System - Discovery and atmosphere
5. Horror/Tension System - Dread and suspense
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple
import random


# =============================================================================
# COMBAT NARRATION SYSTEM
# =============================================================================

class CombatBeatType(Enum):
    """Types of combat narrative beats."""
    OPENING_SALVO = "opening"       # Combat initiation
    EXCHANGE = "exchange"           # Back and forth
    MOMENTUM_SHIFT = "shift"        # Advantage changes
    DESPERATION = "desperation"     # Backs against wall
    TURNING_POINT = "turning"       # Key moment
    CLIMAX = "climax"               # Decisive action
    AFTERMATH = "aftermath"         # Dust settling


class CombatScale(Enum):
    """Scale of combat encounter."""
    DUEL = "duel"                   # 1v1
    SKIRMISH = "skirmish"           # Small group
    BATTLE = "battle"               # Large engagement
    CHASE = "chase"                 # Pursuit
    ESCAPE = "escape"               # Getting away


@dataclass
class CombatNarrationSystem:
    """
    Provides cinematic combat narration guidance.
    
    Ensures fights are dynamic, readable, and emotionally engaging
    rather than mechanical dice-roll descriptions.
    """
    
    current_beat: CombatBeatType = CombatBeatType.OPENING_SALVO
    rounds_elapsed: int = 0
    momentum: float = 0.5  # 0.0 = enemies winning, 1.0 = players winning
    
    # Narration techniques by beat
    BEAT_TECHNIQUES: Dict[CombatBeatType, List[str]] = field(default_factory=lambda: {
        CombatBeatType.OPENING_SALVO: [
            "Establish spatial awareness—where is everyone?",
            "First move sets the tone (ambush feels different from standoff)",
            "Show the enemy's fighting style immediately",
            "Describe the moment of transition from peace to violence"
        ],
        CombatBeatType.EXCHANGE: [
            "Vary the rhythm—not every exchange is equal",
            "Show the cost of attacks (effort, position, resources)",
            "Use environment—cover, obstacles, hazards",
            "Include near-misses and close calls for tension"
        ],
        CombatBeatType.MOMENTUM_SHIFT: [
            "Something changes—injury, new enemy, trap sprung",
            "Character reactions to the shift",
            "Tactical reassessment mid-fight",
            "The feel of the fight transforms"
        ],
        CombatBeatType.DESPERATION: [
            "Resources running low, options narrowing",
            "Risky moves become necessary",
            "Time pressure intensifies",
            "Show fear/determination in equal measure"
        ],
        CombatBeatType.TURNING_POINT: [
            "The moment everything depends on",
            "Slow time for critical actions",
            "Show the choice being made",
            "Consequences visible immediately"
        ],
        CombatBeatType.CLIMAX: [
            "Maximum intensity, minimum words",
            "Decisive action, clear outcome",
            "Emotional release through violence",
            "The end should feel earned"
        ],
        CombatBeatType.AFTERMATH: [
            "Bodies, damage, silence",
            "Character processing what happened",
            "Cost of victory/defeat visible",
            "Transition back to non-combat state"
        ]
    })
    
    # Action verbs by combat type
    ACTION_VOCABULARY: Dict[str, List[str]] = field(default_factory=lambda: {
        "melee": ["slashed", "drove", "swept", "caught", "deflected", "locked", "disengaged", "pressed"],
        "ranged": ["tracked", "squeezed", "snapped", "bracketed", "suppressed", "adjusted", "steadied"],
        "unarmed": ["drove", "trapped", "wrenched", "slipped", "countered", "closed", "created distance"],
        "tactical": ["flanked", "covered", "repositioned", "pinned", "advanced", "withdrew", "coordinated"]
    })
    
    def advance_beat(self):
        """Progress to next combat beat based on rounds."""
        self.rounds_elapsed += 1
        
        if self.rounds_elapsed <= 1:
            self.current_beat = CombatBeatType.OPENING_SALVO
        elif self.rounds_elapsed <= 3:
            self.current_beat = CombatBeatType.EXCHANGE
        elif self.momentum < 0.3 or self.momentum > 0.7:
            self.current_beat = CombatBeatType.MOMENTUM_SHIFT
        elif self.rounds_elapsed >= 5:
            self.current_beat = CombatBeatType.TURNING_POINT
    
    def get_combat_guidance(self, scale: CombatScale = CombatScale.SKIRMISH,
                             player_health: float = 1.0,
                             enemy_count: int = 1) -> str:
        """Generate combat narration guidance."""
        
        techniques = self.BEAT_TECHNIQUES.get(self.current_beat, [])
        technique_text = "\n".join([f"  - {t}" for t in techniques[:3]])
        
        vocab_category = random.choice(list(self.ACTION_VOCABULARY.keys()))
        verbs = self.ACTION_VOCABULARY[vocab_category]
        
        desperation_note = ""
        if player_health < 0.3:
            desperation_note = "\n⚠️ LOW HEALTH: Show the cost, the struggle, the desperation."
        
        return f"""<combat_narration>
COMBAT BEAT: {self.current_beat.value.upper()} | Round: {self.rounds_elapsed}
Scale: {scale.value} | Enemies: {enemy_count} | Momentum: {"Player" if self.momentum > 0.5 else "Enemy"} advantage
{desperation_note}

TECHNIQUES FOR THIS BEAT:
{technique_text}

ACTION VOCABULARY ({vocab_category}):
  {', '.join(random.sample(verbs, min(5, len(verbs))))}

CINEMATIC PRINCIPLES:
  - Geography: Where is everyone? What's between them?
  - Economy: Each action costs something (position, ammo, energy)
  - Consequence: Hits should HURT. Near-misses should terrify.
  - Rhythm: Short sentences = fast action. Longer = tactical pause.

AVOID:
  - "He swings. He hits. He does 5 damage." (Mechanical, not narrative)
  - Perfect accuracy (misses create tension)
  - Painless combat (violence should have weight)
  - Forgetting the environment (use it!)
</combat_narration>"""
    
    def to_dict(self) -> dict:
        return {
            "current_beat": self.current_beat.value,
            "rounds_elapsed": self.rounds_elapsed,
            "momentum": self.momentum
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CombatNarrationSystem":
        system = cls()
        system.current_beat = CombatBeatType(data.get("current_beat", "opening"))
        system.rounds_elapsed = data.get("rounds_elapsed", 0)
        system.momentum = data.get("momentum", 0.5)
        return system


# =============================================================================
# INVESTIGATION SCENE SYSTEM
# =============================================================================

class ClueType(Enum):
    """Types of clues in investigation."""
    PHYSICAL = "physical"          # Objects, traces, evidence
    TESTIMONIAL = "testimonial"    # What people say
    DOCUMENTARY = "documentary"    # Records, logs, messages
    ENVIRONMENTAL = "environmental" # Scene tells a story
    BEHAVIORAL = "behavioral"      # How someone acts
    ABSENCE = "absence"            # What's missing


@dataclass
class InvestigationSystem:
    """
    Provides guidance for mystery and investigation scenes.
    
    Ensures clues are fair, discoveries feel earned,
    and the investigation maintains momentum.
    """
    
    clues_found: List[Dict[str, str]] = field(default_factory=list)
    red_herrings_planted: int = 0
    truth_proximity: float = 0.0  # How close to the answer (0.0-1.0)
    
    # Clue presentation techniques
    CLUE_TECHNIQUES: Dict[ClueType, List[str]] = field(default_factory=lambda: {
        ClueType.PHYSICAL: [
            "Describe before revealing significance",
            "Multiple interpretations possible",
            "Condition tells a story (fresh, old, hidden)",
            "What does it prove? What questions does it raise?"
        ],
        ClueType.TESTIMONIAL: [
            "How do they tell it? (nervous, rehearsed, angry)",
            "What do they NOT mention?",
            "Contradictions with other testimony",
            "Their motive for revealing/concealing"
        ],
        ClueType.ENVIRONMENTAL: [
            "Let the scene tell the story without narration",
            "Sequence of events readable from evidence",
            "Something doesn't match the official story",
            "The space itself as witness"
        ],
        ClueType.ABSENCE: [
            "What SHOULD be here but isn't?",
            "The gap in the record",
            "The person who wasn't where they should be",
            "The missing piece that rearranges the puzzle"
        ]
    })
    
    # Investigation momentum guidance
    PACING_GUIDANCE: Dict[str, str] = field(default_factory=lambda: {
        "stuck": "Introduce new information: witness appears, document discovered, pattern noticed",
        "overwhelmed": "Focus on most promising thread, let others wait",
        "false_trail": "Let them follow it—the wrongness should become apparent naturally",
        "breakthrough": "Don't rush—let the realization breathe, show connections clicking"
    })
    
    def record_clue(self, clue_type: ClueType, description: str, 
                    significance: str, is_red_herring: bool = False):
        """Record a clue that was found."""
        self.clues_found.append({
            "type": clue_type.value,
            "description": description,
            "significance": significance,
            "red_herring": is_red_herring
        })
        if is_red_herring:
            self.red_herrings_planted += 1
        else:
            self.truth_proximity = min(1.0, self.truth_proximity + 0.15)
    
    def get_investigation_guidance(self, scene_focus: str = "general") -> str:
        """Generate investigation narration guidance."""
        
        # Select a clue type to focus on
        clue_type = random.choice(list(ClueType))
        techniques = self.CLUE_TECHNIQUES.get(clue_type, [])
        
        clue_text = "\n".join([f"  - {t}" for t in techniques[:3]])
        
        # Progress indicator
        progress_note = ""
        if self.truth_proximity < 0.3:
            progress_note = "EARLY INVESTIGATION: Establish the mystery, plant the questions"
        elif self.truth_proximity < 0.7:
            progress_note = "MID-INVESTIGATION: Connections forming, complications arising"
        else:
            progress_note = "APPROACHING TRUTH: Pieces falling together, tension building"
        
        return f"""<investigation_guidance>
{progress_note}
Clues found: {len(self.clues_found)} | Red herrings: {self.red_herrings_planted}

CLUE PRESENTATION ({clue_type.value}):
{clue_text}

THE THREE-CLUE RULE:
For any critical conclusion, plant AT LEAST three clues pointing to it.
Players will miss one, ignore one, and hopefully find one.

FAIR PLAY PRINCIPLES:
  - All clues available to player before solution
  - False solutions should be possible but less satisfying
  - The truth should recontextualize earlier clues
  - "I should have seen it!" is the goal reaction

PACING:
  - Dead ends should reveal character, not just frustrate
  - Each scene should change what they know OR what they think they know
  - Complications > roadblocks (add problems, don't remove options)

AVOID:
  - Obvious clues that insult intelligence
  - Withholding information arbitrarily
  - Solutions that require knowledge player couldn't have
</investigation_guidance>"""
    
    def to_dict(self) -> dict:
        return {
            "clues_found": self.clues_found,
            "red_herrings_planted": self.red_herrings_planted,
            "truth_proximity": self.truth_proximity
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "InvestigationSystem":
        system = cls()
        system.clues_found = data.get("clues_found", [])
        system.red_herrings_planted = data.get("red_herrings_planted", 0)
        system.truth_proximity = data.get("truth_proximity", 0.0)
        return system


# =============================================================================
# SOCIAL ENCOUNTER SYSTEM
# =============================================================================

class SocialStakes(Enum):
    """What's at stake in social encounter."""
    INFORMATION = "information"     # Learning something
    PERSUASION = "persuasion"       # Changing a mind
    NEGOTIATION = "negotiation"     # Making a deal
    DECEPTION = "deception"         # Hiding truth
    INTIMIDATION = "intimidation"   # Using fear
    SEDUCTION = "seduction"         # Using attraction
    MANIPULATION = "manipulation"   # Subtle control


@dataclass
class SocialEncounterSystem:
    """
    Provides guidance for dialogue-heavy social scenes.
    
    Ensures conversations have stakes, subtext,
    and character-revealing choices.
    """
    
    rapport_level: float = 0.5  # -1.0 hostile to 1.0 allied
    information_revealed: List[str] = field(default_factory=list)
    lies_told: List[str] = field(default_factory=list)
    
    # Conversation dynamics
    DYNAMIC_TECHNIQUES: Dict[str, List[str]] = field(default_factory=lambda: {
        "status_play": [
            "Who has power? Watch it shift mid-conversation.",
            "High status: less words, more silence, others adjust to them",
            "Low status: more words, seeking approval, adapting",
            "Status attacks: interruption, dismissal, name-using"
        ],
        "information_trading": [
            "Information has value—don't give it away free",
            "Each party has something the other wants",
            "Partial truths are more believable than whole ones",
            "What they ask reveals what they don't know"
        ],
        "emotional_undercurrent": [
            "The conversation on top, the feelings underneath",
            "What can't they say directly?",
            "Body language contradicting words",
            "The thing they're circling around but not naming"
        ],
        "tactical_dialogue": [
            "Every line is a move in a game",
            "Probing for weakness, testing boundaries",
            "The real negotiation happens between the lines",
            "Silence is a weapon"
        ]
    })
    
    # NPC reaction patterns
    NPC_BEHAVIORS: Dict[str, str] = field(default_factory=lambda: {
        "guarded": "Answers questions with questions. Reveals nothing for free.",
        "cooperative": "Helpful but has limits. What are they holding back?",
        "hostile": "Everything is a challenge. But hostility often masks fear.",
        "deceptive": "Plausible lies, consistent story. But watch for details.",
        "nervous": "Talks too much. Contradicts self. Wants this conversation over.",
        "calculating": "Every word measured. Playing a longer game."
    })
    
    def get_social_guidance(self, stakes: SocialStakes = SocialStakes.INFORMATION,
                             npc_disposition: str = "guarded") -> str:
        """Generate social encounter guidance."""
        
        dynamic = random.choice(list(self.DYNAMIC_TECHNIQUES.keys()))
        techniques = self.DYNAMIC_TECHNIQUES[dynamic]
        technique_text = "\n".join([f"  - {t}" for t in techniques[:3]])
        
        npc_behavior = self.NPC_BEHAVIORS.get(npc_disposition, self.NPC_BEHAVIORS["guarded"])
        
        rapport_desc = "hostile" if self.rapport_level < -0.3 else \
                       "tense" if self.rapport_level < 0.3 else \
                       "neutral" if self.rapport_level < 0.6 else "friendly"
        
        return f"""<social_encounter>
STAKES: {stakes.value.upper()} | Rapport: {rapport_desc}
NPC Disposition: {npc_disposition} - {npc_behavior}

CONVERSATION DYNAMICS ({dynamic}):
{technique_text}

DIALOGUE CRAFT:
  - What does each party WANT from this conversation?
  - What are they willing to GIVE?
  - What's the WORST that could happen if this goes wrong?
  - What's being LEFT UNSAID?

SUBTEXT LAYERS:
  - Surface: The words being spoken
  - Tactic: What they're trying to achieve with those words
  - Emotion: What they're actually feeling
  - Need: The deeper thing driving the conversation

NPC AUTHENTICITY:
  - NPCs have their own agendas (not just obstacles to player goals)
  - They can be persuaded, but not effortlessly
  - They remember what was said to them before
  - Their reactions should surprise but feel right

AVOID:
  - NPCs who give up information without reason
  - Binary success/failure (degrees of success create nuance)
  - Conversations without subtext (surface only = boring)
</social_encounter>"""
    
    def to_dict(self) -> dict:
        return {
            "rapport_level": self.rapport_level,
            "information_revealed": self.information_revealed,
            "lies_told": self.lies_told
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SocialEncounterSystem":
        system = cls()
        system.rapport_level = data.get("rapport_level", 0.5)
        system.information_revealed = data.get("information_revealed", [])
        system.lies_told = data.get("lies_told", [])
        return system


# =============================================================================
# EXPLORATION SCENE SYSTEM
# =============================================================================

class ExplorationFocus(Enum):
    """Focus of exploration scene."""
    DISCOVERY = "discovery"        # Finding something new
    NAVIGATION = "navigation"      # Getting somewhere
    SURVIVAL = "survival"          # Enduring the environment
    WONDER = "wonder"              # Experiencing beauty/awe
    MYSTERY = "mystery"            # Understanding a place


@dataclass
class ExplorationSystem:
    """
    Provides guidance for exploration and discovery scenes.
    
    Ensures environments feel alive, discoveries feel earned,
    and travel has purpose beyond getting from A to B.
    """
    
    locations_discovered: List[str] = field(default_factory=list)
    environmental_hazards_active: List[str] = field(default_factory=list)
    
    # Discovery types
    DISCOVERY_TYPES: List[Dict[str, str]] = field(default_factory=lambda: [
        {"type": "Remnant", "desc": "Evidence of those who came before"},
        {"type": "Resource", "desc": "Something useful for survival or mission"},
        {"type": "Danger", "desc": "A threat that must be navigated around"},
        {"type": "Beauty", "desc": "Something that takes the breath away"},
        {"type": "Puzzle", "desc": "Something that doesn't make sense yet"},
        {"type": "Shelter", "desc": "A place of temporary safety"},
        {"type": "Connection", "desc": "Link to elsewhere or something known"}
    ])
    
    # Atmosphere techniques
    ATMOSPHERE_TECHNIQUES: Dict[ExplorationFocus, List[str]] = field(default_factory=lambda: {
        ExplorationFocus.DISCOVERY: [
            "The moment before revelation—anticipation",
            "First glimpse should be partial, intriguing",
            "Sensory impact of the new thing",
            "What questions does this raise?"
        ],
        ExplorationFocus.WONDER: [
            "Scale that humbles",
            "Beauty that silences",
            "The pause where words fail",
            "How does this change how they see the universe?"
        ],
        ExplorationFocus.SURVIVAL: [
            "The environment as antagonist",
            "Resources dwindling, visible cost",
            "Adaptation and ingenuity",
            "The body's honest response to hardship"
        ],
        ExplorationFocus.MYSTERY: [
            "Things that don't add up",
            "Evidence of something not quite explained",
            "The space between what's seen and what's understood",
            "Questions that multiply with each answer"
        ]
    })
    
    def get_exploration_guidance(self, focus: ExplorationFocus = ExplorationFocus.DISCOVERY) -> str:
        """Generate exploration narration guidance."""
        
        techniques = self.ATMOSPHERE_TECHNIQUES.get(focus, [])
        technique_text = "\n".join([f"  - {t}" for t in techniques[:3]])
        
        # Random discovery suggestion
        discovery = random.choice(self.DISCOVERY_TYPES)
        
        return f"""<exploration_guidance>
EXPLORATION FOCUS: {focus.value.upper()}

ATMOSPHERE TECHNIQUES:
{technique_text}

DISCOVERY OPPORTUNITY:
  Type: {discovery['type']}
  "{discovery['desc']}"

ENVIRONMENT AS CHARACTER:
  - The place has moods, rhythms, dangers
  - Weather/conditions affect everything
  - Small details that reward attention
  - History readable in the landscape

PACING:
  - Quiet stretches make discoveries hit harder
  - Fatigue and distance should be felt
  - Moments of beauty between moments of danger
  - The journey changes the traveler

SENSORY IMMERSION:
  - What does this place SOUND like?
  - What TEMPERATURE/texture is the air?
  - What SMELLS mark this as unique?
  - How does gravity/movement FEEL here?

AVOID:
  - "You travel for three days uneventfully" (empty time)
  - Environments that are just backdrops (they should participate)
  - Discovery without wonder (everything should feel significant)
</exploration_guidance>"""
    
    def to_dict(self) -> dict:
        return {
            "locations_discovered": self.locations_discovered,
            "environmental_hazards_active": self.environmental_hazards_active
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ExplorationSystem":
        system = cls()
        system.locations_discovered = data.get("locations_discovered", [])
        system.environmental_hazards_active = data.get("environmental_hazards_active", [])
        return system


# =============================================================================
# HORROR/TENSION SYSTEM
# =============================================================================

class HorrorElement(Enum):
    """Elements of horror/tension."""
    DREAD = "dread"               # Anticipation of something bad
    UNCANNY = "uncanny"           # Something wrong with the familiar
    HELPLESSNESS = "helplessness" # Loss of control/power
    ISOLATION = "isolation"       # Cut off from help
    UNKNOWN = "unknown"           # Fear of what isn't understood
    BODY_HORROR = "body"          # Violation of physical self
    COSMIC = "cosmic"             # Insignificance before vastness


@dataclass
class HorrorTensionSystem:
    """
    Provides guidance for horror and tension scenes.
    
    Ensures dread builds properly, the unknown stays unknown
    long enough, and fear feels earned.
    """
    
    tension_level: float = 0.3
    unknown_elements: List[str] = field(default_factory=list)
    revealed_horrors: List[str] = field(default_factory=list)
    
    # Horror techniques
    HORROR_TECHNIQUES: Dict[HorrorElement, List[str]] = field(default_factory=lambda: {
        HorrorElement.DREAD: [
            "Anticipation is worse than the thing itself",
            "Small wrongnesses that accumulate",
            "The character noticing something the reader hasn't",
            "Time stretching as fear takes hold"
        ],
        HorrorElement.UNCANNY: [
            "The familiar made strange",
            "Something in the wrong place, wrong posture, wrong expression",
            "Recognition of what should not be recognized",
            "The moment before understanding something horrible"
        ],
        HorrorElement.UNKNOWN: [
            "What you DON'T see is scarier than what you do",
            "Glimpses, not reveals—imagination does the work",
            "Rules that don't make sense (yet)",
            "The limits of human comprehension"
        ],
        HorrorElement.ISOLATION: [
            "No one to call for help",
            "Communication cut, or worse—ignored",
            "The realization that you're alone with it",
            "Distance from safety becoming visceral"
        ],
        HorrorElement.COSMIC: [
            "Scale that renders human concerns meaningless",
            "Time that makes lifetimes insignificant",
            "Intelligence that doesn't register humans as relevant",
            "The universe's indifference made manifest"
        ]
    })
    
    def get_horror_guidance(self, element: HorrorElement = HorrorElement.DREAD) -> str:
        """Generate horror/tension guidance."""
        
        techniques = self.HORROR_TECHNIQUES.get(element, [])
        technique_text = "\n".join([f"  - {t}" for t in techniques])
        
        reveal_note = ""
        if len(self.revealed_horrors) < len(self.unknown_elements):
            reveal_note = f"""
UNKNOWN > REVEALED: {len(self.unknown_elements)} unknown, {len(self.revealed_horrors)} revealed
Continue to withhold—the unknown is still scarier."""
        
        return f"""<horror_tension>
HORROR ELEMENT: {element.value.upper()}
Tension level: {self.tension_level:.0%}
{reveal_note}

TECHNIQUES:
{technique_text}

THE FEAR EQUATION:
  Fear = Unknown + Helplessness + Personal Stakes
  Maximize all three before the reveal.

PACING HORROR:
  1. Establish normal (so violation is clear)
  2. Introduce wrongness (small, dismissible)
  3. Escalate (wrongness multiplies, can't be dismissed)
  4. Crisis (must confront what was avoided)
  5. Cost (horror always costs something)

SENSORY HORROR:
  - Sound: What shouldn't make that sound? What's too quiet?
  - Touch: Textures that revolt, temperatures that wrong
  - Smell: Decay, wrongness, the body's warning signals
  - Sight: Shapes in darkness, movement at edge of vision

THE REVEAL PARADOX:
  Revealing the horror is often a relief (known > unknown).
  Keep the unknown unknown as long as tension can be sustained.
  When you reveal, reveal MOST but not all.

AVOID:
  - Jump scares without buildup (cheap, unsatisfying)
  - Over-describing the monster (mystery is scarier)
  - Protagonists acting stupidly for plot convenience
  - Horror without aftermath (trauma should linger)
</horror_tension>"""
    
    def to_dict(self) -> dict:
        return {
            "tension_level": self.tension_level,
            "unknown_elements": self.unknown_elements,
            "revealed_horrors": self.revealed_horrors
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "HorrorTensionSystem":
        system = cls()
        system.tension_level = data.get("tension_level", 0.3)
        system.unknown_elements = data.get("unknown_elements", [])
        system.revealed_horrors = data.get("revealed_horrors", [])
        return system


# =============================================================================
# MASTER SPECIALIZED SCENES ENGINE
# =============================================================================

@dataclass
class SpecializedScenesEngine:
    """Master engine coordinating all specialized scene systems."""
    
    combat: CombatNarrationSystem = field(default_factory=CombatNarrationSystem)
    investigation: InvestigationSystem = field(default_factory=InvestigationSystem)
    social: SocialEncounterSystem = field(default_factory=SocialEncounterSystem)
    exploration: ExplorationSystem = field(default_factory=ExplorationSystem)
    horror: HorrorTensionSystem = field(default_factory=HorrorTensionSystem)
    
    current_scene_type: str = "general"
    
    def get_scene_guidance(self, scene_type: str = "general", **kwargs) -> str:
        """Get guidance for the current scene type."""
        
        if scene_type == "combat":
            return self.combat.get_combat_guidance(
                scale=kwargs.get('scale', CombatScale.SKIRMISH),
                player_health=kwargs.get('player_health', 1.0)
            )
        elif scene_type == "investigation":
            return self.investigation.get_investigation_guidance()
        elif scene_type == "social":
            return self.social.get_social_guidance(
                stakes=kwargs.get('stakes', SocialStakes.INFORMATION),
                npc_disposition=kwargs.get('disposition', 'guarded')
            )
        elif scene_type == "exploration":
            return self.exploration.get_exploration_guidance(
                focus=kwargs.get('focus', ExplorationFocus.DISCOVERY)
            )
        elif scene_type == "horror":
            return self.horror.get_horror_guidance(
                element=kwargs.get('element', HorrorElement.DREAD)
            )
        
        return ""
    
    def to_dict(self) -> dict:
        return {
            "combat": self.combat.to_dict(),
            "investigation": self.investigation.to_dict(),
            "social": self.social.to_dict(),
            "exploration": self.exploration.to_dict(),
            "horror": self.horror.to_dict(),
            "current_scene_type": self.current_scene_type
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SpecializedScenesEngine":
        engine = cls()
        if "combat" in data:
            engine.combat = CombatNarrationSystem.from_dict(data["combat"])
        if "investigation" in data:
            engine.investigation = InvestigationSystem.from_dict(data["investigation"])
        if "social" in data:
            engine.social = SocialEncounterSystem.from_dict(data["social"])
        if "exploration" in data:
            engine.exploration = ExplorationSystem.from_dict(data["exploration"])
        if "horror" in data:
            engine.horror = HorrorTensionSystem.from_dict(data["horror"])
        engine.current_scene_type = data.get("current_scene_type", "general")
        return engine


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SPECIALIZED SCENES ENGINE - TEST")
    print("=" * 60)
    
    engine = SpecializedScenesEngine()
    
    # Test each scene type
    scene_types = ["combat", "investigation", "social", "exploration", "horror"]
    
    for st in scene_types:
        print(f"\n{'='*60}")
        print(f"SCENE TYPE: {st.upper()}")
        print("=" * 60)
        print(engine.get_scene_guidance(st))
