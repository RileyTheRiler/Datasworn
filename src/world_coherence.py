"""
World Coherence & Session Systems - Narrative Consistency and Player Experience

This module provides systems for maintaining world consistency, validating
player agency, generating narrative surprises, and creating session recaps.

Key Systems:
1. World State Coherence - Track world changes and ensure consistency
2. Player Agency Validator - Ensure choices matter and have consequences
3. Narrative Surprise Engine - Generate unexpected but earned twists
4. Session Recap Generator - Create "Previously on..." summaries
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Set, Tuple, Any
import random
from collections import defaultdict


# =============================================================================
# WORLD STATE COHERENCE
# =============================================================================

class WorldFactType(Enum):
    """Types of world facts to track."""
    LOCATION_STATE = "location"        # State of a place
    NPC_STATUS = "npc_status"          # Alive, dead, disposition
    OBJECT_POSITION = "object"         # Where something is
    FACTION_RELATION = "faction"       # Political state
    TECHNOLOGY_STATE = "tech"          # What works, what's broken
    RESOURCE_LEVEL = "resource"        # Supplies, power, etc.
    TIME_SENSITIVE = "temporal"        # Things that change with time
    PLAYER_REPUTATION = "reputation"   # How player is known


@dataclass
class WorldFact:
    """A discrete fact about the world state."""
    fact_type: WorldFactType
    subject: str             # What/who the fact is about
    state: str               # Current state
    last_updated: int        # Scene number
    previous_states: List[Tuple[int, str]] = field(default_factory=list)
    contradiction_risk: float = 0.0  # How likely narrator might forget


@dataclass
class WorldStateCoherence:
    """
    Tracks world changes and ensures narrative consistency.
    
    Prevents "The door was locked" when it was opened 3 scenes ago.
    Remembers who's dead, what's broken, and what's changed.
    """
    
    facts: Dict[str, WorldFact] = field(default_factory=dict)
    current_scene: int = 0
    
    # High-priority facts to always include
    critical_fact_types: Set[WorldFactType] = field(default_factory=lambda: {
        WorldFactType.NPC_STATUS,
        WorldFactType.LOCATION_STATE,
        WorldFactType.PLAYER_REPUTATION
    })
    
    def record_fact(self, fact_type: WorldFactType, subject: str, state: str):
        """Record or update a world fact."""
        key = f"{fact_type.value}:{subject}"
        
        if key in self.facts:
            # Update existing fact
            old_fact = self.facts[key]
            old_fact.previous_states.append((old_fact.last_updated, old_fact.state))
            old_fact.state = state
            old_fact.last_updated = self.current_scene
            # Keep only last 5 states
            if len(old_fact.previous_states) > 5:
                old_fact.previous_states = old_fact.previous_states[-5:]
        else:
            # New fact
            self.facts[key] = WorldFact(
                fact_type=fact_type,
                subject=subject,
                state=state,
                last_updated=self.current_scene
            )
    
    def get_fact(self, fact_type: WorldFactType, subject: str) -> Optional[WorldFact]:
        """Retrieve a specific fact."""
        key = f"{fact_type.value}:{subject}"
        return self.facts.get(key)
    
    def get_stale_facts(self, threshold: int = 5) -> List[WorldFact]:
        """Get facts that haven't been referenced recently (risk of contradiction)."""
        stale = []
        for fact in self.facts.values():
            if self.current_scene - fact.last_updated >= threshold:
                fact.contradiction_risk = min(1.0, (self.current_scene - fact.last_updated) / 10)
                stale.append(fact)
        return sorted(stale, key=lambda f: f.contradiction_risk, reverse=True)
    
    def get_coherence_context(self, location: str = "", 
                               active_npcs: List[str] = None) -> str:
        """Generate world coherence reminders for narrator."""
        reminders = []
        
        # Always include critical NPCs status
        if active_npcs:
            for npc in active_npcs:
                fact = self.get_fact(WorldFactType.NPC_STATUS, npc)
                if fact:
                    reminders.append(f"  - {npc}: {fact.state}")
        
        # Include current location state
        if location:
            loc_fact = self.get_fact(WorldFactType.LOCATION_STATE, location)
            if loc_fact:
                reminders.append(f"  - {location}: {loc_fact.state}")
        
        # Include stale facts that might be contradicted
        stale = self.get_stale_facts()[:3]
        if stale:
            reminders.append("\n  STALE (high contradiction risk):")
            for fact in stale:
                reminders.append(f"  ⚠️ {fact.subject}: {fact.state} (not referenced for {self.current_scene - fact.last_updated} scenes)")
        
        # Get recent changes
        recent_changes = []
        for fact in self.facts.values():
            if fact.previous_states and self.current_scene - fact.last_updated <= 3:
                old = fact.previous_states[-1][1]
                recent_changes.append(f"  - {fact.subject}: {old} → {fact.state}")
        
        if recent_changes:
            reminders.append("\n  RECENT CHANGES:")
            reminders.extend(recent_changes[:5])
        
        if not reminders:
            return ""
        
        return f"""<world_coherence>
WORLD STATE REMINDERS:
{chr(10).join(reminders)}

COHERENCE RULES:
  - Dead NPCs stay dead (unless resurrection is established)
  - Broken things stay broken (unless fixed on-screen)
  - Revealed secrets can't be un-revealed
  - Distances/travel times must be consistent
</world_coherence>"""
    
    def advance_scene(self):
        """Move to next scene."""
        self.current_scene += 1
    
    def to_dict(self) -> dict:
        return {
            "facts": {
                k: {
                    "fact_type": f.fact_type.value,
                    "subject": f.subject,
                    "state": f.state,
                    "last_updated": f.last_updated,
                    "previous_states": f.previous_states,
                    "contradiction_risk": f.contradiction_risk
                } for k, f in self.facts.items()
            },
            "current_scene": self.current_scene
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "WorldStateCoherence":
        coherence = cls()
        coherence.current_scene = data.get("current_scene", 0)
        
        for k, f in data.get("facts", {}).items():
            coherence.facts[k] = WorldFact(
                fact_type=WorldFactType(f["fact_type"]),
                subject=f["subject"],
                state=f["state"],
                last_updated=f["last_updated"],
                previous_states=f.get("previous_states", []),
                contradiction_risk=f.get("contradiction_risk", 0.0)
            )
        return coherence


# =============================================================================
# PLAYER AGENCY VALIDATOR
# =============================================================================

class ChoiceType(Enum):
    """Types of player choices."""
    DIALOGUE = "dialogue"          # What they said
    ACTION = "action"              # What they did
    STRATEGIC = "strategic"        # Planning decisions
    MORAL = "moral"                # Ethical choices
    RESOURCE = "resource"          # Spending/saving
    RELATIONSHIP = "relationship"  # Who to trust/ally with
    PATH = "path"                  # Which way to go


@dataclass
class PlayerChoice:
    """A recorded player choice."""
    choice_type: ChoiceType
    description: str
    scene: int
    alternatives: List[str] = field(default_factory=list)  # What they didn't choose
    consequence_delivered: bool = False
    consequence_description: str = ""
    weight: float = 1.0  # How significant (0.1 minor, 1.0 major)


@dataclass
class PlayerAgencyValidator:
    """
    Ensures player choices matter and have consequences.
    
    Tracks what players chose, what they didn't choose,
    and ensures meaningful consequences emerge from decisions.
    """
    
    choices: List[PlayerChoice] = field(default_factory=list)
    pending_consequences: List[str] = field(default_factory=list)
    current_scene: int = 0
    
    # Consequence patterns
    CONSEQUENCE_PATTERNS: Dict[ChoiceType, List[str]] = field(default_factory=lambda: {
        ChoiceType.DIALOGUE: [
            "NPC remembers what was said and references it",
            "Information revealed/concealed shapes NPC behavior",
            "Tone of conversation affects relationship"
        ],
        ChoiceType.ACTION: [
            "Direct physical consequence of action",
            "Witnesses remember and react",
            "Resources/options changed by action"
        ],
        ChoiceType.MORAL: [
            "Character's reputation affected",
            "Internal conflict/guilt emerges",
            "Others judge them by this choice"
        ],
        ChoiceType.STRATEGIC: [
            "Plan succeeds or fails based on choice",
            "Unforeseen complication from approach",
            "Alternative path closed off"
        ],
        ChoiceType.RELATIONSHIP: [
            "Ally becomes available/unavailable",
            "Trusted character has information/resources",
            "Betrayal/loyalty callback to trust given"
        ]
    })
    
    def record_choice(self, choice_type: ChoiceType, description: str,
                      alternatives: List[str] = None, weight: float = 1.0):
        """Record a player choice."""
        choice = PlayerChoice(
            choice_type=choice_type,
            description=description,
            scene=self.current_scene,
            alternatives=alternatives or [],
            weight=weight
        )
        self.choices.append(choice)
        
        # Queue consequence reminder for later
        if weight >= 0.5:
            patterns = self.CONSEQUENCE_PATTERNS.get(choice_type, [])
            if patterns:
                self.pending_consequences.append(
                    f"Choice '{description}' ({choice_type.value}) needs consequence"
                )
    
    def mark_consequence_delivered(self, choice_description: str, 
                                     consequence: str):
        """Mark that a choice has received its consequence."""
        for choice in self.choices:
            if choice.description == choice_description:
                choice.consequence_delivered = True
                choice.consequence_description = consequence
                # Remove from pending
                self.pending_consequences = [
                    p for p in self.pending_consequences 
                    if choice_description not in p
                ]
                break
    
    def get_unconsequenced_choices(self) -> List[PlayerChoice]:
        """Get significant choices that haven't had consequences yet."""
        unconsequenced = []
        for choice in self.choices:
            if not choice.consequence_delivered and choice.weight >= 0.5:
                # Check if enough time has passed for consequence
                scenes_since = self.current_scene - choice.scene
                if scenes_since >= 2:  # Give some breathing room
                    unconsequenced.append(choice)
        
        return sorted(unconsequenced, key=lambda c: c.weight, reverse=True)
    
    def get_agency_guidance(self) -> str:
        """Generate player agency validation guidance."""
        unconsequenced = self.get_unconsequenced_choices()[:3]
        
        if not unconsequenced:
            return """<player_agency>
All significant choices have received consequences. Good!

AGENCY PRINCIPLES:
  - Every choice should matter (even if not immediately)
  - Show the road not taken (glimpses of what would have happened)
  - Respect player decisions (don't undo their choices narratively)
</player_agency>"""
        
        consequence_suggestions = []
        for choice in unconsequenced:
            patterns = self.CONSEQUENCE_PATTERNS.get(choice.choice_type, [])
            pattern = random.choice(patterns) if patterns else "Natural consequence"
            scenes_ago = self.current_scene - choice.scene
            
            consequence_suggestions.append(f"""  [{choice.choice_type.value}] (scene {choice.scene}, {scenes_ago} ago)
    Choice: "{choice.description}"
    Alternatives rejected: {', '.join(choice.alternatives) if choice.alternatives else 'N/A'}
    Consequence pattern: {pattern}""")
        
        return f"""<player_agency>
⚠️ CHOICES AWAITING CONSEQUENCES:

{chr(10).join(consequence_suggestions)}

AGENCY VALIDATION:
  - Choices without consequences = meaningless
  - Reference what they DIDN'T choose occasionally
  - Present moment should connect to past decisions
  - World should feel responsive to player actions
</player_agency>"""
    
    def to_dict(self) -> dict:
        return {
            "choices": [
                {
                    "choice_type": c.choice_type.value,
                    "description": c.description,
                    "scene": c.scene,
                    "alternatives": c.alternatives,
                    "consequence_delivered": c.consequence_delivered,
                    "consequence_description": c.consequence_description,
                    "weight": c.weight
                } for c in self.choices[-30:]  # Keep last 30
            ],
            "pending_consequences": self.pending_consequences,
            "current_scene": self.current_scene
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "PlayerAgencyValidator":
        validator = cls()
        validator.current_scene = data.get("current_scene", 0)
        validator.pending_consequences = data.get("pending_consequences", [])
        
        for c in data.get("choices", []):
            validator.choices.append(PlayerChoice(
                choice_type=ChoiceType(c["choice_type"]),
                description=c["description"],
                scene=c["scene"],
                alternatives=c.get("alternatives", []),
                consequence_delivered=c.get("consequence_delivered", False),
                consequence_description=c.get("consequence_description", ""),
                weight=c.get("weight", 1.0)
            ))
        return validator


# =============================================================================
# NARRATIVE SURPRISE ENGINE
# =============================================================================

class SurpriseType(Enum):
    """Types of narrative surprises."""
    REVERSAL = "reversal"           # Situation is opposite of assumed
    REVELATION = "revelation"        # Hidden truth exposed
    RETURN = "return"               # Someone/something thought gone
    BETRAYAL = "betrayal"           # Trusted figure turns
    ESCALATION = "escalation"       # Stakes suddenly much higher
    CONNECTION = "connection"       # Unrelated things linked
    INVERSION = "inversion"         # Hero becomes villain or vice versa
    RECOGNITION = "recognition"     # True identity revealed


@dataclass
class SurpriseElement:
    """A potential surprise element being set up."""
    surprise_type: SurpriseType
    setup: str                      # What's been established
    hidden_truth: str               # What's actually true
    plant_scene: int
    reveal_window: Tuple[int, int]  # When to reveal (min, max)
    clues_planted: List[str] = field(default_factory=list)
    is_revealed: bool = False


@dataclass  
class NarrativeSurpriseEngine:
    """
    Generates unexpected but earned twists.
    
    Every surprise must be:
    - Set up in advance (not random)
    - Clued fairly (retrospectively inevitable)
    - Emotionally resonant (not just clever)
    """
    
    potential_surprises: Dict[str, SurpriseElement] = field(default_factory=dict)
    revealed_surprises: List[str] = field(default_factory=list)
    current_scene: int = 0
    
    # Surprise templates
    SURPRISE_TEMPLATES: Dict[SurpriseType, List[Dict[str, str]]] = field(default_factory=lambda: {
        SurpriseType.REVERSAL: [
            {"setup": "The enemy hunting them", "hidden": "Is actually trying to protect them"},
            {"setup": "The safe haven they're seeking", "hidden": "Is the source of the threat"},
            {"setup": "The object they're protecting", "hidden": "Is worthless—they themselves are valuable"}
        ],
        SurpriseType.REVELATION: [
            {"setup": "The mysterious benefactor", "hidden": "Has personal connection to protagonist"},
            {"setup": "The accident that started everything", "hidden": "Was deliberately caused"},
            {"setup": "The protagonist's trusted memory", "hidden": "Has been altered/is false"}
        ],
        SurpriseType.BETRAYAL: [
            {"setup": "The loyal ally who's always helped", "hidden": "Has been reporting to the enemy"},
            {"setup": "The cause they're fighting for", "hidden": "Is a manipulation by the true enemy"},
            {"setup": "The rival who opposes them", "hidden": "Was right all along"}
        ],
        SurpriseType.CONNECTION: [
            {"setup": "Two seemingly unrelated events", "hidden": "Share the same mastermind"},
            {"setup": "The stranger they met early", "hidden": "Is connected to their past/goal"},
            {"setup": "The minor detail mentioned in passing", "hidden": "Is the key to everything"}
        ]
    })
    
    def plan_surprise(self, surprise_id: str, surprise_type: SurpriseType,
                       setup: str, hidden_truth: str,
                       min_delay: int = 5, max_delay: int = 15):
        """Plan a future surprise with setup and hidden truth."""
        self.potential_surprises[surprise_id] = SurpriseElement(
            surprise_type=surprise_type,
            setup=setup,
            hidden_truth=hidden_truth,
            plant_scene=self.current_scene,
            reveal_window=(self.current_scene + min_delay, self.current_scene + max_delay)
        )
    
    def add_clue(self, surprise_id: str, clue: str):
        """Add a fairly-planted clue to a surprise."""
        if surprise_id in self.potential_surprises:
            self.potential_surprises[surprise_id].clues_planted.append(clue)
    
    def reveal_surprise(self, surprise_id: str):
        """Mark a surprise as revealed."""
        if surprise_id in self.potential_surprises:
            self.potential_surprises[surprise_id].is_revealed = True
            self.revealed_surprises.append(surprise_id)
    
    def get_ripe_surprises(self) -> List[Tuple[str, SurpriseElement]]:
        """Get surprises ready for reveal."""
        ripe = []
        for sid, surprise in self.potential_surprises.items():
            if surprise.is_revealed:
                continue
            min_scene, max_scene = surprise.reveal_window
            if self.current_scene >= min_scene:
                ripe.append((sid, surprise))
        
        return sorted(ripe, key=lambda x: x[1].reveal_window[1])
    
    def get_surprise_guidance(self) -> str:
        """Generate surprise planning/reveal guidance."""
        ripe = self.get_ripe_surprises()
        
        # Suggestions for new surprises
        new_suggestions = []
        if len(self.potential_surprises) < 3:
            template_type = random.choice(list(self.SURPRISE_TEMPLATES.keys()))
            templates = self.SURPRISE_TEMPLATES[template_type]
            template = random.choice(templates)
            new_suggestions.append(f"""CONSIDER PLANTING ({template_type.value}):
  Setup: "{template['setup']}"
  Hidden: "{template['hidden']}"
  Plant clues early. Fair play matters.""")
        
        # Ripe surprises
        ripe_text = ""
        if ripe:
            ripe_items = []
            for sid, surprise in ripe[:2]:
                clues = f"Clues planted: {len(surprise.clues_planted)}" if surprise.clues_planted else "⚠️ NO CLUES YET"
                overdue = "🔴 OVERDUE" if self.current_scene > surprise.reveal_window[1] else ""
                ripe_items.append(f"""  [{surprise.surprise_type.value}] {overdue}
    Setup: "{surprise.setup}"
    Truth: "{surprise.hidden_truth}"
    {clues}""")
            
            ripe_text = f"""SURPRISES READY FOR REVEAL:
{chr(10).join(ripe_items)}"""
        
        return f"""<surprise_engine>
{ripe_text if ripe_text else "No surprises currently ripe for reveal."}

{chr(10).join(new_suggestions) if new_suggestions else ""}

THE FAIR PLAY DOCTRINE:
  - Every twist must be clued (at least 3 clues before reveal)
  - Clues should be visible in retrospect, invisible on first read
  - Emotional truth matters more than plot cleverness
  - Best surprises recontextualize—don't just shock

CLUE HIDING TECHNIQUES:
  - Bury in lists (the important item among mundane ones)
  - Distract with action (clue during tense moment)
  - Character dismisses it (reader follows the dismissal)
  - True meaning disguised (sounds like something else)
</surprise_engine>"""
    
    def to_dict(self) -> dict:
        return {
            "potential_surprises": {
                sid: {
                    "surprise_type": s.surprise_type.value,
                    "setup": s.setup,
                    "hidden_truth": s.hidden_truth,
                    "plant_scene": s.plant_scene,
                    "reveal_window": s.reveal_window,
                    "clues_planted": s.clues_planted,
                    "is_revealed": s.is_revealed
                } for sid, s in self.potential_surprises.items()
            },
            "revealed_surprises": self.revealed_surprises,
            "current_scene": self.current_scene
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "NarrativeSurpriseEngine":
        engine = cls()
        engine.current_scene = data.get("current_scene", 0)
        engine.revealed_surprises = data.get("revealed_surprises", [])
        
        for sid, s in data.get("potential_surprises", {}).items():
            engine.potential_surprises[sid] = SurpriseElement(
                surprise_type=SurpriseType(s["surprise_type"]),
                setup=s["setup"],
                hidden_truth=s["hidden_truth"],
                plant_scene=s["plant_scene"],
                reveal_window=tuple(s["reveal_window"]),
                clues_planted=s.get("clues_planted", []),
                is_revealed=s.get("is_revealed", False)
            )
        return engine


# =============================================================================
# SESSION RECAP GENERATOR
# =============================================================================

class SceneMemory:
    """A summarized memory of a scene."""
    def __init__(self, scene_num: int, summary: str, 
                 key_events: List[str] = None,
                 emotional_high: str = "",
                 characters_involved: List[str] = None):
        self.scene_num = scene_num
        self.summary = summary
        self.key_events = key_events or []
        self.emotional_high = emotional_high
        self.characters_involved = characters_involved or []


@dataclass
class SessionRecapGenerator:
    """
    Creates "Previously on..." summaries for session continuity.
    
    Helps players remember what happened and sets up
    returning to a story after time away.
    """
    
    scene_memories: List[SceneMemory] = field(default_factory=list)
    session_boundaries: List[int] = field(default_factory=list)  # Scene nums where sessions ended
    current_scene: int = 0
    
    # Templates for different recap styles
    RECAP_TEMPLATES: Dict[str, str] = field(default_factory=lambda: {
        "dramatic": """PREVIOUSLY...
{events}

AND NOW, THE STORY CONTINUES...""",
        "concise": """LAST TIME:
{events}

WHERE WE LEFT OFF: {cliffhanger}""",
        "narrative": """When last we saw {protagonist}...
{events}

Now, {transition}""",
        "questions": """UNANSWERED QUESTIONS:
{questions}

RECENT DEVELOPMENTS:
{events}"""
    })
    
    def record_scene(self, summary: str, key_events: List[str] = None,
                      emotional_high: str = "", characters: List[str] = None):
        """Record a scene for future recaps."""
        memory = SceneMemory(
            scene_num=self.current_scene,
            summary=summary,
            key_events=key_events or [],
            emotional_high=emotional_high,
            characters_involved=characters or []
        )
        self.scene_memories.append(memory)
        self.current_scene += 1
    
    def mark_session_end(self):
        """Mark current position as session boundary."""
        self.session_boundaries.append(self.current_scene)
    
    def generate_recap(self, style: str = "dramatic", 
                        scenes_back: int = 5,
                        protagonist: str = "our hero") -> str:
        """Generate a session recap."""
        if not self.scene_memories:
            return "No previous events to recap."
        
        recent = self.scene_memories[-scenes_back:]
        
        # Compile events
        events = []
        for memory in recent:
            if memory.key_events:
                events.extend(memory.key_events)
            else:
                events.append(memory.summary)
        
        events_text = "\n".join([f"  • {e}" for e in events[:7]])
        
        # Get cliffhanger (last emotional high or event)
        cliffhanger = ""
        if recent:
            last = recent[-1]
            cliffhanger = last.emotional_high or last.summary
        
        # Generate based on template
        template = self.RECAP_TEMPLATES.get(style, self.RECAP_TEMPLATES["dramatic"])
        
        return template.format(
            events=events_text,
            cliffhanger=cliffhanger,
            protagonist=protagonist,
            transition="the situation grows more complex...",
            questions="• Who can be trusted?\n• What waits in the darkness?\n• Will they find what they seek?"
        )
    
    def get_key_threads(self) -> List[str]:
        """Get ongoing story threads that need resolution."""
        threads = set()
        
        for memory in self.scene_memories[-10:]:
            for event in memory.key_events:
                # Simple heuristic: events with "?" or unresolved language
                if any(word in event.lower() for word in 
                       ["discovered", "revealed", "promised", "threatened", "warned", "searching"]):
                    threads.add(event)
        
        return list(threads)[:5]
    
    def get_session_context(self) -> str:
        """Generate session continuity context for narrator."""
        if not self.scene_memories:
            return ""
        
        # Recent summary
        recent = self.scene_memories[-3:]
        recent_text = "\n".join([f"  Scene {m.scene_num}: {m.summary}" for m in recent])
        
        # Ongoing threads
        threads = self.get_key_threads()
        threads_text = "\n".join([f"  • {t}" for t in threads]) if threads else "  (No major threads identified)"
        
        # Character tracker
        recent_chars = set()
        for m in self.scene_memories[-5:]:
            recent_chars.update(m.characters_involved)
        chars_text = ", ".join(recent_chars) if recent_chars else "None tracked"
        
        return f"""<session_continuity>
RECENT SCENES:
{recent_text}

ONGOING THREADS:
{threads_text}

RECENT CHARACTERS: {chars_text}

CONTINUITY CHECKLIST:
  ✓ Reference recent events naturally
  ✓ Maintain character voice/behavior consistency
  ✓ Honor promises/threats made earlier
  ✓ Progress or complicate ongoing threads
</session_continuity>"""
    
    def to_dict(self) -> dict:
        return {
            "scene_memories": [
                {
                    "scene_num": m.scene_num,
                    "summary": m.summary,
                    "key_events": m.key_events,
                    "emotional_high": m.emotional_high,
                    "characters_involved": m.characters_involved
                } for m in self.scene_memories[-30:]  # Keep last 30
            ],
            "session_boundaries": self.session_boundaries,
            "current_scene": self.current_scene
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "SessionRecapGenerator":
        generator = cls()
        generator.current_scene = data.get("current_scene", 0)
        generator.session_boundaries = data.get("session_boundaries", [])
        
        for m in data.get("scene_memories", []):
            generator.scene_memories.append(SceneMemory(
                scene_num=m["scene_num"],
                summary=m["summary"],
                key_events=m.get("key_events", []),
                emotional_high=m.get("emotional_high", ""),
                characters_involved=m.get("characters_involved", [])
            ))
        return generator


# =============================================================================
# MASTER WORLD COHERENCE ENGINE
# =============================================================================

@dataclass
class WorldCoherenceEngine:
    """Master engine coordinating all world coherence and session systems."""
    
    world_state: WorldStateCoherence = field(default_factory=WorldStateCoherence)
    agency: PlayerAgencyValidator = field(default_factory=PlayerAgencyValidator)
    surprises: NarrativeSurpriseEngine = field(default_factory=NarrativeSurpriseEngine)
    session: SessionRecapGenerator = field(default_factory=SessionRecapGenerator)
    
    def get_comprehensive_guidance(
        self,
        location: str = "",
        active_npcs: List[str] = None,
        is_session_start: bool = False,
        protagonist: str = ""
    ) -> str:
        """Generate comprehensive world coherence guidance."""
        
        sections = []
        
        # Session recap if returning
        if is_session_start and self.session.scene_memories:
            recap = self.session.generate_recap(protagonist=protagonist)
            sections.append(f"<session_recap>\n{recap}\n</session_recap>")
        
        # World state coherence
        coherence = self.world_state.get_coherence_context(
            location=location,
            active_npcs=active_npcs or []
        )
        if coherence:
            sections.append(coherence)
        
        # Player agency
        agency_guidance = self.agency.get_agency_guidance()
        if agency_guidance:
            sections.append(agency_guidance)
        
        # Surprise engine
        surprise_guidance = self.surprises.get_surprise_guidance()
        if surprise_guidance:
            sections.append(surprise_guidance)
        
        # Session continuity (always)
        session_context = self.session.get_session_context()
        if session_context:
            sections.append(session_context)
        
        if not sections:
            return ""
        
        return f"""
<world_coherence_systems>
=== WORLD COHERENCE & SESSION GUIDANCE ===
{chr(10).join(sections)}
</world_coherence_systems>
"""
    
    def advance_scene(self):
        """Move all systems to next scene."""
        self.world_state.advance_scene()
        self.agency.current_scene += 1
        self.surprises.current_scene += 1
    
    def to_dict(self) -> dict:
        return {
            "world_state": self.world_state.to_dict(),
            "agency": self.agency.to_dict(),
            "surprises": self.surprises.to_dict(),
            "session": self.session.to_dict()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "WorldCoherenceEngine":
        engine = cls()
        if "world_state" in data:
            engine.world_state = WorldStateCoherence.from_dict(data["world_state"])
        if "agency" in data:
            engine.agency = PlayerAgencyValidator.from_dict(data["agency"])
        if "surprises" in data:
            engine.surprises = NarrativeSurpriseEngine.from_dict(data["surprises"])
        if "session" in data:
            engine.session = SessionRecapGenerator.from_dict(data["session"])
        return engine


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("WORLD COHERENCE ENGINE - TEST")
    print("=" * 60)
    
    engine = WorldCoherenceEngine()
    
    # Set up some world facts
    engine.world_state.record_fact(WorldFactType.NPC_STATUS, "Captain Torres", "Alive, suspicious of player")
    engine.world_state.record_fact(WorldFactType.LOCATION_STATE, "Cargo Bay Alpha", "Power offline, partial vacuum")
    engine.world_state.record_fact(WorldFactType.OBJECT_POSITION, "Access Keycard", "In player's possession")
    
    # Record some player choices
    engine.agency.record_choice(
        ChoiceType.MORAL,
        "Lied to Torres about mission purpose",
        alternatives=["Told the truth", "Refused to answer"],
        weight=0.8
    )
    
    # Plan a surprise
    engine.surprises.plan_surprise(
        "torres_secret",
        SurpriseType.REVELATION,
        setup="Torres's hostility toward player",
        hidden_truth="Torres knows the player's secret identity",
        min_delay=3,
        max_delay=8
    )
    
    # Record some scene memories
    engine.session.record_scene(
        "Player arrived at Station Omega under false pretenses",
        key_events=["Received mysterious message", "Lied to Torres"],
        characters=["Torres", "Docking Officer"]
    )
    
    # Advance time
    for _ in range(3):
        engine.advance_scene()
    
    print("\n--- COMPREHENSIVE GUIDANCE ---")
    guidance = engine.get_comprehensive_guidance(
        location="Cargo Bay Alpha",
        active_npcs=["Torres"],
        protagonist="the operative"
    )
    print(guidance[:3000] + "..." if len(guidance) > 3000 else guidance)
