"""
Director Agent for Starforged AI Game Master.
Manages pacing, tone, and dramatic arc across the campaign.
The Director provides hidden instructions to the Narrator - it never speaks to players.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import json
import json
import ollama
from .psych_profile import PsychologicalProfile, PsychologicalEngine
from .inner_voice import InnerVoiceSystem
from .relationship_system import RelationshipWeb
from .dream_system import DreamEngine


# ============================================================================
# Enums and Constants
# ============================================================================

class StoryAct(str, Enum):
    """Acts in the dramatic arc."""
    ACT_1_SETUP = "act_1_setup"
    ACT_2_RISING = "act_2_rising"
    ACT_3_CLIMAX = "act_3_climax"
    ACT_4_RESOLUTION = "act_4_resolution"


class Pacing(str, Enum):
    """Narrative pacing states."""
    SLOW = "slow"       # Atmospheric, introspective. 2-4 paragraphs.
    STANDARD = "standard"  # Balanced. 1-3 paragraphs.
    FAST = "fast"       # Terse, urgent. Short paragraphs.


class Tone(str, Enum):
    """Emotional tone palette."""
    OMINOUS = "ominous"       # Something is wrong. Foreshadowing. Dread.
    TENSE = "tense"           # Immediate threat. Stakes are clear.
    MELANCHOLIC = "melancholic"  # Loss echoes. Regret. Bittersweet.
    HOPEFUL = "hopeful"       # Light breaking through. Connection.
    TRIUMPHANT = "triumphant"  # Victory earned. Catharsis.
    MYSTERIOUS = "mysterious"  # Questions multiply. Unknown beckons.


# ============================================================================
# Director State
# ============================================================================

@dataclass
class DirectorState:
    """
    Tracks the dramatic state of the campaign.
    Updated after each scene to inform future pacing decisions.
    """
    current_act: StoryAct = StoryAct.ACT_1_SETUP
    recent_pacing: list[str] = field(default_factory=list)  # Last 5 pacing decisions
    active_beats: list[str] = field(default_factory=list)   # Queue of dramatic goals
    tension_level: float = 0.2  # 0.0 - 1.0
    scenes_since_breather: int = 0
    foreshadowing: list[str] = field(default_factory=list)
    moral_patterns: list[str] = field(default_factory=list)  # Track player choices
    
    def record_pacing(self, pacing: str) -> None:
        """Record a pacing decision, keeping last 5."""
        self.recent_pacing.append(pacing)
        if len(self.recent_pacing) > 5:
            self.recent_pacing.pop(0)
    
    def needs_breather(self) -> bool:
        """Check if we need to slow down after intense scenes."""
        if self.scenes_since_breather >= 3:
            if self.recent_pacing and self.recent_pacing[-1] == Pacing.FAST.value:
                return True
        return False
    
    def increment_scene(self, was_fast: bool) -> None:
        """Update scene counter."""
        if was_fast:
            self.scenes_since_breather += 1
        else:
            self.scenes_since_breather = 0
    
    def add_beat(self, beat: str) -> None:
        """Add a dramatic beat to the queue."""
        if beat not in self.active_beats:
            self.active_beats.append(beat)
    
    def consume_beat(self, beat: str) -> None:
        """Remove a beat that has been addressed."""
        if beat in self.active_beats:
            self.active_beats.remove(beat)
    
    def to_dict(self) -> dict:
        """Serialize for storage."""
        return {
            "current_act": self.current_act.value,
            "recent_pacing": self.recent_pacing,
            "active_beats": self.active_beats,
            "tension_level": self.tension_level,
            "scenes_since_breather": self.scenes_since_breather,
            "foreshadowing": self.foreshadowing,
            "moral_patterns": self.moral_patterns,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "DirectorState":
        """Deserialize from storage."""
        return cls(
            current_act=StoryAct(data.get("current_act", "act_1_setup")),
            recent_pacing=data.get("recent_pacing", []),
            active_beats=data.get("active_beats", []),
            tension_level=data.get("tension_level", 0.2),
            scenes_since_breather=data.get("scenes_since_breather", 0),
            foreshadowing=data.get("foreshadowing", []),
            moral_patterns=data.get("moral_patterns", []),
        )


# ============================================================================
# Director Plan (Output)
# ============================================================================

@dataclass
class DirectorPlan:
    """
    The Director's output - guidance for the Narrator.
    This is injected into the Narrator's context but never shown to players.
    """
    pacing: Pacing = Pacing.STANDARD
    tone: Tone = Tone.MYSTERIOUS
    beats: list[str] = field(default_factory=list)  # 1-3 target moments
    notes_for_narrator: str = ""
    subversion: str | None = None  # Psychological subversion suggestion
    inner_voices: list[dict] = field(default_factory=list) # Thoughts from the psyche
    
    def to_prompt_injection(self) -> str:
        """Format for injection into Narrator's system prompt."""
        lines = [
            "\n<director_guidance>",
            f"Pacing: {self.pacing.value}",
            f"Tone: {self.tone.value}",
        ]
        
        if self.beats:
            lines.append(f"Work toward these dramatic moments: {', '.join(self.beats)}")
        
        if self.notes_for_narrator:
            lines.append(f"Specific guidance: {self.notes_for_narrator}")

        if self.subversion:
            lines.append(f"PSYCHOLOGICAL SUBVERSION: {self.subversion}")
            lines.append("Use this to challenge or unsettle the player based on their profile.")
        
        if self.inner_voices:
            lines.append("\n[INNER PSYCHE]")
            for voice in self.inner_voices:
                lines.append(f"[{voice['aspect'].upper()}]: {voice['content']}")
            lines.append("Weave these thoughts into the narrative as internal monologue.")
        
        # Add pacing-specific instructions
        if self.pacing == Pacing.SLOW:
            lines.append("Write 2-4 paragraphs. Linger on atmosphere and sensory detail.")
            lines.append("Allow space for internal character moments and relationship building.")
        elif self.pacing == Pacing.FAST:
            lines.append("Write 1-2 short paragraphs. Terse, urgent prose.")
            lines.append("Short sentences. Immediate danger. Time pressure.")
        else:
            lines.append("Write 1-3 paragraphs. Balance description and action.")
            lines.append("Clear decision points. Forward momentum.")
        
        # Add tone-specific instructions
        tone_guidance = {
            Tone.OMINOUS: "Emphasize wrongness. Details that don't quite fit. Silence where there should be sound.",
            Tone.TENSE: "Short sentences. Immediate sensory details. Make stakes visceral.",
            Tone.MELANCHOLIC: "Longer sentences. Memory and loss. Find beauty in decay.",
            Tone.HOPEFUL: "Warmth in small details. Human connection. Light imagery.",
            Tone.TRIUMPHANT: "Earned catharsis. Physical release of tension. But not without cost.",
            Tone.MYSTERIOUS: "Questions multiply. The unknown beckons. Curiosity over fear.",
        }
        lines.append(tone_guidance.get(self.tone, ""))
        
        lines.append("</director_guidance>")
        return "\n".join(lines)


