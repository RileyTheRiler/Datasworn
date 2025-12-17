"""
Intent Prediction System using N-gram Pattern Matching.
Predicts player intent to preload context and speed up responses.

Based on Game AI Pro patterns for player behavior prediction.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict
from typing import Any
import re


# ============================================================================
# Intent Categories
# ============================================================================

class IntentCategory:
    """Categorization of player intents."""
    COMBAT = "combat"
    EXPLORATION = "exploration"
    SOCIAL = "social"
    CRAFTING = "crafting"
    QUEST = "quest"
    MOVEMENT = "movement"
    INVENTORY = "inventory"
    STEALTH = "stealth"
    INVESTIGATION = "investigation"
    REST = "rest"


# Keyword mappings for quick intent detection
INTENT_KEYWORDS = {
    IntentCategory.COMBAT: [
        "attack", "fight", "shoot", "strike", "kill", "stab", "punch",
        "defend", "dodge", "block", "fire", "swing", "slash", "combat",
    ],
    IntentCategory.EXPLORATION: [
        "explore", "search", "look", "examine", "investigate", "check",
        "find", "discover", "wander", "travel", "scout",
    ],
    IntentCategory.SOCIAL: [
        "talk", "speak", "ask", "tell", "convince", "persuade", "negotiate",
        "greet", "threaten", "bribe", "flirt", "charm", "lie",
    ],
    IntentCategory.CRAFTING: [
        "craft", "build", "make", "create", "repair", "modify", "upgrade",
        "forge", "assemble", "construct",
    ],
    IntentCategory.QUEST: [
        "accept", "complete", "vow", "swear", "fulfill", "abandon",
        "progress", "objective", "goal", "mission",
    ],
    IntentCategory.MOVEMENT: [
        "go", "move", "walk", "run", "travel", "head", "enter", "leave",
        "return", "flee", "escape", "approach", "follow",
    ],
    IntentCategory.INVENTORY: [
        "take", "grab", "pick", "drop", "give", "use", "equip", "unequip",
        "open", "close", "inventory", "loot",
    ],
    IntentCategory.STEALTH: [
        "sneak", "hide", "stealth", "creep", "silent", "shadow",
        "ambush", "spy", "eavesdrop",
    ],
    IntentCategory.INVESTIGATION: [
        "examine", "inspect", "analyze", "study", "read", "decipher",
        "research", "learn", "understand",
    ],
    IntentCategory.REST: [
        "rest", "sleep", "camp", "heal", "recover", "wait", "meditate",
    ],
}


# ============================================================================
# N-gram Model
# ============================================================================

@dataclass
class ActionSequence:
    """A recorded sequence of player actions."""
    actions: list[str] = field(default_factory=list)
    intents: list[str] = field(default_factory=list)
    timestamp: int = 0  # Scene number


class NGramPredictor:
    """
    Predicts next player action based on N-gram analysis.
    Learns from player's action history.
    """
    
    def __init__(self, n: int = 3):
        self.n = n  # Size of the N-gram (e.g., 3 = trigram)
        self.ngram_counts: dict[tuple, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.action_history: list[str] = []
        self.intent_history: list[str] = []
        self.total_actions: int = 0
    
    def record_action(self, action: str, intent: str = "") -> None:
        """Record a player action."""
        # Normalize action
        action_lower = action.lower().strip()
        
        # Auto-detect intent if not provided
        if not intent:
            intent = self._detect_intent(action_lower)
        
        # Update history
        self.action_history.append(action_lower)
        self.intent_history.append(intent)
        self.total_actions += 1
        
        # Update N-gram counts
        if len(self.action_history) >= self.n:
            context = tuple(self.intent_history[-(self.n):])
            # The "next" action for this context
            if len(self.intent_history) > self.n:
                next_intent = self.intent_history[-1]
                prev_context = tuple(self.intent_history[-(self.n+1):-1])
                self.ngram_counts[prev_context][next_intent] += 1
    
    def _detect_intent(self, action: str) -> str:
        """Detect intent from action text."""
        action_words = set(re.findall(r'\w+', action.lower()))
        
        best_intent = IntentCategory.EXPLORATION  # Default
        best_score = 0
        
        for intent, keywords in INTENT_KEYWORDS.items():
            score = len(action_words.intersection(keywords))
            if score > best_score:
                best_score = score
                best_intent = intent
        
        return best_intent
    
    def predict_next(self, n_predictions: int = 3) -> list[tuple[str, float]]:
        """
        Predict the most likely next intents.
        
        Returns:
            List of (intent, probability) tuples
        """
        if len(self.intent_history) < self.n - 1:
            # Not enough history, return defaults
            return [
                (IntentCategory.EXPLORATION, 0.3),
                (IntentCategory.COMBAT, 0.2),
                (IntentCategory.SOCIAL, 0.2),
            ]
        
        # Get current context
        context = tuple(self.intent_history[-(self.n-1):])
        
        # Check if we have data for this context
        if context not in self.ngram_counts:
            # Fall back to (n-1)-gram or unigram
            return self._fallback_prediction(n_predictions)
        
        # Calculate probabilities
        counts = self.ngram_counts[context]
        total = sum(counts.values())
        
        predictions = []
        for intent, count in counts.items():
            prob = count / total
            predictions.append((intent, prob))
        
        # Sort by probability
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        return predictions[:n_predictions]
    
    def _fallback_prediction(self, n: int) -> list[tuple[str, float]]:
        """Fallback prediction using overall intent frequencies."""
        if not self.intent_history:
            return [(IntentCategory.EXPLORATION, 0.5)]
        
        # Count all intents
        counts: dict[str, int] = defaultdict(int)
        for intent in self.intent_history:
            counts[intent] += 1
        
        total = len(self.intent_history)
        predictions = [(intent, count / total) for intent, count in counts.items()]
        predictions.sort(key=lambda x: x[1], reverse=True)
        
        return predictions[:n]
    
    def get_likely_context_type(self) -> str:
        """
        Get the most likely context type for preloading.
        
        Returns:
            Context type string for the system to preload
        """
        predictions = self.predict_next(1)
        if not predictions:
            return "general"
        
        top_intent = predictions[0][0]
        
        # Map intents to context types
        context_mapping = {
            IntentCategory.COMBAT: "combat",
            IntentCategory.SOCIAL: "dialogue",
            IntentCategory.EXPLORATION: "exploration",
            IntentCategory.QUEST: "quest",
            IntentCategory.INVESTIGATION: "lore",
            IntentCategory.STEALTH: "stealth",
        }
        
        return context_mapping.get(top_intent, "general")
    
    def get_prediction_context(self) -> str:
        """Generate context about predicted intent for the narrator."""
        predictions = self.predict_next(2)
        
        if not predictions:
            return ""
        
        lines = ["[PREDICTED PLAYER INTENT]"]
        for intent, prob in predictions:
            if prob > 0.2:
                lines.append(f"- {intent.capitalize()}: {prob:.0%} likely")
        
        return "\n".join(lines)
    
    def get_action_patterns(self) -> dict:
        """Get analysis of player's action patterns."""
        if not self.intent_history:
            return {"patterns": [], "dominant_style": "unknown"}
        
        # Count intent frequencies
        counts: dict[str, int] = defaultdict(int)
        for intent in self.intent_history:
            counts[intent] += 1
        
        total = len(self.intent_history)
        
        # Find dominant playstyle
        if counts.get(IntentCategory.COMBAT, 0) > total * 0.4:
            style = "aggressive"
        elif counts.get(IntentCategory.SOCIAL, 0) > total * 0.3:
            style = "diplomatic"
        elif counts.get(IntentCategory.STEALTH, 0) > total * 0.2:
            style = "stealthy"
        elif counts.get(IntentCategory.EXPLORATION, 0) > total * 0.4:
            style = "explorer"
        else:
            style = "balanced"
        
        # Find common sequences
        common_sequences = []
        for context, next_counts in self.ngram_counts.items():
            for next_intent, count in next_counts.items():
                if count >= 3:  # Pattern appears at least 3 times
                    seq = list(context) + [next_intent]
                    common_sequences.append((seq, count))
        
        common_sequences.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "total_actions": self.total_actions,
            "dominant_style": style,
            "intent_distribution": dict(counts),
            "common_patterns": common_sequences[:5],
        }
    
    def to_dict(self) -> dict:
        return {
            "n": self.n,
            "ngram_counts": {
                str(k): dict(v) for k, v in self.ngram_counts.items()
            },
            "action_history": self.action_history[-100:],  # Keep last 100
            "intent_history": self.intent_history[-100:],
            "total_actions": self.total_actions,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "NGramPredictor":
        predictor = cls(n=data.get("n", 3))
        predictor.action_history = data.get("action_history", [])
        predictor.intent_history = data.get("intent_history", [])
        predictor.total_actions = data.get("total_actions", 0)
        
        for context_str, counts in data.get("ngram_counts", {}).items():
            # Parse string tuple back to tuple
            context = eval(context_str)  # Safe for our controlled format
            predictor.ngram_counts[context] = defaultdict(int, counts)
        
        return predictor


# ============================================================================
# Convenience Functions
# ============================================================================

def create_intent_predictor(n: int = 3) -> NGramPredictor:
    """Create a new intent predictor."""
    return NGramPredictor(n=n)


def quick_intent_detection(action: str) -> str:
    """Quick single-action intent detection."""
    predictor = NGramPredictor()
    return predictor._detect_intent(action)


def get_recommended_context(predictions: list[tuple[str, float]]) -> list[str]:
    """
    Get recommended context types to preload based on predictions.
    
    Returns:
        List of context module names to preload
    """
    if not predictions:
        return ["general"]
    
    contexts = []
    for intent, prob in predictions:
        if prob > 0.15:
            if intent == IntentCategory.COMBAT:
                contexts.extend(["combat", "enemies", "weapons"])
            elif intent == IntentCategory.SOCIAL:
                contexts.extend(["npcs", "dialogue", "reputation"])
            elif intent == IntentCategory.EXPLORATION:
                contexts.extend(["locations", "lore", "discoveries"])
            elif intent == IntentCategory.QUEST:
                contexts.extend(["vows", "objectives", "rewards"])
            elif intent == IntentCategory.INVESTIGATION:
                contexts.extend(["lore", "clues", "secrets"])
    
    return list(set(contexts)) or ["general"]
