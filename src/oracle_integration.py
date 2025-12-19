"""
Deep Oracle Integration System

Automatically triggers oracle rolls during exploration, discovery, and
generation moments. Provides contextual oracle suggestions and chains
multiple oracle results for richer narrative content.

This transforms oracles from player-requested tools into an active part
of the narrative generation process.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
import random


class OracleContext(Enum):
    """Contexts that trigger different oracle categories."""
    EXPLORATION = "exploration"
    COMBAT = "combat"
    SOCIAL = "social"
    DISCOVERY = "discovery"
    MYSTERY = "mystery"
    TRAVEL = "travel"
    SETTLEMENT = "settlement"
    SPACE = "space"
    DERELICT = "derelict"
    CREATURE = "creature"
    CHARACTER = "character"
    FACTION = "faction"


@dataclass
class OracleChain:
    """A sequence of oracle rolls that combine for richer results."""
    name: str
    oracle_paths: List[str]  # Paths to roll in sequence
    template: str  # Template to combine results: "{0} who {1} and {2}"
    context: OracleContext
    probability: float = 0.5  # Chance to trigger when context matches

    def roll(self, datasworn) -> Optional[str]:
        """Roll all oracles in the chain and combine results."""
        results = []
        for path in self.oracle_paths:
            # Search for matching oracle
            oracles = datasworn.search_oracles(path)
            if oracles:
                # Get the first matching oracle and roll it
                for key in datasworn._oracles.keys():
                    if path.lower() in key.lower():
                        result = datasworn.roll_oracle(key)
                        if result:
                            results.append(result)
                            break

        if len(results) < len(self.oracle_paths):
            return None

        # Combine using template
        try:
            return self.template.format(*results)
        except (IndexError, KeyError):
            return " - ".join(results)


@dataclass
class OracleTrigger:
    """Defines when an oracle should automatically trigger."""
    keywords: List[str]  # Trigger words in player input
    oracle_paths: List[str]  # Oracle paths to potentially use
    context: OracleContext
    probability: float = 0.3  # Base probability to trigger
    cooldown_turns: int = 3  # Minimum turns between triggers
    narrative_injection: str = ""  # Template for injecting result: "You notice {result}"


# Pre-defined oracle chains for rich content generation
ORACLE_CHAINS: Dict[str, OracleChain] = {
    "npc_full": OracleChain(
        name="Full NPC",
        oracle_paths=["character/name", "character/role", "character/disposition"],
        template="{0}, a {1} who seems {2}",
        context=OracleContext.CHARACTER,
        probability=0.6,
    ),
    "settlement_full": OracleChain(
        name="Full Settlement",
        oracle_paths=["settlements/name", "settlements/population", "settlements/authority"],
        template="{0}, a {1} settlement under {2} control",
        context=OracleContext.SETTLEMENT,
        probability=0.7,
    ),
    "planet_full": OracleChain(
        name="Full Planet",
        oracle_paths=["planets/class", "planets/atmosphere", "planets/life"],
        template="A {0} world with {1} atmosphere and {2}",
        context=OracleContext.SPACE,
        probability=0.6,
    ),
    "derelict_full": OracleChain(
        name="Full Derelict",
        oracle_paths=["derelicts/type", "derelicts/condition", "derelicts/outer first look"],
        template="A {1} {0}, its exterior showing {2}",
        context=OracleContext.DERELICT,
        probability=0.7,
    ),
    "creature_full": OracleChain(
        name="Full Creature",
        oracle_paths=["creatures/form", "creatures/size", "creatures/behavior"],
        template="A {1} {0} that appears {2}",
        context=OracleContext.CREATURE,
        probability=0.5,
    ),
    "action_theme": OracleChain(
        name="Action + Theme",
        oracle_paths=["core/action", "core/theme"],
        template="{0} {1}",
        context=OracleContext.MYSTERY,
        probability=0.4,
    ),
    "story_complication": OracleChain(
        name="Story Complication",
        oracle_paths=["moves/story complication"],
        template="Complication: {0}",
        context=OracleContext.DISCOVERY,
        probability=0.3,
    ),
}

# Oracle triggers for auto-activation
ORACLE_TRIGGERS: List[OracleTrigger] = [
    # Exploration triggers
    OracleTrigger(
        keywords=["explore", "search", "investigate", "look around", "examine"],
        oracle_paths=["core/descriptor", "core/focus"],
        context=OracleContext.EXPLORATION,
        probability=0.4,
        cooldown_turns=2,
        narrative_injection="Your search reveals: {result}",
    ),
    # Character encounter triggers
    OracleTrigger(
        keywords=["meet", "encounter", "someone", "stranger", "person", "figure"],
        oracle_paths=["character/name", "character/role"],
        context=OracleContext.CHARACTER,
        probability=0.5,
        cooldown_turns=3,
        narrative_injection="You encounter {result}",
    ),
    # Space travel triggers
    OracleTrigger(
        keywords=["jump", "warp", "travel", "voyage", "course", "system"],
        oracle_paths=["space/stellar object", "space/sector name"],
        context=OracleContext.SPACE,
        probability=0.3,
        cooldown_turns=4,
        narrative_injection="Sensors detect {result}",
    ),
    # Settlement arrival triggers
    OracleTrigger(
        keywords=["arrive", "dock", "land", "settlement", "station", "port"],
        oracle_paths=["settlements/name", "settlements/first look"],
        context=OracleContext.SETTLEMENT,
        probability=0.5,
        cooldown_turns=5,
        narrative_injection="You arrive at {result}",
    ),
    # Derelict exploration triggers
    OracleTrigger(
        keywords=["derelict", "wreck", "abandoned", "hulk", "ruin"],
        oracle_paths=["derelicts/type", "derelicts/zone"],
        context=OracleContext.DERELICT,
        probability=0.6,
        cooldown_turns=3,
        narrative_injection="The derelict appears to be {result}",
    ),
    # Mystery/secret triggers
    OracleTrigger(
        keywords=["secret", "hidden", "mystery", "clue", "evidence"],
        oracle_paths=["core/action", "core/theme"],
        context=OracleContext.MYSTERY,
        probability=0.4,
        cooldown_turns=2,
        narrative_injection="The evidence suggests: {result}",
    ),
    # Creature encounter triggers
    OracleTrigger(
        keywords=["creature", "beast", "animal", "lifeform", "wildlife"],
        oracle_paths=["creatures/form", "creatures/behavior"],
        context=OracleContext.CREATURE,
        probability=0.5,
        cooldown_turns=3,
        narrative_injection="You observe {result}",
    ),
    # Faction triggers
    OracleTrigger(
        keywords=["faction", "organization", "guild", "group", "syndicate"],
        oracle_paths=["factions/name", "factions/influence"],
        context=OracleContext.FACTION,
        probability=0.4,
        cooldown_turns=4,
        narrative_injection="You learn of {result}",
    ),
]


@dataclass
class OracleResult:
    """Result of an oracle roll with metadata."""
    oracle_name: str
    result: str
    context: OracleContext
    was_chain: bool = False
    raw_results: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "oracle_name": self.oracle_name,
            "result": self.result,
            "context": self.context.value,
            "was_chain": self.was_chain,
            "raw_results": self.raw_results,
        }


class OracleIntegrationEngine:
    """
    Engine for deep oracle integration into narrative.

    Features:
    - Auto-triggering based on player input keywords
    - Oracle chaining for rich content
    - Cooldown management
    - Context-aware oracle selection
    - Narrative injection templates
    """

    def __init__(self, datasworn=None):
        self._datasworn = datasworn
        self._cooldowns: Dict[str, int] = {}  # trigger_key -> turns remaining
        self._recent_results: List[OracleResult] = []
        self._turn_count: int = 0

    def _get_datasworn(self):
        """Lazy-load datasworn data."""
        if self._datasworn is None:
            try:
                from src.datasworn import load_starforged_data
                self._datasworn = load_starforged_data()
            except Exception:
                pass
        return self._datasworn

    def advance_turn(self):
        """Advance turn counter and decrement cooldowns."""
        self._turn_count += 1
        for key in list(self._cooldowns.keys()):
            self._cooldowns[key] -= 1
            if self._cooldowns[key] <= 0:
                del self._cooldowns[key]

    def check_triggers(
        self,
        player_input: str,
        context_hint: Optional[OracleContext] = None
    ) -> List[OracleTrigger]:
        """Check which oracle triggers match the player input."""
        input_lower = player_input.lower()
        matched = []

        for trigger in ORACLE_TRIGGERS:
            # Check cooldown
            trigger_key = f"{trigger.context.value}_{trigger.oracle_paths[0]}"
            if trigger_key in self._cooldowns:
                continue

            # Check context hint
            if context_hint and trigger.context != context_hint:
                continue

            # Check keywords
            if any(kw in input_lower for kw in trigger.keywords):
                matched.append(trigger)

        return matched

    def should_trigger(self, trigger: OracleTrigger) -> bool:
        """Determine if a matched trigger should actually fire."""
        return random.random() < trigger.probability

    def roll_triggered_oracle(
        self,
        trigger: OracleTrigger
    ) -> Optional[OracleResult]:
        """Roll oracle(s) for a trigger."""
        datasworn = self._get_datasworn()
        if not datasworn:
            return None

        # Set cooldown
        trigger_key = f"{trigger.context.value}_{trigger.oracle_paths[0]}"
        self._cooldowns[trigger_key] = trigger.cooldown_turns

        results = []
        for path in trigger.oracle_paths:
            # Search for matching oracle
            for key in datasworn._oracles.keys():
                if path.lower() in key.lower():
                    result = datasworn.roll_oracle(key)
                    if result:
                        results.append(result)
                        break

        if not results:
            return None

        combined = " / ".join(results)

        oracle_result = OracleResult(
            oracle_name=trigger.oracle_paths[0],
            result=combined,
            context=trigger.context,
            was_chain=len(trigger.oracle_paths) > 1,
            raw_results=results,
        )

        self._recent_results.append(oracle_result)
        return oracle_result

    def roll_chain(self, chain_name: str) -> Optional[OracleResult]:
        """Roll a specific oracle chain."""
        chain = ORACLE_CHAINS.get(chain_name)
        if not chain:
            return None

        datasworn = self._get_datasworn()
        if not datasworn:
            return None

        result = chain.roll(datasworn)
        if not result:
            return None

        oracle_result = OracleResult(
            oracle_name=chain.name,
            result=result,
            context=chain.context,
            was_chain=True,
        )

        self._recent_results.append(oracle_result)
        return oracle_result

    def auto_generate(
        self,
        player_input: str,
        current_context: Optional[OracleContext] = None
    ) -> List[OracleResult]:
        """
        Automatically generate oracle results based on player input.

        This is the main method to call during narrative generation.
        Returns list of oracle results that should be woven into narrative.
        """
        self.advance_turn()
        results = []

        # Check triggers
        triggers = self.check_triggers(player_input, current_context)

        for trigger in triggers:
            if self.should_trigger(trigger):
                result = self.roll_triggered_oracle(trigger)
                if result:
                    results.append(result)

        # Check for chain opportunities based on context
        if current_context:
            for chain_name, chain in ORACLE_CHAINS.items():
                if chain.context == current_context:
                    if random.random() < chain.probability * 0.5:  # Reduce chain probability
                        result = self.roll_chain(chain_name)
                        if result:
                            results.append(result)
                            break  # Only one chain per turn

        return results

    def get_narrator_injection(
        self,
        results: List[OracleResult]
    ) -> str:
        """
        Generate narrator injection text for oracle results.

        Returns text that can be added to the narrator prompt.
        """
        if not results:
            return ""

        injections = []
        for result in results:
            # Find matching trigger for injection template
            template = "Oracle reveals: {result}"
            for trigger in ORACLE_TRIGGERS:
                if trigger.context == result.context:
                    if trigger.narrative_injection:
                        template = trigger.narrative_injection
                        break

            injections.append(template.format(result=result.result))

        return "\n".join([
            "[ORACLE INTEGRATION - WEAVE INTO NARRATIVE]",
            *injections,
            "[END ORACLE - incorporate naturally, don't quote directly]"
        ])

    def suggest_oracles_for_context(
        self,
        context: OracleContext,
        max_suggestions: int = 5
    ) -> List[str]:
        """Suggest relevant oracle paths for a given context."""
        suggestions = []

        # Direct context matches from triggers
        for trigger in ORACLE_TRIGGERS:
            if trigger.context == context:
                suggestions.extend(trigger.oracle_paths)

        # Chain matches
        for chain in ORACLE_CHAINS.values():
            if chain.context == context:
                suggestions.extend(chain.oracle_paths)

        return list(set(suggestions))[:max_suggestions]

    def generate_npc(self) -> Optional[Dict[str, str]]:
        """Generate a full NPC using oracle chains."""
        datasworn = self._get_datasworn()
        if not datasworn:
            return None

        npc = {}

        # Name
        for key in datasworn._oracles.keys():
            if "character" in key.lower() and "name" in key.lower():
                name = datasworn.roll_oracle(key)
                if name:
                    npc["name"] = name
                    break

        # Role
        for key in datasworn._oracles.keys():
            if "character" in key.lower() and "role" in key.lower():
                role = datasworn.roll_oracle(key)
                if role:
                    npc["role"] = role
                    break

        # Disposition
        for key in datasworn._oracles.keys():
            if "character" in key.lower() and "disposition" in key.lower():
                disp = datasworn.roll_oracle(key)
                if disp:
                    npc["disposition"] = disp
                    break

        # Goal (action + theme)
        action = None
        theme = None
        for key in datasworn._oracles.keys():
            if "action" in key.lower() and not action:
                action = datasworn.roll_oracle(key)
            if "theme" in key.lower() and not theme:
                theme = datasworn.roll_oracle(key)
            if action and theme:
                break

        if action and theme:
            npc["goal"] = f"{action} {theme}"

        return npc if npc else None

    def generate_location(self, location_type: str = "settlement") -> Optional[Dict[str, str]]:
        """Generate a location using oracles."""
        datasworn = self._get_datasworn()
        if not datasworn:
            return None

        location = {"type": location_type}
        type_lower = location_type.lower()

        for key in datasworn._oracles.keys():
            key_lower = key.lower()
            if type_lower in key_lower:
                if "name" in key_lower and "name" not in location:
                    result = datasworn.roll_oracle(key)
                    if result:
                        location["name"] = result
                elif "look" in key_lower and "first_look" not in location:
                    result = datasworn.roll_oracle(key)
                    if result:
                        location["first_look"] = result
                elif "trouble" in key_lower and "trouble" not in location:
                    result = datasworn.roll_oracle(key)
                    if result:
                        location["trouble"] = result

        return location if len(location) > 1 else None

    def roll_story_prompt(self) -> Optional[str]:
        """Roll a story prompt (action + theme combo)."""
        datasworn = self._get_datasworn()
        if not datasworn:
            return None

        action = None
        theme = None

        for key in datasworn._oracles.keys():
            if "action" in key.lower() and not action:
                action = datasworn.roll_oracle(key)
            if "theme" in key.lower() and not theme:
                theme = datasworn.roll_oracle(key)
            if action and theme:
                break

        if action and theme:
            return f"{action} + {theme}"
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize engine state."""
        return {
            "cooldowns": self._cooldowns,
            "turn_count": self._turn_count,
            "recent_results": [r.to_dict() for r in self._recent_results[-10:]],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OracleIntegrationEngine":
        """Deserialize engine state."""
        engine = cls()
        engine._cooldowns = data.get("cooldowns", {})
        engine._turn_count = data.get("turn_count", 0)
        return engine


# =============================================================================
# NARRATOR INTEGRATION HELPERS
# =============================================================================

def get_oracle_context_for_scene(
    location: str,
    is_combat: bool,
    recent_action: str
) -> Optional[OracleContext]:
    """Determine the most relevant oracle context for current scene."""
    location_lower = location.lower()
    action_lower = recent_action.lower()

    if is_combat:
        return OracleContext.COMBAT

    # Location-based context
    if any(w in location_lower for w in ["derelict", "wreck", "hulk", "ruin"]):
        return OracleContext.DERELICT
    if any(w in location_lower for w in ["settlement", "station", "port", "city"]):
        return OracleContext.SETTLEMENT
    if any(w in location_lower for w in ["space", "void", "system", "sector"]):
        return OracleContext.SPACE

    # Action-based context
    if any(w in action_lower for w in ["explore", "search", "investigate"]):
        return OracleContext.EXPLORATION
    if any(w in action_lower for w in ["talk", "speak", "meet", "negotiate"]):
        return OracleContext.SOCIAL
    if any(w in action_lower for w in ["discover", "find", "uncover"]):
        return OracleContext.DISCOVERY

    return None


def generate_oracle_narrative_injection(
    player_input: str,
    location: str = "",
    is_combat: bool = False,
    engine: OracleIntegrationEngine = None
) -> Tuple[str, List[OracleResult]]:
    """
    Main integration function for narrator node.

    Returns:
    - Narrator injection text
    - List of oracle results for tracking
    """
    if engine is None:
        engine = OracleIntegrationEngine()

    context = get_oracle_context_for_scene(location, is_combat, player_input)
    results = engine.auto_generate(player_input, context)

    injection = engine.get_narrator_injection(results)
    return injection, results


# =============================================================================
# MODULE TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("ORACLE INTEGRATION TEST")
    print("=" * 60)

    engine = OracleIntegrationEngine()

    # Test trigger checking
    test_inputs = [
        "I explore the abandoned corridor",
        "Let's meet whoever is in charge here",
        "We jump to the next system",
        "I search the derelict for survivors",
        "What creature is making that sound?",
    ]

    for input_text in test_inputs:
        print(f"\n--- Input: '{input_text}' ---")
        triggers = engine.check_triggers(input_text)
        print(f"Matched triggers: {[t.context.value for t in triggers]}")

        results = engine.auto_generate(input_text)
        for r in results:
            print(f"  Oracle: {r.oracle_name} -> {r.result}")

    # Test NPC generation
    print("\n--- NPC Generation ---")
    npc = engine.generate_npc()
    if npc:
        print(f"Generated NPC: {npc}")

    # Test location generation
    print("\n--- Location Generation ---")
    loc = engine.generate_location("settlement")
    if loc:
        print(f"Generated Location: {loc}")

    # Test story prompt
    print("\n--- Story Prompt ---")
    prompt = engine.roll_story_prompt()
    if prompt:
        print(f"Story Prompt: {prompt}")
