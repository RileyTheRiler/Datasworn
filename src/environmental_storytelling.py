"""
Environmental Storytelling & Callbacks - TLOU-Style Implied Narrative.
Implements "show don't tell" through discoveries, artifacts, and callbacks.

Key principles:
- Imply tragedy rather than state it
- Found objects tell stories of absent people
- Callbacks create emotional payoffs at climax
- Small details matter more than exposition
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import random


# ============================================================================
# Environmental Discovery Types
# ============================================================================

class DiscoveryType(Enum):
    """Types of environmental storytelling discoveries."""
    ARTIFACT = "artifact"  # Object that tells a story
    NOTE = "note"  # Written message from the past
    SCENE = "scene"  # Arrangement of objects that implies events
    AUDIO = "audio"  # Recording or overheard fragment
    GRAFFITI = "graffiti"  # Mark left by others
    REMAINS = "remains"  # Evidence of what happened to someone


class EmotionalTone(Enum):
    """Emotional tone of the discovery."""
    TRAGIC = "tragic"
    HOPEFUL = "hopeful"
    OMINOUS = "ominous"
    BITTERSWEET = "bittersweet"
    PEACEFUL = "peaceful"
    HORRIFYING = "horrifying"


# ============================================================================
# Discovery Templates
# ============================================================================

DISCOVERY_TEMPLATES = {
    DiscoveryType.ARTIFACT: {
        EmotionalTone.TRAGIC: [
            "A child's toy, carefully placed on a shelf. Waiting for someone who won't return.",
            "Two wedding rings, tied together with a faded ribbon. Left behind.",
            "A packed bag by the door. They never made it out.",
            "A birthday cake, dried and collapsed. Candles never lit.",
        ],
        EmotionalTone.HOPEFUL: [
            "A makeshift calendar. Someone's been counting days. Still alive?",
            "A collection of seeds, carefully sorted. Planning for a future.",
            "A child's drawing of a happy family. The paper is new.",
            "A repaired toy—someone fixed it with care. Love persists.",
        ],
        EmotionalTone.BITTERSWEET: [
            "A photograph, worn from handling. Their faces barely visible now.",
            "A journal with blank pages after a certain date. The story continues elsewhere.",
            "Two cups, one still half-full. Someone left quickly.",
            "A locket containing a lock of hair. Carried far from home.",
        ],
    },
    DiscoveryType.NOTE: {
        EmotionalTone.TRAGIC: [
            "Scratched on the wall: 'WE TRIED TO WAIT FOR YOU.' No other marks.",
            "A letter, addressed but never sent. The words 'I forgive you' at the end.",
            "A list of names, some crossed out. The last name has no line through it.",
            "Written in a child's hand: 'Mom said she'd be right back.'",
        ],
        EmotionalTone.HOPEFUL: [
            "A note: 'Heading north. Look for the blue door. We made it.'",
            "Scratched into metal: 'Still alive. Still fighting.'",
            "A map with a route marked. Someone found a way.",
            "Written on a wall: 'There are good people left. Keep looking.'",
        ],
        EmotionalTone.OMINOUS: [
            "A single word, repeated across every surface: 'RUN'",
            "A list of rules. The last one says: 'Never open the basement.'",
            "Counting marks on the wall. Hundreds. Then they stop.",
            "A note: 'We should never have opened it.'",
        ],
    },
    DiscoveryType.SCENE: {
        EmotionalTone.TRAGIC: [
            "Two chairs facing each other. A game of chess, frozen mid-play forever.",
            "A table set for dinner. Four places. Food long rotted away.",
            "A crib, mobile still spinning slowly in the draft. The room is empty.",
            "Packed suitcases by a door that was never opened.",
        ],
        EmotionalTone.PEACEFUL: [
            "A hammock between two trees. Someone found rest here.",
            "A garden, overgrown but clearly once loved.",
            "A reading nook. The book is still open to a middle page.",
            "Wind chimes, still singing for no one in particular.",
        ],
        EmotionalTone.HORRIFYING: [
            "Claw marks on the inside of a sealed door.",
            "A circle of figures, arranged facing outward. Defending something.",
            "The trail leads here. It ends here. Something is missing.",
            "Everything is in place. Except the people.",
        ],
    },
}


@dataclass
class EnvironmentalDiscovery:
    """A piece of environmental storytelling."""
    discovery_type: DiscoveryType
    tone: EmotionalTone
    description: str
    implied_story: str  # What the narrator should understand
    player_reaction_prompt: str  # Optional prompt for player response
    scene: int = 0  # When discovered
    
    def get_narrator_context(self) -> str:
        """Generate context for narrator."""
        lines = [f"[ENVIRONMENTAL DISCOVERY: {self.discovery_type.value.upper()}]"]
        lines.append(f"Tone: {self.tone.value}")
        lines.append(f"What the player finds: {self.description}")
        lines.append(f"Implied story: {self.implied_story}")
        lines.append("")
        lines.append("NARRATOR GUIDANCE:")
        lines.append("- Describe ONLY what is seen. Do not explain.")
        lines.append("- Let silence do the work.")
        lines.append("- The player's imagination fills in the horror/beauty.")
        
        return "\n".join(lines)


# ============================================================================
# Callback System
# ============================================================================

@dataclass
class NarrativeCallback:
    """A moment from earlier that should be referenced later."""
    scene_created: int
    description: str
    characters_involved: list[str] = field(default_factory=list)
    emotional_weight: float = 0.5  # 0-1, how impactful
    callback_used: bool = False
    ideal_callback_context: str = ""  # When to reference this
    
    def generate_callback(self, current_scene: int) -> str:
        """Generate the callback reference for narrator."""
        scenes_ago = current_scene - self.scene_created
        
        if scenes_ago < 5:
            timing = "moments ago"
        elif scenes_ago < 15:
            timing = "earlier"
        else:
            timing = "a lifetime ago"
        
        return (
            f"[CALLBACK OPPORTUNITY]\n"
            f"Reference this moment from {timing}:\n"
            f"\"{self.description}\"\n"
            f"Characters: {', '.join(self.characters_involved) if self.characters_involved else 'none'}\n"
            f"Context: This should create emotional resonance. The player should feel the distance traveled."
        )


class CallbackManager:
    """Manages narrative callbacks for emotional payoffs."""
    
    def __init__(self):
        self.callbacks: list[NarrativeCallback] = []
        self.used_callbacks: list[NarrativeCallback] = []
    
    def store_moment(
        self,
        scene: int,
        description: str,
        characters: list[str] = None,
        emotional_weight: float = 0.5,
        ideal_context: str = "",
    ) -> None:
        """Store a moment for potential future callback."""
        callback = NarrativeCallback(
            scene_created=scene,
            description=description,
            characters_involved=characters or [],
            emotional_weight=emotional_weight,
            ideal_callback_context=ideal_context,
        )
        self.callbacks.append(callback)
    
    def get_callback_for_moment(
        self,
        current_scene: int,
        context: str = "",
        character: str | None = None,
    ) -> str | None:
        """Get an appropriate callback for the current moment."""
        available = [c for c in self.callbacks if not c.callback_used]
        
        if not available:
            return None
        
        # Prioritize by match
        scored = []
        for cb in available:
            score = cb.emotional_weight
            
            # Bonus for character match
            if character and character in cb.characters_involved:
                score += 0.3
            
            # Bonus for context match
            if cb.ideal_callback_context and cb.ideal_callback_context.lower() in context.lower():
                score += 0.2
            
            # Prefer older callbacks (more distance = more impact)
            age = current_scene - cb.scene_created
            if age > 10:
                score += 0.1
            
            scored.append((cb, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        
        if scored and scored[0][1] > 0.3:
            best = scored[0][0]
            best.callback_used = True
            self.used_callbacks.append(best)
            return best.generate_callback(current_scene)
        
        return None
    
    def to_dict(self) -> dict:
        return {
            "callbacks": [
                {
                    "scene_created": c.scene_created,
                    "description": c.description,
                    "characters_involved": c.characters_involved,
                    "emotional_weight": c.emotional_weight,
                    "callback_used": c.callback_used,
                    "ideal_callback_context": c.ideal_callback_context,
                }
                for c in self.callbacks
            ],
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "CallbackManager":
        manager = cls()
        for cb_data in data.get("callbacks", []):
            cb = NarrativeCallback(
                scene_created=cb_data.get("scene_created", 0),
                description=cb_data.get("description", ""),
                characters_involved=cb_data.get("characters_involved", []),
                emotional_weight=cb_data.get("emotional_weight", 0.5),
                callback_used=cb_data.get("callback_used", False),
                ideal_callback_context=cb_data.get("ideal_callback_context", ""),
            )
            manager.callbacks.append(cb)
        return manager


# ============================================================================
# Environmental Storytelling Generator
# ============================================================================

class EnvironmentalStoryGenerator:
    """Generates environmental storytelling prompts for the narrator."""
    
    def __init__(self):
        self.discoveries_generated: list[str] = []
    
    def generate_discovery(
        self,
        discovery_type: DiscoveryType | None = None,
        tone: EmotionalTone | None = None,
        location_context: str = "",
    ) -> EnvironmentalDiscovery:
        """Generate an environmental discovery."""
        if discovery_type is None:
            discovery_type = random.choice(list(DiscoveryType))
        
        if tone is None:
            # Infer from location context
            if any(word in location_context.lower() for word in ["child", "family", "home"]):
                tone = random.choice([EmotionalTone.TRAGIC, EmotionalTone.BITTERSWEET])
            elif any(word in location_context.lower() for word in ["danger", "threat", "dark"]):
                tone = random.choice([EmotionalTone.OMINOUS, EmotionalTone.HORRIFYING])
            else:
                tone = random.choice(list(EmotionalTone))
        
        # Get template
        templates = DISCOVERY_TEMPLATES.get(discovery_type, {}).get(tone)
        if not templates:
            # Fallback
            templates = DISCOVERY_TEMPLATES[DiscoveryType.ARTIFACT][EmotionalTone.BITTERSWEET]
        
        description = random.choice(templates)
        
        # Generate implied story
        implied_stories = {
            EmotionalTone.TRAGIC: "Someone's story ended here. Not peacefully.",
            EmotionalTone.HOPEFUL: "Life continues. Someone is still fighting.",
            EmotionalTone.OMINOUS: "Something happened here. Something may still be here.",
            EmotionalTone.BITTERSWEET: "Love existed here. Exists still, in these traces.",
            EmotionalTone.PEACEFUL: "A moment of peace, frozen. A reminder of what's worth saving.",
            EmotionalTone.HORRIFYING: "The end came here. It wasn't quick.",
        }
        
        discovery = EnvironmentalDiscovery(
            discovery_type=discovery_type,
            tone=tone,
            description=description,
            implied_story=implied_stories.get(tone, "A story left untold."),
            player_reaction_prompt="What does this make the player feel?",
        )
        
        self.discoveries_generated.append(description)
        return discovery
    
    def get_show_dont_tell_guidance(self) -> str:
        """Get general narrator guidance for environmental storytelling."""
        return """[ENVIRONMENTAL STORYTELLING GUIDANCE]
        
