"""
Bark System & Environmental Reactions.
NPCs vocally react to the world and notice player traces.

"Did I leave that open?" - The moment the world feels alive.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import random

from src.psych_profile import PsychologicalProfile, EmotionalState


# ============================================================================
# Bark Types
# ============================================================================

class BarkType(Enum):
    """Types of NPC vocalizations."""
    IDLE = "idle"  # Ambient chatter
    ALERT = "alert"  # Noticed something
    SUSPICIOUS = "suspicious"  # Something's off
    COMBAT = "combat"  # In a fight
    PAIN = "pain"  # Took damage
    DEATH = "death"  # Final words
    SEARCH = "search"  # Looking for something
    FOUND = "found"  # Discovered something
    RELIEF = "relief"  # Threat passed
    SPOTTING = "spotting"  # Saw the player
    FRIENDLY = "friendly"  # Greeting ally


class BarkTrigger(Enum):
    """What triggers a bark."""
    ENTER_AREA = "enter_area"
    SEE_PLAYER = "see_player"
    LOSE_PLAYER = "lose_player"
    HEAR_NOISE = "hear_noise"
    FIND_EVIDENCE = "find_evidence"
    ALLY_DOWN = "ally_down"
    TAKE_DAMAGE = "take_damage"
    KILL_ENEMY = "kill_enemy"
    SEARCH_TIMEOUT = "search_timeout"
    ENVIRONMENTAL = "environmental"


# ============================================================================
# Bark Templates
# ============================================================================

BARK_TEMPLATES = {
    BarkType.IDLE: [
        "*hums tunelessly*",
        "*shifts weight, sighs*",
        "Another quiet night...",
        "*checks equipment*",
        "*mutters something unintelligible*",
    ],
    BarkType.ALERT: [
        "What was that?",
        "Did you hear something?",
        "Hold up—",
        "*freezes*",
        "Eyes up.",
    ],
    BarkType.SUSPICIOUS: [
        "Something's not right here.",
        "This doesn't feel right.",
        "Stay sharp.",
        "Did I leave that...?",
        "Someone's been here.",
    ],
    BarkType.COMBAT: [
        "Contact!",
        "There! Open fire!",
        "Got movement!",
        "Engaging!",
        "*opens fire*",
    ],
    BarkType.PAIN: [
        "Gah—!",
        "*grunts in pain*",
        "I'm hit!",
        "*staggers*",
        "Damn—that hurt!",
    ],
    BarkType.DEATH: [
        "*collapses*",
        "*final gasp*",
        "Tell... tell them...",
        "*silence*",
        "*falls*",
    ],
    BarkType.SEARCH: [
        "They're here somewhere...",
        "Check everywhere.",
        "Don't let them slip away.",
        "Spread out.",
        "They can't have gone far.",
    ],
    BarkType.FOUND: [
        "There!",
        "Found you!",
        "Got visual!",
        "I see them!",
        "*points*",
    ],
    BarkType.RELIEF: [
        "*exhales* Must've been nothing.",
        "Clear. Stand down.",
        "False alarm.",
        "*relaxes grip on weapon*",
        "All clear.",
    ],
    BarkType.SPOTTING: [
        "Hey—who's that?",
        "Hold it right there.",
        "You! Stop!",
        "We got company.",
        "Someone's here.",
    ],
    BarkType.FRIENDLY: [
        "Hey.",
        "*nods in greeting*",
        "Staying out of trouble?",
        "Anything to report?",
        "*waves*",
    ],
}

# Psychological State-Aware Barks
PSYCH_AWARE_BARKS = {
    EmotionalState.ANXIOUS: [
        "You alright? You look pale.",
        "Calm down. Deep breaths, you're shaking.",
        "You're shaking. What's wrong?",
        "*eyes narrow* Nervous about something?",
    ],
    EmotionalState.ANGRY: [
        "Whoa, easy there.",
        "Back off. I don't want trouble.",
        "*raises hands defensively*",
        "Calm yourself.",
    ],
    EmotionalState.AFRAID: [
        "You look terrified. What happened?",
        "*concerned* Are you okay?",
        "What's got you so spooked?",
    ],
    EmotionalState.SUSPICIOUS: [
        "Why are you looking at me like that?",
        "*meets your gaze* Something on your mind?",
        "You don't trust me, do you?",
    ],
    EmotionalState.GUILTY: [
        "You look like you've seen a ghost.",
        "What did you do?",
        "*suspicious* You're hiding something.",
    ],
}

# Trauma-Aware Barks
TRAUMA_BARKS = {
    "Shattered Trust": [
        "Keep your distance.",
        "I don't trust you.",
        "*steps back* Keep your distance.",
    ],
    "Hyper-Vigilance": [
        "*jumps at sudden movement*",
        "You startled me.",
        "Don't sneak up on people.",
    ],
}


@dataclass
class Bark:
    """A single bark/vocalization."""
    bark_type: BarkType
    text: str
    npc_name: str = ""
    is_whispered: bool = False
    targets_player: bool = False


# ============================================================================
# Environmental Evidence
# ============================================================================

class EvidenceType(Enum):
    """Types of environmental evidence players leave."""
    OPEN_DOOR = "open_door"
    DEAD_BODY = "dead_body"
    MOVED_OBJECT = "moved_object"
    BLOOD_TRAIL = "blood_trail"
    FOOTPRINTS = "footprints"
    MISSING_ITEM = "missing_item"
    BROKEN_LOCK = "broken_lock"
    POWERED_DOWN = "powered_down"
    NOISE = "noise"


@dataclass
class EnvironmentalEvidence:
    """Evidence the player has left behind."""
    evidence_type: EvidenceType
    location: str
    description: str
    suspicion_level: float = 0.5  # 0-1, how suspicious
    decay_time: int = 10  # Scenes until evidence is ignored


EVIDENCE_REACTIONS = {
    EvidenceType.OPEN_DOOR: [
        "Did I leave that open?",
        "This door was closed...",
        "Someone came through here.",
        "*frowns at the open door*",
    ],
    EvidenceType.DEAD_BODY: [
        "Body! We got a body here!",
        "What the—?! *raises alarm*",
        "They got Marcus. They're gonna pay.",
        "*kneels by the body* Still warm...",
    ],
    EvidenceType.MOVED_OBJECT: [
        "This wasn't here before...",
        "Someone's been touching things.",
        "*tilts head* That's not right.",
        "We got a visitor.",
    ],
    EvidenceType.BLOOD_TRAIL: [
        "Blood. Fresh.",
        "Someone's hurt. Follow this.",
        "*crouches* They went this way.",
        "Trail leads that direction.",
    ],
    EvidenceType.FOOTPRINTS: [
        "Tracks. Recent.",
        "Someone came through here.",
        "*examines prints* Not one of ours.",
        "These lead somewhere...",
    ],
    EvidenceType.MISSING_ITEM: [
        "Where's the—? It was right here!",
        "Someone took it.",
        "We've got a thief.",
        "*checks inventory* That's gone.",
    ],
    EvidenceType.BROKEN_LOCK: [
        "Lock's been forced.",
        "Breach here. Lock's shot.",
        "They broke through.",
        "*examines damage* Professional job.",
    ],
    EvidenceType.NOISE: [
        "You hear that?",
        "What was that noise?",
        "*listens* Over there.",
        "Something's moving.",
    ],
}


# ============================================================================
# Bark Manager
# ============================================================================

class BarkManager:
    """
    Manages NPC vocalizations and evidence reactions.
    """
    
    def __init__(self):
        self.recent_barks: list[Bark] = []
        self.evidence_log: list[EnvironmentalEvidence] = []
        self.npc_bark_cooldowns: dict[str, int] = {}  # npc_id -> turns until can bark again
    
    def generate_bark(
        self,
        npc_name: str,
        bark_type: BarkType,
        context: str = "",
        psych_profile: PsychologicalProfile | None = None,
    ) -> Bark | None:
        """Generate a bark for an NPC."""
        # Check cooldown
        if self.npc_bark_cooldowns.get(npc_name, 0) > 0:
            return None
        
        # Psych-aware bark selection
        if psych_profile and bark_type == BarkType.FRIENDLY:
            # Check for emotional state overrides
            if psych_profile.current_emotion in PSYCH_AWARE_BARKS:
                templates = PSYCH_AWARE_BARKS[psych_profile.current_emotion]
                text = random.choice(templates)
            # Check for trauma-based reactions
            elif psych_profile.trauma_scars:
                for scar in psych_profile.trauma_scars:
                    if scar.name in TRAUMA_BARKS:
                        templates = TRAUMA_BARKS[scar.name]
                        text = random.choice(templates)
                        break
                else:
                    templates = BARK_TEMPLATES.get(bark_type, BARK_TEMPLATES[BarkType.IDLE])
                    text = random.choice(templates)
            else:
                templates = BARK_TEMPLATES.get(bark_type, BARK_TEMPLATES[BarkType.IDLE])
                text = random.choice(templates)
        else:
            # Default behavior
            templates = BARK_TEMPLATES.get(bark_type, BARK_TEMPLATES[BarkType.IDLE])
            text = random.choice(templates)
        
        # Customize based on context
        if context and "{context}" in text:
            text = text.replace("{context}", context)
        
        bark = Bark(
            bark_type=bark_type,
            text=text,
            npc_name=npc_name,
        )
        
        self.recent_barks.append(bark)
        self.npc_bark_cooldowns[npc_name] = 2  # 2 turn cooldown
        
        return bark
    
    def add_evidence(
        self,
        evidence_type: EvidenceType,
        location: str,
        description: str = "",
    ) -> EnvironmentalEvidence:
        """Add environmental evidence."""
        evidence = EnvironmentalEvidence(
            evidence_type=evidence_type,
            location=location,
            description=description or f"Evidence of {evidence_type.value}",
        )
        self.evidence_log.append(evidence)
        return evidence
    
    def check_for_evidence_reaction(
        self,
        npc_name: str,
        npc_location: str,
    ) -> Bark | None:
        """Check if NPC should react to evidence at their location."""
        for evidence in self.evidence_log:
            if evidence.location == npc_location and evidence.decay_time > 0:
                # React to this evidence
                reactions = EVIDENCE_REACTIONS.get(evidence.evidence_type, [])
                if reactions:
                    text = random.choice(reactions)
                    bark = Bark(
                        bark_type=BarkType.SUSPICIOUS,
                        text=text,
                        npc_name=npc_name,
                    )
                    evidence.decay_time -= 1  # Evidence becomes less notable
                    return bark
        return None
    
    def update_cooldowns(self) -> None:
        """Tick down bark cooldowns each turn."""
        for npc in list(self.npc_bark_cooldowns.keys()):
            self.npc_bark_cooldowns[npc] = max(0, self.npc_bark_cooldowns[npc] - 1)
        
        # Decay evidence
        for evidence in self.evidence_log:
            evidence.decay_time = max(0, evidence.decay_time - 1)
        
        # Remove old evidence
        self.evidence_log = [e for e in self.evidence_log if e.decay_time > 0]
    
    def get_narrator_context(self) -> str:
        """Generate context for narrator about barks and evidence."""
        lines = []
        
        if self.recent_barks:
            lines.append("[NPC VOCALIZATIONS]")
            for bark in self.recent_barks[-3:]:
                lines.append(f'{bark.npc_name}: "{bark.text}"')
        
        if self.evidence_log:
            lines.append("\n[ENVIRONMENTAL EVIDENCE]")
            for evidence in self.evidence_log[:3]:
                lines.append(f"• {evidence.location}: {evidence.description}")
                lines.append(f"  (Suspicion: {evidence.suspicion_level:.1f}, Decay: {evidence.decay_time})")
        
        if not lines:
            return ""
        
        return "\n".join(lines)
    
    def to_dict(self) -> dict:
        return {
            "recent_barks": [
                {"type": b.bark_type.value, "text": b.text, "npc": b.npc_name}
                for b in self.recent_barks[-10:]
            ],
            "evidence_log": [
                {
                    "type": e.evidence_type.value,
                    "location": e.location,
                    "description": e.description,
                    "suspicion": e.suspicion_level,
                    "decay": e.decay_time,
                }
                for e in self.evidence_log
            ],
            "cooldowns": self.npc_bark_cooldowns,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BarkManager":
        manager = cls()
        
        for bark_data in data.get("recent_barks", []):
            bark = Bark(
                bark_type=BarkType(bark_data.get("type", "idle")),
                text=bark_data.get("text", ""),
                npc_name=bark_data.get("npc", ""),
            )
            manager.recent_barks.append(bark)
        
        for ev_data in data.get("evidence_log", []):
            evidence = EnvironmentalEvidence(
                evidence_type=EvidenceType(ev_data.get("type", "noise")),
                location=ev_data.get("location", ""),
                description=ev_data.get("description", ""),
                suspicion_level=ev_data.get("suspicion", 0.5),
                decay_time=ev_data.get("decay", 5),
            )
            manager.evidence_log.append(evidence)
        
        manager.npc_bark_cooldowns = data.get("cooldowns", {})
        return manager


# ============================================================================
# Convenience Functions
# ============================================================================

def create_bark_manager() -> BarkManager:
    """Create a new bark manager."""
    return BarkManager()


def quick_bark(npc_name: str, bark_type: str = "idle") -> str:
    """Generate a quick bark."""
    try:
        btype = BarkType(bark_type)
    except ValueError:
        btype = BarkType.IDLE
    
    manager = BarkManager()
    bark = manager.generate_bark(npc_name, btype)
    return f'{npc_name}: "{bark.text}"' if bark else ""


def detect_evidence(player_action: str) -> list[EvidenceType]:
    """Detect what evidence a player action might leave."""
    action_lower = player_action.lower()
    evidence = []
    
    if any(word in action_lower for word in ["open", "door", "enter"]):
        evidence.append(EvidenceType.OPEN_DOOR)
    if any(word in action_lower for word in ["kill", "attack", "fight", "shoot"]):
        evidence.append(EvidenceType.DEAD_BODY)
    if any(word in action_lower for word in ["take", "steal", "grab", "pocket"]):
        evidence.append(EvidenceType.MISSING_ITEM)
    if any(word in action_lower for word in ["break", "force", "hack", "pick"]):
        evidence.append(EvidenceType.BROKEN_LOCK)
    if any(word in action_lower for word in ["run", "sprint", "flee"]):
        evidence.append(EvidenceType.FOOTPRINTS)
    
    return evidence