# ============================================================================
# Director System Prompt
# ============================================================================

DIRECTOR_SYSTEM_PROMPT = """You are the Director for a Starforged campaign. You never speak to the player.

Your role is to analyze the current game state and provide structured guidance to the Narrator about pacing, tone, and dramatic direction.

INPUTS YOU RECEIVE:
- world_state: Characters, locations, vows, relationships, recent events
- session_history: Summary of recent scenes and player choices
- mechanical_results: Recent dice outcomes (strong hits, misses, matches)

YOUR ANALYSIS PROCESS:
1. Assess the dramatic arc position (where are we in the story?)
2. Evaluate recent pacing (has it been relentless or slow?)
3. Identify unresolved narrative threads
4. Consider mechanical outcomes (a Miss creates complication opportunity)
5. Check vow progress (near completion = escalate stakes)

OUTPUT FORMAT (JSON only, no explanation):
{
  "current_act": "act_1_setup | act_2_rising | act_3_climax | act_4_resolution",
  "pacing": "slow | standard | fast",
  "tone": "ominous | tense | melancholic | hopeful | triumphant | mysterious",
  "beats": ["1-3 short phrases describing target dramatic moments"],
  "notes_for_narrator": "2-3 sentences of specific guidance for the next scene",
  "tension_adjustment": -0.1 to 0.2 (how much to adjust tension level)
}

PACING RULES:
- After 2+ high-tension scenes: recommend "slow" for breathing room
- Before major vow confrontations: recommend "fast" to build pressure
- During exploration/investigation: use "standard" with "mysterious" tone
- After devastating losses: use "slow" with "melancholic" tone

BEAT GENERATION:
- Tie beats to existing vows, NPCs, and world state
- Include at least one beat that threatens something the player cares about
- Include at least one beat that offers unexpected opportunity
- Foreshadow 1-2 sessions ahead

Never explain your reasoning. Output only the JSON structure."""


