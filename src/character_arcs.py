"""
Character & Story Arc Systems - Long-Form Narrative Tracking

This module provides systems for tracking character development,
foreshadowing payoffs, pacing patterns, and emotional resonance
across extended narrative sessions.

Key Systems:
1. Character Arc Tracker - Monitor protagonist growth and transformation
2. Foreshadowing Payoff System - Track planted seeds and ensure payoffs
3. Pacing Rhythm Analyzer - Ensure proper scene-type alternation
4. Emotional Resonance Amplifier - Detect and deepen key emotional moments
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple, Set
import random
import math


# =============================================================================
# CHARACTER ARC TRACKER
# =============================================================================

class ArcPhase(Enum):
    """Phases of character transformation arc."""
    ORDINARY_WORLD = "ordinary_world"      # Status quo, comfort zone
    CALL_TO_ADVENTURE = "call"             # Inciting incident
    REFUSAL = "refusal"                    # Initial resistance
    CROSSING_THRESHOLD = "threshold"        # Commitment to journey
    TESTS_ALLIES_ENEMIES = "tests"         # Learning the new world
    APPROACH_CAVE = "approach"             # Preparing for ordeal
    ORDEAL = "ordeal"                      # Central crisis, death/rebirth
    REWARD = "reward"                      # Seizing the prize
    ROAD_BACK = "road_back"                # Returning changed
    RESURRECTION = "resurrection"          # Final test, transformation
    RETURN_ELIXIR = "return"               # New equilibrium


class CharacterFlaw(Enum):
    """Common character flaws that drive arcs."""
    PRIDE = "pride"                        # Believes they're always right
    FEAR = "fear"                          # Avoids confrontation/risk
    GUILT = "guilt"                        # Burdened by past failure
    DISTRUST = "distrust"                  # Can't rely on others
    CONTROL = "control"                    # Must control everything
    ISOLATION = "isolation"                # Pushes others away
    PERFECTIONISM = "perfectionism"        # Can't accept imperfection
    VENGEANCE = "vengeance"                # Consumed by revenge
    DENIAL = "denial"                      # Refuses to face truth
    SELFISHNESS = "selfishness"            # Prioritizes self over others


@dataclass
class CharacterState:
    """Tracks a character's arc state."""
    name: str
    primary_flaw: CharacterFlaw
    flaw_intensity: float  # 0.0 (overcome) to 1.0 (max)
    current_phase: ArcPhase
    growth_moments: List[Dict[str, str]] = field(default_factory=list)  # {scene, description}
    regression_moments: List[Dict[str, str]] = field(default_factory=list)
    internal_goal: str = ""  # What they want emotionally
    external_goal: str = ""  # What they want materially
    ghost: str = ""  # Past trauma driving behavior
    lie_believed: str = ""  # False belief they must overcome
    truth_needed: str = ""  # What they need to learn