SHOW, DON'T TELL:
- Describe objects, not emotions
- Let emptiness speak
- Trust the player to feel

LESS IS MORE:
- A single detail beats a paragraph
- What's missing matters more than what's there
- Silence after a discovery

THE RULE OF THREE:
- One visual detail
- One sensory detail (sound, smell, texture)
- One implication

NEVER SAY:
- "This made you feel sad"
- "Clearly something terrible happened"
- "You realized..."

INSTEAD:
- Describe what IS. Let them feel.
"""


# ============================================================================
# Convenience Functions
# ============================================================================

def create_callback_manager() -> CallbackManager:
    """Create a new callback manager."""
    return CallbackManager()


def create_environmental_generator() -> EnvironmentalStoryGenerator:
    """Create a new environmental story generator."""
    return EnvironmentalStoryGenerator()


def quick_discovery(discovery_type: str = "artifact", tone: str = "tragic") -> str:
    """Generate a quick discovery description."""
    try:
        dtype = DiscoveryType(discovery_type)
    except ValueError:
        dtype = DiscoveryType.ARTIFACT
    
    try:
        dtone = EmotionalTone(tone)
    except ValueError:
        dtone = EmotionalTone.TRAGIC
    
    generator = EnvironmentalStoryGenerator()
    discovery = generator.generate_discovery(discovery_type=dtype, tone=dtone)
    return discovery.get_narrator_context()
