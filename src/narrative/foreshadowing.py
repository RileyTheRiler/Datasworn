"""
Foreshadowing System for Starforged AI Game Master.
Plants seeds (Environmental, Dialogue, Symbolic) based on player archetype and progression.
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field
import random

from src.character_identity import WoundType

class SeedType(str, Enum):
    ENVIRONMENTAL = "environmental"
    DIALOGUE = "dialogue"
    SYMBOLIC = "symbolic"

class GamePhase(str, Enum):
    AMBIENT = "ambient"      # 0-25%
    TARGETED = "targeted"    # 25-60%
    CONVERGENCE = "convergence" # 60-85%
    REVELATION = "revelation"   # 85%+

@dataclass
class ForeshadowingSeed:
    content: str
    seed_type: SeedType
    archetype: WoundType
    location: Optional[str] = None
    npc: Optional[str] = None
    payoff: Optional[str] = None
    phase: GamePhase = GamePhase.AMBIENT

@dataclass
class ForeshadowingEngine:
    seeds: List[ForeshadowingSeed] = field(default_factory=list)
    planted_seeds: List[ForeshadowingSeed] = field(default_factory=list)
    
    def __post_init__(self):
        self._initialize_seeds()

    def _initialize_seeds(self):
        # THE CONTROLLER
        self.seeds.extend([
            # Environmental
            ForeshadowingSeed("Navigation charts with obsessive annotations—the captain's.", SeedType.ENVIRONMENTAL, WoundType.CONTROLLER, location="Bridge", payoff="Captain was also a controller; couldn't accept uncertainty", phase=GamePhase.AMBIENT),
            ForeshadowingSeed("Journal entry: 'Tried to control the outcome. Should have let it breathe.'", SeedType.ENVIRONMENTAL, WoundType.CONTROLLER, location="Captain's Quarters", payoff="Mirror to player's approach", phase=GamePhase.TARGETED),
            ForeshadowingSeed("A system labeled 'Manual Override'—used too often, now broken.", SeedType.ENVIRONMENTAL, WoundType.CONTROLLER, location="Engineering", payoff="Over-control damages systems", phase=GamePhase.TARGETED),
            ForeshadowingSeed("Broken lock—forced open, not picked.", SeedType.ENVIRONMENTAL, WoundType.CONTROLLER, location="Cargo Bay", payoff="Force doesn't work on everything", phase=GamePhase.CONVERGENCE),
            
            # Dialogue
            ForeshadowingSeed("'The captain always needed to know everything. Even things that didn't concern him.'", SeedType.DIALOGUE, WoundType.CONTROLLER, npc="Torres", payoff="'You remind me of him. The need to know.'", phase=GamePhase.AMBIENT),
            ForeshadowingSeed("'You can't control addiction. You can only... I don't know. Accept it.'", SeedType.DIALOGUE, WoundType.CONTROLLER, npc="Kai", payoff="'You couldn't accept it either, could you?'", phase=GamePhase.TARGETED),
            ForeshadowingSeed("'My mom tried to control everything. It didn't work.'", SeedType.DIALOGUE, WoundType.CONTROLLER, npc="Ember", payoff="'You're doing the thing. The thing my mom did.'", phase=GamePhase.TARGETED),
            ForeshadowingSeed("'In medicine, you learn—some things you can't fix. You can only be present.'", SeedType.DIALOGUE, WoundType.CONTROLLER, npc="Okonkwo", payoff="'You never learned that, did you?'", phase=GamePhase.CONVERGENCE),
            
            # Symbolic
            ForeshadowingSeed("Recurring Image: Hands gripping controls, tools, objects—always tight, white-knuckled.", SeedType.SYMBOLIC, WoundType.CONTROLLER, phase=GamePhase.AMBIENT),
            ForeshadowingSeed("Weather/Environment: Storms, turbulence, systems malfunctioning outside player control.", SeedType.SYMBOLIC, WoundType.CONTROLLER, phase=GamePhase.TARGETED),
            ForeshadowingSeed("Sound: Alarms that can't be silenced; static on comms.", SeedType.SYMBOLIC, WoundType.CONTROLLER, phase=GamePhase.CONVERGENCE),
        ])

        # THE JUDGE
        self.seeds.extend([
            # Environmental
            ForeshadowingSeed("Old case files—some marked 'GUILTY,' some marked 'COMPLICATED'.", SeedType.ENVIRONMENTAL, WoundType.JUDGE, location="Brig", payoff="Not everything is binary", phase=GamePhase.AMBIENT),
            ForeshadowingSeed("Photo of captain with someone in a prison uniform—smiling.", SeedType.ENVIRONMENTAL, WoundType.JUDGE, location="Captain's Quarters", payoff="He forgave someone once", phase=GamePhase.TARGETED),
            ForeshadowingSeed("Chart showing 'Stages of Recovery'—for the captain's illness.", SeedType.ENVIRONMENTAL, WoundType.JUDGE, location="Med Bay", payoff="Dying changes moral calculus", phase=GamePhase.TARGETED),
            ForeshadowingSeed("Yuki's hidden belongings—corporate ID with a different name.", SeedType.ENVIRONMENTAL, WoundType.JUDGE, location="Crew Quarters", payoff="She was someone else once", phase=GamePhase.CONVERGENCE),
            
            # Dialogue
            ForeshadowingSeed("'We've all done things. Some of us got caught. Some didn't.'", SeedType.DIALOGUE, WoundType.JUDGE, npc="Torres", payoff="'You judge fast. What have you done that no one caught?'", phase=GamePhase.AMBIENT),
            ForeshadowingSeed("'Everyone's got a past. Mine's colorful. Doesn't make me evil.'", SeedType.DIALOGUE, WoundType.JUDGE, npc="Vasquez", payoff="'You decided about me early. Were you right?'", phase=GamePhase.TARGETED),
            ForeshadowingSeed("'The company made me what I am. Does that make it my fault?'", SeedType.DIALOGUE, WoundType.JUDGE, npc="Kai", payoff="'You blame me. But I didn't choose this brain.'", phase=GamePhase.TARGETED),
            ForeshadowingSeed("'Some people aren't bad. They just made bad choices. There's a difference.'", SeedType.DIALOGUE, WoundType.JUDGE, npc="Ember", payoff="'You don't see the difference, do you?'", phase=GamePhase.CONVERGENCE),
            
            # Symbolic
            ForeshadowingSeed("Recurring Image: Scales, balances, things being weighed.", SeedType.SYMBOLIC, WoundType.JUDGE, phase=GamePhase.AMBIENT),
            ForeshadowingSeed("Lighting: High contrast—harsh light, dark shadow, no gray.", SeedType.SYMBOLIC, WoundType.JUDGE, phase=GamePhase.TARGETED),
            ForeshadowingSeed("Sound: Gavel sounds, doors slamming, verdict-like finality.", SeedType.SYMBOLIC, WoundType.JUDGE, phase=GamePhase.CONVERGENCE),
        ])

        # THE GHOST
        self.seeds.extend([
            # Environmental
            ForeshadowingSeed("A room no one uses—personal effects still there.", SeedType.ENVIRONMENTAL, WoundType.GHOST, location="Empty Quarters", payoff="Someone left; presence lingers", phase=GamePhase.AMBIENT),
            ForeshadowingSeed("Window looking out at void—beautiful and empty.", SeedType.ENVIRONMENTAL, WoundType.GHOST, location="Observation Deck", payoff="Isolation is beautiful and deadly", phase=GamePhase.TARGETED),
            ForeshadowingSeed("Scan of a heart—labeled 'tissue damage from prolonged stress'.", SeedType.ENVIRONMENTAL, WoundType.GHOST, location="Med Bay", payoff="Isolation damages physically", phase=GamePhase.TARGETED),
            ForeshadowingSeed("Cryo-pods—people frozen, preserved, not living.", SeedType.ENVIRONMENTAL, WoundType.GHOST, location="Cargo Bay", payoff="Stasis isn't life", phase=GamePhase.CONVERGENCE),
            
            # Dialogue
            ForeshadowingSeed("'You're hard to read. Is that on purpose?'", SeedType.DIALOGUE, WoundType.GHOST, npc="Torres", payoff="'I've known you for days and I still don't know you.'", phase=GamePhase.AMBIENT),
            ForeshadowingSeed("'Most people warm up after a few days. You're still cold.'", SeedType.DIALOGUE, WoundType.GHOST, npc="Vasquez", payoff="'Still waiting for you to show up.'", phase=GamePhase.TARGETED),
            ForeshadowingSeed("'I use substances to numb out. What do you use?'", SeedType.DIALOGUE, WoundType.GHOST, npc="Kai", payoff="'You're numb without the drugs. That's worse.'", phase=GamePhase.TARGETED),
            ForeshadowingSeed("'Sometimes you look right through me.'", SeedType.DIALOGUE, WoundType.GHOST, npc="Ember", payoff="'Are you even here? Or are you already gone?'", phase=GamePhase.CONVERGENCE),
            
            # Symbolic
            ForeshadowingSeed("Recurring Image: Empty chairs, vacant spaces, footprints leading away.", SeedType.SYMBOLIC, WoundType.GHOST, phase=GamePhase.AMBIENT),
            ForeshadowingSeed("Temperature: Coldness, frost, things frozen.", SeedType.SYMBOLIC, WoundType.GHOST, phase=GamePhase.TARGETED),
            ForeshadowingSeed("Sound: Silence, echoes, the ship creaking alone.", SeedType.SYMBOLIC, WoundType.GHOST, phase=GamePhase.CONVERGENCE),
        ])

        # THE FUGITIVE
        self.seeds.extend([
            # Environmental
            ForeshadowingSeed("Emergency escape pod—prepped and ready.", SeedType.ENVIRONMENTAL, WoundType.FUGITIVE, location="Airlock", payoff="Exit always on mind", phase=GamePhase.AMBIENT),
            ForeshadowingSeed("Chart with many jumps—captain was running from something too.", SeedType.ENVIRONMENTAL, WoundType.FUGITIVE, location="Navigation", payoff="Everyone runs from something", phase=GamePhase.TARGETED),
            ForeshadowingSeed("Half-packed bag in player's quarters.", SeedType.ENVIRONMENTAL, WoundType.FUGITIVE, location="Personal Storage", payoff="Ready to leave at any moment", phase=GamePhase.TARGETED),
            ForeshadowingSeed("Old transmission—blocked, never sent.", SeedType.ENVIRONMENTAL, WoundType.FUGITIVE, location="Comms Room", payoff="Message to the past undelivered", phase=GamePhase.CONVERGENCE),
            
            # Dialogue
            ForeshadowingSeed("'New crew always have a reason they left the last ship.'", SeedType.DIALOGUE, WoundType.FUGITIVE, npc="Torres", payoff="'You still haven't told me why you're really here.'", phase=GamePhase.AMBIENT),
            ForeshadowingSeed("'I recognize runners. Takes one to know one.'", SeedType.DIALOGUE, WoundType.FUGITIVE, npc="Yuki", payoff="'We've been running the same direction. Different crimes.'", phase=GamePhase.TARGETED),
            ForeshadowingSeed("'Everyone arrives with baggage. Some unpack. Some don't.'", SeedType.DIALOGUE, WoundType.FUGITIVE, npc="Okonkwo", payoff="'You never unpacked, did you?'", phase=GamePhase.TARGETED),
            ForeshadowingSeed("'Where were you before here?'", SeedType.DIALOGUE, WoundType.FUGITIVE, npc="Ember", payoff="'You change the subject every time I ask about before.'", phase=GamePhase.CONVERGENCE),
            
            # Symbolic
            ForeshadowingSeed("Recurring Image: Doorways, corridors, paths leading away.", SeedType.SYMBOLIC, WoundType.FUGITIVE, phase=GamePhase.AMBIENT),
            ForeshadowingSeed("Motion: Everything moving, nothing still.", SeedType.SYMBOLIC, WoundType.FUGITIVE, phase=GamePhase.TARGETED),
            ForeshadowingSeed("Sound: Footsteps, engine hum, the sound of transit.", SeedType.SYMBOLIC, WoundType.FUGITIVE, phase=GamePhase.CONVERGENCE),
        ])

        # THE CYNIC
        self.seeds.extend([
            # Environmental
            ForeshadowingSeed("Record of past betrayals on the ship—small ones, petty ones.", SeedType.ENVIRONMENTAL, WoundType.CYNIC, location="Security Logs", payoff="Trust has been broken before", phase=GamePhase.AMBIENT),
            ForeshadowingSeed("Letter from someone who disappointed him—he kept it.", SeedType.ENVIRONMENTAL, WoundType.CYNIC, location="Captain's Quarters", payoff="He kept hoping despite evidence", phase=GamePhase.TARGETED),
            ForeshadowingSeed("Broken trust exercise poster—'TEAM BUILDING DAY' with burn marks.", SeedType.ENVIRONMENTAL, WoundType.CYNIC, location="Mess Hall", payoff="Someone gave up on hope here", phase=GamePhase.TARGETED),
            ForeshadowingSeed("Messages between crew—more honest than face-to-face.", SeedType.ENVIRONMENTAL, WoundType.CYNIC, location="Comms", payoff="Everyone has private doubts", phase=GamePhase.CONVERGENCE),
            
            # Dialogue
            ForeshadowingSeed("'Trust is earned. You don't give it away.'", SeedType.DIALOGUE, WoundType.CYNIC, npc="Torres", payoff="'You never give it. Not even when it's earned.'", phase=GamePhase.AMBIENT),
            ForeshadowingSeed("'I like you. You don't believe that, do you?'", SeedType.DIALOGUE, WoundType.CYNIC, npc="Vasquez", payoff="'I told you I liked you. I meant it. You still don't believe it.'", phase=GamePhase.TARGETED),
            ForeshadowingSeed("'Cynicism is just disappointed idealism.'", SeedType.DIALOGUE, WoundType.CYNIC, npc="Okonkwo", payoff="'You used to believe in something. What happened?'", phase=GamePhase.TARGETED),
            ForeshadowingSeed("'You expect everyone to be bad. That's sad.'", SeedType.DIALOGUE, WoundType.CYNIC, npc="Ember", payoff="'I trusted you. Was that stupid?'", phase=GamePhase.CONVERGENCE),
            
            # Symbolic
            ForeshadowingSeed("Recurring Image: Locks, walls, barriers.", SeedType.SYMBOLIC, WoundType.CYNIC, phase=GamePhase.AMBIENT),
            ForeshadowingSeed("Weather: Overcast, dim lighting, things obscured.", SeedType.SYMBOLIC, WoundType.CYNIC, phase=GamePhase.TARGETED),
            ForeshadowingSeed("Sound: Static, distortion, words that don't quite come through.", SeedType.SYMBOLIC, WoundType.CYNIC, phase=GamePhase.CONVERGENCE),
        ])

        # THE SAVIOR
        self.seeds.extend([
            # Environmental
            ForeshadowingSeed("Cabinet labeled 'EMERGENCY ONLY'—opened too often.", SeedType.ENVIRONMENTAL, WoundType.SAVIOR, location="Med Bay", payoff="Over-helping depletes resources", phase=GamePhase.AMBIENT),
            ForeshadowingSeed("Failed attempts at recovery—programs started, abandoned.", SeedType.ENVIRONMENTAL, WoundType.SAVIOR, location="Kai's Quarters", payoff="Can't save someone who isn't ready", phase=GamePhase.TARGETED),
            ForeshadowingSeed("Equipment for saving others—rescue gear, medical supplies.", SeedType.ENVIRONMENTAL, WoundType.SAVIOR, location="Cargo Bay", payoff="Tools for saving, but not self", phase=GamePhase.TARGETED),
            ForeshadowingSeed("Note: 'Tried to help Yuki. Maybe it's not mine to fix.'", SeedType.ENVIRONMENTAL, WoundType.SAVIOR, location="Captain's Quarters", payoff="Even the captain couldn't save her", phase=GamePhase.CONVERGENCE),
            
            # Dialogue
            ForeshadowingSeed("'Some people don't want help. Respect that.'", SeedType.DIALOGUE, WoundType.SAVIOR, npc="Torres", payoff="'You couldn't respect it. You kept pushing.'", phase=GamePhase.AMBIENT),
            ForeshadowingSeed("'I need to want to get better. No one can want it for me.'", SeedType.DIALOGUE, WoundType.SAVIOR, npc="Kai", payoff="'You wanted it more than I did. That's the problem.'", phase=GamePhase.TARGETED),
            ForeshadowingSeed("'The hardest part of medicine is accepting when you can't help.'", SeedType.DIALOGUE, WoundType.SAVIOR, npc="Okonkwo", payoff="'You never accepted it.'", phase=GamePhase.TARGETED),
            ForeshadowingSeed("'You don't have to fix me. I'm okay.'", SeedType.DIALOGUE, WoundType.SAVIOR, npc="Ember", payoff="'Why can't you just be with people without fixing them?'", phase=GamePhase.CONVERGENCE),
            
            # Symbolic
            ForeshadowingSeed("Recurring Image: Hands reaching, offering, extending.", SeedType.SYMBOLIC, WoundType.SAVIOR, phase=GamePhase.AMBIENT),
            ForeshadowingSeed("Posture: Player character leaning toward others.", SeedType.SYMBOLIC, WoundType.SAVIOR, phase=GamePhase.TARGETED),
            ForeshadowingSeed("Sound: Heartbeats, breathing—life signs being monitored.", SeedType.SYMBOLIC, WoundType.SAVIOR, phase=GamePhase.CONVERGENCE),
        ])

        # THE DESTROYER
        self.seeds.extend([
            # Environmental
            ForeshadowingSeed("Small damages—things broken, dented, scarred.", SeedType.ENVIRONMENTAL, WoundType.DESTROYER, location="Throughout Ship", payoff="Violence leaves marks", phase=GamePhase.AMBIENT),
            ForeshadowingSeed("Controlled burn marks—fire used for something.", SeedType.ENVIRONMENTAL, WoundType.DESTROYER, location="Engine Room", payoff="Destruction can be purposeful", phase=GamePhase.TARGETED),
            ForeshadowingSeed("Scratch marks near the emergency release.", SeedType.ENVIRONMENTAL, WoundType.DESTROYER, location="Airlock", payoff="Someone almost vented their rage", phase=GamePhase.TARGETED),
            ForeshadowingSeed("Smashed crate—contents salvaged, but the breaking was the point.", SeedType.ENVIRONMENTAL, WoundType.DESTROYER, location="Cargo Bay", payoff="Destruction as expression", phase=GamePhase.CONVERGENCE),
            
            # Dialogue
            ForeshadowingSeed("'Anger's useful. Until it's not.'", SeedType.DIALOGUE, WoundType.DESTROYER, npc="Torres", payoff="'You passed useful a long time ago.'", phase=GamePhase.AMBIENT),
            ForeshadowingSeed("'I break things when I'm using. What's your excuse?'", SeedType.DIALOGUE, WoundType.DESTROYER, npc="Kai", payoff="'You're not using. But you're still breaking.'", phase=GamePhase.TARGETED),
            ForeshadowingSeed("'Careful. Break too much and there's nothing left to trade.'", SeedType.DIALOGUE, WoundType.DESTROYER, npc="Vasquez", payoff="'Look around. What have you built? Only ruins.'", phase=GamePhase.TARGETED),
            ForeshadowingSeed("'Are you okay? You seem... angry.'", SeedType.DIALOGUE, WoundType.DESTROYER, npc="Ember", payoff="'The anger never went away. It just found more targets.'", phase=GamePhase.CONVERGENCE),
            
            # Symbolic
            ForeshadowingSeed("Recurring Image: Fire, wreckage, things torn apart.", SeedType.SYMBOLIC, WoundType.DESTROYER, phase=GamePhase.AMBIENT),
            ForeshadowingSeed("Color: Red, black, char.", SeedType.SYMBOLIC, WoundType.DESTROYER, phase=GamePhase.TARGETED),
            ForeshadowingSeed("Sound: Crashing, breaking, the sound of destruction.", SeedType.SYMBOLIC, WoundType.DESTROYER, phase=GamePhase.CONVERGENCE),
        ])

    def get_phase_from_progress(self, progress: float) -> GamePhase:
        if progress < 0.25: return GamePhase.AMBIENT
        if progress < 0.60: return GamePhase.TARGETED
        if progress < 0.85: return GamePhase.CONVERGENCE
        return GamePhase.REVELATION

    def select_seeds(
        self,
        archetype_scores: Dict[WoundType, float],
        progress: float,
        location: Optional[str] = None,
        npc: Optional[str] = None,
        limit: int = 2
    ) -> List[ForeshadowingSeed]:
        """Select relevant seeds based on archetype and progress."""
        current_phase = self.get_phase_from_progress(progress)
        
        # Identify top archetypes (score > threshold)
        active_archetypes = [a for a, s in archetype_scores.items() if s > 0.1]
        if not active_archetypes:
            # Fallback to generic ambient seeds if no archetype is clear
            active_archetypes = [WoundType.UNKNOWN] 

        # Filter candidates
        candidates = []
        for seed in self.seeds:
            # Phase matching: Ambient is always available, Targeted/Convergence unlock later
            if current_phase == GamePhase.AMBIENT and seed.phase != GamePhase.AMBIENT:
                continue
            if current_phase == GamePhase.TARGETED and seed.phase not in [GamePhase.AMBIENT, GamePhase.TARGETED]:
                continue
            if current_phase == GamePhase.CONVERGENCE and seed.phase == GamePhase.REVELATION:
                continue
            
            # Archetype matching
            if seed.archetype not in active_archetypes and seed.archetype != WoundType.UNKNOWN:
                continue
            
            # Context matching (Environmental requires location, Dialogue requires NPC)
            if seed.seed_type == SeedType.ENVIRONMENTAL and seed.location:
                if location and seed.location.lower() not in location.lower():
                    continue
            if seed.seed_type == SeedType.DIALOGUE and seed.npc:
                if npc and seed.npc.lower() not in npc.lower():
                    continue
            
            # Avoid repeating seeds
            if seed in self.planted_seeds:
                continue
                
            candidates.append(seed)

        # Weighting: Prefer seeds that match current phase exactly
        weighted_candidates = []
        for c in candidates:
            weight = 1
            if c.phase == current_phase:
                weight = 5
            # Preference for specific archetype over UNKNOWN
            if c.archetype != WoundType.UNKNOWN:
                weight *= 2
            
            for _ in range(weight):
                weighted_candidates.append(c)

        if not weighted_candidates:
            return []

        selected = random.sample(candidates, min(len(candidates), limit))
        self.planted_seeds.extend(selected)
        return selected

    def get_narrator_instructions(self, seeds: List[ForeshadowingSeed]) -> str:
        """Convert selected seeds into instructions for the LLM."""
        if not seeds:
            return ""
            
        instructions = ["<foreshadowing_seeds>"]
        for seed in seeds:
            instructions.append(f"  - [{seed.seed_type.value.upper()}]: {seed.content}")
            if seed.payoff:
                instructions.append(f"    (Payoff Context: {seed.payoff})")
        instructions.append("INSTRUCTION: Integrate these details subtly into your narrative. Do not reveal the payoff yet. Let the pattern emerge naturally.</foreshadowing_seeds>")
        
        return "\n".join(instructions)

    def to_dict(self) -> dict:
        return {
            "planted_seeds_indices": [self.seeds.index(s) for s in self.planted_seeds if s in self.seeds]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ForeshadowingEngine":
        engine = cls()
        indices = data.get("planted_seeds_indices", [])
        for i in indices:
            if 0 <= i < len(engine.seeds):
                engine.planted_seeds.append(engine.seeds[i])
        return engine