@dataclass
class CharacterArcTracker:
    """
    Monitors protagonist growth and transformation across sessions.
    
    Tracks the Hero's Journey phases, character flaws, growth/regression,
    and provides guidance for meaningful character moments.
    """
    
    characters: Dict[str, CharacterState] = field(default_factory=dict)
    current_scene: int = 0
    
    # Arc phase guidance
    PHASE_GUIDANCE: Dict[ArcPhase, Dict[str, str]] = field(default_factory=lambda: {
        ArcPhase.ORDINARY_WORLD: {
            "purpose": "Establish sympathy, show the flaw in action, hint at potential",
            "focus": "What does the character want? What are they afraid of?",
            "avoid": "Making them too perfect or too flawed to root for"
        },
        ArcPhase.CALL_TO_ADVENTURE: {
            "purpose": "Disrupt comfort zone, present opportunity/threat",
            "focus": "The call should threaten what they love or offer what they want",
            "avoid": "Random events—call should connect to their core needs"
        },
        ArcPhase.REFUSAL: {
            "purpose": "Show the flaw preventing action, raise stakes",
            "focus": "Their reason for refusing reveals their flaw",
            "avoid": "Making refusal last too long—momentum matters"
        },
        ArcPhase.CROSSING_THRESHOLD: {
            "purpose": "Commit to change, enter new world (literal or metaphorical)",
            "focus": "Point of no return—they can't go back to who they were",
            "avoid": "Passive crossing—they must CHOOSE to cross"
        },
        ArcPhase.TESTS_ALLIES_ENEMIES: {
            "purpose": "Learn new rules, form bonds, face obstacles",
            "focus": "Each test should pressure the flaw in different ways",
            "avoid": "Repetitive tests—variety in challenges and character dynamics"
        },
        ArcPhase.APPROACH_CAVE: {
            "purpose": "Prepare for greatest challenge, doubt creeps in",
            "focus": "Last chance for character to confront their lie",
            "avoid": "Rushing to ordeal—savor the anticipation"
        },
        ArcPhase.ORDEAL: {
            "purpose": "Death and rebirth—old self must die for new to emerge",
            "focus": "Crisis forces choice between flaw and growth",
            "avoid": "Easy victories—this should cost them something real"
        },
        ArcPhase.REWARD: {
            "purpose": "Seize what was sought, moment of triumph",
            "focus": "Pride before fall—or genuine transformation?",
            "avoid": "Hollow reward—it must feel earned"
        },
        ArcPhase.ROAD_BACK: {
            "purpose": "Consequences of ordeal, pursuit by forces of change",
            "focus": "Will they hold onto growth under pressure?",
            "avoid": "Easy resolution—road back should test new self"
        },
        ArcPhase.RESURRECTION: {
            "purpose": "Final test proving transformation is real",
            "focus": "Must face the SAME choice that defined their flaw",
            "avoid": "New test—it must echo the original failure"
        },
        ArcPhase.RETURN_ELIXIR: {
            "purpose": "Share transformation, new equilibrium established",
            "focus": "How are they different? How has world changed?",
            "avoid": "Rushing the ending—let transformation resonate"
        }
    })
    
    # Flaw manifestation guidance
    FLAW_MANIFESTATIONS: Dict[CharacterFlaw, List[str]] = field(default_factory=lambda: {
        CharacterFlaw.PRIDE: [
            "Dismisses others' ideas without consideration",
            "Takes credit, deflects blame",
            "Can't admit when wrong, doubles down on mistakes"
        ],
        CharacterFlaw.FEAR: [
            "Avoids confrontation, lets problems fester",
            "Chooses safe path over right path",
            "Freezes in crucial moments"
        ],
        CharacterFlaw.GUILT: [
            "Punishes self through risky behavior",
            "Can't accept forgiveness or praise",
            "Sees self as fundamentally unworthy"
        ],
        CharacterFlaw.DISTRUST: [
            "Refuses help even when desperately needed",
            "Assumes worst motivations in others",
            "Keeps crucial information secret"
        ],
        CharacterFlaw.CONTROL: [
            "Micromanages, can't delegate",
            "Falls apart when plans change",
            "Manipulates others 'for their own good'"
        ],
        CharacterFlaw.ISOLATION: [
            "Pushes away those who get close",
            "Sabotages relationships before they can hurt",
            "Convinces self they work better alone"
        ]
    })
    
    def register_character(self, name: str, flaw: CharacterFlaw,
                           internal_goal: str = "", external_goal: str = "",
                           ghost: str = "", lie: str = "", truth: str = "") -> CharacterState:
        """Register a character for arc tracking."""
        char = CharacterState(
            name=name,
            primary_flaw=flaw,
            flaw_intensity=0.9,  # Start high
            current_phase=ArcPhase.ORDINARY_WORLD,
            internal_goal=internal_goal,
            external_goal=external_goal,
            ghost=ghost,
            lie_believed=lie,
            truth_needed=truth
        )
        self.characters[name] = char
        return char
    
    def record_growth(self, name: str, description: str):
        """Record a moment of character growth."""
        if name in self.characters:
            char = self.characters[name]
            char.growth_moments.append({
                "scene": str(self.current_scene),
                "description": description
            })
            # Decrease flaw intensity
            char.flaw_intensity = max(0.0, char.flaw_intensity - 0.1)
    
    def record_regression(self, name: str, description: str):
        """Record a moment of character regression."""
        if name in self.characters:
            char = self.characters[name]
            char.regression_moments.append({
                "scene": str(self.current_scene),
                "description": description
            })
            # Increase flaw intensity
            char.flaw_intensity = min(1.0, char.flaw_intensity + 0.05)
    
    def advance_phase(self, name: str):
        """Move character to next arc phase."""
        if name in self.characters:
            phases = list(ArcPhase)
            current_idx = phases.index(self.characters[name].current_phase)
            if current_idx < len(phases) - 1:
                self.characters[name].current_phase = phases[current_idx + 1]
    
    def get_arc_guidance(self, name: str) -> str:
        """Generate character arc guidance for narrator."""
        if name not in self.characters:
            return ""
        
        char = self.characters[name]
        phase_info = self.PHASE_GUIDANCE.get(char.current_phase, {})
        flaw_manifest = self.FLAW_MANIFESTATIONS.get(char.primary_flaw, [])
        
        growth_summary = ""
        if char.growth_moments:
            recent = char.growth_moments[-2:]
            growth_summary = f"\nRECENT GROWTH: {'; '.join([g['description'] for g in recent])}"
        
        regression_summary = ""
        if char.regression_moments:
            recent = char.regression_moments[-2:]
            regression_summary = f"\nRECENT SETBACKS: {'; '.join([r['description'] for r in recent])}"
        
        flaw_examples = "\n".join([f"  - {m}" for m in flaw_manifest[:2]])
        
        return f"""<character_arc name="{name}">
PHASE: {char.current_phase.value.upper()}
FLAW: {char.primary_flaw.value} (intensity: {char.flaw_intensity:.0%})
{growth_summary}{regression_summary}

PHASE PURPOSE: {phase_info.get('purpose', '')}
FOCUS: {phase_info.get('focus', '')}
AVOID: {phase_info.get('avoid', '')}

FLAW MANIFESTATIONS (show, don't tell):
{flaw_examples}

THE LIE: "{char.lie_believed}"
THE TRUTH: "{char.truth_needed}"
THE GHOST: {char.ghost}

SCENE OPPORTUNITY:
This scene can pressure the flaw through:
  - A choice that tempts the flaw-driven response
  - A consequence of previous flaw-driven choices
  - A mirror character showing what they could become
</character_arc>"""
    
    def to_dict(self) -> dict:
        return {
            "characters": {
                name: {
                    "name": c.name,
                    "primary_flaw": c.primary_flaw.value,
                    "flaw_intensity": c.flaw_intensity,
                    "current_phase": c.current_phase.value,
                    "growth_moments": c.growth_moments,
                    "regression_moments": c.regression_moments,
                    "internal_goal": c.internal_goal,
                    "external_goal": c.external_goal,
                    "ghost": c.ghost,
                    "lie_believed": c.lie_believed,
                    "truth_needed": c.truth_needed
                } for name, c in self.characters.items()
            },
            "current_scene": self.current_scene
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CharacterArcTracker":
        tracker = cls()
        tracker.current_scene = data.get("current_scene", 0)
        
        for name, c in data.get("characters", {}).items():
            tracker.characters[name] = CharacterState(
                name=c["name"],
                primary_flaw=CharacterFlaw(c["primary_flaw"]),
                flaw_intensity=c["flaw_intensity"],
                current_phase=ArcPhase(c["current_phase"]),
                growth_moments=c.get("growth_moments", []),
                regression_moments=c.get("regression_moments", []),
                internal_goal=c.get("internal_goal", ""),
                external_goal=c.get("external_goal", ""),
                ghost=c.get("ghost", ""),
                lie_believed=c.get("lie_believed", ""),
                truth_needed=c.get("truth_needed", "")
            )
        return tracker


# =============================================================================
# FORESHADOWING PAYOFF SYSTEM
# =============================================================================

class SeedType(Enum):
    """Types of narrative seeds that need payoff."""
    CHEKHOV_GUN = "chekhov_gun"       # Object shown must be used
    PROMISE = "promise"               # Character vow requiring resolution
    MYSTERY = "mystery"               # Question raised requiring answer
    PROPHECY = "prophecy"             # Prediction requiring fulfillment/subversion
    RELATIONSHIP = "relationship"     # Connection requiring development
    THREAT = "threat"                 # Danger foreshadowed
    SKILL = "skill"                   # Competence shown must be relevant
    WEAKNESS = "weakness"             # Vulnerability that will be tested


@dataclass
class NarrativeSeed:
    """A planted story element requiring payoff."""
    seed_type: SeedType
    description: str
    planted_scene: int
    ideal_payoff_window: Tuple[int, int]  # Min/max scenes until payoff
    payoff_hint: str  # How might this pay off?
    is_paid: bool = False
    payoff_description: str = ""
    urgency: float = 0.0  # 0.0 to 1.0, increases as deadline approaches


@dataclass
class ForeshadowingSystem:
    """
    Tracks planted narrative seeds and ensures payoffs.
    
    Every gun on the wall in Act 1 must fire by Act 3.
    This system tracks what's been set up and reminds
    the narrator when payoffs are due.
    """
    
    seeds: Dict[str, NarrativeSeed] = field(default_factory=dict)
    current_scene: int = 0
    paid_seeds: List[str] = field(default_factory=list)
    
    # Payoff guidance by type
    PAYOFF_PATTERNS: Dict[SeedType, List[str]] = field(default_factory=lambda: {
        SeedType.CHEKHOV_GUN: [
            "Object used in unexpected but inevitable way",
            "Object used by unexpected person",
            "Object use subverted—expected use, unexpected outcome"
        ],
        SeedType.PROMISE: [
            "Promise kept at great cost",
            "Promise broken with devastating consequence",
            "Promise kept in letter but not spirit"
        ],
        SeedType.MYSTERY: [
            "Answer recontextualizes everything",
            "Partial answer raises deeper question",
            "Answer was hiding in plain sight"
        ],
        SeedType.PROPHECY: [
            "Literal fulfillment, figurative meaning",
            "Subverted—true meaning was misunderstood",
            "Self-fulfilling—attempt to prevent caused it"
        ],
        SeedType.THREAT: [
            "Threat materializes when least expected",
            "Threat anticipated—but worse than imagined",
            "Threat came from unexpected direction"
        ]
    })
    
    def plant_seed(self, seed_id: str, seed_type: SeedType,
                   description: str, min_delay: int = 3, max_delay: int = 10,
                   payoff_hint: str = "") -> NarrativeSeed:
        """Plant a new narrative seed."""
        seed = NarrativeSeed(
            seed_type=seed_type,
            description=description,
            planted_scene=self.current_scene,
            ideal_payoff_window=(
                self.current_scene + min_delay,
                self.current_scene + max_delay
            ),
            payoff_hint=payoff_hint
        )
        self.seeds[seed_id] = seed
        return seed
    
    def payoff_seed(self, seed_id: str, payoff_description: str):
        """Mark a seed as paid off."""
        if seed_id in self.seeds:
            self.seeds[seed_id].is_paid = True
            self.seeds[seed_id].payoff_description = payoff_description
            self.paid_seeds.append(seed_id)
    
    def get_ripe_seeds(self) -> List[Tuple[str, NarrativeSeed]]:
        """Get seeds that are ready for payoff."""
        ripe = []
        for seed_id, seed in self.seeds.items():
            if seed.is_paid:
                continue
            
            min_scene, max_scene = seed.ideal_payoff_window
            if self.current_scene >= min_scene:
                # Calculate urgency
                if self.current_scene >= max_scene:
                    seed.urgency = 1.0
                else:
                    window_size = max_scene - min_scene
                    progress = self.current_scene - min_scene
                    seed.urgency = progress / window_size if window_size > 0 else 1.0
                
                ripe.append((seed_id, seed))
        
        # Sort by urgency
        ripe.sort(key=lambda x: x[1].urgency, reverse=True)
        return ripe
    
    def get_payoff_guidance(self) -> str:
        """Generate foreshadowing payoff guidance for narrator."""
        ripe = self.get_ripe_seeds()
        
        if not ripe:
            # Suggest planting new seeds
            return """<foreshadowing>
No seeds currently ripe for payoff.

CONSIDER PLANTING:
  - An object that will matter later (Chekhov's gun)
  - A promise that will be tested
  - A mystery that will recontextualize events
  - A skill the protagonist will need in crisis

Good foreshadowing is invisible on first read, inevitable on second.
</foreshadowing>"""
        
        seed_list = []
        for seed_id, seed in ripe[:3]:
            urgency_label = "⚠️ OVERDUE" if seed.urgency >= 1.0 else f"({seed.urgency:.0%} ripe)"
            patterns = self.PAYOFF_PATTERNS.get(seed.seed_type, ["Pay off naturally"])
            pattern = random.choice(patterns)
            
            seed_list.append(f"""  [{seed.seed_type.value}] {urgency_label}
    Planted: "{seed.description}"
    Hint: {seed.payoff_hint}
    Pattern: {pattern}""")
        
        return f"""<foreshadowing_payoff>
SEEDS READY FOR HARVEST:

{chr(10).join(seed_list)}

PAYOFF PRINCIPLES:
  - Inevitable but not predictable
  - Recontextualizes, doesn't just resolve
  - Emotional payoff > plot payoff
  - Subversion is valid if earned
</foreshadowing_payoff>"""
    
    def advance_scene(self):
        """Move to next scene."""
        self.current_scene += 1
    
    def to_dict(self) -> dict:
        return {
            "seeds": {
                sid: {
                    "seed_type": s.seed_type.value,
                    "description": s.description,
                    "planted_scene": s.planted_scene,
                    "ideal_payoff_window": s.ideal_payoff_window,
                    "payoff_hint": s.payoff_hint,
                    "is_paid": s.is_paid,
                    "payoff_description": s.payoff_description,
                    "urgency": s.urgency
                } for sid, s in self.seeds.items()
            },
            "current_scene": self.current_scene,
            "paid_seeds": self.paid_seeds
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ForeshadowingSystem":
        system = cls()
        system.current_scene = data.get("current_scene", 0)
        system.paid_seeds = data.get("paid_seeds", [])
        
        for sid, s in data.get("seeds", {}).items():
            system.seeds[sid] = NarrativeSeed(
                seed_type=SeedType(s["seed_type"]),
                description=s["description"],
                planted_scene=s["planted_scene"],
                ideal_payoff_window=tuple(s["ideal_payoff_window"]),
                payoff_hint=s["payoff_hint"],
                is_paid=s.get("is_paid", False),
                payoff_description=s.get("payoff_description", ""),
                urgency=s.get("urgency", 0.0)
            )
        return system


# =============================================================================
# PACING RHYTHM ANALYZER
# =============================================================================

class SceneType(Enum):
    """Types of scenes for pacing analysis."""
    ACTION = "action"           # Physical conflict, chase, danger
    DIALOGUE = "dialogue"       # Character interaction, revelation
    QUIET = "quiet"             # Reflection, rest, intimacy
    INVESTIGATION = "investigation"  # Discovery, research, tracking
    TENSION = "tension"         # Building dread without action
    EMOTIONAL = "emotional"     # Character breakdown/breakthrough
    TRANSITION = "transition"   # Travel, time passage


@dataclass
class PacingRhythmAnalyzer:
    """
    Ensures proper scene-type alternation for narrative rhythm.
    
    Action, action, action = exhausting.
    Quiet, quiet, quiet = boring.
    Varied rhythm = engaging.
    """
    
    scene_history: List[Tuple[int, SceneType]] = field(default_factory=list)
    current_scene: int = 0
    
    # Ideal scene type sequences
    RHYTHM_PATTERNS: Dict[str, List[SceneType]] = field(default_factory=lambda: {
        "tension_build": [SceneType.QUIET, SceneType.TENSION, SceneType.ACTION],
        "aftermath": [SceneType.ACTION, SceneType.EMOTIONAL, SceneType.QUIET],
        "investigation": [SceneType.DIALOGUE, SceneType.INVESTIGATION, SceneType.TENSION],
        "character": [SceneType.ACTION, SceneType.QUIET, SceneType.DIALOGUE],
    })
    
    # Scene type compatibility (what naturally follows)
    GOOD_FOLLOWS: Dict[SceneType, List[SceneType]] = field(default_factory=lambda: {
        SceneType.ACTION: [SceneType.EMOTIONAL, SceneType.QUIET, SceneType.DIALOGUE],
        SceneType.DIALOGUE: [SceneType.TENSION, SceneType.ACTION, SceneType.INVESTIGATION],
        SceneType.QUIET: [SceneType.TENSION, SceneType.DIALOGUE, SceneType.ACTION],
        SceneType.INVESTIGATION: [SceneType.TENSION, SceneType.DIALOGUE, SceneType.ACTION],
        SceneType.TENSION: [SceneType.ACTION, SceneType.EMOTIONAL],
        SceneType.EMOTIONAL: [SceneType.QUIET, SceneType.DIALOGUE, SceneType.TRANSITION],
        SceneType.TRANSITION: [SceneType.QUIET, SceneType.ACTION, SceneType.INVESTIGATION]
    })
    
    def record_scene(self, scene_type: SceneType):
        """Record a scene's type."""
        self.scene_history.append((self.current_scene, scene_type))
        self.current_scene += 1
    
    def get_rhythm_issues(self) -> List[str]:
        """Detect pacing rhythm issues."""
        issues = []
        
        if len(self.scene_history) < 3:
            return issues
        
        recent = [s[1] for s in self.scene_history[-5:]]
        
        # Check for repetition
        if len(recent) >= 3 and recent[-1] == recent[-2] == recent[-3]:
            issues.append(f"⚠️ Three consecutive {recent[-1].value} scenes—vary the rhythm!")
        
        # Check for missing quiet moments
        last_quiet = None
        for i, (scene, stype) in enumerate(reversed(self.scene_history)):
            if stype in [SceneType.QUIET, SceneType.EMOTIONAL]:
                last_quiet = len(self.scene_history) - i - 1
                break
        
        if last_quiet is not None:
            scenes_since_quiet = self.current_scene - last_quiet
            if scenes_since_quiet >= 4:
                issues.append(f"⚠️ {scenes_since_quiet} scenes since last quiet moment—readers need to breathe")
        
        # Check for action fatigue
        action_count = sum(1 for s in recent if s == SceneType.ACTION)
        if action_count >= 3:
            issues.append("⚠️ Too much action—diminishing returns on tension")
        
        return issues
    
    def suggest_next_scene_type(self) -> str:
        """Suggest appropriate scene type based on rhythm."""
        if not self.scene_history:
            return f"Any scene type appropriate for opening"
        
        last_type = self.scene_history[-1][1]
        good_follows = self.GOOD_FOLLOWS.get(last_type, list(SceneType))
        
        return f"Consider: {', '.join([s.value for s in good_follows[:3]])}"
    
    def get_pacing_guidance(self) -> str:
        """Generate pacing rhythm guidance for narrator."""
        issues = self.get_rhythm_issues()
        suggestion = self.suggest_next_scene_type()
        
        # Visualize recent rhythm
        rhythm_viz = ""
        if self.scene_history:
            recent = self.scene_history[-8:]
            symbols = {
                SceneType.ACTION: "⚔️",
                SceneType.DIALOGUE: "💬",
                SceneType.QUIET: "🌙",
                SceneType.INVESTIGATION: "🔍",
                SceneType.TENSION: "⏳",
                SceneType.EMOTIONAL: "💔",
                SceneType.TRANSITION: "→"
            }
            rhythm_viz = " ".join([symbols.get(s[1], "?") for s in recent])
        
        issues_text = "\n".join(issues) if issues else "Rhythm is healthy"
        
        return f"""<pacing_rhythm>
RECENT RHYTHM: {rhythm_viz}

{issues_text}

NEXT SCENE: {suggestion}

RHYTHM PRINCIPLES:
  - Vary intensity like a heartbeat, not a flatline
  - Every "up" scene needs a "down" scene to recover
  - Quiet scenes do the most character work
  - Readers need time to process before next intensity spike
</pacing_rhythm>"""
    
    def to_dict(self) -> dict:
        return {
            "scene_history": [(s, t.value) for s, t in self.scene_history[-20:]],
            "current_scene": self.current_scene
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PacingRhythmAnalyzer":
        analyzer = cls()
        analyzer.current_scene = data.get("current_scene", 0)
        for s, t in data.get("scene_history", []):
            analyzer.scene_history.append((s, SceneType(t)))
        return analyzer


# =============================================================================
# EMOTIONAL RESONANCE AMPLIFIER
# =============================================================================

class EmotionalBeat(Enum):
    """Types of emotional beats to amplify."""
    REUNION = "reunion"           # Characters reunite after separation
    LOSS = "loss"                 # Character loses something/someone valued
    BETRAYAL = "betrayal"         # Trust broken
    SACRIFICE = "sacrifice"       # Character gives up something for another
    TRIUMPH = "triumph"           # Overcoming against odds
    CONFESSION = "confession"     # Truth revealed with emotional stakes
    FORGIVENESS = "forgiveness"   # Letting go of grievance
    RECOGNITION = "recognition"   # Character finally seen/understood
    GOODBYE = "goodbye"           # Parting, possibly final
    PROMISE = "promise"           # Vow made with weight


@dataclass
class EmotionalMoment:
    """A detected emotional moment."""
    beat_type: EmotionalBeat
    characters_involved: List[str]
    context: str
    scene: int
    intensified: bool = False


@dataclass
class EmotionalResonanceAmplifier:
    """
    Detects key emotional moments and provides guidance to deepen them.
    
    These moments are the heart of storytelling. This system
    identifies when they're occurring and provides techniques
    to maximize their impact.
    """
    
    emotional_history: List[EmotionalMoment] = field(default_factory=list)
    current_scene: int = 0
    
    # Amplification techniques by beat type
    AMPLIFICATION_TECHNIQUES: Dict[EmotionalBeat, List[str]] = field(default_factory=lambda: {
        EmotionalBeat.REUNION: [
            "Slow the moment—time dilates in high emotion",
            "Focus on a small detail (the way they still smell, a new scar)",
            "What goes UNSAID speaks loudest",
            "Physical distance decreasing = internal journey"
        ],
        EmotionalBeat.LOSS: [
            "Stay in the moment—don't rush past the pain",
            "Use absence to make presence felt (empty chair, silence)",
            "Character denial before acceptance",
            "Small domestic details hit harder than grand gestures"
        ],
        EmotionalBeat.BETRAYAL: [
            "Show the trust before breaking it (callback)",
            "Betrayer's perspective adds dimension",
            "Focus on the betrayed's PHYSICAL response",
            "What hurts most is what the betrayal reveals"
        ],
        EmotionalBeat.SACRIFICE: [
            "Make the cost VISIBLE and specific",
            "Show what they're giving up, not just why",
            "Others' reaction amplifies the act",
            "Silence after sacrifice > immediate reaction"
        ],
        EmotionalBeat.TRIUMPH: [
            "Earn it—callback to moments of doubt",
            "Victory has a cost or complication",
            "Character's surprise at their own capability",
            "Others seeing them differently now"
        ],
        EmotionalBeat.CONFESSION: [
            "Building to confession > the confession itself",
            "Listener's face, not speaker's words",
            "What it costs to say it",
            "Aftermath silence while truth sinks in"
        ],
        EmotionalBeat.FORGIVENESS: [
            "It's not instant—show the struggle to forgive",
            "Forgiving isn't forgetting—acknowledge both",
            "Physical gesture seals emotional shift",
            "What forgiveness makes possible now"
        ],
        EmotionalBeat.GOODBYE: [
            "What's left unsaid = what matters most",
            "Small rituals of departure",
            "Looking back (or deliberately not)",
            "The space they leave behind"
        ]
    })
    
    # Context clues that suggest emotional beats
    BEAT_TRIGGERS: Dict[EmotionalBeat, List[str]] = field(default_factory=lambda: {
        EmotionalBeat.REUNION: ["return", "back", "again", "found", "together"],
        EmotionalBeat.LOSS: ["gone", "dead", "lost", "never", "last"],
        EmotionalBeat.BETRAYAL: ["lied", "secret", "truth", "trusted", "believed"],
        EmotionalBeat.SACRIFICE: ["give up", "instead", "save", "cost", "for them"],
        EmotionalBeat.CONFESSION: ["tell", "admit", "sorry", "truth", "finally"],
        EmotionalBeat.GOODBYE: ["leave", "goodbye", "farewell", "last time"]
    })
    
    def detect_emotional_beat(self, narrative: str, 
                               characters: List[str]) -> Optional[EmotionalBeat]:
        """Detect if narrative contains an emotional beat."""
        narrative_lower = narrative.lower()
        
        for beat, triggers in self.BEAT_TRIGGERS.items():
            if any(t in narrative_lower for t in triggers):
                return beat
        return None
    
    def record_moment(self, beat_type: EmotionalBeat,
                      characters: List[str], context: str):
        """Record an emotional moment."""
        moment = EmotionalMoment(
            beat_type=beat_type,
            characters_involved=characters,
            context=context,
            scene=self.current_scene
        )
        self.emotional_history.append(moment)
    
    def get_amplification_guidance(self, beat_type: EmotionalBeat) -> str:
        """Get guidance for amplifying an emotional beat."""
        techniques = self.AMPLIFICATION_TECHNIQUES.get(beat_type, [])
        if not techniques:
            return ""
        
        selected = random.sample(techniques, min(3, len(techniques)))
        
        return f"""<emotional_amplification beat="{beat_type.value}">
⭐ EMOTIONAL BEAT DETECTED: {beat_type.value.upper()}

This is a moment that could resonate deeply. Slow down. Earn it.

AMPLIFICATION TECHNIQUES:
{chr(10).join([f"  - {t}" for t in selected])}

UNIVERSAL PRINCIPLES:
  - Restraint > melodrama. Less is more.
  - Body > dialogue. Show physical response.
  - Silence speaks. Let moments breathe.
  - Specific > general. The unique detail imprints.
  - Callback to earlier moments multiplies impact.

THE 30-SECOND RULE:
If this were a film, would you hold on this moment for 30 seconds?
That's the weight it deserves. Don't rush past it.
</emotional_amplification>"""
    
    def get_emotional_history_context(self) -> str:
        """Get context about recent emotional history."""
        if not self.emotional_history:
            return ""
        
        recent = self.emotional_history[-5:]
        moments = []
        for m in recent:
            chars = ", ".join(m.characters_involved) if m.characters_involved else "unknown"
            moments.append(f"  Scene {m.scene}: {m.beat_type.value} ({chars})")
        
        return f"""<emotional_history>
RECENT EMOTIONAL BEATS:
{chr(10).join(moments)}

Consider callbacks to these moments for resonance amplification.
</emotional_history>"""
    
    def to_dict(self) -> dict:
        return {
            "emotional_history": [
                {
                    "beat_type": m.beat_type.value,
                    "characters_involved": m.characters_involved,
                    "context": m.context,
                    "scene": m.scene,
                    "intensified": m.intensified
                } for m in self.emotional_history[-20:]
            ],
            "current_scene": self.current_scene
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "EmotionalResonanceAmplifier":
        amplifier = cls()
        amplifier.current_scene = data.get("current_scene", 0)
        
        for m in data.get("emotional_history", []):
            amplifier.emotional_history.append(EmotionalMoment(
                beat_type=EmotionalBeat(m["beat_type"]),
                characters_involved=m["characters_involved"],
                context=m["context"],
                scene=m["scene"],
                intensified=m.get("intensified", False)
            ))
        return amplifier


# =============================================================================
# MASTER CHARACTER ARC ENGINE
# =============================================================================

@dataclass
class CharacterArcEngine:
    """Master engine coordinating all character and story arc systems."""
    
    arc_tracker: CharacterArcTracker = field(default_factory=CharacterArcTracker)
    foreshadowing: ForeshadowingSystem = field(default_factory=ForeshadowingSystem)
    pacing: PacingRhythmAnalyzer = field(default_factory=PacingRhythmAnalyzer)
    emotional: EmotionalResonanceAmplifier = field(default_factory=EmotionalResonanceAmplifier)
    
    def get_comprehensive_guidance(
        self,
        protagonist_name: str = "",
        detected_emotion: Optional[EmotionalBeat] = None,
        current_scene_type: Optional[SceneType] = None
    ) -> str:
        """Generate comprehensive character and story arc guidance."""
        
        sections = []
        
        # Character arc for protagonist
        if protagonist_name and protagonist_name in self.arc_tracker.characters:
            sections.append(self.arc_tracker.get_arc_guidance(protagonist_name))
        
        # Foreshadowing payoffs
        foreshadow_guidance = self.foreshadowing.get_payoff_guidance()
        if foreshadow_guidance:
            sections.append(foreshadow_guidance)
        
        # Pacing rhythm
        if current_scene_type:
            self.pacing.record_scene(current_scene_type)
        sections.append(self.pacing.get_pacing_guidance())
        
        # Emotional amplification
        if detected_emotion:
            sections.append(self.emotional.get_amplification_guidance(detected_emotion))
        else:
            hist = self.emotional.get_emotional_history_context()
            if hist:
                sections.append(hist)
        
        if not sections:
            return ""
        
        return f"""
<character_story_arcs>
=== CHARACTER & STORY ARC GUIDANCE ===
{chr(10).join(sections)}
</character_story_arcs>
"""
    
    def advance_scene(self):
        """Move all systems to next scene."""
        self.arc_tracker.current_scene += 1
        self.foreshadowing.advance_scene()
        self.emotional.current_scene += 1
    
    def to_dict(self) -> dict:
        return {
            "arc_tracker": self.arc_tracker.to_dict(),
            "foreshadowing": self.foreshadowing.to_dict(),
            "pacing": self.pacing.to_dict(),
            "emotional": self.emotional.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CharacterArcEngine":
        engine = cls()
        if "arc_tracker" in data:
            engine.arc_tracker = CharacterArcTracker.from_dict(data["arc_tracker"])
        if "foreshadowing" in data:
            engine.foreshadowing = ForeshadowingSystem.from_dict(data["foreshadowing"])
        if "pacing" in data:
            engine.pacing = PacingRhythmAnalyzer.from_dict(data["pacing"])
        if "emotional" in data:
            engine.emotional = EmotionalResonanceAmplifier.from_dict(data["emotional"])
        return engine


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("CHARACTER ARC ENGINE - TEST")
    print("=" * 60)
    
    engine = CharacterArcEngine()
    
    # Register protagonist
    engine.arc_tracker.register_character(
        name="Kira",
        flaw=CharacterFlaw.DISTRUST,
        internal_goal="Learn to rely on others",
        external_goal="Find her missing brother",
        ghost="Parents abandoned her as a child",
        lie="I can only count on myself",
        truth="Strength comes from connection, not isolation"
    )
    
    # Plant some foreshadowing
    engine.foreshadowing.plant_seed(
        "brothers_locket",
        SeedType.CHEKHOV_GUN,
        "The locket her brother gave her before disappearing",
        min_delay=5,
        max_delay=12,
        payoff_hint="Opens something, contains something, or is recognized"
    )
    
    engine.foreshadowing.plant_seed(
        "strange_symbol",
        SeedType.MYSTERY,
        "The symbol carved into the station wall that Kira's brother was researching",
        min_delay=3,
        max_delay=8,
        payoff_hint="Reveals connection to larger conspiracy"
    )
    
    # Simulate some scenes
    scene_types = [SceneType.QUIET, SceneType.DIALOGUE, SceneType.TENSION, 
                   SceneType.ACTION, SceneType.EMOTIONAL]
    
    for i, st in enumerate(scene_types):
        print(f"\n{'='*60}")
        print(f"SCENE {i+1}: {st.value.upper()}")
        print("=" * 60)
        
        guidance = engine.get_comprehensive_guidance(
            protagonist_name="Kira",
            current_scene_type=st,
            detected_emotion=EmotionalBeat.LOSS if i == 4 else None
        )
        print(guidance[:2000] + "..." if len(guidance) > 2000 else guidance)
        engine.advance_scene()