# ============================================================================
# Director Agent
# ============================================================================

@dataclass
class DirectorAgent:
    """
    The Director analyzes dramatic state and produces guidance for the Narrator.
    Uses LLM for complex analysis but has fallback heuristics.
    """
    model: str = "llama3.1"
    state: DirectorState = field(default_factory=DirectorState)
    psycho_engine: PsychologicalEngine = field(default_factory=PsychologicalEngine)
    inner_voice: InnerVoiceSystem = field(default_factory=InnerVoiceSystem)
    relationships: RelationshipWeb = field(default_factory=RelationshipWeb)
    dream_engine: DreamEngine = field(default_factory=DreamEngine)
    _client: ollama.Client = field(default_factory=ollama.Client, repr=False)
    
    def analyze(
        self,
        world_state: dict[str, Any],
        session_history: str,
        player_action: str = "",  # Added for profiling
        last_roll_outcome: str = "",
        vow_progress: float = 0.0,
    ) -> DirectorPlan:
        """
        Analyze current state and produce a DirectorPlan.
        
        Args:
            world_state: Current character, location, NPC states
            session_history: Summary of recent events
            last_roll_outcome: "strong_hit", "weak_hit", "miss", or ""
            vow_progress: 0.0 - 1.0 completion of current vow
        
        Returns:
            DirectorPlan with pacing, tone, and beat guidance
        """
        # 0. Update Psychological Profile if action provided
        subversion = None
        if player_action and world_state.get('psyche'):
            profile = world_state['psyche'].profile
            self.psycho_engine.evolve_from_event(profile, player_action, outcome=last_roll_outcome)
            
            # Update Relationships if an NPC ID is found in the action or context
            # (Heuristic: search for NPC IDs in the text)
            act_type = "observe" # Default action type for perception update
            for npc_id, npc in self.relationships.crew.items():
                if npc_id in player_action.lower() or npc.name.lower() in player_action.lower():
                    # Determine action type heuristically or let RelationshipWeb decide
                    # For now, let's assume "help" if outcome is good, else neutral-ish
                    act_type = "help" if last_roll_outcome == "strong_hit" else "investigate"
                    self.relationships.apply_action(act_type, npc_id, context=session_history, psych_profile=profile)
            
            # Deep Mechanics: Value Conflicts
            conflict = self.psycho_engine.detect_value_conflict(profile, player_action)
            
            # Deep Mechanics: Compulsion Tracking
            self.psycho_engine.track_compulsion(profile, player_action)
            self.psycho_engine.apply_withdrawal(profile)
            
            # Deep Mechanics: Memory Corruption (on high stress)
            if profile.stress_level > 0.8 and profile.memories:
                import random
                if random.random() < 0.3:
                    self.psycho_engine.corrupt_memory(profile)
            
            # Deep Mechanics: Social Perception Update
            self.relationships.update_perception(act_type, last_roll_outcome)
            
        # 0.5 Generate Inner Voice Commentary & Check Hijack
        # Extract profile context for inner voice
        profile_context = ""
        if world_state.get('psyche'):
            profile_context = self.psycho_engine.get_narrative_context(world_state['psyche'].profile)
            self.inner_voice.sync_with_profile(world_state['psyche'].profile)
        
        thoughts = self.inner_voice.trigger_voices(f"{session_history}\n{profile_context}")
        hijack = self.inner_voice.check_hijack()
        
        # Deep Mechanics: Dream Sequences
        dream_content = ""
        if world_state.get('psyche'):
            profile = world_state['psyche'].profile
            dream_content = self.dream_engine.generate_dream(profile, session_history)
            if not dream_content:
                dream_content = self.dream_engine.get_narrator_injection(profile)
        
        # Deep Mechanics: NPC Tells
        npc_tells = []
        if world_state.get('psyche'):
            player_emotion = world_state['psyche'].profile.current_emotion
            for npc_id in self.relationships.crew.keys():
                reaction = self.relationships.get_npc_reaction_to_emotion(npc_id, player_emotion)
                if reaction:
                    npc_tells.append(reaction)

        plan = self._apply_heuristics(last_roll_outcome, vow_progress)
        plan.subversion = subversion
        plan.inner_voices = thoughts
        
        # Inject deep mechanics context
        if dream_content:
            plan.notes_for_narrator = (plan.notes_for_narrator or "") + f"\n\n{dream_content}"
        if npc_tells:
            plan.notes_for_narrator = (plan.notes_for_narrator or "") + f"\n\n[NPC REACTIONS: {' | '.join(npc_tells)}]"
        
        # Add perception context
        perception_ctx = self.relationships.get_perception_context()
        if perception_ctx:
            plan.notes_for_narrator = (plan.notes_for_narrator or "") + f"\n\n{perception_ctx}"
        
        # HIJACK OVERRIDE
        if hijack:
            plan.notes_for_narrator = (
                f"!!! NEURAL HIJACK IN PROGRESS !!!\n"
                f"Region: {hijack['aspect']}\n"
                f"Effect: {hijack['description']}\n"
                f"INSTRUCTION: The player has NO CONTROL. Describe them involuntarily performing the action described above. "
                f"Ignore any player intent to the contrary."
            )
            plan.beats = ["The mind snaps.", "Control is lost.", f"The {hijack['aspect']} takes the wheel."]
            # Return early to prevent LLM from overriding the hijack with "sensible" plot
            return plan

        # Then try LLM analysis for richer guidance
        try:
            llm_plan = self._llm_analyze(world_state, session_history, last_roll_outcome)
            if llm_plan:
                # Merge LLM insights with heuristic plan
                plan = self._merge_plans(plan, llm_plan)
        except Exception as e:
            # Fall back to heuristics only
            import logging
            logging.getLogger("director").warning(f"LLM analysis failed: {e}")
        
        # Update state
        self.state.record_pacing(plan.pacing.value)
        self.state.increment_scene(plan.pacing == Pacing.FAST)
        
        return plan
    
    def _apply_heuristics(
        self,
        last_roll_outcome: str,
        vow_progress: float,
    ) -> DirectorPlan:
        """Apply rule-based pacing decisions."""
        pacing = Pacing.STANDARD
        tone = Tone.MYSTERIOUS
        notes = ""
        
        # Pacing heuristics
        if self.state.needs_breather():
            pacing = Pacing.SLOW
            tone = Tone.MELANCHOLIC if last_roll_outcome == "miss" else Tone.HOPEFUL
            notes = "The player needs a breather. Allow space for reflection."
        elif vow_progress > 0.8:
            pacing = Pacing.FAST
            tone = Tone.TENSE
            notes = "Vow is near completion. Escalate stakes and pressure."
        
        # Outcome-based tone adjustments
        if last_roll_outcome == "miss":
            tone = Tone.OMINOUS
            notes += " A miss creates opportunity for complication or danger."
        elif last_roll_outcome == "strong_hit":
            if pacing != Pacing.SLOW:
                tone = Tone.HOPEFUL
        
        return DirectorPlan(
            pacing=pacing,
            tone=tone,
            beats=self.state.active_beats[:3],  # Top 3 beats
            notes_for_narrator=notes.strip(),
        )
    
    def _llm_analyze(
        self,
        world_state: dict[str, Any],
        session_history: str,
        last_roll_outcome: str,
    ) -> DirectorPlan | None:
        """Use LLM for deeper dramatic analysis."""
        # Build context for LLM
        context = {
            "world_state": world_state,
            "session_history": session_history,
            "last_roll": last_roll_outcome,
            "director_state": self.state.to_dict(),
        }
        
        prompt = f"""Analyze this game state and provide Director guidance:

{json.dumps(context, indent=2, default=str)}

Remember: Output ONLY valid JSON, no explanation."""
        
        try:
            response = self._client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": DIRECTOR_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                },
            )
            
            content = response.get("message", {}).get("content", "")
            
            # Parse JSON response
            # Try to extract JSON from the response
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                data = json.loads(json_str)
                
                return DirectorPlan(
                    pacing=Pacing(data.get("pacing", "standard")),
                    tone=Tone(data.get("tone", "mysterious")),
                    beats=data.get("beats", []),
                    notes_for_narrator=data.get("notes_for_narrator", ""),
                )
        except (json.JSONDecodeError, ValueError, KeyError):
            return None
        except Exception:
            return None
        
        return None
    
    def _merge_plans(self, heuristic: DirectorPlan, llm: DirectorPlan) -> DirectorPlan:
        """Merge heuristic and LLM plans, preferring LLM for creative elements."""
        # LLM provides better beats and notes
        # Heuristics provide safety rails for pacing
        
        # If heuristics say we need a breather, respect that
        if self.state.needs_breather():
            pacing = Pacing.SLOW
        else:
            pacing = llm.pacing
        
        return DirectorPlan(
            pacing=pacing,
            tone=llm.tone,
            beats=llm.beats if llm.beats else heuristic.beats,
            notes_for_narrator=llm.notes_for_narrator or heuristic.notes_for_narrator,
            subversion=heuristic.subversion,  # Carry over subversion
            inner_voices=heuristic.inner_voices, # Carry over voices
        )
    
    def add_delayed_beat(self, beat: str, trigger_after_scenes: int = 3) -> None:
        """
        Add a beat that should trigger after a delay.
        For now, adds directly to the queue - future enhancement could
        track scene counts for delayed triggering.
        """
        self.state.add_beat(beat)
    
    def record_moral_choice(self, choice_description: str) -> None:
        """Track player's moral choices for pattern analysis."""
        self.state.moral_patterns.append(choice_description)
        # Keep last 10 choices
        if len(self.state.moral_patterns) > 10:
            self.state.moral_patterns.pop(0)
    
    def get_moral_pattern_callout(self) -> str | None:
        """
        Analyze moral patterns and return a potential callout for the narrator.
        Returns None if no clear pattern or not enough data.
        """
        if len(self.state.moral_patterns) < 4:
            return None
        
        patterns = self.state.moral_patterns[-6:]
        
        # Count moral categories
        mercy_count = sum(1 for p in patterns if any(w in p.lower() for w in ["spare", "mercy", "save", "help", "protect"]))
        violence_count = sum(1 for p in patterns if any(w in p.lower() for w in ["kill", "attack", "destroy", "fight"]))
        betrayal_count = sum(1 for p in patterns if any(w in p.lower() for w in ["betray", "lie", "deceive", "abandon"]))
        loyalty_count = sum(1 for p in patterns if any(w in p.lower() for w in ["ally", "trust", "honor", "promise"]))
        
        # Generate callout based on dominant pattern
        callouts = []
        if mercy_count >= 3:
            callouts.append("You have shown mercy repeatedly. Someone will test whether this mercy has limits.")
        elif violence_count >= 3:
            callouts.append("Blood follows you. The Forge remembers what you've done.")
        
        if betrayal_count >= 2:
            callouts.append("Your broken promises echo. Trust is hard to rebuild.")
        elif loyalty_count >= 2:
            callouts.append("Your word has weight. Others notice.")
        
        return callouts[0] if callouts else None
    
    def get_retroactive_foreshadowing(self, current_event: str) -> str | None:
        """
        When a significant event triggers, check if we can reference earlier foreshadowing.
        """
        if not self.state.foreshadowing:
            return None
        
        current_lower = current_event.lower()
        
        # Look for matching foreshadowing
        for i, foreshadow in enumerate(self.state.foreshadowing):
            foreshadow_keywords = set(foreshadow.lower().split())
            current_keywords = set(current_lower.split())
            
            # If there's keyword overlap, this might be a callback
            if len(foreshadow_keywords & current_keywords) >= 2:
                # Remove the used foreshadowing
                self.state.foreshadowing.pop(i)
                return f"You remember {foreshadow}—now it makes sense."
        
        return None
    
    def add_foreshadowing(self, hint: str) -> None:
        """Add a foreshadowing hint for potential later callback."""
        self.state.foreshadowing.append(hint)
        # Keep last 5 foreshadowing hints
        if len(self.state.foreshadowing) > 5:
            self.state.foreshadowing.pop(0)
    
    def get_vow_complication_suggestion(self, vow_name: str, vow_progress: float) -> str | None:
        """
        Suggest a complication based on vow phase.
        These are injected into Director's notes for narrator.
        """
        if vow_progress < 0.25:
            # Establishing phase
            return f"Establish what's truly at stake with '{vow_name}'. Show why this vow matters personally."
        elif vow_progress < 0.5:
            # Developing phase
            complications = [
                f"An ally's needs conflict with progress on '{vow_name}'.",
                f"A shortcut presents itself for '{vow_name}'—but at what ethical cost?",
                f"Someone from the past complicates '{vow_name}'.",
            ]
            import random
            return random.choice(complications)
        elif vow_progress < 0.75:
            # Escalating phase
            complications = [
                f"The true scope of '{vow_name}' reveals itself—and it's worse than expected.",
                f"Someone must be sacrificed to fulfill '{vow_name}'.",
                f"Fulfilling '{vow_name}' will break another promise.",
            ]
            import random
            return random.choice(complications)
        elif vow_progress < 1.0:
            # Approaching climax
            return f"The final obstacle to '{vow_name}' is here. There's no turning back. What must be paid?"
        else:
            return None


# ============================================================================
# Convenience Functions
# ============================================================================

def create_director(model: str = "llama3.1") -> DirectorAgent:
    """Create a new Director with default state."""
    return DirectorAgent(model=model)


def analyze_for_narrator(
    director: DirectorAgent,
    character_name: str,
    location: str,
    vows: list[dict],
    session_summary: str,
    player_action: str = "",
    last_roll: str = "",
) -> str:
    """
    Convenience function to get Director guidance as a prompt injection string.
    
    Args:
        director: The DirectorAgent instance
        character_name: PC name
        location: Current location
        vows: List of active vows with progress
        session_summary: Recent events summary
        last_roll: The last roll outcome
    
    Returns:
        String to inject into Narrator's prompt
    """
    # Calculate vow progress (use highest progress vow)
    vow_progress = 0.0
    if vows:
        vow_progress = max(v.get("ticks", 0) / 40.0 for v in vows)
    
    world_state = {
        "character": character_name,
        "location": location,
        "active_vows": vows,
    }
    
    plan = director.analyze(
        world_state=world_state,
        session_history=session_summary,
        player_action=player_action,
        last_roll_outcome=last_roll,
        vow_progress=vow_progress,
    )
    
    return plan.to_prompt_injection()
