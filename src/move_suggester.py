"""
Move Suggester - Help players learn the Starforged move set.
Suggests appropriate moves based on player intent description.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Optional
import re

from src.logging_config import get_logger

logger = get_logger("move_suggester")


@dataclass
class MoveSuggestion:
    """A suggested move with explanation."""
    move_name: str
    stat: str
    confidence: float  # 0.0 to 1.0
    reason: str
    trigger_phrase: str
    outcome_preview: str
    odds_hint: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "move_name": self.move_name,
            "stat": self.stat,
            "confidence": self.confidence,
            "reason": self.reason,
            "trigger_phrase": self.trigger_phrase,
            "outcome_preview": self.outcome_preview,
            "odds_hint": self.odds_hint,
        }


# Move definitions with triggers and stats
STARFORGED_MOVES = {
    # Adventure Moves
    "face_danger": {
        "name": "Face Danger",
        "stats": ["edge", "heart", "iron", "shadow", "wits"],
        "stat_contexts": {
            "edge": "speed, mobility, agility",
            "heart": "resolve, leadership, charm",
            "iron": "strength, endurance, aggression",
            "shadow": "deception, stealth, trickery",
            "wits": "expertise, focus, observation",
        },
        "keywords": ["overcome", "react", "push through", "resist", "endure", "avoid", "escape", "survive", "face"],
        "trigger": "When you attempt something risky or react to an imminent threat",
        "outcomes": {
            "strong_hit": "You succeed. Take +1 momentum.",
            "weak_hit": "You succeed, but with a cost or complication.",
            "miss": "You fail, or succeed at a steep cost.",
        },
    },
    "secure_an_advantage": {
        "name": "Secure an Advantage",
        "stats": ["edge", "heart", "iron", "shadow", "wits"],
        "stat_contexts": {
            "edge": "speed, mobility",
            "heart": "resolve, charm",
            "iron": "strength, aggression",
            "shadow": "deception, stealth",
            "wits": "expertise, observation",
        },
        "keywords": ["prepare", "position", "ready", "plan", "scout", "analyze", "study", "set up", "gain advantage"],
        "trigger": "When you assess a situation, make preparations, or try to gain leverage",
        "outcomes": {
            "strong_hit": "Gain an advantage. Take +2 momentum or +1 on your next move.",
            "weak_hit": "Gain advantage, but with a cost.",
            "miss": "Your attempt backfires. Pay the Price.",
        },
    },
    "gather_information": {
        "name": "Gather Information",
        "stats": ["wits", "shadow", "heart"],
        "stat_contexts": {
            "wits": "observation, expertise, analysis",
            "shadow": "infiltration, eavesdropping",
            "heart": "persuading someone to share",
        },
        "keywords": ["investigate", "search", "scan", "analyze", "research", "ask", "look for", "examine", "learn", "discover"],
        "trigger": "When you search for clues, conduct an investigation, or ask questions",
        "outcomes": {
            "strong_hit": "Discover something useful. Take +2 momentum.",
            "weak_hit": "Information comes at a cost or is incomplete.",
            "miss": "Reveal a dire threat or unwelcome truth.",
        },
    },
    "compel": {
        "name": "Compel",
        "stats": ["heart", "iron", "shadow"],
        "stat_contexts": {
            "heart": "charm, pacify, encourage",
            "iron": "threaten, intimidate",
            "shadow": "deceive, manipulate",
        },
        "keywords": ["convince", "persuade", "threaten", "intimidate", "negotiate", "bribe", "charm", "seduce", "manipulate", "deceive", "lie"],
        "trigger": "When you try to persuade someone or make them do what you want",
        "outcomes": {
            "strong_hit": "They do what you want.",
            "weak_hit": "They comply, but want something in return.",
            "miss": "They refuse and the situation worsens.",
        },
    },

    # Combat Moves
    "enter_the_fray": {
        "name": "Enter the Fray",
        "stats": ["heart", "shadow", "wits"],
        "stat_contexts": {
            "heart": "facing danger head-on, protecting others",
            "shadow": "ambush, deception",
            "wits": "tactical advantage, prepared",
        },
        "keywords": ["attack", "fight", "combat", "battle", "ambush", "engage", "draw weapon", "strike first"],
        "trigger": "When you initiate combat or are forced into a fight",
        "outcomes": {
            "strong_hit": "Take initiative. +2 momentum.",
            "weak_hit": "Choose: bolster position or take initiative.",
            "miss": "Combat begins badly. Pay the Price.",
        },
    },
    "strike": {
        "name": "Strike",
        "stats": ["iron", "edge"],
        "stat_contexts": {
            "iron": "in close combat, brute force",
            "edge": "at range, with precision",
        },
        "keywords": ["hit", "attack", "shoot", "slash", "punch", "stab", "strike", "fire"],
        "trigger": "When you attack in combat",
        "outcomes": {
            "strong_hit": "Inflict harm. +1 momentum.",
            "weak_hit": "Inflict harm, but exposed to danger.",
            "miss": "Attack fails. Pay the Price.",
        },
    },
    "clash": {
        "name": "Clash",
        "stats": ["iron", "edge"],
        "stat_contexts": {
            "iron": "close quarters",
            "edge": "at range",
        },
        "keywords": ["counter", "trade blows", "fight back", "exchange", "clash"],
        "trigger": "When you fight back against an attacker",
        "outcomes": {
            "strong_hit": "Inflict harm and avoid their attack.",
            "weak_hit": "Trade harm for harm.",
            "miss": "Suffer harm without dealing it.",
        },
    },

    # Connection Moves
    "make_a_connection": {
        "name": "Make a Connection",
        "stats": ["heart"],
        "stat_contexts": {
            "heart": "building rapport and trust",
        },
        "keywords": ["meet", "befriend", "connect", "introduce", "ally", "recruit", "bond", "relationship"],
        "trigger": "When you try to establish a bond with someone",
        "outcomes": {
            "strong_hit": "Connection made. Mark progress on bond track.",
            "weak_hit": "Connection is tenuous or complicated.",
            "miss": "They reject you or have ulterior motives.",
        },
    },
    "aid_your_ally": {
        "name": "Aid Your Ally",
        "stats": ["heart", "wits", "iron"],
        "stat_contexts": {
            "heart": "encouragement, moral support",
            "wits": "providing information, guidance",
            "iron": "physical assistance, protection",
        },
        "keywords": ["help", "assist", "support", "aid", "protect", "back up", "cover"],
        "trigger": "When you try to help an ally",
        "outcomes": {
            "strong_hit": "They gain +1 on their move.",
            "weak_hit": "You expose yourself to danger.",
            "miss": "Your help backfires.",
        },
    },

    # Exploration Moves
    "undertake_an_expedition": {
        "name": "Undertake an Expedition",
        "stats": ["wits", "edge", "shadow"],
        "stat_contexts": {
            "wits": "careful navigation",
            "edge": "speed, outpacing threats",
            "shadow": "stealth, avoiding detection",
        },
        "keywords": ["travel", "journey", "expedition", "navigate", "explore", "trek", "voyage", "set course"],
        "trigger": "When you travel through dangerous or unknown territory",
        "outcomes": {
            "strong_hit": "Mark progress. +1 momentum.",
            "weak_hit": "Mark progress but face a peril.",
            "miss": "Face a crisis or setback.",
        },
    },
    "explore_a_waypoint": {
        "name": "Explore a Waypoint",
        "stats": ["wits"],
        "stat_contexts": {
            "wits": "careful observation and investigation",
        },
        "keywords": ["explore", "search location", "investigate area", "look around", "survey"],
        "trigger": "When you explore a notable location during an expedition",
        "outcomes": {
            "strong_hit": "Make a discovery. +2 momentum.",
            "weak_hit": "Discover something, but it's complicated.",
            "miss": "Face a danger or setback.",
        },
    },
}


def suggest_moves(player_input: str, max_suggestions: int = 3) -> list[MoveSuggestion]:
    """
    Analyze player input and suggest appropriate moves.

    Args:
        player_input: What the player wants to do
        max_suggestions: Maximum number of suggestions to return

    Returns:
        List of MoveSuggestion objects, sorted by confidence
    """
    input_lower = player_input.lower()
    suggestions = []

    for move_id, move_data in STARFORGED_MOVES.items():
        # Calculate keyword matches
        keyword_matches = sum(
            1 for kw in move_data["keywords"]
            if kw in input_lower
        )

        if keyword_matches == 0:
            continue

        confidence = min(keyword_matches * 0.3, 0.9)

        # Determine best stat based on context
        best_stat = move_data["stats"][0]
        best_stat_reason = move_data["stat_contexts"].get(best_stat, "")

        # Try to match stat context to input
        for stat, context in move_data.get("stat_contexts", {}).items():
            context_words = context.lower().split(", ")
            if any(word in input_lower for word in context_words):
                best_stat = stat
                best_stat_reason = context
                confidence += 0.1
                break

        # Build reason
        matched_keywords = [kw for kw in move_data["keywords"] if kw in input_lower]
        reason = f"Your action mentions: {', '.join(matched_keywords[:3])}"

        odds_hint = f"Best stat: {best_stat.title()} ({best_stat_reason})"

        # Build outcome preview
        outcomes = move_data.get("outcomes", {})
        outcome_preview = (
            f"Strong Hit: {outcomes.get('strong_hit', 'Success')} | "
            f"Weak Hit: {outcomes.get('weak_hit', 'Partial success')} | "
            f"Miss: {outcomes.get('miss', 'Failure')}"
        )

        suggestions.append(MoveSuggestion(
            move_name=move_data["name"],
            stat=best_stat.title(),
            confidence=min(confidence, 1.0),
            reason=reason,
            trigger_phrase=move_data["trigger"],
            outcome_preview=outcome_preview,
            odds_hint=odds_hint,
        ))

    # Sort by confidence descending
    suggestions.sort(key=lambda x: x.confidence, reverse=True)

    return suggestions[:max_suggestions]


def get_move_help(move_name: str) -> Optional[dict[str, Any]]:
    """
    Get detailed help for a specific move.

    Args:
        move_name: Name of the move

    Returns:
        Dict with move details or None if not found
    """
    # Normalize move name
    normalized = move_name.lower().replace(" ", "_").replace("'", "")

    move_data = STARFORGED_MOVES.get(normalized)
    if not move_data:
        # Try partial match
        for move_id, data in STARFORGED_MOVES.items():
            if normalized in move_id or normalized in data["name"].lower():
                move_data = data
                break

    if not move_data:
        return None

    return {
        "name": move_data["name"],
        "trigger": move_data["trigger"],
        "stats": [
            {"stat": stat.title(), "when": move_data["stat_contexts"].get(stat, "")}
            for stat in move_data["stats"]
        ],
        "outcomes": move_data["outcomes"],
        "keywords": move_data["keywords"],
    }


def format_suggestions_for_display(suggestions: list[MoveSuggestion]) -> str:
    """
    Format move suggestions for text display.

    Args:
        suggestions: List of MoveSuggestion objects

    Returns:
        Formatted string for display
    """
    if not suggestions:
        return "No specific move matches. Describe your action and the Oracle will interpret."

    lines = ["**Suggested Moves:**\n"]

    for i, s in enumerate(suggestions, 1):
        confidence_bar = "●" * int(s.confidence * 5) + "○" * (5 - int(s.confidence * 5))
        lines.append(f"{i}. **{s.move_name}** ({s.stat}) [{confidence_bar}]")
        lines.append(f"   *{s.trigger_phrase}*")
        lines.append(f"   {s.reason}")
        if s.odds_hint:
            lines.append(f"   {s.odds_hint}")
        lines.append("")

    lines.append("*Type the move name to roll, or continue describing your action.*")

    return "\n".join(lines)


def should_suggest_moves(player_input: str) -> bool:
    """
    Determine if we should suggest moves for this input.

    Args:
        player_input: What the player typed

    Returns:
        True if we should show move suggestions
    """
    # Don't suggest for very short inputs
    if len(player_input.split()) < 3:
        return False

    # Don't suggest if already naming a move
    input_lower = player_input.lower()
    for move_id, move_data in STARFORGED_MOVES.items():
        if move_data["name"].lower() in input_lower:
            return False

    # Don't suggest for commands
    if player_input.startswith("!") or player_input.startswith("/"):
        return False

    # Check if any action keywords present
    all_keywords = set()
    for move_data in STARFORGED_MOVES.values():
        all_keywords.update(move_data["keywords"])

    return any(kw in input_lower for kw in all_keywords)
